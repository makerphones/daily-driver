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

    # Swivel bore at the bottom (axis Z) — takes the fork swivel-hub pin. Fixed
    # depth (hosts the hub) so it stays below the mount bores.
    swivel = (
        cq.Workplane("XY")
        .workplane(offset=-h / 2 - 1)
        .circle(P.slider_swivel_bore / 2)
        .extrude(P.yoke_swivel_hub_height + 1)   # up from the bottom, not through
    )
    slider = slider.cut(swivel)

    return slider


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
