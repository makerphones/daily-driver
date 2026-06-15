# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Printability gate — the build ritual's verification step, made enforceable.

This promotes the checks we've been running by hand into a committed linter:
build the printed parts in-process and assert they are actually printable. A HARD
failure exits non-zero (CI fails before anyone wastes filament); a SOFT warning
prints but does not fail (cosmetic / deferred / measured-later items).

It does NOT change what the checks are — only makes them enforceable. Thresholds
live as named constants below so they're transparent and tunable.

    python gate.py        # build parts in-process, run checks, exit 0/1

Core deps only (cadquery) — never imports render/matplotlib, so CI can run it
with just requirements.txt.
"""

import math
import sys

import cadquery as cq
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_ON

from params import P
from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider

# ---- Thresholds (named + transparent; not new checks, just the limits) -------
MIN_WALL = 2.0          # mm — FDM floor for any load-bearing wall (design wall 3)
MIN_BOSS_WALL = 1.0     # mm — material around a heat-set insert bore
MIN_PIVOT_PROUD = 2.0   # mm — pivot boss must stand proud of the cup wall
OPEN_MIN = 0.30         # grille open-area band (acoustic + structural) ...
OPEN_MAX = 0.50         # ... around the 0.40 target; outside = out of range


class Report:
    def __init__(self):
        self.fails = 0
        self.warns = 0

    def hard(self, ok, name, detail):
        if ok:
            print(f"  [PASS] {name}: {detail}")
        else:
            self.fails += 1
            print(f"  [FAIL] {name}: {detail}")

    def soft(self, ok, name, detail):
        if ok:
            print(f"  [PASS] {name}: {detail}")
        else:
            self.warns += 1
            print(f"  [warn] {name}: {detail}")


def _single_solid(wp):
    """(solid_count, is_valid) for a built part."""
    val = wp.val()
    return len(val.Solids()), bool(val.isValid())


def _grille_open_fraction(cup_wp, n=400):
    """Measured open-area fraction over the grille zone (geometry, not params)."""
    body = max(cup_wp.val().Solids(), key=lambda s: s.Volume())
    cls = BRepClass3d_SolidClassifier(body.wrapped)

    def inside(x, y, z):
        cls.Perform(gp_Pnt(x, y, z), 1e-7)
        return cls.State() in (TopAbs_IN, TopAbs_ON)

    zone_r = P.grille_outer_ring_radius + P.grille_member_width / 2
    zmid = P.wall_thickness / 2
    step = 2 * zone_r / n
    mat = tot = 0
    for ix in range(n):
        x = -zone_r + (ix + 0.5) * step
        for iy in range(n):
            y = -zone_r + (iy + 0.5) * step
            if math.hypot(x, y) > zone_r:
                continue
            tot += 1
            if inside(x, y, zmid):
                mat += 1
    return 1 - mat / tot


def main():
    print("Daily Driver — printability gate\n")
    print("Building printed parts in-process (part [warn]s below are the")
    print("deferred-cosmetic SOFT warnings; they do not fail the gate)…\n")

    cup = make_cup()
    baffle = make_baffle()
    yoke = make_yoke()
    slider = make_slider()
    parts = {"cup": cup, "baffle": baffle, "yoke": yoke, "slider": slider}

    r = Report()

    print("\n— HARD checks (a failure exits non-zero) —")

    # 1. Manifold: every printed part is exactly one valid, connected solid.
    for name, wp in parts.items():
        n_solids, valid = _single_solid(wp)
        r.hard(n_solids == 1 and valid, f"manifold:{name}",
               f"{n_solids} solid(s), valid={valid} (want 1, True)")

    # 2. Wall thickness >= FDM floor.
    r.hard(P.wall_thickness >= MIN_WALL, "wall-thickness",
           f"wall {P.wall_thickness} mm >= {MIN_WALL} mm floor")

    # 3. Grille members >= printability floor.
    r.hard(P.grille_member_width >= P.grille_member_min_width, "grille-member-width",
           f"member {P.grille_member_width} mm >= {P.grille_member_min_width} mm floor")

    # 4. Grille open area within range (measured from geometry).
    of = _grille_open_fraction(cup)
    r.hard(OPEN_MIN <= of <= OPEN_MAX, "grille-open-area",
           f"open {of:.3f} in [{OPEN_MIN}, {OPEN_MAX}] (target {P.grille_target_open_fraction})")

    # 5. Pivot boss stands proud of the cup wall (boss + insert + arm room).
    proud = P.pivot_boss_outer_radius - P.cup_outer_diameter / 2
    r.hard(proud >= MIN_PIVOT_PROUD, "pivot-clearance",
           f"boss proud {proud:.1f} mm >= {MIN_PIVOT_PROUD} mm")

    # 6. Pivot boss spans deep enough to fully house the heat-set insert.
    r.hard(P.pivot_boss_through_span >= P.insert_boss_depth, "pivot-insert-depth",
           f"span {P.pivot_boss_through_span} mm >= insert {P.insert_boss_depth} mm")

    # 7. Baffle boss reaches the inner wall → blended, not free-standing.
    boss_reach = P.baffle_screw_radius + P.baffle_boss_diameter / 2
    inner_r = P.cup_interior_diameter / 2
    r.hard(boss_reach >= inner_r, "boss-wall-blend",
           f"boss reach {boss_reach:.1f} mm >= inner wall {inner_r:.1f} mm")

    # 8. Material around the insert bore in the baffle boss.
    boss_wall = (P.baffle_boss_diameter - P.m3_insert_hole_diameter) / 2
    r.hard(boss_wall >= MIN_BOSS_WALL, "boss-bore-wall",
           f"wall around insert {boss_wall:.1f} mm >= {MIN_BOSS_WALL} mm")

    print("\n— SOFT checks (warn, do not fail) —")

    # Guard setback vs. the front lamina (held + warned in baffle.py when tight).
    lamina = P.baffle_thickness - P.driver_recess_depth
    need = P.guard_thickness + P.guard_setback
    r.soft(lamina >= need, "guard-setback-lamina",
           f"front lamina {lamina:.1f} mm vs guard {P.guard_thickness}+setback "
           f"{P.guard_setback}={need:.1f} mm")

    print(f"\n{'='*60}")
    print(f"HARD failures: {r.fails}   SOFT warnings: {r.warns}")
    if r.fails:
        print("GATE: FAIL — unprintable part(s); fix before printing.")
        return 1
    print("GATE: PASS — all hard checks clear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
