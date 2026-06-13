"""
Yoke — connects slider to cup, allows +/-20 deg tilt.

STUB. The pivot interface (the project's own 6 mm post) is defined here so the
parameter is exercised, but the yoke's actual geometry and its attachment to
the cup are open work. Build this out in the loop after the cup/baffle fit is
confirmed. Don't invent the cup-side attachment — resolve it with the cup
together (see DESIGN-LOG.md, "yoke-to-cup interface").
"""

import cadquery as cq
from params import P


def make_yoke() -> cq.Workplane:
    # Minimal placeholder: a flat arm with a pivot post at one end and a bore at
    # the other. Real geometry (the curved gimbal arm, the +/-20 deg hard stops,
    # left/right mirror) is TODO.
    arm_len = 40.0
    arm_w = 12.0
    arm_t = 4.0

    yoke = cq.Workplane("XY").box(arm_len, arm_w, arm_t, centered=(False, True, False))

    # pivot post at the far end (mates to the slider bore)
    yoke = (
        yoke.faces(">Z").workplane()
        .center(arm_len - P.pivot_post_diameter, 0)
        .circle(P.pivot_post_diameter / 2)
        .extrude(P.pivot_post_height)
    )
    # M3 retention through-hole down the post
    yoke = (
        yoke.faces(">Z").workplane()
        .center(0, 0)
        .hole(P.m3_clearance_hole)
    )

    return yoke


if __name__ == "__main__":
    cq.exporters.export(make_yoke(), "output/yoke.stl")
    print("wrote output/yoke.stl  (STUB geometry)")
