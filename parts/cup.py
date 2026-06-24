# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Cup shell — the heart of the Daily Driver (v0.3 engineering pass).

Build order: acoustic void → shell → clean concentric grille (decoupled from the
bosses) → 4 wall-blended baffle bosses (front-facing heat-set bore) → 2 external
yoke pivot bosses on the side walls (radial heat-set bore for the fork shoulder
screw). Every dimension is an ESTIMATE flagged in params.py — measured values
overwrite cleanly.

Reconciled to design-spec.md v0.3: the baffle bosses moved OFF the grille and
into the perimeter wall, so the grille's outer ring is now its own radius
(P.grille_outer_ring_radius), no longer pinned to the boss circle.
"""

import math

import cadquery as cq
from params import P
from parts import features


def pivot_stop_pins() -> cq.Workplane:
    """The two over-rotation stop pins, in the cup frame.

    Shared by make_cup (unioned onto the cup) and gate.py (rotated to verify the
    hard stop), so the gate checks the exact geometry that ships. Each pin sits on
    a boss end-cap face, pivot_stop_radius below the pivot axis (−Z), and reaches
    through the mating yoke eye's arc slot. Re-derived from Open-Omega's cup
    rotation limiter (credited in DESIGN-LOG); nothing copied.
    """
    r_out_boss = P.pivot_boss_outer_radius
    zc = P.pivot_boss_z
    pins = None
    for sign in (+1, -1):
        pin = (
            cq.Workplane("YZ")
            .workplane(offset=sign * (r_out_boss - 2.0))
            .center(0, zc - P.pivot_stop_radius)
            .circle(P.pivot_stop_pin_diameter / 2)
            .extrude(sign * (P.yoke_arm_thickness + 2.0))
        )
        pins = pin if pins is None else pins.union(pin)
    return pins


def make_cup() -> cq.Workplane:
    od = P.cup_outer_diameter
    total_h = P.cup_total_height

    # 1. Solid blank, front (+Z) up, closed back at the bottom.
    cup = cq.Workplane("XY").circle(od / 2).extrude(total_h)

    # 2. Shell out the front face → open cup, walls = wall_thickness, back closed.
    cup = cup.faces(">Z").shell(-P.wall_thickness)

    # 3. Rear vent grille — clean concentric-ring grille, DECOUPLED from the
    #    bosses. Remaining material = center hub + grille_ring_count rings +
    #    grille_spoke_count spokes; gaps open to the driver. Outer ring sits at
    #    P.grille_outer_ring_radius (its own value now). Built as an annular
    #    CUTTER (zone disc minus kept members), cut from the closed back. Cut
    #    BEFORE the bosses so nothing slices a boss.
    w = P.grille_member_width
    r_out = P.grille_outer_ring_radius
    hub_r = P.grille_hub_diameter / 2
    if P.grille_ring_count <= 1:
        ring_radii = [r_out]
    elif P.grille_ring_count == 2:
        ring_radii = [P.grille_inner_ring_radius, r_out]
    else:  # fill remaining rings evenly between inner and outer
        r_lo = P.grille_inner_ring_radius
        n = P.grille_ring_count
        ring_radii = [r_lo + (r_out - r_lo) * k / (n - 1) for k in range(n)]
    zone_r = r_out + w / 2  # outer edge of the outer ring = grille zone radius

    z0 = -1.0
    cut_h = P.wall_thickness + 2.0

    def _disc(radius):
        return cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(cut_h)

    zone = _disc(zone_r)
    keep = _disc(hub_r)  # center hub
    for rc in ring_radii:  # concentric rings (annuli of width w)
        ring = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .circle(rc + w / 2)
            .circle(max(rc - w / 2, 0.01))
            .extrude(cut_h)
        )
        keep = keep.union(ring)
    for i in range(P.grille_spoke_count):  # radial spokes
        ang = i * 360.0 / P.grille_spoke_count
        spoke = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .transformed(rotate=(0, 0, ang))
            .center(zone_r / 2, 0)
            .rect(zone_r, w)
            .extrude(cut_h)
        )
        keep = keep.union(spoke)

    cup = cup.cut(zone.cut(keep))

    # 4. Baffle-mounting bosses — wall-blended (NOT free-standing posts). Columns
    #    on the diagonals at the bolt circle (r=baffle_screw_radius=35), from the
    #    interior floor up to the baffle underside (seat_z). baffle_boss_diameter
    #    (10) is sized so each boss reaches the inner wall (35 + 5 = 40 > 39 R)
    #    and the outer grille ring (32), merging into both — that's the "blended
    #    into the perimeter wall" the v0.3 spec calls for. The heat-set bore in
    #    the front-facing top takes the baffle screw from the front.
    boss_points = [
        (
            P.baffle_screw_radius * math.cos(math.radians(45 + i * 360 / P.baffle_screw_count)),
            P.baffle_screw_radius * math.sin(math.radians(45 + i * 360 / P.baffle_screw_count)),
        )
        for i in range(P.baffle_screw_count)
    ]
    cup = features.boss(
        cup,
        boss_points,
        floor_z=P.cup_interior_floor_z,
        outer_diameter=P.baffle_boss_diameter,
        bore_diameter=P.m3_insert_hole_diameter,
        height=P.baffle_boss_height,
        bore_depth=P.insert_boss_depth,
        base_fillet=P.boss_base_fillet,
    )

    # 5. Yoke pivot bosses — two external bosses at 0/180 on the cup side walls,
    #    at mid-height, each a radial cylinder spanning THROUGH the wall (from an
    #    inner lug to an outer seat) so it fully houses an M3 heat-set insert
    #    bored from the outside. The fork's shoulder screw threads into it.
    #    TODO: yoke_pivot_centres (88) is only ~2 mm proud of cup_od per side, so
    #    the inner end is a small lug protruding into the cavity — fine here,
    #    revisit the boss form when the real fork is measured.
    r_out_boss = P.pivot_boss_outer_radius              # 44
    r_in_boss = r_out_boss - P.pivot_boss_through_span  # 35
    span = P.pivot_boss_through_span
    zc = P.pivot_boss_z
    for sign in (+1, -1):
        # boss body: cylinder axis ±X, dia pivot_boss_diameter
        body = (
            cq.Workplane("YZ")
            .workplane(offset=sign * r_in_boss)
            .center(0, zc)
            .circle(P.pivot_boss_diameter / 2)
            .extrude(sign * span)
        )
        cup = cup.union(body)
        # heat-set bore from the outer face inward (insert installed from outside)
        bore = (
            cq.Workplane("YZ")
            .workplane(offset=sign * r_out_boss)
            .center(0, zc)
            .circle(P.m3_insert_hole_diameter / 2)
            .extrude(-sign * P.insert_boss_depth)
        )
        cup = cup.cut(bore)

    # 5b. Over-rotation STOP pin — a small pin on each boss end-cap face, offset
    #     pivot_stop_radius straight up (+Z) from the pivot axis, protruding into
    #     the mating yoke eye's arc slot (see yoke.py). The slot ends are the hard
    #     stop; this pin is the follower. Re-derived from Open-Omega's cup rotation
    #     limiter (credited in DESIGN-LOG); nothing copied. Placed at the BOTTOM
    #     of the eye (−Z), clear of the arm bar that joins at the top. Geometry is
    #     in pivot_stop_pins() so the gate verifies exactly what ships.
    cup = cup.union(pivot_stop_pins())

    # 6. Best-effort comfort fillet on the outer wall (no-op on the current
    #    cylindrical form; warns rather than silently swallowing — see history).
    outer_r = P.cup_outer_diameter / 2
    outer_edges = cup.edges("|Z").filter(
        lambda e: abs(math.hypot(e.Center().x, e.Center().y) - outer_r) < 3.0
    )
    if outer_edges.vals():
        try:
            cup = outer_edges.fillet(P.edge_fillet)
        except Exception as e:  # noqa: BLE001 — report, don't mask
            print(
                f"  [warn] cup: outer-edge comfort fillet skipped ({e}). "
                "Deferred to the form pass once the outer profile is set."
            )

    return cup


if __name__ == "__main__":
    cq.exporters.export(make_cup(), "output/cup.stl")
    print("wrote output/cup.stl")
