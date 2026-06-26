# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Fork-yoke — wraparound bracket that follows the earcup (v0.3 engineering pass).

Two arms sweep from a top swivel hub down AROUND the round cup to two pivot eyes
on its ±X sides. Each arm follows a quarter-ellipse (semi-axes a = eye x, b = hub
z) so it mimics the cup's circular outline with clearance — wider over the top than
at the sides so the cup can tilt without striking the bracket (cf. the Extreme
Isolation yoke). Each eye takes an M3 shoulder screw into the cup's pivot boss (the
tilt joint, ±tilt_range); the swivel hub's vertical bore mates the slider above.

Local frame: pivot axis at z=0 (eyes at ±yoke_pivot_centres/2, 0, 0); the hub is at
z=yoke_fork_height. In assembly the frame is lifted so z=0 lands on the cup's pivot
bosses (cup mid-height).

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
    a = P.yoke_pivot_centres / 2             # 49 — eye x = ellipse semi-axis (sides)
    b = P.yoke_fork_height                   # 55 — hub z = ellipse semi-axis (top)
    arm_w = P.yoke_arm_width
    arm_t = P.yoke_arm_thickness
    hub_z = P.yoke_fork_height

    yoke = None
    for sign in (+1, -1):
        x_eye = sign * a
        # eye: cylinder axis X around the pivot hole
        eye = (
            cq.Workplane("YZ")
            .workplane(offset=x_eye - arm_t / 2)
            .center(0, 0)
            .circle(P.yoke_pivot_eye_diameter / 2)
            .extrude(arm_t)
        )
        # The arm WRAPS the round cup: it follows a quarter-ellipse from the eye
        # (a, 0) at the cup's side up and over to the hub (0, b) at the top,
        # mimicking the cup's circular outline (cf. the Extreme Isolation bracket).
        # The ellipse is taller than wide (b > a), so the gap to the cup grows from
        # ~4 mm at the sides to ~(b − cup_r) at the top — the cup needs that extra
        # top room to tilt in/out without striking the bracket. Built from short
        # tapered bars (robust; OCC sweep/fillet are unreliable on this build).
        n = 32                          # dense → the chord facets read as a smooth curve
        cpts = [(sign * a * math.cos(math.radians(90 * i / n)),
                 b * math.sin(math.radians(90 * i / n))) for i in range(n + 1)]
        arm = eye
        m = len(cpts) - 1
        for j in range(m):
            s0, s1 = j / m, (j + 1) / m
            w0 = arm_w + (P.yoke_arm_hub_width - arm_w) * s0
            w1 = arm_w + (P.yoke_arm_hub_width - arm_w) * s1
            arm = arm.union(_bar(cpts[j], cpts[j + 1], w0, w1, arm_t))
        yoke = arm if yoke is None else yoke.union(arm)

    # Junction hub + vertical adjustment POST (replaces the fixed swivel hub). The
    # arms tie into a short junction hub at the apex; a round POST rises from it and
    # SLIDES in the slider for height (head-size) adjustment, locked by the slider
    # thumbscrew (Grado HP1000-style). Round → the cup also swivels when unlocked.
    hub_d = P.yoke_post_diameter + 4.0          # short junction hub, wider than the post
    hub = (
        cq.Workplane("XY").workplane(offset=hub_z - 4)
        .circle(hub_d / 2).extrude(8)
    )
    post = (
        cq.Workplane("XY").workplane(offset=hub_z - 4)
        .circle(P.yoke_post_diameter / 2).extrude(8 + P.yoke_post_length)
    )
    yoke = yoke.union(hub).union(post)

    # bores: pivot holes (axis X) through each eye. (The adjustment post is SOLID —
    # no bore; it slides in the slider and the slider thumbscrew locks it.)
    for sign in (+1, -1):
        x = sign * a
        bore = (
            cq.Workplane("YZ")
            .workplane(offset=x - (arm_t / 2 + 1))
            .center(0, 0)
            .circle(P.yoke_pivot_hole_diameter / 2)
            .extrude(arm_t + 2)
        )
        yoke = yoke.cut(bore)

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
        x = sign * a
        for k in range(nseg):
            ang = math.radians(-half_a + 2 * half_a * k / (nseg - 1))
            seg = (
                cq.Workplane("YZ")
                .workplane(offset=x - (arm_t / 2 + 1))
                .center(rp * math.sin(ang), -rp * math.cos(ang))  # radius rp, ±ang from −Z
                .circle(slot_r)
                .extrude(arm_t + 2)
            )
            yoke = yoke.cut(seg)

    # best-effort fillets at the knee/junctions (printability); warn, don't mask
    try:
        yoke = yoke.edges("|Y").fillet(1.0)
    except Exception as e:  # noqa: BLE001
        print(f"  [warn] yoke: junction fillet skipped ({e}).")

    # Tilt clearance: the wraparound arms follow an ellipse that clears the cup by
    # ~4 mm at the sides and ~10 mm over the top, so the cup tilts in/out without
    # striking the bracket. VERIFIED IN-CAD by gate.py (pivot-tilt-clearance):
    # rotating the cup through the full ±tilt_range adds <1% to the 0° cup∩yoke
    # bearing overlap. A test print should still confirm the real friction/feel.
    return yoke


if __name__ == "__main__":
    cq.exporters.export(make_yoke(), "output/yoke.stl")
    print("wrote output/yoke.stl")
