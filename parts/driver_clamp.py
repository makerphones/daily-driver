# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Driver clamp ring — holds the driver to the baffle (3-bolt, the maker's prototype).

A 3-ear ring (like an exhaust flange) that presses the driver into the baffle's back
recess, bolted to 3 M3 heat-set inserts in the baffle BACK. A raised front LIP bears
on the driver's mounting flange; the open centre clears the magnet/dome. Light: a
thin eared ring. Independent of the baffle→frame mount.

Local frame: ring back at z=0, front (lip, toward the driver/baffle) at +Z. In
assembly it sits behind the driver; the lip presses forward. All driver-fit dims are
REF / driver-pending (params.py).
"""

import math

import cadquery as cq
from params import P


def make_driver_clamp() -> cq.Workplane:
    ir = P.driver_clamp_inner_diameter / 2        # open centre
    orr = P.driver_clamp_ring_outer / 2           # ring body OD
    th = P.driver_clamp_thickness
    bcr = P.driver_clamp_bolt_circle / 2          # bolt circle
    ear_r = P.driver_clamp_ear_diameter / 2
    n = P.driver_clamp_count

    # Main ring (z0..th).
    clamp = cq.Workplane("XY").circle(orr).circle(ir).extrude(th)

    # Three ears: a pad at each bolt point + a bar tying it back to the ring.
    for i in range(n):
        a = math.radians(i * 360.0 / n)           # 0 / 120 / 240
        ex, ey = bcr * math.cos(a), bcr * math.sin(a)
        pad = cq.Workplane("XY").center(ex, ey).circle(ear_r).extrude(th)
        bar = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, math.degrees(a)))
            .center((orr + bcr) / 2, 0)
            .rect(bcr - orr + 2 * ear_r, 2 * ear_r)
            .extrude(th)
        )
        clamp = clamp.union(pad).union(bar)

    # Front contact LIP — a raised ring [inner .. driver_od/2] that bears on the
    # driver's mounting flange and stands the ring off the recess floor.
    lip = (
        cq.Workplane("XY").workplane(offset=th)
        .circle(P.driver_od / 2).circle(ir)
        .extrude(P.driver_clamp_lip_height)
    )
    clamp = clamp.union(lip)

    # M3 clearance holes through each ear.
    for i in range(n):
        a = math.radians(i * 360.0 / n)
        ex, ey = bcr * math.cos(a), bcr * math.sin(a)
        hole = (
            cq.Workplane("XY").workplane(offset=-0.5)
            .center(ex, ey).circle(P.m3_clearance_hole / 2)
            .extrude(th + P.driver_clamp_lip_height + 1.0)
        )
        clamp = clamp.cut(hole)

    return clamp


if __name__ == "__main__":
    cq.exporters.export(make_driver_clamp(), "output/driver_clamp.stl")
    print("wrote output/driver_clamp.stl")
