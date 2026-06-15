# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Fork-yoke — DT880-style wishbone (v0.3 engineering pass).

Two arms drop from a top swivel hub down to two pivot eyes that straddle the cup
on its ±X sides. Each eye takes an M3 shoulder screw into the cup's pivot boss
(the tilt joint, ±tilt_range). The swivel hub's vertical bore mates the slider
above (the swivel joint).

Local frame: pivot axis at z=0 (eyes at ±yoke_pivot_centres/2, 0, 0); the hub is
straight up at z=yoke_fork_height. To clear the cup (radius cup_od/2) the arms run
VERTICALLY past the cup mid-height, then angle inward to the hub above the cup —
a straight eye→hub bar would cut through the cup. In assembly the frame is lifted
so z=0 lands on the cup's pivot bosses (cup mid-height).

All dimensions are ESTIMATES flagged in params.py.
"""

import math

import cadquery as cq
from params import P


def _bar(p0, p1, width, thick):
    """A flat bar (width × thick) in the XZ plane from p0 to p1 (each (x, z))."""
    (x0, z0), (x1, z1) = p0, p1
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    length = math.hypot(x1 - x0, z1 - z0)
    ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
    return (
        cq.Workplane("XZ")
        .transformed(offset=(cx, cz, 0), rotate=(0, 0, ang))
        .rect(length, width)
        .extrude(thick / 2, both=True)
    )


def make_yoke() -> cq.Workplane:
    half = P.yoke_pivot_centres / 2          # 44 — eye x position
    arm_w = P.yoke_arm_width
    arm_t = P.yoke_arm_thickness
    hub_z = P.yoke_fork_height               # 55
    # knee just above the cup top (local cup top = cup mid-height above the pivot)
    knee_z = P.cup_total_height / 2 + 2.0

    yoke = None
    for sign in (+1, -1):
        x = sign * half
        # eye: cylinder axis X around the pivot hole
        lower_x = x - arm_t / 2
        eye = (
            cq.Workplane("YZ")
            .workplane(offset=lower_x)
            .center(0, 0)
            .circle(P.yoke_pivot_eye_diameter / 2)
            .extrude(arm_t)
        )
        bar_a = _bar((x, 0), (x, knee_z), arm_w, arm_t)        # vertical, clears cup
        bar_b = _bar((x, knee_z), (0, hub_z), arm_w, arm_t)    # angle in to the hub
        arm = eye.union(bar_a).union(bar_b)
        yoke = arm if yoke is None else yoke.union(arm)

    # swivel hub at the top (axis Z), bore for the vertical slider pin
    hub = (
        cq.Workplane("XY")
        .workplane(offset=hub_z - P.yoke_swivel_hub_height / 2)
        .circle(P.yoke_swivel_hub_diameter / 2)
        .extrude(P.yoke_swivel_hub_height)
    )
    yoke = yoke.union(hub)

    # bores: pivot holes (axis X) through each eye, swivel bore (axis Z) through hub
    for sign in (+1, -1):
        x = sign * half
        bore = (
            cq.Workplane("YZ")
            .workplane(offset=x - (arm_t / 2 + 1))
            .center(0, 0)
            .circle(P.yoke_pivot_hole_diameter / 2)
            .extrude(arm_t + 2)
        )
        yoke = yoke.cut(bore)
    swivel = (
        cq.Workplane("XY")
        .workplane(offset=hub_z - P.yoke_swivel_hub_height / 2 - 1)
        .circle(P.yoke_swivel_bore / 2)
        .extrude(P.yoke_swivel_hub_height + 2)
    )
    yoke = yoke.cut(swivel)

    # best-effort fillets at the knee/junctions (printability); warn, don't mask
    try:
        yoke = yoke.edges("|Y").fillet(1.0)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] yoke: junction fillet skipped ({e}).")

    # TODO (tilt clearance): arms sit ~2 mm proud of the cup wall at Y=0; verify
    # the cup clears the arms through the full ±tilt_range once the real cup pose
    # is set. Not resolved here — flagged for the measured-fit pass.
    return yoke


if __name__ == "__main__":
    cq.exporters.export(make_yoke(), "output/yoke.stl")
    print("wrote output/yoke.stl")
