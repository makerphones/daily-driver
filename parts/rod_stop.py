# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Rod TOP-STOP knob — a small bought knurled knob that screws into the rod's tapped top end.

The yoke rod's bottom is captured (bonded socket); the slider can't ride off the BOTTOM because the
fork's boss is wider than the bore. This knob is the TOP stop: an M3 stud threads into the rod's
faced+tapped top end, and the knob head is wider than the slider bore, so when the lock is loose and
the cup drops, the head catches the slider's top face — the cup can't slide off. Assembly: drop the
slider onto the rod first, THEN screw this on. REFERENCE/bought viz (a small knurled knob/thumb nut).

Built head-up from z=0 (the rod's top face): head above, M3 stud below into the rod.
"""

import math

import cadquery as cq
from params import P


def make_rod_stop() -> cq.Workplane:
    d = P.rod_stop_diameter
    h = P.rod_stop_height
    knob = cq.Workplane("XY").circle(d / 2).extrude(h)         # head, z=0..h
    knob = knob.union(cq.Workplane("XY").circle(1.45).extrude(-5.0))  # M3 stud, into the rod
    # Knurl hint so it reads as a hand knob (cosmetic, best-effort).
    try:
        for i in range(14):
            a = math.radians(i * 360.0 / 14)
            flute = cq.Solid.makeCylinder(
                0.4, h + 1, cq.Vector(d / 2 * math.cos(a), d / 2 * math.sin(a), -0.5),
                cq.Vector(0, 0, 1))
            knob = knob.cut(cq.Workplane(obj=flute))
    except Exception:  # noqa: BLE001 — knurl is cosmetic
        pass
    return knob


if __name__ == "__main__":
    cq.exporters.export(make_rod_stop(), "output/rod_stop.step")
    print("wrote output/rod_stop.step")
