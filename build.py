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
from parts.slider_shoe import make_slider_shoe
from parts.bow import make_bow
from parts.adapter_ring import make_adapter_ring
from parts.headband_pad import make_headband_pad
from parts.grille_dot import make_grille_dot
from parts.driver_clamp import make_driver_clamp
from parts.driver import make_driver
from parts.earpad import make_earpad
from parts.headband_clamp import make_headband_clamp
from parts.yoke_rod import make_yoke_rod
from parts.vent_plug import make_vent_plug
from parts.coupon import make_driver_coupon, make_pad_coupon

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
    "headband_clamp": make_headband_clamp,
    "slider_shoe": make_slider_shoe,
    "vent_plug": make_vent_plug,
}
# Fit coupons → STL + STEP (printed for QA), but NOT in the reference assembly and
# NOT in the web parts gallery: they isolate a toleranced interface so it can be
# checked against real hardware before a full cup/baffle print. QA tools, not product.
COUPON = {
    "driver_coupon": make_driver_coupon,
    "pad_coupon": make_pad_coupon,
}
# Reference bodies → STEP only (NOT printed): the bought metal bow + a representative
# driver MOCKUP (shown in the assembly so the driver↔baffle↔clamp fit reads).
REFERENCE = {
    "bow": make_bow,
    "yoke_rod": make_yoke_rod,
    "driver": make_driver,
    "earpad": make_earpad,
}
PARTS = {**PRINTED, **ACCESSORY, **COUPON, **REFERENCE}

# One-line role per part — the only hand-kept column in the generated inventory
# (lives next to the dicts so it can't drift far). Counts/categories/output type are
# all derived, so docs/PARTS.md tracks the design automatically (see gen_parts_doc).
PART_ROLES = {
    "cup": "earcup shell — integral lattice grille, baffle bosses, pivot bosses, pad lip",
    "baffle": "front driver plate — aperture, guard, controlled vents, driver seat + collar",
    "yoke": "fork — tilts on the cup pivot, carries the height-adjust post",
    "slider": "headband clamp + post barrel — height lock (knob → shoe → post) + swivel",
    "driver_clamp": "3-ear ring retaining the driver against the baffle back",
    "adapter_ring": "step-down ring to host a smaller driver in a bigger baffle (optional)",
    "headband_pad": "crown cushion under the bow (TPU)",
    "grille_dot": "press-in accent cap at the grille centre (the mark's orange dot)",
    "headband_clamp": "inner cover plate that sandwiches the metal bow end",
    "slider_shoe": "captive pressure shoe — knob presses it onto the post (no marring)",
    "vent_plug": "press-fit plug for the closed-back tuning ports (reversible openness knob)",
    "driver_coupon": "FIT COUPON — driver seat/collar + clamp standoff interface (QA)",
    "pad_coupon": "FIT COUPON — pad-skirt grip on the cup OD (QA)",
    "bow": "bought Beyer metal head bow (917017/973361) or DIY spring-steel blank (reference)",
    "yoke_rod": "the adjustment-post shoulder screw, ISO 7379 Ø6×M5×50 (reference viz)",
    "driver": "representative 40 mm driver mockup (reference)",
    "earpad": "representative round earpad mockup (reference)",
}

OUT = "output"
RENDERS = "renders"                                  # ships with the design (NOT gitignored)
MODELS = os.path.join("docs", "models")              # Pages-served GLB target
GLB_PATH = os.path.join(MODELS, "daily-driver.glb")
GROUPS_PATH = os.path.join(MODELS, "daily-driver.groups.json")


