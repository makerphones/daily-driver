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

import cadquery as cq
from params import P


def make_cup() -> cq.Workplane:
    od = P.cup_outer_diameter
    total_h = P.cup_total_height

    # 1. Solid blank, front (+Z) up, closed back at the bottom.
    cup = cq.Workplane("XY").circle(od / 2).extrude(total_h)

    # 2. Shell out the front face → open cup, walls = wall_thickness, back closed.
    #    Interior void = cup_interior_diameter x cup_depth.
    cup = cup.faces(">Z").shell(-P.wall_thickness)

    # 3. Baffle-mounting bosses: 4 posts standing up from the interior back,
    #    reaching toward the front, drilled for M3 heat-set inserts. The baffle
    #    plate screws down into these (screw direction is an open decision — see
    #    DESIGN-LOG.md; this assumes inserts in the cup).
    boss_h = P.insert_boss_depth
    boss = (
        cq.Workplane("XY")
        .workplane(offset=total_h - boss_h)  # start near the front rim
        .polarArray(P.baffle_screw_radius, 45, 360, P.baffle_screw_count)
        .circle(P.insert_boss_diameter / 2)
        .extrude(boss_h)
    )
    # bore the insert holes from the front face downward
    boss = (
        boss.faces(">Z")
        .workplane()
        .polarArray(P.baffle_screw_radius, 45, 360, P.baffle_screw_count)
        .hole(P.m3_insert_hole_diameter, P.insert_boss_depth - 1.0)
    )
    cup = cup.union(boss)

    # 4. Rear vent array: ring of slots cut through the closed back.
    #    Slot length/width are sized toward the open-fraction target; exact
    #    open area and slot shape are an iteration point (the signature look).
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
    try:
        cup = cup.edges("|Z").fillet(P.edge_fillet)
    except Exception:
        # filleting can fail on tricky edge sets; skip rather than break the build
        pass

    return cup


if __name__ == "__main__":
    cq.exporters.export(make_cup(), "output/cup.stl")
    print("wrote output/cup.stl")
