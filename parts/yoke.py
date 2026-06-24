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


def _bar(p0, p1, w0, w1, thick):
    """A flat bar in the XZ plane from p0 to p1 (each (x, z)), tapering in width
    from w0 (at p0) to w1 (at p1). w0 == w1 gives a constant bar. Built from a
    trapezoid profile (no fillets/chamfers — robust on this OCC build)."""
    (x0, z0), (x1, z1) = p0, p1
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    length = math.hypot(x1 - x0, z1 - z0)
    ang = math.degrees(math.atan2(z1 - z0, x1 - x0))
    half = length / 2
    pts = [(-half, -w0 / 2), (-half, w0 / 2), (half, w1 / 2), (half, -w1 / 2)]
    return (
        cq.Workplane("XZ")
        .transformed(offset=(cx, cz, 0), rotate=(0, 0, ang))
        .polyline(pts).close()
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
        # Smooth curved arm (replaces the angular knee): go straight up the cup
        # side to clear it, then a COSINE-EASED sweep in to the hub. The ease has a
        # vertical tangent at the knee, matching the straight part → C1-continuous
        # (no visible corner). Width tapers eye→hub along the path. Built from short
        # tapered segments (robust; OCC sweep/fillet are unreliable on this build).
        cpts = [(x, 0.0), (x, knee_z)]
        n_up = 28                       # dense → the chord facets read as a smooth curve
        for i in range(1, n_up + 1):
            u = i / n_up
            cpts.append((x * math.cos(math.pi / 2 * u),          # |x|: arm_w → 0 (to hub)
                         knee_z + (hub_z - knee_z) * u))
        seg = [math.hypot(cpts[j + 1][0] - cpts[j][0], cpts[j + 1][1] - cpts[j][1])
               for j in range(len(cpts) - 1)]
        total = sum(seg)
        arm = eye
        acc = 0.0
        for j in range(len(cpts) - 1):
            s0, s1 = acc / total, (acc + seg[j]) / total
            acc += seg[j]
            w0 = arm_w + (P.yoke_arm_hub_width - arm_w) * s0
            w1 = arm_w + (P.yoke_arm_hub_width - arm_w) * s1
            arm = arm.union(_bar(cpts[j], cpts[j + 1], w0, w1, arm_t))
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

    # over-rotation STOP arc slot: a clearance pocket at radius pivot_stop_radius
    # around each pivot, spanning ±pivot_stop_slot_halfangle from straight-up. The
    # cup's stop pin rides it; the slot ENDS are the hard stop that bounds tilt
    # just past the ±20° working range, protecting the M3 shoulder screw. Built
    # from a fan of cylinders (this OCP build's revolve is unusable — see bow.py).
    rp = P.pivot_stop_radius
    slot_r = (P.pivot_stop_pin_diameter + 2 * P.pivot_stop_slot_clearance) / 2
    half_a = P.pivot_stop_slot_halfangle
    nseg = 25
    for sign in (+1, -1):
        x = sign * half
        for k in range(nseg):
            a = math.radians(-half_a + 2 * half_a * k / (nseg - 1))
            seg = (
                cq.Workplane("YZ")
                .workplane(offset=x - (arm_t / 2 + 1))
                .center(rp * math.sin(a), -rp * math.cos(a))  # radius rp, ±a from −Z (bottom)
                .circle(slot_r)
                .extrude(arm_t + 2)
            )
            yoke = yoke.cut(seg)

    # best-effort fillets at the knee/junctions (printability); warn, don't mask
    try:
        yoke = yoke.edges("|Y").fillet(1.0)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] yoke: junction fillet skipped ({e}).")

    # Tilt clearance: with yoke_pivot_centres=92 the arms sit ~4 mm proud of the
    # cup wall at Y=0. VERIFIED IN-CAD by gate.py (pivot-tilt-clearance): rotating
    # the cup through the full ±tilt_range about the pivot axis adds <1% to the 0°
    # cup∩yoke bearing overlap — the cup shell never reaches the arms (the boss is
    # coaxial with the tilt axis, so the bearing is invariant). A test print should
    # still confirm the real friction/feel, but geometric collision is ruled out.
    return yoke


if __name__ == "__main__":
    cq.exporters.export(make_yoke(), "output/yoke.stl")
    print("wrote output/yoke.stl")
