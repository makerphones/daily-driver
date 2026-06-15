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


def make_assembly() -> cq.Assembly:
    # Cup at the origin (front +Z up, grille back at z=0).
    cup = make_cup()

    # Baffle front-mounts: modelled back-at-z=0 / pad-lip-up, lifted to seat flush
    # with the cup rim (back rests on the boss tops at baffle_seat_z).
    baffle = make_baffle().translate((0, 0, P.baffle_seat_z))

    # Fork-yoke: local pivot axis (z=0) lifts to the cup pivot bosses (mid-height).
    yoke = make_yoke().translate((0, 0, P.pivot_boss_z))

    # Slider sits on the fork swivel hub (top of the fork, above the cup).
    fork_hub_top = P.pivot_boss_z + P.yoke_fork_height + P.yoke_swivel_hub_height / 2
    slider_z = fork_hub_top - 5.0 + P.slider_block_height / 2
    slider = make_slider().translate((0, 0, slider_z))

    # Bow (reference): bring its near end (the a0 end at +X-low) into the slider
    # channel, so the arc sweeps up and over toward the other ear. Representative.
    end_a = 90 - P.bow_arc_degrees / 2
    ex = P.bow_radius * math.cos(math.radians(end_a))
    ez = P.bow_radius * math.sin(math.radians(end_a))
    channel_y = -P.slider_block_depth / 2 + P.slider_bow_channel_depth / 2
    bow = make_bow().translate((-ex, channel_y, slider_z - ez))

    asm = cq.Assembly(name="daily_driver_side")
    asm.add(cup, name="cup", color=cq.Color(0.30, 0.32, 0.35))        # matte charcoal
    asm.add(baffle, name="baffle", color=cq.Color(0.92, 0.45, 0.10))  # warm-orange accent
    asm.add(yoke, name="yoke", color=cq.Color(0.36, 0.38, 0.42))      # charcoal
    asm.add(slider, name="slider", color=cq.Color(0.42, 0.44, 0.48))  # lighter charcoal
    asm.add(bow, name="bow_ref", color=cq.Color(0.75, 0.76, 0.78))    # brushed steel (REF)
    return asm


if __name__ == "__main__":
    make_assembly().export("output/assembly.step")
    print("wrote output/assembly.step")
