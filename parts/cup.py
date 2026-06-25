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
    a boss end-cap face at pivot_stop_radius from the pivot axis, in the cup −Y
    direction. In the assembly's worn pose the cup is mounted 90° clocked vs the
    yoke, which rotates cup −Y to global −Z — landing the pin in the yoke eye's
    −Z arc slot at the tilt rest. Re-derived from Open-Omega's cup rotation limiter
    (credited in DESIGN-LOG); nothing copied.
    """
    r_out_boss = P.pivot_boss_outer_radius
    zc = P.pivot_boss_z
    pins = None
    for sign in (+1, -1):
        pin = (
            cq.Workplane("YZ")
            .workplane(offset=sign * (r_out_boss - 2.0))
            .center(-P.pivot_stop_radius, zc)        # cup −Y → worn-pose slot at global −Z
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

    # 2. Hollow the acoustic void from the front (+Z), leaving side walls of
    #    wall_thickness and a thicker closed back (cup_back_thickness) — the grille
    #    substrate the chamfer lives in. Explicit cut (not shell) so the back band
    #    can be thicker than the side wall.
    void_r = P.cup_interior_diameter / 2
    void = (
        cq.Workplane("XY").workplane(offset=P.cup_back_thickness)
        .circle(void_r).extrude(total_h)          # up through the open front (and beyond)
    )
    cup = cup.cut(void)

    # 2b. Chamfered back (form pass direction "A"): a ~45° bevel on the back-outer
    #     edge, confined to the back band so the 3 mm side wall (z ≥ back band) is
    #     untouched and the grille zone (r ≤ 34) stays on a flat face. Done before
    #     the grille while the bottom is still a clean disc (one outer edge).
    cup = cup.edges("<Z").chamfer(P.cup_back_chamfer)

    # 3. Rear vent grille — clean concentric-ring grille, DECOUPLED from the
    #    bosses. Remaining material = center hub + grille_ring_count rings +
    #    grille_spoke_count spokes; gaps open to the driver. Outer ring sits at
    #    P.grille_outer_ring_radius (its own value now). Built as an annular
    #    CUTTER (zone disc minus kept members), cut from the closed back. Cut
    #    BEFORE the bosses so nothing slices a boss.
    r_out = P.grille_outer_ring_radius
    hub_r = P.grille_hub_diameter / 2
    # (radius, width) per ring — the OUTER ring is the heavier one (echoes the mark).
    if P.grille_ring_count <= 1:
        ring_specs = [(r_out, P.grille_outer_ring_width)]
    elif P.grille_ring_count == 2:
        ring_specs = [(P.grille_inner_ring_radius, P.grille_inner_ring_width),
                      (r_out, P.grille_outer_ring_width)]
    else:  # fill rings evenly; only the outermost gets the heavy width
        r_lo = P.grille_inner_ring_radius
        n = P.grille_ring_count
        ring_specs = [(r_lo + (r_out - r_lo) * k / (n - 1),
                       P.grille_outer_ring_width if k == n - 1 else P.grille_inner_ring_width)
                      for k in range(n)]
    # Fine support-lattice rings distributed across the open zone — braces the
    # spokes so no thin member spans far enough to be poked in.
    n_lat = P.grille_lattice_ring_count
    for k in range(1, n_lat + 1):
        rr = hub_r + (r_out - hub_r) * k / (n_lat + 1)
        ring_specs.append((rr, P.grille_lattice_member_width))
    zone_r = r_out + P.grille_outer_ring_width / 2  # outer edge of the outer ring = zone

    z0 = -1.0
    cut_h = P.cup_back_thickness + 2.0          # pierce the full (thicker) back band

    def _disc(radius):
        return cq.Workplane("XY").workplane(offset=z0).circle(radius).extrude(cut_h)

    zone = _disc(zone_r)
    keep = _disc(hub_r)  # center DOT
    for rc, rw in ring_specs:  # concentric rings (annuli of per-ring width)
        ring = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .circle(rc + rw / 2)
            .circle(max(rc - rw / 2, 0.01))
            .extrude(cut_h)
        )
        keep = keep.union(ring)
    for i in range(P.grille_spoke_count):  # thin radial spokes (structural only)
        ang = i * 360.0 / P.grille_spoke_count
        spoke = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .transformed(rotate=(0, 0, ang))
            .center(zone_r / 2, 0)
            .rect(zone_r, P.grille_spoke_width)
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
    #    at mid-height, each a radial cylinder spanning the wall to an outer seat so
    #    it fully houses an M3 heat-set insert bored from the outside. The fork's
    #    shoulder screw threads into it. With the pad-driven 90 mm cup the wall is
    #    6 mm, so the boss (span 9) is ~4 mm proud and its inner end now stops IN the
    #    wall — no lug into the cavity (the old thin-wall lug is gone).
    r_out_boss = P.pivot_boss_outer_radius              # 49 (yoke_pivot_centres/2)
    r_in_boss = r_out_boss - P.pivot_boss_through_span  # 40 — inside the 6 mm wall
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

    # 5b. Over-rotation STOP pin — a small pin on each boss end-cap face at
    #     pivot_stop_radius from the pivot axis (cup −Y), protruding into the mating
    #     yoke eye's arc slot. In the worn pose the cup is 90° clocked vs the yoke,
    #     so cup −Y lands at the slot (yoke −Z), away from the arm. The slot ends are
    #     the hard stop; this pin is the follower. Re-derived from Open-Omega's cup
    #     rotation limiter (credited in DESIGN-LOG); nothing copied. Geometry is in
    #     pivot_stop_pins() so the gate verifies exactly what ships.
    cup = cup.union(pivot_stop_pins())

    # 6. Edge treatment: the back-outer comfort/print break is now the chamfer in
    #    step 2b (the form pass "set the outer profile"), so the old no-op outer-
    #    wall fillet — which only ever warned on the bare cylinder — is retired.

    # 7. Earpad RETAINING FLANGE (DT770-style) — a thin brim at the cup's front
    #    OUTER edge that extends the perimeter OUTWARD (radially), so the earpad's
    #    skirt wraps over it and hooks BEHIND it. It sticks OUT toward the perimeter,
    #    NOT up toward the head, so the baffle stays flush (not recessed). The brim
    #    sits at the front edge (top flush with the rim); below it the wall steps
    #    back in, giving the pad skirt an undercut to grip. A lead-in chamfer on the
    #    outer-front corner eases the pad over.
    flange_ir = od / 2 - 1.0                          # overlap the wall → solid union
    flange_or = od / 2 + P.pad_lip_extension          # brim sticks OUT to here
    flange = (
        cq.Workplane("XY")
        .workplane(offset=total_h - P.pad_lip_thickness)
        .circle(flange_or).circle(flange_ir)
        .extrude(P.pad_lip_thickness)
    )
    try:
        flange = flange.edges(">Z").chamfer(P.pad_lip_leadin)
    except Exception as e:  # noqa: BLE001 — report, don't mask; the flange still stands
        print(f"  [warn] cup: pad-flange lead-in chamfer skipped ({e}).")
    cup = cup.union(flange)

    return cup


if __name__ == "__main__":
    cq.exporters.export(make_cup(), "output/cup.stl")
    print("wrote output/cup.stl")
