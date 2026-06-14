# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Cup shell — the heart of the Daily Driver.

Build order follows the spec: model the acoustic void first, shell outward to
wall thickness, then add the baffle-mounting bosses, the rear vent array, and a
provisional yoke mount.

This is geometry v0.1 — functional-first. The form (outer profile, the exact
vent slot shape that becomes the signature look, yoke styling) is deliberately
plain here and is what gets refined in the build loop. Several dimensions are
flagged as open in params.py / DESIGN-LOG.md; respect those flags.
"""

import math

import cadquery as cq
from params import P
from parts import features


def make_cup() -> cq.Workplane:
    od = P.cup_outer_diameter
    total_h = P.cup_total_height

    # 1. Solid blank, front (+Z) up, closed back at the bottom.
    cup = cq.Workplane("XY").circle(od / 2).extrude(total_h)

    # 2. Shell out the front face → open cup, walls = wall_thickness, back closed.
    #    Interior void = cup_interior_diameter x cup_depth.
    cup = cup.faces(">Z").shell(-P.wall_thickness)

    # 3. Rear vent grille: a real concentric-ring grille cut through the closed
    #    back, replacing the old placeholder slot ring entirely. The REMAINING
    #    material is a center hub + grille_ring_count concentric rings +
    #    grille_spoke_count radial spokes; the gaps between them open to the
    #    driver. The outer ring's centerline lands on the baffle-boss radius
    #    (P.grille_outer_radius == P.baffle_screw_radius), so the 4 bosses sit as
    #    NODES on it — that resolves the old boss/vent collision (the screws now
    #    reinforce the grille) and is why we keep cutting BEFORE the bosses: the
    #    ring stays solid where each boss lands, so nothing slices a boss column.
    #
    #    Members are sized via P.grille_member_width to hit
    #    P.grille_target_open_fraction (~0.40), held to the
    #    P.grille_member_min_width FDM floor (see params.py / DESIGN-LOG).
    #
    #    Built as an annular CUTTER (zone disc minus the kept members), then
    #    cut from the cup. The outer ring's outer edge meets the solid rim, so
    #    the grille is continuous with the shell — one connected solid.
    w = P.grille_member_width
    r_out = P.grille_outer_radius
    hub_r = P.grille_hub_diameter / 2
    # Concentric ring centerlines: outer ring on the boss radius, inner ring(s)
    # between hub and outer. v1 ships two rings (inner + outer); if ring_count
    # grows, fill the remaining rings evenly between the inner and outer radii.
    if P.grille_ring_count <= 1:
        ring_radii = [r_out]
    elif P.grille_ring_count == 2:
        ring_radii = [P.grille_inner_ring_radius, r_out]
    else:
        r_lo = P.grille_inner_ring_radius
        n = P.grille_ring_count
        ring_radii = [
            r_lo + (r_out - r_lo) * k / (n - 1) for k in range(n)
        ]
    zone_r = r_out + w / 2  # outer edge of the outer ring = grille zone radius

    # Cut a hair beyond the back plate on both faces so the through-cut is clean.
    z0 = -1.0
    cut_h = P.wall_thickness + 2.0

    def _disc(radius, offset=z0, height=cut_h):
        return cq.Workplane("XY").workplane(offset=offset).circle(radius).extrude(height)

    # Full opening zone, then keep (subtract back) the grille members.
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

    grille_cutter = zone.cut(keep)
    cup = cup.cut(grille_cutter)

    # 4. Baffle-mounting bosses (convention — features.boss). Columns that stand
    #    on the interior back floor (part of the closed back wall), merged and
    #    filleted into it so they're structurally connected and printable. This
    #    fixes the earlier FLOATING-BOSS bug: the old bosses were short cylinders
    #    near the front rim at the screw radius, touching nothing, unioned as
    #    disconnected solids. Now they run floor → baffle underside. The brass
    #    heat-set insert is installed in the open (front-facing) top; the baffle
    #    screws into it from the front.
    #    The boss ring (baffle_screw_radius) and the grille's outer ring share a
    #    radius by construction (P.grille_outer_radius == P.baffle_screw_radius),
    #    so each boss lands on solid ring material as a NODE — the old boss/vent
    #    collision is resolved and the screws reinforce the grille. Boss screw
    #    direction itself is still an open question — see DESIGN-LOG.
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
        outer_diameter=P.insert_boss_diameter,
        bore_diameter=P.m3_insert_hole_diameter,
        height=P.baffle_boss_height,
        bore_depth=P.insert_boss_depth,
        base_fillet=P.boss_base_fillet,
    )

    # 5. Provisional yoke mount: a single boss on the +X side wall with a bore
    #    for the pivot interface. NOTE: cup-side yoke attachment is not fully
    #    specified in the spec — this is a placeholder to make the part whole
    #    and visible, NOT a resolved design. Flagged in DESIGN-LOG.md.
    yoke_boss = (
        cq.Workplane("XZ")
        .workplane(offset=-(od / 2))
        .center(0, total_h / 2)
        .circle(P.yoke_mount_boss_diameter / 2)
        .extrude(-P.insert_boss_depth)
    )
    cup = cup.union(yoke_boss)

    # 6. Soften exposed outer vertical edges for comfort/printability.
    #    Scope to the OUTER WALL only. The original "|Z" selection also grabbed
    #    the vent-slot and boss edges (never the intent — see the comment above),
    #    and a 1.5 mm fillet overruns that small geometry, so OCC aborts the whole
    #    operation. On the current cylindrical first-pass form the outer wall has
    #    essentially no sharp vertical edges to soften anyway (only the yoke-boss
    #    intersection, a curved-on-curved saddle OCC won't fillet), so this is
    #    typically a no-op until the real outer profile lands in the form pass
    #    (cup outer profile is an OPEN form decision — see docs/DESIGN-LOG.md).
    #    Whatever happens, warn rather than silently swallow: a skipped comfort
    #    fillet must be visible in the build, not hidden behind an [ok].
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
