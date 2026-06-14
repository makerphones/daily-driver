# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Basic assembly — the parts that currently have real geometry, in their correct
relationship. Right now that's the CUP + BAFFLE: the baffle plate seated into the
front of the cup, resting on the baffle bosses.

Yoke and slider are still stubs/placeholders, so they're intentionally left out;
they join here once they have real geometry.

View it:  python show.py        (OCP CAD Viewer)
Export:   build.py writes output/assembly.step
"""

import cadquery as cq

from params import P
from parts.cup import make_cup
from parts.baffle import make_baffle


def make_assembly() -> cq.Assembly:
    cup = make_cup()

    # The baffle is modelled z=0..thickness with its driver recess on +Z. Seat it
    # at the cup front: flip 180° about X so the recess faces INTO the cup (driver
    # mounts cup-side and fires forward through the aperture), then lift it so its
    # top is flush with the front rim and its underside rests on the boss tops.
    baffle = (
        make_baffle()
        .rotate((0, 0, 0), (1, 0, 0), 180)
        .translate((0, 0, P.cup_total_height))
    )

    asm = cq.Assembly(name="daily_driver_cup_baffle")
    asm.add(cup, name="cup", color=cq.Color(0.30, 0.32, 0.35))      # matte charcoal
    asm.add(baffle, name="baffle", color=cq.Color(0.92, 0.45, 0.10))  # warm-orange accent
    return asm


if __name__ == "__main__":
    make_assembly().export("output/assembly.step")
    print("wrote output/assembly.step")
