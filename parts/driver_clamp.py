# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Driver clamp ring — retains the driver from the BACK (3-bolt, the maker's prototype).

A 3-ear ring that slips over the back of the driver: the driver's rear nests SLIGHTLY
into a RECESS in the ring, the recess wall captures the driver's outer edge, and the
recess floor (an inner shoulder) bears on the back of the frame rim — pressing the
driver forward into the baffle's recess. The magnet protrudes back through the open
centre. The 3 ears bolt to standoff bosses on the baffle BACK. Independent of the
baffle→frame mount.

Local frame: the shoulder face (bears on the driver rear rim) is at z=0; the RECESS
opens +Z (the driver nests in from +Z); the floor + ears run -Z. All driver-fit dims
are REF / driver-pending (params.py).
"""

import math

import cadquery as cq
from params import P


def make_driver_clamp() -> cq.Workplane:
    ir = P.driver_clamp_inner_diameter / 2                       # open centre (magnet clears)
    rec_r = (P.driver_od + P.driver_clamp_recess_clearance) / 2  # recess: the driver nests in
    orr = rec_r + P.driver_clamp_wall                            # outer wall OD
    floor_th = P.driver_clamp_floor_thickness                    # shoulder floor
    rec_d = P.driver_clamp_recess_depth                          # how far the driver nests
    bcr = P.driver_clamp_bolt_circle / 2
    ear_r = P.driver_clamp_ear_diameter / 2
    n = P.driver_clamp_count

    # Shoulder floor [ir, rec_r] at z(-floor_th .. 0) — bears on the driver rear rim.
    clamp = (cq.Workplane("XY").workplane(offset=-floor_th)
             .circle(rec_r).circle(ir).extrude(floor_th))
    # Outer recess wall [rec_r, orr] full height z(-floor_th .. rec_d) — captures the
    # driver's outer edge; the driver nests into the recess (r < rec_r, z 0..rec_d).
    clamp = clamp.union(cq.Workplane("XY").workplane(offset=-floor_th)
                        .circle(orr).circle(rec_r).extrude(floor_th + rec_d))

    # Three ears at the floor level: a pad at each bolt point + a bar to the wall.
    for i in range(n):
        a = math.radians(i * 360.0 / n)           # 0 / 120 / 240
        ex, ey = bcr * math.cos(a), bcr * math.sin(a)
        pad = (cq.Workplane("XY").workplane(offset=-floor_th).center(ex, ey)
               .circle(ear_r).extrude(floor_th))
        bar = (
            cq.Workplane("XY").workplane(offset=-floor_th)
            .transformed(rotate=(0, 0, math.degrees(a)))
            .center((orr + bcr) / 2, 0)
            .rect(bcr - orr + 2 * ear_r, 2 * ear_r)
            .extrude(floor_th)
        )
        clamp = clamp.union(pad).union(bar)

    # M3 clearance holes through each ear (axial).
    for i in range(n):
        a = math.radians(i * 360.0 / n)
        ex, ey = bcr * math.cos(a), bcr * math.sin(a)
        hole = (cq.Workplane("XY").workplane(offset=-floor_th - 0.5).center(ex, ey)
                .circle(P.m3_clearance_hole / 2).extrude(floor_th + 1.0))
        clamp = clamp.cut(hole)

    return clamp


if __name__ == "__main__":
    cq.exporters.export(make_driver_clamp(), "output/driver_clamp.stl")
    print("wrote output/driver_clamp.stl")
