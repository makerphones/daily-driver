"""
Slider — wraps the spring-steel arc, adjusts length, carries the yoke pivot.

STUB. The friction-clamp spring arm that presses on the steel face, the
three-sided wrap around the 10 mm x 0.7 mm arc, and the detent-ready boss are
all open work. The pivot post here must match the yoke bore. Build out in the
loop once the headband arc radius is settled (an open question in the spec).
"""

import cadquery as cq
from params import P

# Spring-steel arc cross section the slider wraps (from spec)
ARC_WIDTH = 10.0
ARC_THICKNESS = 0.7


def make_slider() -> cq.Workplane:
    # Minimal placeholder: a block with a slot sized to the steel arc, plus a
    # pivot post matching the yoke. Real clamp geometry is TODO.
    body_l = 30.0
    body_w = ARC_WIDTH + 6.0
    body_h = 14.0

    slider = cq.Workplane("XY").box(body_l, body_w, body_h)

    # channel for the steel arc (slip fit)
    slot_w = ARC_THICKNESS + P.fit_clearance_slip
    slider = (
        slider.faces(">Z").workplane()
        .rect(body_l, slot_w)
        .cutBlind(-(ARC_WIDTH))
    )

    # pivot post matching the yoke bore
    slider = (
        slider.faces("<Y").workplane()
        .circle(P.pivot_post_diameter / 2)
        .extrude(P.pivot_post_height)
    )

    return slider


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl  (STUB geometry)")
