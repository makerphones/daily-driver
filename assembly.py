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


def make_assembly() -> cq.Assembly:
    """Both ears + the shared headband — a full-headphone preview.

    The RIGHT ear is the real kinematic chain at the origin; the LEFT ear is its
    mirror across the bow's apex plane (x = -ex). The bow and the crown pad are
    single shared parts. Bow pose + head-size kinematics stay representative
    (ESTIMATE, see params/bow).
    """
    CHARCOAL = cq.Color(0.30, 0.32, 0.35)
    ORANGE = cq.Color(0.92, 0.45, 0.10)
    YOKE_C = cq.Color(0.36, 0.38, 0.42)
    SLIDER_C = cq.Color(0.42, 0.44, 0.48)
    STEEL = cq.Color(0.75, 0.76, 0.78)
    BRASS = cq.Color(0.80, 0.68, 0.30)
    SCREW_C = cq.Color(0.55, 0.57, 0.60)
    PAD_C = cq.Color(0.13, 0.13, 0.15)   # near-black foam/velour

    # ---- RIGHT-ear chain (the real poses) ----
    cup = make_cup()
    baffle = make_baffle().translate((0, 0, P.baffle_seat_z))
    yoke = make_yoke().translate((0, 0, P.pivot_boss_z))
    fork_hub_top = P.pivot_boss_z + P.yoke_fork_height + P.yoke_swivel_hub_height / 2
    slider_z = fork_hub_top - 5.0 + P.slider_block_height / 2
    slider = make_slider().translate((0, 0, slider_z))

    # ---- Shared headband: bow + crown pad ----
    end_a = 90 - P.bow_arc_degrees / 2
    ex = P.bow_radius * math.cos(math.radians(end_a))
    ez = P.bow_radius * math.sin(math.radians(end_a))
    channel_y = -P.slider_block_depth / 2 + P.slider_bow_channel_depth / 2
    bow_xf = (-ex, channel_y, slider_z - ez)              # right end at the slider; sweeps left
    bow = make_bow().translate(bow_xf)
    pad = make_headband_pad().translate(bow_xf)            # hugs the bow's inner face at the crown
    mx = -ex                                               # apex plane: left ear = mirror across x=mx

    asm = cq.Assembly(name="daily_driver")

    # Per-ear parts: RIGHT as-posed, LEFT mirrored across the apex plane (true
    # mirror image — correct chirality for the opposite ear).
    # grille_dot: the warm-orange accent cap at the cup's grille center.
    grille_dot = make_grille_dot()
    for nm, solid, col in (("cup", cup, CHARCOAL), ("baffle", baffle, ORANGE),
                           ("yoke", yoke, YOKE_C), ("slider", slider, SLIDER_C),
                           ("grille_dot", grille_dot, ORANGE)):
        asm.add(solid, name=f"{nm}_R", color=col)
        asm.add(solid.mirror("YZ", (mx, 0, 0)), name=f"{nm}_L", color=col)

    asm.add(bow, name="bow_ref", color=STEEL)              # shared headband (REF)
    asm.add(pad, name="headband_pad", color=PAD_C)         # shared crown cushion

    # Pivot hardware on both ears (viz). Guarded — accurate insert if cq_warehouse
    # is present, else the primitive; never fails the build.
    try:
        from parts.hardware import make_shoulder_screw, make_heatset_insert
        for sign in (+1, -1):
            tag = "p" if sign > 0 else "m"
            insert = (make_heatset_insert()
                      .rotate((0, 0, 0), (0, 1, 0), -90 * sign)
                      .translate((sign * P.pivot_boss_outer_radius, 0, P.pivot_boss_z)))
            screw = (make_shoulder_screw()
                     .rotate((0, 0, 0), (0, 1, 0), 90 * sign)
                     .translate((sign * (P.pivot_boss_outer_radius - P.yoke_arm_thickness),
                                 0, P.pivot_boss_z)))
            asm.add(insert, name=f"insert_{tag}_R", color=BRASS)
            asm.add(insert.mirror("YZ", (mx, 0, 0)), name=f"insert_{tag}_L", color=BRASS)
            asm.add(screw, name=f"screw_{tag}_R", color=SCREW_C)
            asm.add(screw.mirror("YZ", (mx, 0, 0)), name=f"screw_{tag}_L", color=SCREW_C)
    except Exception as e:  # noqa: BLE001 — viz only; never block the build
        print(f"  [warn] assembly: pivot hardware skipped ({e}).")
    return asm


if __name__ == "__main__":
    make_assembly().export("output/assembly.step")
    print("wrote output/assembly.step")
