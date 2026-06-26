# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband clamp COVER — the OUTER plastic piece of the Beyer-style band junction.

Two plastic pieces sandwich the metal bow's end: the INNER piece is the slider collar's
outboard clamp face (parts/slider.py), and this COVER is the OUTER piece. It sits on the
band's outer face and bolts down with two M3 screws (through the band's end-tab holes,
into the slider's inserts). A SLOT on its inner face receives the slider's anti-rotation
rib — the rib passes through the bow's open channel and registers in this slot, so the
band is locked against rotation from both sides.

Frame: plate centred on the origin; thickness along Y, width along X, height along Z —
matching the slider clamp face. Bolt holes + rib slot share the slider's positions
(P.slider_clamp_*). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_headband_clamp() -> cq.Workplane:
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    ct = P.slider_clamp_cover_thickness
    s = P.bow_endtab_hole_spacing / 2

    cover = cq.Workplane("XY").box(cw, ct, ch)

    # Round the long Z edges so the outer plate reads as a finished cap (clean box,
    # round before the cuts). Best-effort.
    try:
        cover = cover.edges("|Z").fillet(2.0)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] headband_clamp: edge round skipped ({e}).")

    # Two M3 clearance holes (axis Y) at the band's end-hole pitch.
    for x in (+s, -s):
        hole = cq.Solid.makeCylinder(
            P.m3_clearance_hole / 2, ct + 2.0,
            cq.Vector(x, -ct / 2 - 1.0, P.slider_clamp_hole_z), cq.Vector(0, 1, 0))
        cover = cover.cut(cq.Workplane(obj=hole))

    # Rib SLOT on the inner (−Y, band-facing) face — the slider's rib seats here after
    # passing through the bow's open channel (registers the band + cover together).
    channel_w = P.bow_width - 2 * P.bow_rail_width
    slot_depth = 2.5
    slot = (
        cq.Workplane("XY").center(0, -ct / 2 + slot_depth / 2 - 0.05)
        .box(channel_w, slot_depth + 0.1, P.slider_clamp_rib_height + 1.0)
        .translate((0, 0, P.slider_clamp_rib_z))
    )
    cover = cover.cut(slot)

    return cover


if __name__ == "__main__":
    cq.exporters.export(make_headband_clamp(), "output/headband_clamp.stl")
    print("wrote output/headband_clamp.stl")
