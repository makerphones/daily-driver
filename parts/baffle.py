"""
Baffle plate — the flat part the driver mounts to.

This is the simplest real part (flat, prints flat with no supports) and the
best one to print first to confirm the whole toolchain end to end. It carries
the driver cutout with a seating ledge, a gasket channel, the four mounting
holes that match the cup's bosses, and a cable pass-through.
"""

import cadquery as cq
from params import P


def make_baffle() -> cq.Workplane:
    r = P.baffle_diameter / 2
    t = P.baffle_thickness

    # 1. Round plate.
    baffle = cq.Workplane("XY").circle(r).extrude(t)

    # 2. Driver opening. The driver sits on a ledge: a smaller acoustic aperture
    #    on the back side, opening up to driver_od on the front so the frame
    #    drops in and rests on the ledge.
    cutout = P.driver_cutout_diameter
    seat = P.driver_od + 0.4  # driver frame drops into this recess
    seat_depth = t * 0.5      # ledge sits halfway through the plate
    # through acoustic aperture
    baffle = (
        baffle.faces(">Z").workplane()
        .hole(cutout)
    )
    # front-side recess so the driver frame seats flush-ish on the ledge
    baffle = (
        baffle.faces(">Z").workplane()
        .circle(seat / 2)
        .cutBlind(-seat_depth)
    )

    # 3. Gasket channel around the driver opening, on the front face.
    gc_outer = (seat + P.gasket_channel_width * 2) / 2
    baffle = (
        baffle.faces(">Z").workplane()
        .circle(gc_outer)
        .circle(seat / 2)
        .cutBlind(-P.gasket_channel_depth)
    )

    # 4. Four clearance holes matching the cup bosses.
    baffle = (
        baffle.faces(">Z").workplane()
        .polarArray(P.baffle_screw_radius, 45, 360, P.baffle_screw_count)
        .hole(P.m3_clearance_hole)
    )

    # 5. Cable pass-through near one edge (toward the headband side, +Y here).
    baffle = (
        baffle.faces(">Z").workplane()
        .center(0, r - P.cable_hole_diameter)
        .hole(P.cable_hole_diameter)
    )

    return baffle


if __name__ == "__main__":
    cq.exporters.export(make_baffle(), "output/baffle.stl")
    print("wrote output/baffle.stl")