def gen_parts_doc(path=os.path.join("docs", "PARTS.md")):
    """Write docs/PARTS.md — the live part inventory + counts, DERIVED from the part
    category dicts so the 'N parts' figure quoted elsewhere can never go stale. This is
    the auto-update half of the stale-doc fix: counts, categories, and output type are
    computed; only PART_ROLES is hand-kept (next to the dicts)."""
    cats = [
        ("Printed", PRINTED, "STL + STEP"),
        ("Accessory — printed, not in the reference assembly", ACCESSORY, "STL + STEP"),
        ("Fit coupon — printed QA tool, not in the assembly", COUPON, "STL + STEP"),
        ("Reference — not printed (bought part / mockup)", REFERENCE, "STEP only"),
    ]
    lines = [
        "# Daily Driver — parts inventory",
        "",
        "**Generated by `build.py` — do not hand-edit; add/remove parts in `build.py`.**",
        "",
        f"**{len(PARTS)} parts total** — {len(PRINTED)} printed · {len(ACCESSORY)} accessory · "
        f"{len(COUPON)} fit coupon · {len(REFERENCE)} reference. A full `build.py` / `gate.py` "
        f"run reports **{len(PARTS)}/{len(PARTS)}**. Sourcing + quantities are in `BOM.md`.",
        "",
    ]
    for title, d, out in cats:
        lines += [f"## {title}", "", "| Part | Output | Role |", "|---|---|---|"]
        lines += [f"| `{name}` | {out} | {PART_ROLES.get(name, '')} |" for name in d]
        lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


def gen_acoustics_doc(path=os.path.join("docs", "ACOUSTICS.md")):
    """Write docs/ACOUSTICS.md — the computed acoustic VOLUMES + the parametric tuning controls,
    derived from params so the figures can't drift. (Acoustic *tuning* — the real damping amount,
    vent open-area, etc. — is measurement-gated; these are the parametric starting points.)"""
    from params import P
    back = "OPEN rear grille" if P.cup_open_back else "CLOSED back + tuning ports"
    total = P.cup_interior_volume_cc + P.front_cavity_volume_cc
    lines = [
        "# Daily Driver — acoustic summary",
        "",
        "**Generated by `build.py` — do not hand-edit; change `params.py`.** Figures are computed",
        "from the geometry, so they track the design. Acoustic *tuning* (real damping amount, vent",
        "open-area, exact volume target) is measurement-gated — these are the parametric starting points.",
        "",
        "## Acoustic volumes",
        "",
        "| Cavity | Volume | Set by |",
        "|---|---|---|",
        f"| Rear (cup interior) | **{P.cup_interior_volume_cc:.0f} cc** | ⌀{P.cup_interior_diameter:.0f} mm × {P.cup_depth:.0f} mm deep |",
        f"| Front (ear ↔ baffle) | **{P.front_cavity_volume_cc:.0f} cc** | pad opening ⌀{P.earpad_inner_diameter:.0f} mm × {P.earpad_depth:.0f} mm pad depth |",
        f"| **Total** | **{total:.0f} cc** | |",
        "",
        "## Tuning controls (all parametric)",
        "",
        f"- **Back:** {back} (`cup_open_back`) — closed-back is a regenerate, not a redesign.",
        f"- **Rear vents (closed-back):** {P.cup_port_count} × ⌀{P.cup_port_diameter:.0f} mm ports, each pluggable "
        f"(`vent_plug`) — plug N to dial openness.",
        f"- **Rear damping:** ⌀{P.damping_felt_diameter:.0f} × {P.damping_felt_thickness:.0f} mm felt disc, seated in the cup's damping ring over the grille.",
        f"- **Front seal:** {P.front_gasket_thickness:.1f} mm foam gasket at ~{P.front_gasket_squeeze*100:.0f}% squeeze (gate-checked into 30–50%).",
        f"- **Front cavity = pad depth** ({P.earpad_depth:.0f} mm) — the main tuning lever (swap pads).",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path


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
            if name in PRINTED or name in ACCESSORY or name in COUPON:
                stl_path = os.path.join(OUT, f"{name}.stl")
                cq.exporters.export(model, stl_path)
                tag = ("" if name in PRINTED else
                       "  (COUPON — fit test, not in the assembly)" if name in COUPON else
                       "  (ACCESSORY — not in the assembly)")
                print(f"  [ok]   {name}.stl + {name}.step{tag}")
                # Coupons are QA tools — no web gallery render/GLB for them.
                if name in COUPON:
                    ok.append(name)
                    continue
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
            print("  [ok]   assembly.step (cup + baffle + driver + clamp + yoke + slider + bow ref)")
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

        # Generated parts inventory — keeps the 'N parts' count from drifting.
        try:
            print(f"  [ok]   {gen_parts_doc()} (parts inventory — generated)")
            print(f"  [ok]   {gen_acoustics_doc()} (acoustic summary — generated)")
        except Exception as e:  # noqa: BLE001 — never fail the build on a doc
            print(f"  [warn] PARTS.md / ACOUSTICS.md skipped: {e}")

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
