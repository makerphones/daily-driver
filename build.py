# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Build all parts to output/.

Printed parts (cup, baffle, fork-yoke, slider) export as both STL (ready to
print) and STEP (clean B-rep). The BOW is a REFERENCE body (bought Beyer part /
DIY blank) — STEP only, never in the printed-STL set. One failing part won't stop
the others; you get a per-part status so you can iterate on just one part.

Side effects beyond output/:
  - renders/   headless front/iso/side PNGs per printed part (render.py). Needs
               matplotlib (requirements-dev.txt); SKIPPED cleanly if absent, so a
               forker with only the core deps still builds parts.
  - docs/models/daily-driver.glb   the assembly as a web-viewable GLB for the
               Pages build page (model-viewer). An intentional published artifact.

Usage:
    python build.py            # build everything
    python build.py cup baffle # build only named parts
"""

import sys
import os
import json
import shutil
import cadquery as cq

from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.bow import make_bow
from parts.adapter_ring import make_adapter_ring
from parts.headband_pad import make_headband_pad
from parts.grille_dot import make_grille_dot
from parts.driver_clamp import make_driver_clamp

# render.py is RENDER-ONLY (matplotlib). Guarded so the core build never depends
# on it: no matplotlib → rendering simply skips, parts still build.
try:
    from render import render as _render
    _HAVE_RENDER = True
except Exception:  # noqa: BLE001 — ImportError or backend issue → skip rendering
    _HAVE_RENDER = False

# Printed parts → STL + STEP. The earcup is a one-piece cup (integral lattice
# grille + buttressed baffle bosses + the yoke pivots + the pad lip).
PRINTED = {
    "cup": make_cup,
    "baffle": make_baffle,
    "yoke": make_yoke,
    "slider": make_slider,
}
# Printable ACCESSORIES → STL + STEP, but NOT part of the reference assembly
# (e.g. the step-down driver adapter ring — an optional "design big, adapt down").
ACCESSORY = {
    "driver_clamp": make_driver_clamp,
    "adapter_ring": make_adapter_ring,
    "headband_pad": make_headband_pad,
    "grille_dot": make_grille_dot,
}
# Reference bodies → STEP only (NOT printed).
REFERENCE = {
    "bow": make_bow,
}
PARTS = {**PRINTED, **ACCESSORY, **REFERENCE}

OUT = "output"
RENDERS = "renders"                                  # ships with the design (NOT gitignored)
MODELS = os.path.join("docs", "models")              # Pages-served GLB target
GLB_PATH = os.path.join(MODELS, "daily-driver.glb")
GROUPS_PATH = os.path.join(MODELS, "daily-driver.groups.json")


def _render_part(stl_path, name):
    """Best-effort multi-view PNGs. A render failure NEVER fails the build."""
    if not _HAVE_RENDER:
        return
    try:
        _render(stl_path, RENDERS, name)
        print(f"           ↳ renders/{name}_{{front,iso,side}}.png")
    except Exception as e:  # noqa: BLE001 — report, never fail the build
        print(f"           ↳ [warn] render skipped for {name}: {e}")


def build(names):
    os.makedirs(OUT, exist_ok=True)
    ok, failed = [], []
    for name in names:
        try:
            model = PARTS[name]()
            cq.exporters.export(model, os.path.join(OUT, f"{name}.step"))
            if name in PRINTED or name in ACCESSORY:
                stl_path = os.path.join(OUT, f"{name}.stl")
                cq.exporters.export(model, stl_path)
                tag = "" if name in PRINTED else "  (ACCESSORY — not in the assembly)"
                print(f"  [ok]   {name}.stl + {name}.step{tag}")
                _render_part(stl_path, name)
                # Per-part GLB for the website parts gallery's 3D view (a COMMITTED
                # artifact in docs/models/, served from Pages alongside the assembly
                # GLB). A neutral mid-grey so the geometry reads in the viewer's
                # neutral environment (the dark charcoal was hard to see). Best-effort.
                try:
                    os.makedirs(MODELS, exist_ok=True)
                    part_asm = cq.Assembly(model, name=name,
                                           color=cq.Color(0.62, 0.64, 0.67))
                    part_asm.export(os.path.join(MODELS, f"{name}.glb"),
                                    exportType="GLTF", tolerance=0.05, angularTolerance=0.1)
                    print(f"           ↳ {MODELS}/{name}.glb (web part viewer)")
                except Exception as e:  # noqa: BLE001 — never fail the build on a GLB
                    print(f"           ↳ [warn] GLB skipped for {name}: {e}")
            else:
                print(f"  [ok]   {name}.step  (REFERENCE — not printed)")
            ok.append(name)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed.append(name)

    # Full side assembly (cup + baffle + yoke + slider + bow ref), isolated.
    if PRINTED.keys() <= set(names):
        try:
            from assembly import make_assembly
            asm = make_assembly()
            asm.export(os.path.join(OUT, "assembly.step"))
            print("  [ok]   assembly.step (frame + module + baffle + yoke + slider + bow ref)")
            # Web-viewable GLB for the Pages build page (model-viewer). Committed
            # as a published artifact (unlike the gitignored working STL/STEP).
            try:
                os.makedirs(MODELS, exist_ok=True)
                asm.export(GLB_PATH, exportType="GLTF",
                           tolerance=0.05, angularTolerance=0.1)
                print(f"  [ok]   {GLB_PATH} (web 3D viewer)")
                # Sub-assembly manifest the manual's parts viewer fetches (groups +
                # node names). Single source: assembly.SUBASSEMBLIES. Committed next
                # to the GLB and served from the same Pages origin.
                from assembly import SUBASSEMBLIES
                with open(GROUPS_PATH, "w") as gf:
                    json.dump(SUBASSEMBLIES, gf, indent=2)
                print(f"  [ok]   {GROUPS_PATH} (sub-assembly manifest)")
            except Exception as e:  # noqa: BLE001
                print(f"  [warn] GLB/manifest export skipped: {e}")
        except Exception as e:
            print(f"  [FAIL] assembly: {e}")

        # Hardware BOM — what a forker needs to source (part of the open product,
        # like the DESIGN-LOG). Derived from params, so it tracks the design.
        try:
            from bom import write_bom
            print(f"  [ok]   {write_bom()} (hardware bill of materials)")
        except Exception as e:  # noqa: BLE001 — never fail the build on the BOM
            print(f"  [warn] BOM.md skipped: {e}")

    # Mirror the per-part renders into docs/ so GitHub Pages serves them at
    # /renders/<name>.png — the manual's parts gallery uses them as posters from the
    # SAME cross-origin origin as the GLB (renders/ at the repo root is not served).
    if os.path.isdir(RENDERS):
        docs_renders = os.path.join("docs", "renders")
        os.makedirs(docs_renders, exist_ok=True)
        copied = 0
        for fn in os.listdir(RENDERS):
            if fn.endswith(".png"):
                shutil.copy2(os.path.join(RENDERS, fn), os.path.join(docs_renders, fn))
                copied += 1
        if copied:
            print(f"  [ok]   docs/renders/ ({copied} part posters for the manual)")

    print(f"\nBuilt {len(ok)}/{len(names)}: {', '.join(ok) or 'none'}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    requested = sys.argv[1:] or list(PARTS.keys())
    unknown = [n for n in requested if n not in PARTS]
    if unknown:
        print(f"Unknown part(s): {', '.join(unknown)}")
        print(f"Available: {', '.join(PARTS)}")
        sys.exit(2)
    print("Building Daily Driver parts...\n")
    build(requested)
