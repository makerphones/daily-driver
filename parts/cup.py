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

    # 3. Rear vent array: ring of slots cut through the closed back. Cut BEFORE
    #    the bosses so the cutThruAll never slices the boss columns. Slot
    #    length/width are sized toward the open-fraction target; exact open area
    #    and slot shape are an iteration point (the signature look) — NOT touched
    #    here (deferred to the grille taste pass).
    back_r = od / 2
    vent_r = back_r * P.vent_ring_radius_fraction
    # crude size: distribute target open area across the slot count
    target_area = 3.1416 * (vent_r ** 2) * P.vent_open_fraction
    slot_area_each = target_area / P.vent_slot_count
    slot_w = 5.0  # slot width (fixed, tune in loop)
    slot_len = max(slot_w * 1.5, slot_area_each / slot_w)  # length to hit area
    cup = (
        cup.faces("<Z")
        .workplane()
        .polarArray(vent_r, 0, 360, P.vent_slot_count)
        .slot2D(slot_len, slot_w, 90)  # radial-ish orientation
        .cutThruAll()
    )

    # 4. Baffle-mounting bosses (convention — features.boss). Columns that stand
    #    on the interior back floor (part of the closed back wall), merged and
    #    filleted into it so they're structurally connected and printable. This
    #    fixes the earlier FLOATING-BOSS bug: the old bosses were short cylinders
    #    near the front rim at the screw radius, touching nothing, unioned as
    #    disconnected solids. Now they run floor → baffle underside. The brass
    #    heat-set insert is installed in the open (front-facing) top; the baffle
    #    screws into it from the front.
    #    NOTE: the boss ring (baffle_screw_radius ~70% R) nearly coincides with
    #    the placeholder vent ring (~62% R), so a boss base can overlap a vent
    #    slot. Flagged for the grille taste pass (pattern the real grille around
    #    the four boss footprints). Boss screw direction itself is still an open
    #    question — see DESIGN-LOG.
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
