# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — IN-LINE clamp carrying the headband on the post (v0.6 junction pass).

Stacked layout (band → slider → post → yoke → cup, one vertical line, no sideways
offset): the yoke's round POST slides up into the slider's LOWER barrel bore (its top
stops just under the band, so the band sits DIRECTLY ABOVE the post), and the band's
metal end clamps on TOP. A side THUMBSCREW clamps the post (Grado set-and-lock).

HEADBAND JUNCTION (Beyer-style two-piece clamp): the clamp's INNER wall (−Y) seats the
band; a registering RIB enters the bow's open CHANNEL (between the rails) for
anti-rotation; and a separate COVER plate (parts/headband_clamp.py, the +Y piece)
sandwiches the metal with two M3 screws through the band's end-tab holes.

Frame: z=0 at the slider BOTTOM (where the post enters). Barrel/post-bore in z 0..bd
(bd=slider_collar_height); clamp above. The band sits centred at Y=0 (above the post
bore); inner wall on −Y, cover on +Y; thumbscrew on +X (front). ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2
    bd = P.slider_collar_height          # lower barrel / post-bore depth
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    wall = P.slider_clamp_standoff       # inner-wall depth (Y), behind the band
    bt = P.bow_thickness
    s = P.bow_endtab_hole_spacing / 2

    band_face = -bt / 2 - 0.3            # band's −Y face (band centred at Y=0)

    # Lower BARREL — post-bore region, z 0..bd. The post slides up from below; its top
    # stops at the barrel top (bd), just under the band clamp above.
    collar = cq.Workplane("XY").circle(R).extrude(bd)

    # Inner CLAMP wall on −Y, z bd..bd+ch — the band seats on its +Y face (band centred
    # at Y=0, directly above the post bore). Sits on the barrel top → fuses.
    collar = collar.union(
        cq.Workplane("XY").workplane(offset=bd)
        .center(0, band_face - wall / 2)
        .box(cw, wall, ch, centered=(True, True, False)))

    # Anti-rotation RIB — protrudes +Y from the wall face into the bow's open channel.
    channel_w = P.bow_width - 2 * P.bow_rail_width
    collar = collar.union(
        cq.Workplane("XY")
        .workplane(offset=bd + P.slider_clamp_rib_z - P.slider_clamp_rib_height / 2)
        .center(0, band_face + P.slider_clamp_rib_depth / 2)
        .box(channel_w - 1.0, P.slider_clamp_rib_depth, P.slider_clamp_rib_height,
             centered=(True, True, False)))

    # Post BORE — z −1..bd (through the barrel only; the clamp above is solid, so the
    # post stops below the band). Cut after the unions.
    collar = collar.cut(
        cq.Workplane("XY").workplane(offset=-1).circle(bore_r).extrude(bd + 1))

    # Two M3 inserts in the inner wall (axis −Y) at the band's hole pitch + height.
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            P.m3_insert_hole_diameter / 2, P.insert_boss_depth,
            cq.Vector(x, band_face, bd + P.slider_clamp_hole_z), cq.Vector(0, -1, 0))
        collar = collar.cut(cq.Workplane(obj=bore))

    # THUMBSCREW on the +X (front) face of the barrel — tip presses the post in the bore.
    boss_h = 4.0
    bovl = 4.0
    zc = bd / 2
    boss = cq.Solid.makeCylinder(P.slider_thumbscrew_boss / 2, boss_h + bovl,
                                 cq.Vector(R - bovl, 0, zc), cq.Vector(1, 0, 0))
    collar = collar.union(cq.Workplane(obj=boss))
    ins = cq.Solid.makeCylinder(P.slider_thumbscrew_insert_hole / 2, P.insert_boss_depth,
                                cq.Vector(R + boss_h, 0, zc), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=ins))
    clrc = cq.Solid.makeCylinder(P.slider_thumbscrew_diameter / 2 + 0.2, R + boss_h,
                                 cq.Vector(R + boss_h, 0, zc), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=clrc))

    return collar


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
