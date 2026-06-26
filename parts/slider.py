# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — CLAMP COLLAR carrying the headband on the bow (v0.5 junction pass).

A slim rounded BARREL wraps the yoke's round adjustment POST: the post slides AND
swivels in the barrel bore (one robust bearing, no separate weak joint), and a side
THUMBSCREW clamps it (Grado HP1000-style, set-and-lock).

HEADBAND JUNCTION (Beyer-style two-piece clamp): the barrel's OUTBOARD (+Y) face is
the INNER plastic piece. The bow's metal end seats on it; a registering RIB enters the
bow's open CHANNEL (the gap between the rails) for anti-rotation + stiffness; and a
separate COVER plate (parts/headband_clamp.py) sandwiches the metal with two M3 screws
through the bow's end-tab holes. The band mounts ALONGSIDE the post (band outermost) so
the post slides past without intersecting it.

Frame: barrel centred on the origin, axis Z (the post runs through it). Clamp on +Y;
thumbscrew boss on +X (front). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    h = P.slider_collar_height
    bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2   # post slide + swivel fit
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    cs = P.slider_clamp_standoff
    s = P.bow_endtab_hole_spacing / 2

    # Barrel — a solid cylinder first, rims rounded while CLEAN, centred at the origin.
    collar = cq.Workplane("XY").workplane(offset=-h / 2).circle(R).extrude(h)
    try:
        collar = collar.edges(">Z or <Z").fillet(P.slider_collar_rim_round)
    except Exception as e:  # noqa: BLE001 — report, don't mask; barrel still prints
        print(f"  [warn] slider: barrel rim roundover skipped ({e}).")

    # Clamp SLAB on the +Y (outboard) face — the inner plastic piece the band seats on.
    # Overlaps DEEP into the barrel so the union fuses to one solid (a curved-surface
    # tangent kiss leaves two disjoint solids on this OCC build).
    ovl = 6.0
    slab_d = cs + ovl
    slab_cy = R + cs - slab_d / 2                            # spans y = R−ovl .. R+cs
    collar = collar.union(cq.Workplane("XY").center(0, slab_cy).box(cw, slab_d, ch))
    seat_y = R + cs                                          # the +Y seat face (band rests here)

    # Anti-rotation RIB — a vertical rib that enters the bow's open channel (between the
    # rails); its width matches the channel so the band can't twist. Protrudes +Y.
    channel_w = P.bow_width - 2 * P.bow_rail_width
    rib_w = channel_w - 1.0                                  # slip clearance in the channel
    rib = (
        cq.Workplane("XY").center(0, seat_y + P.slider_clamp_rib_depth / 2)
        .box(rib_w, P.slider_clamp_rib_depth, P.slider_clamp_rib_height)
        .translate((0, 0, P.slider_clamp_rib_z))
    )
    collar = collar.union(rib)

    # Two M3 mount inserts in the slab (axis +Y) at the bow's end-hole pitch — the band
    # + cover bolt down here. Bored from the seat face inward (−Y).
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            P.m3_insert_hole_diameter / 2, P.insert_boss_depth,
            cq.Vector(x, seat_y, P.slider_clamp_hole_z), cq.Vector(0, -1, 0))
        collar = collar.cut(cq.Workplane(obj=bore))

    # Vertical POST bore (axis Z, centre) — the post slides + swivels through it.
    post_bore = (cq.Workplane("XY").workplane(offset=-h / 2 - 1)
                 .circle(bore_r).extrude(h + 2))
    collar = collar.cut(post_bore)

    # THUMBSCREW lock on the +X (front) face — boss with an M4 heat-set bore; the
    # screw tip presses the post (locks height + swivel). Deep-overlap the boss.
    boss_h = 4.0
    bovl = 4.0
    boss = cq.Solid.makeCylinder(
        P.slider_thumbscrew_boss / 2, boss_h + bovl,
        cq.Vector(R - bovl, 0, 0), cq.Vector(1, 0, 0))
    collar = collar.union(cq.Workplane(obj=boss))
    ins = cq.Solid.makeCylinder(
        P.slider_thumbscrew_insert_hole / 2, P.insert_boss_depth,
        cq.Vector(R + boss_h, 0, 0), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=ins))
    clr = cq.Solid.makeCylinder(
        P.slider_thumbscrew_diameter / 2 + 0.2, R + boss_h,     # to the post bore, not through
        cq.Vector(R + boss_h, 0, 0), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=clr))

    return collar


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
