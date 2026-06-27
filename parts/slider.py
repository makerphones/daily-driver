# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — OFFSET-OUTER clamp, sleek lofted wing (v0.8).

Layout (maker's call): the metal band rides INSIDE (head-side) and the rod + tube ride
OUTSIDE it. The post-bore TUBE (the barrel) is the OUTER body; the band attaches on a
WING flaring off the barrel's INNER (−Y, head-side) face:

    head ──  COVER │ BAND │ wing (+RIB) │ BARREL + POST  ── outside

The WING is LOFTED, not a slab: full width at the bolts (z_lo), tapering NARROWER and
its inner face RECEDING (pulling back toward the barrel) toward the top — so the band
SWEEPS OUT cleanly above the grip instead of fighting a tall flat plate, and the wasted
corner mass is shed. The band's two prongs drop into a RECESS in the wing's lower face;
a short registering RIB enters the bow's open channel; the COVER plate
(parts/headband_clamp.py) sits on the band's inner face and bolts through the prong-tip
holes into inserts in the wing. A side M3 THUMBSCREW friction-locks the post.

Frame: z=0 at the barrel MID. Wing spans z_lo..z_hi; bolts at hole_z. ESTIMATES (params).
"""

import cadquery as cq
from params import P


def _rect_wire(z, x_half, y0, y1):
    """A rectangle wire at height z, spanning ±x_half in X and [y0, y1] in Y."""
    pts = [(-x_half, y0, z), (x_half, y0, z), (x_half, y1, z), (-x_half, y1, z), (-x_half, y0, z)]
    return cq.Wire.makePolygon([cq.Vector(*p) for p in pts])


def make_slider() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    h = P.slider_collar_height
    bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2
    cw = P.slider_clamp_width
    pd = P.slider_clamp_standoff
    bt = P.bow_thickness
    s = P.bow_endtab_hole_spacing / 2
    z_lo = P.slider_clamp_z_lo
    z_hi = P.slider_clamp_z_hi
    ovl = 6.0
    y_in = -R - pd                                       # clamp face (inner / head-side)
    y_out = -R + ovl                                     # buried into the barrel (overlap → fuses)

    # BARREL = post-bore TUBE, full height, centred z=0. OUTER body; the post slides + swivels.
    collar = cq.Workplane("XY").workplane(offset=-h / 2).circle(R).extrude(h)
    try:
        collar = collar.edges(">Z or <Z").fillet(P.slider_collar_rim_round)
    except Exception as e:  # noqa: BLE001 — kernel may refuse on this OCC build
        print(f"  [warn] slider: barrel rim roundover skipped ({e}).")

    # CLAMP WING — lofted: full width + full depth at the bottom (the bolts), tapering to a
    # narrower width and a RECEDED inner face at the top so the band sweeps out clean.
    wing = cq.Solid.makeLoft([
        _rect_wire(z_lo, cw / 2, y_in, y_out),
        _rect_wire(z_hi, P.slider_clamp_top_width / 2, y_in + P.slider_clamp_top_recede, y_out)])
    collar = collar.union(cq.Workplane(obj=wing))

    # RECESS — pocket in the wing's inner face the band's prongs drop into (lower grip only).
    rec_d = bt + 0.6
    rec_top = P.slider_clamp_hole_z + 5.0
    collar = collar.cut(
        cq.Workplane("XY").workplane(offset=(z_lo + rec_top) / 2)
        .center(0, y_in + rec_d / 2).box(P.bow_width + 1.5, rec_d + 0.02, rec_top - z_lo))
    seat_y = y_in + rec_d                                # recess floor (band's outer face seats here)

    # Anti-rotation RIB — short, into the bow's open channel; +Y end overlaps DEEP into the
    # wing so the union stays ONE solid (a tangent kiss at the floor would split it).
    channel_w = P.bow_width - 2 * P.bow_rail_width
    rib_far = seat_y + 1.5
    rib_near = seat_y - P.slider_clamp_rib_depth
    collar = collar.union(
        cq.Workplane("XY")
        .workplane(offset=P.slider_clamp_rib_z - P.slider_clamp_rib_height / 2)
        .center(0, (rib_far + rib_near) / 2)
        .box(channel_w - 1.0, rib_far - rib_near, P.slider_clamp_rib_height,
             centered=(True, True, False)))

    # POST BORE through the barrel (after the unions).
    collar = collar.cut(
        cq.Workplane("XY").workplane(offset=-h / 2 - 1).circle(bore_r).extrude(h + 2))

    # Two M3 inserts in the wing (axis +Y from the recess floor) at the prong-hole pitch.
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            P.m3_insert_hole_diameter / 2, P.insert_boss_depth,
            cq.Vector(x, seat_y, P.slider_clamp_hole_z), cq.Vector(0, 1, 0))
        collar = collar.cut(cq.Workplane(obj=bore))

    # THUMBSCREW boss on the +X (front) face — small M3 lock; tip presses the post in the bore.
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
