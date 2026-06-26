# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband clamp COVER — the OUTER (+Y) plastic piece of the in-line band junction.

Two plastic pieces sandwich the metal bow's end: the INNER piece is the slider's clamp
wall (parts/slider.py, on −Y), and this COVER is the OUTER (+Y) piece. It sits on the
band's outer face and bolts down with two M3 screws (through the band's end-tab holes
into the slider's inserts). A SLOT on its inner (−Y) face receives the slider's
anti-rotation rib, which passes through the bow's open channel — locking the band from
both sides.

Frame matches the slider (z=0 at the slider bottom): the plate spans the clamp region
z = bd .. bd+clamp_height on the band's +Y side, sharing the slider's bolt/rib positions
(P.slider_clamp_*). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_headband_clamp() -> cq.Workplane:
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    ct = P.slider_clamp_cover_thickness
    bd = P.slider_collar_height
    bt = P.bow_thickness
    s = P.bow_endtab_hole_spacing / 2

    band_outer = bt / 2 + 0.3                       # band's +Y face (band centred at Y=0)

    # Plate on the band's +Y side, z = bd .. bd+ch, centred in X.
    cover = (cq.Workplane("XY").workplane(offset=bd)
             .center(0, band_outer + ct / 2)
             .box(cw, ct, ch, centered=(True, True, False)))

    # Two M3 clearance holes (axis Y) at the band's end-hole pitch + height.
    for x in (+s, -s):
        hole = cq.Solid.makeCylinder(
            P.m3_clearance_hole / 2, ct + 2.0,
            cq.Vector(x, band_outer - 1.0, bd + P.slider_clamp_hole_z), cq.Vector(0, 1, 0))
        cover = cover.cut(cq.Workplane(obj=hole))

    # Rib SLOT on the inner (−Y) face — the slider's rib (through the bow channel) seats
    # here, registering the band + cover together.
    channel_w = P.bow_width - 2 * P.bow_rail_width
    slot_depth = 2.5
    slot = (cq.Workplane("XY")
            .workplane(offset=bd + P.slider_clamp_rib_z - P.slider_clamp_rib_height / 2 - 0.5)
            .center(0, band_outer + slot_depth / 2)
            .box(channel_w, slot_depth, P.slider_clamp_rib_height + 1.0, centered=(True, True, False)))
    cover = cover.cut(slot)

    return cover


if __name__ == "__main__":
    cq.exporters.export(make_headband_clamp(), "output/headband_clamp.stl")
    print("wrote output/headband_clamp.stl")
