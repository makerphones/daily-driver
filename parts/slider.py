# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — BOLTS to the bow end tab, carries the fork (v0.3 engineering pass).

The band's end tab fastens to the slider's INSIDE (head-side, -Y) face with two
M3 screws (into heat-set inserts), matching the bow's two holes per end — a
positive bolt-on, not the old friction clamp-ride. A shallow seat pocket on the
-Y face registers the tab; a vertical swivel bore at the bottom mates the fork's
swivel hub. The two mount bores sit ABOVE the swivel bore (and the pair straddles
the centre across X) so they stay clear of it.

Frame: block centred on the origin. Tab seat + mount bores on the -Y face; swivel
bore at the bottom. All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    w = P.slider_block_width      # X — hosts the 33 mm tab + the across-width bores
    d = P.slider_block_depth      # Y
    h = P.slider_block_height     # Z

    slider = cq.Workplane("XY").box(w, d, h)

    # Soft-form pass: round ALL block edges into a hand-friendly form BEFORE cutting
    # the pocket/bores — OCC on this build declines fillets once a part has pockets,
    # so the roundover must go on the clean box first.
    try:
        slider = slider.edges().fillet(P.slider_block_fillet)
    except Exception as e:  # noqa: BLE001 — report, don't mask; block still prints
        print(f"  [warn] slider: block fillet skipped ({e}).")

    # Tab seat on the -Y (inside / head-side) face: a shallow pocket the band's end
    # tab registers into. (Was a sliding channel; the band now BOLTS here — it does
    # not ride.) Width = slider_tab_seat_width (X), shallow depth (Y), full Z.
    seat_w = P.slider_tab_seat_width
    seat_d = P.slider_tab_seat_depth
    floor_y = -d / 2 + seat_d                    # +Y face of the pocket (tab seats here)
    seat = (
        cq.Workplane("XY")
        .center(0, -d / 2 + seat_d / 2)          # sit against the -Y face
        .box(seat_w, seat_d + 0.2, h + 2, centered=(True, True, True))
    )
    slider = slider.cut(seat)

    # Two M3 mount bores through the seat floor (axis +Y) — the band end tab bolts
    # to this inside face with two screws (heat-set inserts in the slider), spaced
    # at the band's end-hole pitch ACROSS the width and set high so they clear the
    # swivel bore below. Screws enter from the inside (head side).
    bore_r = P.m3_insert_hole_diameter / 2
    s = P.bow_endtab_hole_spacing / 2            # half-pitch across width (X)
    mount_z = P.slider_mount_bore_z              # above the swivel bore
    for x in (+s, -s):
        bore = cq.Solid.makeCylinder(
            bore_r, P.insert_boss_depth,
            cq.Vector(x, floor_y, mount_z), cq.Vector(0, 1, 0))
        slider = slider.cut(cq.Workplane(obj=bore))

    # Vertical POST bore (axis Z, centre) — the yoke's round adjustment post slides
    # THROUGH this for height (head-size) adjustment, so it runs the full block.
    post_bore_d = P.yoke_post_diameter + P.slider_post_clearance
    post_bore = (
        cq.Workplane("XY").workplane(offset=-h / 2 - 1)
        .circle(post_bore_d / 2).extrude(h + 2)
    )
    slider = slider.cut(post_bore)

    # THUMBSCREW lock (Grado HP1000-style) — a boss on the +Y (outer) face with an M4
    # heat-set bore; the thumbscrew threads in and its tip presses the post (friction
    # lock, no detent). A clearance hole carries the screw shaft to the post bore.
    ts_z, boss_h = 0.0, 4.0
    boss = cq.Solid.makeCylinder(
        P.slider_thumbscrew_boss / 2, boss_h,
        cq.Vector(0, d / 2, ts_z), cq.Vector(0, 1, 0))
    slider = slider.union(cq.Workplane(obj=boss))
    ins = cq.Solid.makeCylinder(
        P.slider_thumbscrew_insert_hole / 2, P.insert_boss_depth,
        cq.Vector(0, d / 2 + boss_h, ts_z), cq.Vector(0, -1, 0))
    slider = slider.cut(cq.Workplane(obj=ins))
    clr = cq.Solid.makeCylinder(
        P.slider_thumbscrew_diameter / 2 + 0.2, d / 2 + boss_h,   # to the post bore centre, not through
        cq.Vector(0, d / 2 + boss_h, ts_z), cq.Vector(0, -1, 0))
    slider = slider.cut(cq.Workplane(obj=clr))

    return slider


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
