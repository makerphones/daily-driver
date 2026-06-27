# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — OFFSET-OUTER clamp carrying the headband (v0.7 junction pass).

Layout (maker's call): the metal band rides INSIDE (head-side) and the rod + tube ride
OUTSIDE it. So the post-bore TUBE (the barrel) is the OUTER body, and the band's end
attaches on the barrel's INNER (−Y, head-side) face:

    head ──  COVER │ BAND │ clamp-plate(+RIB) │ BARREL+POST  ── outside

The band's two prongs drop into a RECESS milled in the clamp plate (registers them
laterally); a registering RIB enters the bow's open CHANNEL (the big gap between the
prongs) for anti-rotation; the separate COVER plate (parts/headband_clamp.py) sits on
the band's inner face and bolts down with two M3 screws through the prong-tip holes into
inserts in the plate. A side THUMBSCREW clamps the round post in the barrel (Grado
set-and-lock); the post slides + swivels the full barrel height and may poke past it.

Frame: z=0 at the barrel MID (the clamp is centred there). Barrel/post-bore z −h/2..h/2;
clamp plate on −Y; thumbscrew on +X (front). ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    h = P.slider_collar_height
    bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2
    cw = P.slider_clamp_width
    ch = P.slider_clamp_height
    pd = P.slider_clamp_standoff
    bt = P.bow_thickness
    s = P.bow_endtab_hole_spacing / 2

    # BARREL = the post-bore TUBE, full height, centred on z=0. This is the OUTER body:
    # the yoke's round post/rod slides + swivels up through it (the assembly places it
    # OUTBOARD of the band). The post can poke past either end freely — nothing stacks on it.
    collar = cq.Workplane("XY").workplane(offset=-h / 2).circle(R).extrude(h)
    try:
        collar = collar.edges(">Z or <Z").fillet(P.slider_collar_rim_round)
    except Exception as e:  # noqa: BLE001 — kernel may refuse on this OCC build
        print(f"  [warn] slider: barrel rim roundover skipped ({e}).")

    # CLAMP PLATE on the −Y (INNER, head-side) face — the band's prongs drop into a RECESS
    # here, the cover sandwiches them. Deep-overlap the barrel so the union fuses to ONE
    # solid (a tangent kiss would leave two disjoint solids on this kernel).
    ovl = 6.0
    plate_d = pd + ovl
    plate_cy = -R + ovl - plate_d / 2                    # Y span: −R−pd .. −R+ovl
    collar = collar.union(cq.Workplane("XY").center(0, plate_cy).box(cw, plate_d, ch))
    clamp_face = -R - pd                                 # plate's −Y (clamp) face

    # RECESS — a shallow pocket milled into the clamp face the band's end drops into
    # (registers it laterally; the cover presses it home).
    rec_d = bt + 0.6
    collar = collar.cut(
        cq.Workplane("XY").center(0, clamp_face + rec_d / 2)
        .box(P.bow_width + 1.5, rec_d + 0.02, ch + 0.1))
    seat_y = clamp_face + rec_d                          # recess floor (band's outer face seats here)

    # Anti-rotation RIB — protrudes −Y from the recess floor into the bow's open channel
    # (the big gap between the two prongs), poking through toward the cover's slot. Its +Y
    # end overlaps DEEP into the plate (past the recess floor) so the union fuses to one
    # solid — a tangent kiss at the floor would leave two disjoint solids on this kernel.
    channel_w = P.bow_width - 2 * P.bow_rail_width
    rib_ovl = 1.5
    rib_far = seat_y + rib_ovl                           # +Y end, buried in the plate
    rib_near = seat_y - P.slider_clamp_rib_depth         # −Y end, out in the channel
    collar = collar.union(
        cq.Workplane("XY")
        .workplane(offset=P.slider_clamp_rib_z - P.slider_clamp_rib_height / 2)
        .center(0, (rib_far + rib_near) / 2)
        .box(channel_w - 1.0, rib_far - rib_near, P.slider_clamp_rib_height,
             centered=(True, True, False)))

    # POST BORE through the barrel (cut after the unions).
    collar = collar.cut(
        cq.Workplane("XY").workplane(offset=-h / 2 - 1).circle(bore_r).extrude(h + 2))

    # Two M3 inserts in the plate (axis +Y, from the recess floor outward) at the
    # prong-hole pitch + clamp height.
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            P.m3_insert_hole_diameter / 2, P.insert_boss_depth,
            cq.Vector(x, seat_y, P.slider_clamp_hole_z), cq.Vector(0, 1, 0))
        collar = collar.cut(cq.Workplane(obj=bore))

    # THUMBSCREW on the +X (front) face of the barrel — tip presses the post in the bore.
    boss_h = 4.0
    bovl = 4.0
    boss = cq.Solid.makeCylinder(P.slider_thumbscrew_boss / 2, boss_h + bovl,
                                 cq.Vector(R - bovl, 0, 0), cq.Vector(1, 0, 0))
    collar = collar.union(cq.Workplane(obj=boss))
    ins = cq.Solid.makeCylinder(P.slider_thumbscrew_insert_hole / 2, P.insert_boss_depth,
                                cq.Vector(R + boss_h, 0, 0), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=ins))
    clrc = cq.Solid.makeCylinder(P.slider_thumbscrew_diameter / 2 + 0.2, R + boss_h,
                                 cq.Vector(R + boss_h, 0, 0), cq.Vector(-1, 0, 0))
    collar = collar.cut(cq.Workplane(obj=clrc))
    return collar


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
