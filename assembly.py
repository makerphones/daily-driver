# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Assembly — one side of the Daily Driver in its correct relationship (v0.3).

Chain: cup → baffle (front-mounted) → fork-yoke (pivoted to the cup) → slider
(on the fork swivel hub) → bow (REFERENCE body). The cup/baffle/yoke/slider poses
are the real kinematic chain; the bow is posed representatively so one end sits in
the slider channel and the arc sweeps over toward the other (mirror) side — the
full head-size kinematics are TBD from the measured bow (ESTIMATES, see params).

View it:  python show.py        (OCP CAD Viewer)
Export:   build.py writes output/assembly.step
"""

import math

import cadquery as cq

from params import P
from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.bow import make_bow
from parts.headband_pad import make_headband_pad
from parts.grille_dot import make_grille_dot


# Sub-assembly groups for the manual's interactive parts viewer. The node NAMES
# below are a PUBLIC CONTRACT: the website viewer toggles/isolates parts by them
# (they match the asm.add(name=...) calls in make_assembly). Renaming a part there
# means updating this too (and the manual). build.py emits this to
# docs/models/daily-driver.groups.json next to the GLB; the viewer fetches it.
SUBASSEMBLIES = {
    "groups": [
        {"id": "earcup", "label": "Earcup",
         "nodes": ["cup_R", "cup_L", "baffle_R", "baffle_L", "grille_dot_R", "grille_dot_L"]},
        {"id": "gimbal", "label": "Gimbal",
         "nodes": ["yoke_R", "yoke_L", "insert_p_R", "insert_p_L", "insert_m_R",
                   "insert_m_L", "screw_p_R", "screw_p_L", "screw_m_R", "screw_m_L"]},
        {"id": "headband", "label": "Headband",
         "nodes": ["bow_ref", "headband_pad", "slider_R", "slider_L"]},
    ],
    "bought": ["bow_ref"],
}


def make_assembly() -> cq.Assembly:
    """Both ears + the shared headband, posed like a WORN headphone.

    Head frame (global): X = inter-ear (right ear at +Xe, pad facing −X inward),
    Z = up (bow over the crown), Y = front-back (the tilt-pivot axis). The cup and
    yoke are co-designed with pad ∥ arch (both +Z), which is why earlier the cup sat
    "face-up". Here they're mounted at the correct 90° relative clocking:
      • cup-group  T_cup : pad (cup +Z) → −X (inward), pivot (cup ±X) → ±Y,
                           up (cup +Y) → +Z;  pivot centre → (Xe, 0, 0).
      • yoke-group T_yoke: eyes (yoke ±X) → ±Y, arch (yoke +Z) stays +Z (up);
                           pivot centre → (Xe, 0, 0)  (90° clocked about Y vs the cup).
    The two pivots coincide at (±Xe, 0, 0); the LEFT ear is the mirror across x=0.
    The bow + crown pad are shared parts arcing between the two sliders; ear spacing
    = the bow's own end span so the headband fits the cups. Bow dims + exact head
    fit remain ESTIMATE (see params/bow).

    FLAGGED: the over-rotation stop pin/slot are still clocked for the old pad-up
    rest pose, so they read ~90° off in this view — cosmetic here (the gate verifies
    the stop at the part level). Re-clocking them to this rest pose is a follow-up.
    """
    CHARCOAL = cq.Color(0.30, 0.32, 0.35)
    ORANGE = cq.Color(0.92, 0.45, 0.10)
    YOKE_C = cq.Color(0.36, 0.38, 0.42)
    SLIDER_C = cq.Color(0.42, 0.44, 0.48)
    STEEL = cq.Color(0.75, 0.76, 0.78)
    BRASS = cq.Color(0.80, 0.68, 0.30)
    SCREW_C = cq.Color(0.55, 0.57, 0.60)
    PAD_C = cq.Color(0.13, 0.13, 0.15)   # near-black foam/velour

    pbz = P.pivot_boss_z
    end_a = 90 - P.bow_arc_degrees / 2
    Xe = P.bow_radius * math.cos(math.radians(end_a))      # ear half-spacing = bow end x
    ez = P.bow_radius * math.sin(math.radians(end_a))

    def T_cup(w):    # pad → −X, pivot → ±Y, up → +Z; pivot centre → (Xe,0,0)
        return (w.rotate((0, 0, 0), (0, 1, 0), -90)
                 .rotate((0, 0, 0), (1, 0, 0), 90)
                 .translate((Xe + pbz, 0, 0)))

    def T_yoke(w):   # eyes → ±Y, arch stays +Z (up); pivot centre → (Xe,0,0)
        return w.rotate((0, 0, 0), (0, 0, 1), -90).translate((Xe, 0, 0))

    def mirror_L(w):  # right ear → left ear (true mirror across the head centre)
        return w.mirror("YZ", (0, 0, 0))

    # ---- RIGHT ear ----
    cup = T_cup(make_cup())
    baffle = T_cup(make_baffle().translate((0, 0, P.baffle_seat_z)))
    grille_dot = T_cup(make_grille_dot())
    yoke = T_yoke(make_yoke())
    slider_z = P.yoke_fork_height + P.yoke_swivel_hub_height / 2 - 5.0 + P.slider_block_height / 2
    slider = T_yoke(make_slider().translate((0, 0, slider_z)))

    # ---- Shared headband: bow + crown pad, arcing between the two sliders ----
    bow_xf = (0, 0, slider_z - ez)                         # ends land at (±Xe, 0, slider_z)
    bow = make_bow().translate(bow_xf)
    pad = make_headband_pad().translate(bow_xf)

    asm = cq.Assembly(name="daily_driver")
    for nm, solid, col in (("cup", cup, CHARCOAL), ("baffle", baffle, ORANGE),
                           ("yoke", yoke, YOKE_C), ("slider", slider, SLIDER_C),
                           ("grille_dot", grille_dot, ORANGE)):
        asm.add(solid, name=f"{nm}_R", color=col)
        asm.add(mirror_L(solid), name=f"{nm}_L", color=col)

    asm.add(bow, name="bow_ref", color=STEEL)              # shared headband (REF)
    asm.add(pad, name="headband_pad", color=PAD_C)         # shared crown cushion

    # Pivot hardware on both ears (viz), riding with the cup group. Guarded.
    try:
        from parts.hardware import make_shoulder_screw, make_heatset_insert
        for sign in (+1, -1):
            tag = "p" if sign > 0 else "m"
            insert = T_cup(make_heatset_insert()
                           .rotate((0, 0, 0), (0, 1, 0), -90 * sign)
                           .translate((sign * P.pivot_boss_outer_radius, 0, pbz)))
            screw = T_cup(make_shoulder_screw()
                          .rotate((0, 0, 0), (0, 1, 0), 90 * sign)
                          .translate((sign * (P.pivot_boss_outer_radius - P.yoke_arm_thickness),
                                      0, pbz)))
            asm.add(insert, name=f"insert_{tag}_R", color=BRASS)
            asm.add(mirror_L(insert), name=f"insert_{tag}_L", color=BRASS)
            asm.add(screw, name=f"screw_{tag}_R", color=SCREW_C)
            asm.add(mirror_L(screw), name=f"screw_{tag}_L", color=SCREW_C)
    except Exception as e:  # noqa: BLE001 — viz only; never block the build
        print(f"  [warn] assembly: pivot hardware skipped ({e}).")
    return asm


if __name__ == "__main__":
    make_assembly().export("output/assembly.step")
    print("wrote output/assembly.step")
