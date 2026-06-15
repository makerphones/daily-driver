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
import cadquery as cq

from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.bow import make_bow

# render.py is RENDER-ONLY (matplotlib). Guarded so the core build never depends
# on it: no matplotlib → rendering simply skips, parts still build.
try:
    from render import render as _render
    _HAVE_RENDER = True
except Exception:  # noqa: BLE001 — ImportError or backend issue → skip rendering
    _HAVE_RENDER = False

# Printed parts → STL + STEP.
PRINTED = {
    "cup": make_cup,
    "baffle": make_baffle,
    "yoke": make_yoke,
    "slider": make_slider,
}
# Reference bodies → STEP only (NOT printed).
REFERENCE = {
    "bow": make_bow,
}
PARTS = {**PRINTED, **REFERENCE}

OUT = "output"
RENDERS = "renders"                                  # ships with the design (NOT gitignored)
MODELS = os.path.join("docs", "models")              # Pages-served GLB target
GLB_PATH = os.path.join(MODELS, "daily-driver.glb")


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
            if name in PRINTED:
                stl_path = os.path.join(OUT, f"{name}.stl")
                cq.exporters.export(model, stl_path)
                print(f"  [ok]   {name}.stl + {name}.step")
                _render_part(stl_path, name)
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
            print("  [ok]   assembly.step (cup + baffle + yoke + slider + bow ref)")
            # Web-viewable GLB for the Pages build page (model-viewer). Committed
            # as a published artifact (unlike the gitignored working STL/STEP).
            try:
                os.makedirs(MODELS, exist_ok=True)
                asm.export(GLB_PATH, exportType="GLTF",
                           tolerance=0.05, angularTolerance=0.1)
                print(f"  [ok]   {GLB_PATH} (web 3D viewer)")
            except Exception as e:  # noqa: BLE001
                print(f"  [warn] GLB export skipped: {e}")
        except Exception as e:
            print(f"  [FAIL] assembly: {e}")

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
