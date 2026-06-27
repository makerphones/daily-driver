# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband clamp COVER — the INNER (head-side, −Y) plastic piece of the band junction.

Two plastic pieces sandwich the metal bow's end. The OUTER piece is the slider's clamp
plate (parts/slider.py) — it carries the recess + rib + inserts and the post-bore barrel
behind it. This COVER is the INNER (−Y) piece: it sits on the band's head-side face and
bolts down with two M3 screws (through the prong-tip holes into the slider's inserts). A
SLOT on its outer (+Y) face receives the slider's anti-rotation rib, which pokes through
the bow's open channel — locking the band from both sides.

Frame matches the slider (z=0 at the barrel mid): the plate spans the clamp region
centred on z=0, on the band's −Y (inner) side, sharing the slider's bolt/rib positions
(P.slider_clamp_*). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_headband_clamp() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    pd = P.slider_clamp_standoff
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    ct = P.slider_clamp_cover_thickness
    s = P.bow_endtab_hole_spacing / 2

    clamp_face = -R - pd                            # recess opening (band's inner face ≈ here)

    # Plate on the band's INNER (−Y) side, its +Y face at the recess opening, centred z=0.
    cover = (cq.Workplane("XY").center(0, clamp_face - ct / 2).box(cw, ct, ch))

    # Two M3 clearance holes (axis Y) at the prong-tip hole pitch + clamp height.
    for x in (+s, -s):
        hole = cq.Solid.makeCylinder(
            P.m3_clearance_hole / 2, ct + 2.0,
            cq.Vector(x, clamp_face + 1.0, P.slider_clamp_hole_z), cq.Vector(0, -1, 0))
        cover = cover.cut(cq.Workplane(obj=hole))

    # Rib SLOT on the outer (+Y) face — the slider's rib (poking through the bow channel)
    # seats here, registering the band + cover together.
    channel_w = P.bow_width - 2 * P.bow_rail_width
    slot_depth = 2.5
    slot = (cq.Workplane("XY")
            .workplane(offset=P.slider_clamp_rib_z - P.slider_clamp_rib_height / 2 - 0.5)
            .center(0, clamp_face - slot_depth / 2 + 0.01)
            .box(channel_w, slot_depth, P.slider_clamp_rib_height + 1.0,
                 centered=(True, True, False)))
    cover = cover.cut(slot)
    return cover


if __name__ == "__main__":
    cq.exporters.export(make_headband_clamp(), "output/headband_clamp.stl")
    print("wrote output/headband_clamp.stl")
