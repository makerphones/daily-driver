# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband clamp COVER — the INNER (head-side, −Y) plastic piece of the band junction.

Two plastic pieces sandwich the metal bow's end. The OUTER piece is the slider's lofted
clamp WING (parts/slider.py) — it carries the recess + rib + inserts and the post-bore
barrel behind it. This COVER is the INNER (−Y) piece: it sits on the band's head-side
face and bolts down with two M3 screws (through the prong-tip holes into the wing's
inserts). It only spans the GRIP region (around the bolts) — the band sweeps out freely
above it, so nothing on the inner side fights the band's exit. A SLOT on its outer (+Y)
face receives the slider's anti-rotation rib.

Frame matches the slider (z=0 at the barrel mid); shares the slider's bolt/rib positions
(P.slider_clamp_*). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_headband_clamp() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    pd = P.slider_clamp_standoff
    cw = P.slider_clamp_width
    ct = P.slider_clamp_cover_thickness
    s = P.bow_endtab_hole_spacing / 2
    z_lo = P.slider_clamp_z_lo
    z_top = P.slider_clamp_hole_z + 4.0                  # ends just above the bolts; band exits above
    clamp_face = -R - pd                                 # recess opening (band's inner face ≈ here)

    # Plate on the band's INNER (−Y) side over the grip region only, its +Y face at the
    # recess opening.
    cover = (cq.Workplane("XY").workplane(offset=(z_lo + z_top) / 2)
             .center(0, clamp_face - ct / 2).box(cw, ct, z_top - z_lo))

    # Two M3 clearance holes (axis Y) at the prong-tip hole pitch + bolt height.
    for x in (+s, -s):
        hole = cq.Solid.makeCylinder(
            P.m3_clearance_hole / 2, ct + 2.0,
            cq.Vector(x, clamp_face + 1.0, P.slider_clamp_hole_z), cq.Vector(0, -1, 0))
        cover = cover.cut(cq.Workplane(obj=hole))

    # Rib SLOT on the outer (+Y) face — the slider's rib (through the bow channel) seats here.
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
