# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — CLAMP COLLAR carrying the fork on the bow (v0.4 de-bulk pass).

Replaces the old box block. A slim rounded BARREL wraps the yoke's round adjustment
POST: the post slides AND swivels in the barrel bore (one robust bearing — the swivel
the user needs, with no separate small joint to fail), and a side THUMBSCREW clamps it
to lock both height and swivel (Grado HP1000-style, set-and-lock). The band's end tab
bolts to a slim mount TAB on the barrel's inside (−Y) face with two M3 screws (into
heat-set inserts), matching the bow's two holes per end.

Frame: barrel centred on the origin, axis Z (the post runs through it). Mount tab on
−Y; thumbscrew boss on +Y. All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    R = P.slider_collar_diameter / 2
    h = P.slider_collar_height
    bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2   # post slide + swivel fit
    pw = P.slider_mount_plate_width
    ph = P.slider_mount_plate_height
    pt = P.slider_mount_plate_thickness
    s = P.bow_endtab_hole_spacing / 2

    # Barrel — a solid cylinder first, rims rounded while CLEAN (OCC won't fillet it
    # once the bore/mount are cut), centred at the origin.
    collar = cq.Workplane("XY").workplane(offset=-h / 2).circle(R).extrude(h)
    try:
        collar = collar.edges(">Z or <Z").fillet(P.slider_collar_rim_round)
    except Exception as e:  # noqa: BLE001 — report, don't mask; barrel still prints
        print(f"  [warn] slider: barrel rim roundover skipped ({e}).")

    # Bow mount TAB on the −Y (inside / head-side) face: a slim pad the band's end tab
    # bolts to. It overlaps DEEP into the barrel (OVL) so the union fuses to ONE solid
    # — a thin tangent kiss leaves two disjoint solids. pt = how far it stands proud.
    ovl = 6.0
    depth = pt + ovl
    tab_cy = -R + ovl - depth / 2                            # centre (deep overlap + proud standoff)
    collar = collar.union(
        cq.Workplane("XY").center(0, tab_cy).box(pw, depth, ph)
    )

    # Two M3 mount bores through the tab (axis +Y) — the band end tab bolts here with
    # two screws (heat-set inserts in the tab), at the bow's end-hole pitch across X.
    seat_y = -R - pt                                         # tab outer (seat) face
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            P.m3_insert_hole_diameter / 2, P.insert_boss_depth,
            cq.Vector(x, seat_y, 0), cq.Vector(0, 1, 0))
        collar = collar.cut(cq.Workplane(obj=bore))

    # Vertical POST bore (axis Z, centre) — the yoke's round post slides + swivels
    # through this, so it runs the full barrel. Cut after the rim roundover.
    post_bore = (cq.Workplane("XY").workplane(offset=-h / 2 - 1)
                 .circle(bore_r).extrude(h + 2))
    collar = collar.cut(post_bore)

    # THUMBSCREW lock (Grado HP1000-style) — a boss on the +Y (outer) face with an M4
    # heat-set bore; the thumbscrew threads in and its tip presses the post (friction
    # lock on both height + swivel). A clearance hole carries the shaft to the bore.
    boss_h = 4.0
    boss_ovl = 4.0                                           # merge into the CURVED barrel (no tangent kiss)
    boss = cq.Solid.makeCylinder(
        P.slider_thumbscrew_boss / 2, boss_h + boss_ovl,
        cq.Vector(0, R - boss_ovl, 0), cq.Vector(0, 1, 0))
    collar = collar.union(cq.Workplane(obj=boss))
    ins = cq.Solid.makeCylinder(
        P.slider_thumbscrew_insert_hole / 2, P.insert_boss_depth,
        cq.Vector(0, R + boss_h, 0), cq.Vector(0, -1, 0))
    collar = collar.cut(cq.Workplane(obj=ins))
    clr = cq.Solid.makeCylinder(
        P.slider_thumbscrew_diameter / 2 + 0.2, R + boss_h,     # to the post bore, not through
        cq.Vector(0, R + boss_h, 0), cq.Vector(0, -1, 0))
    collar = collar.cut(cq.Workplane(obj=clr))

    return collar


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
