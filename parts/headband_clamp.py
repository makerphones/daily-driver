# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband clamp COVER — the INNER (head-side, −Y) plastic piece of the band junction.

Two plastic pieces sandwich the metal bow's end. The OUTER piece is the slider's rounded
clamp LOZENGE (parts/slider.py) — it carries the recess + rib + inserts and the post-bore
barrel behind it. This COVER is the INNER (−Y) piece: a small ROUNDED plate over the GRIP
region only, bolted through the prong-tip holes into the lozenge's inserts. Spanning just
the grip lets the band sweep out freely above it. A SLOT on its outer (+Y) face takes the
slider's anti-rotation rib.

Frame matches the slider (z=0 at the barrel mid); shares the slider's bolt/rib positions
(P.slider_clamp_*). Rounded outline is a hand-built arc wire (fillets fail on this OCC build).
"""

import cadquery as cq
from params import P


def _rounded_rect_wire(plane, width, thick, r):
    """Rounded-rectangle WIRE on `plane` (local-x = width, local-y = thick, corner r)."""
    hw = width / 2.0
    ht = thick / 2.0
    r = min(r, hw - 1e-3, ht - 1e-3)
    sx, sy = hw - r, ht - r
    k = r * 0.70710678
    wp = (cq.Workplane(plane).moveTo(-sx, -ht)
          .lineTo(sx, -ht).threePointArc((hw - r + k, -ht + r - k), (hw, -sy))
          .lineTo(hw, sy).threePointArc((hw - r + k, ht - r + k), (sx, ht))
          .lineTo(-sx, ht).threePointArc((-hw + r - k, ht - r + k), (-hw, sy))
          .lineTo(-hw, -sy).threePointArc((-hw + r - k, -ht + r - k), (-sx, -ht))
          .close())
    return wp.val()


def make_headband_clamp() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    pd = P.slider_clamp_standoff
    ct = P.slider_clamp_cover_thickness
    s = P.bow_endtab_hole_spacing / 2
    z_lo = P.slider_clamp_z_lo
    z_top = P.slider_clamp_hole_z + 4.0                  # ends just above the bolts; band exits above
    z_mid = (z_lo + z_top) / 2
    clamp_face = -R - pd                                 # recess opening (band's inner face)

    # Small ROUNDED plate over the grip, sitting on the band's inner (−Y) face. Loft two
    # equal stadium wires for a clean rounded outline.
    cw = P.slider_clamp_width - 6.0                      # a touch narrower than the lozenge
    ch = (z_top - z_lo) + 4.0
    rr = min(P.slider_clamp_corner_r - 1.0, ch / 2 - 0.5)

    ce = P.slider_clamp_cover_ease

    def wire(y, inset=0.0):
        plane = cq.Plane(origin=(0, y, z_mid), xDir=(1, 0, 0), normal=(0, 1, 0))
        return _rounded_rect_wire(plane, cw - 2 * inset, ch - 2 * inset, max(rr - inset, 1.0))

    # The cover is the FIRST thing to touch the head (it stands proud of the lozenge by ct).
    # Draft its head-side (-Y) face inward (ce) so the rim recedes from the temple → a soft
    # central crown instead of a square plate edge. Band-side stays full (seats on the lozenge).
    cover = cq.Workplane(obj=cq.Solid.makeLoft([wire(clamp_face - ct, ce), wire(clamp_face)]))

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
