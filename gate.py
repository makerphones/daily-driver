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
from parts.adapter_ring import make_adapter_ring
from parts.headband_pad import make_headband_pad
from parts.grille_dot import make_grille_dot
from parts.driver_clamp import make_driver_clamp
from parts.hardware import shoulder_screw_envelope, heatset_insert_envelope

# ---- Thresholds (named + transparent; not new checks, just the limits) -------
MIN_WALL = 2.0          # mm — FDM floor for any load-bearing wall (design wall 3)
MIN_BOSS_WALL = 1.0     # mm — material around a heat-set insert bore
MIN_PIVOT_PROUD = 2.0   # mm — pivot boss must stand proud of the cup wall
OPEN_MIN = 0.30         # grille open-area band (acoustic + structural) ...
OPEN_MAX = 0.50         # ... around the 0.40 target; outside = out of range
MIN_THREAD_ENGAGE = 0.95  # frac of screw thread that must sit inside the insert
MAX_TILT_EXTRA_FRAC = 0.20  # tilted cup∩yoke may exceed the 0° bearing overlap by ≤20%
# The yoke is LOAD-BEARING, so its load-path sections are held to the 4 mm
# STRUCTURAL floor (params.wall_thickness_structural), not the 2 mm wall floor —
# per the spec's "4 mm at structural points" and Openmod's v1→Mk2 thin-section fix.
MIN_YOKE_STRUCTURAL = P.wall_thickness_structural


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

    zone_r = P.grille_outer_ring_radius + P.grille_outer_ring_width / 2
    zmid = P.cup_back_thickness / 2
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


def _solid_volume(wp):
    """Volume of a boolean result, 0 if it's empty (no overlap)."""
    v = wp.val()
    return v.Volume() if v is not None and v.Solids() else 0.0


def _thread_engagement():
    """Fraction of the shoulder-screw THREAD that sits inside the insert envelope.

    Real geometry (parts/hardware.py): the screw datum z=0 is the shoulder↔thread
    boundary, thread runs to -thread_length; the insert is seated z∈[-len, 0]. Only
    the thread reaches z<=0, so screw∩insert == thread∩insert. ~1.0 = fully housed
    (good grip, no bottoming past the insert).
    """
    screw = shoulder_screw_envelope()
    insert = heatset_insert_envelope().translate((0, 0, -P.heatset_insert_length))
    thread_vol = math.pi * (P.shoulder_screw_thread_diameter / 2) ** 2 \
        * P.shoulder_screw_thread_length
    try:
        inter = _solid_volume(screw.intersect(insert))
    except Exception:  # noqa: BLE001 — degenerate boolean → treat as no engagement
        inter = 0.0
    return inter / thread_vol if thread_vol else 0.0


def _tilt_clearance(cup, yoke_origin):
    """cup∩yoke volume at 0° and ±tilt_range, rotating the cup about the pivot axis.

    The pivot axis is X through the cup mid-height (z=pivot_boss_z). Returns
    (base, plus, minus). A real arm/body collision shows up as a large jump over
    the 0° bearing overlap; the bearing itself is coaxial with the axis (invariant).
    """
    yoke = yoke_origin.translate((0, 0, P.pivot_boss_z))

    def vol(angle):
        c = cup.rotate((0, 0, P.pivot_boss_z), (1, 0, P.pivot_boss_z), angle)
        try:
            return _solid_volume(c.intersect(yoke))
        except Exception:  # noqa: BLE001
            return 0.0

    return vol(0.0), vol(P.pivot_tilt_degrees), vol(-P.pivot_tilt_degrees)


def main():
    print("Daily Driver — printability gate\n")
    print("Building printed parts in-process (part [warn]s below are the")
    print("deferred-cosmetic SOFT warnings; they do not fail the gate)…\n")

    cup = make_cup()
    baffle = make_baffle()
    yoke = make_yoke()
    slider = make_slider()
    adapter = make_adapter_ring()
    headband_pad = make_headband_pad()
    grille_dot = make_grille_dot()
    driver_clamp = make_driver_clamp()
    parts = {"cup": cup, "baffle": baffle, "yoke": yoke,
             "slider": slider, "driver_clamp": driver_clamp, "adapter_ring": adapter,
             "headband_pad": headband_pad, "grille_dot": grille_dot}

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

    # 2b. The cup's actual (pad-driven) wall must clear the floor too — it's the
    #     pad seat AND the pivot-boss housing, so it can't go below the min wall.
    r.hard(P.cup_wall_thickness >= MIN_WALL, "cup-wall",
           f"cup wall {P.cup_wall_thickness:.1f} mm (= (od−id)/2) >= {MIN_WALL} mm floor")

    # 3. Grille members >= printability floor (thinnest of the lattice bar + logo rings).
    grille_min_member = min(P.grille_outer_ring_width, P.grille_inner_ring_width,
                            P.grille_lattice_member_width)
    r.hard(grille_min_member >= P.grille_member_min_width, "grille-member-width",
           f"thinnest member {grille_min_member} mm >= {P.grille_member_min_width} mm floor")

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

    # --- Pivot HARDWARE FIT — validated against the real M3 shoulder screw +
    #     heat-set insert (parts/hardware.py), not a placeholder. ---

    # 6a. Shoulder must span the yoke eye + the tilt-friction WASHER STACK so the eye pivots on
    #     the SMOOTH shoulder (not the thread) and is captured but never clamped.
    washer_stack = 2 * P.pivot_nylon_washer_thickness + P.pivot_wave_washer_height
    r.hard(P.shoulder_screw_shoulder_length >= P.yoke_arm_thickness + washer_stack,
           "pivot-shoulder-spans-stack",
           f"shoulder {P.shoulder_screw_shoulder_length} mm >= eye {P.yoke_arm_thickness} + "
           f"washers {washer_stack:.1f} mm")

    # 6a-2. The eye BORE must CLEAR the shoulder OD or the eye can't ride it. This was the latent
    #       bug — a Ø3.4 (M3-clearance) bore on a Ø4.0 shoulder — that the gate previously missed.
    #       Pairs with the eye-web check below: the bore admits the shoulder AND the web survives it.
    r.hard(P.yoke_pivot_hole_diameter >= P.shoulder_screw_shoulder_diameter + 0.15,
           "pivot-bore-clears-shoulder",
           f"eye bore {P.yoke_pivot_hole_diameter} mm >= shoulder "
           f"{P.shoulder_screw_shoulder_diameter} + 0.15 mm clr")

    # 6b. Thread fully engages the insert and doesn't bottom out past it
    #     (geometric: thread solid ∩ insert envelope).
    engage = _thread_engagement()
    r.hard(engage >= MIN_THREAD_ENGAGE, "pivot-thread-engages-insert",
           f"thread inside insert {engage:.2f} >= {MIN_THREAD_ENGAGE} (no bottoming)")

    # 6c. Material around the INSTALLED insert OD (4.70, cq_warehouse-verified) in
    #     the pivot boss — the conservative case vs the undersized install bore.
    pivot_insert_wall = (P.pivot_boss_diameter - P.heatset_insert_diameter) / 2
    r.hard(pivot_insert_wall >= MIN_BOSS_WALL, "pivot-insert-wall",
           f"wall around insert {pivot_insert_wall:.2f} mm >= {MIN_BOSS_WALL} mm")

    # 6d. ±tilt clearance IN-CAD (was an open test-print TODO in yoke.py): rotate
    #     the cup through the full ±tilt_range about the pivot axis and confirm it
    #     doesn't bite into the yoke beyond the bearing overlap it has at 0°.
    base, plus, minus = _tilt_clearance(cup, yoke)
    worst = max(plus, minus)
    r.hard(worst <= base * (1 + MAX_TILT_EXTRA_FRAC), "pivot-tilt-clearance",
           f"cup∩yoke at ±{P.pivot_tilt_degrees:.0f}° = {worst:.0f} mm³ vs 0° "
           f"{base:.0f} mm³ (<= +{int(MAX_TILT_EXTRA_FRAC*100)}%)")


    # --- Yoke structural floor — load-bearing sections held to the 4 mm
    #     STRUCTURAL floor, not the 2 mm wall floor (Openmod's v1→Mk2 lesson:
    #     thin yoke sections snap). ---
    yoke_arm_min = min(P.yoke_arm_thickness, P.yoke_arm_width, P.yoke_arm_hub_width)
    r.hard(yoke_arm_min >= MIN_YOKE_STRUCTURAL, "yoke-arm-structural",
           f"arm thinnest(t,w,hub) {yoke_arm_min} mm >= {MIN_YOKE_STRUCTURAL} mm structural")

    eye_web = (P.yoke_pivot_eye_diameter - P.yoke_pivot_hole_diameter) / 2
    r.hard(eye_web >= MIN_YOKE_STRUCTURAL, "yoke-eye-web",
           f"eye bearing web {eye_web:.1f} mm >= {MIN_YOKE_STRUCTURAL} mm structural")

    r.hard(P.yoke_post_diameter >= MIN_YOKE_STRUCTURAL, "yoke-post-structural",
           f"adjustment post Ø{P.yoke_post_diameter} mm >= {MIN_YOKE_STRUCTURAL} mm structural")
    # (slider post-bore wall is now the collar-wall check in the slider section below)

    # --- Step-down adapter ring (accessory) — printable walls. ---
    adapter_wall = (P.adapter_host_diameter - P.adapter_target_driver_od) / 2
    r.hard(adapter_wall >= MIN_WALL, "adapter-ring-wall",
           f"ring wall {adapter_wall:.1f} mm >= {MIN_WALL} mm")
    adapter_seat = (P.adapter_target_driver_od - P.adapter_target_aperture) / 2
    r.hard(adapter_seat >= MIN_WALL, "adapter-seat-ledge",
           f"seat ledge {adapter_seat:.1f} mm >= {MIN_WALL} mm")

    # --- Bow (reference) + slider interface — measured Beyer band ------------
    # The relaxed and flexed bands must be the SAME physical strap: both arcs
    # derive from the one measured developed length, so this guards a future
    # hardcode. At rest the ends sit past the half-circle (observed); flexed it
    # opens out (larger R, smaller arc).
    r.hard(180.0 < P.bow_arc_degrees < 270.0, "bow-arc-at-rest",
           f"at-rest arc {P.bow_arc_degrees:.0f}° in (180, 270) — ends past the half-circle")
    r.hard(P.bow_worn_radius > P.bow_radius and P.bow_worn_arc_degrees < P.bow_arc_degrees,
           "bow-flex-opens",
           f"{P.bow_radius:.0f} mm/{P.bow_arc_degrees:.0f}° at rest → "
           f"{P.bow_worn_radius:.0f} mm/{P.bow_worn_arc_degrees:.0f}° worn (R up, arc down)")

    # The clamp collar carries the bow: the barrel must wall the post bore, the mount
    # tab hosts the two bolts at the bow's hole pitch, and those bolts must clear the
    # central post bore. (The round post in the bore is the swivel + height bearing.)
    bore_r = P.m3_insert_hole_diameter / 2
    post_bore_r = (P.yoke_post_diameter + P.slider_post_clearance) / 2
    mount_x = P.bow_endtab_hole_spacing / 2
    collar_wall = P.slider_collar_diameter / 2 - post_bore_r
    r.hard(collar_wall >= MIN_WALL, "slider-collar-wall",
           f"barrel wall (collar↔post bore) {collar_wall:.1f} mm >= {MIN_WALL} mm")
    r.hard(mount_x - bore_r >= post_bore_r, "slider-mount-clears-postbore",
           f"mount bore x{mount_x:.0f}−r{bore_r:.1f} clears central post bore r{post_bore_r:.1f}")
    r.hard(P.bow_endtab_hole_spacing + P.m3_insert_hole_diameter <= P.slider_clamp_width,
           "slider-mount-bores-in-clamp",
           f"pitch {P.bow_endtab_hole_spacing} + bore {P.m3_insert_hole_diameter} "
           f"<= clamp width {P.slider_clamp_width} mm")

    # 7. Baffle boss reaches the inner wall → blended, not free-standing.
    boss_reach = P.baffle_screw_radius + P.baffle_boss_diameter / 2
    inner_r = P.cup_interior_diameter / 2
    r.hard(boss_reach >= inner_r, "boss-wall-blend",
           f"boss reach {boss_reach:.1f} mm >= inner wall {inner_r:.1f} mm")

    # 8. Material around the insert bore in the baffle boss.
    boss_wall = (P.baffle_boss_diameter - P.m3_insert_hole_diameter) / 2
    r.hard(boss_wall >= MIN_BOSS_WALL, "boss-bore-wall",
           f"wall around insert {boss_wall:.1f} mm >= {MIN_BOSS_WALL} mm")

    # 9. Earpad retaining FLANGE at the cup's front outer edge — printable in both
    #    the radial (extension) and axial (thickness) directions.
    r.hard(P.pad_lip_extension >= MIN_WALL, "pad-flange-extension",
           f"flange sticks out {P.pad_lip_extension} mm >= {MIN_WALL} mm")
    r.hard(P.pad_lip_thickness >= MIN_WALL, "pad-flange-thickness",
           f"flange thickness {P.pad_lip_thickness} mm >= {MIN_WALL} mm")

    # Baffle bosses tall enough to house the heat-set insert (full-height column on
    # the back floor, buttressed at the base).
    r.hard(P.baffle_boss_height >= P.insert_boss_depth, "baffle-boss-houses-insert",
           f"boss height {P.baffle_boss_height} mm >= insert bore {P.insert_boss_depth} mm")

    # --- Driver clamp ring (3-bolt) — clears the vents + catches the flange ----
    clamp_bcr = P.driver_clamp_bolt_circle / 2
    vent_r = (P.driver_aperture / 2 + P.baffle_screw_radius) / 2   # == baffle.py's derivation
    r.hard(P.driver_aperture / 2 < clamp_bcr < P.baffle_screw_radius, "driver-clamp-bcd-band",
           f"clamp bcd r{clamp_bcr:.1f} between vents r{vent_r:.1f} and frame bcd r{P.baffle_screw_radius:.0f}")
    # The 3 clamp bosses (0/120/240) must clear the 6 vents (offset 30°) angularly,
    # since they share the baffle back at overlapping radii.
    clamp_half = math.degrees(math.asin(min(1.0, (P.insert_boss_diameter / 2) / clamp_bcr)))
    vent_half = math.degrees(math.asin(min(1.0, (P.baffle_vent_diameter / 2) / vent_r)))
    gap = 30.0 - (clamp_half + vent_half)
    r.hard(gap > 0, "driver-clamp-clears-vents",
           f"clamp boss↔vent gap {gap:.1f}° > 0 (bosses 0/120/240 vs vents offset 30°)")
    r.hard(P.driver_clamp_inner_diameter < P.driver_od, "driver-clamp-catches-flange",
           f"clamp inner Ø{P.driver_clamp_inner_diameter} < driver Ø{P.driver_od} (lip catches the flange)")

    print("\n— SOFT checks (warn, do not fail) —")

    # Guard setback vs. the front lamina (held + warned in baffle.py when tight).
    lamina = P.baffle_thickness - P.driver_recess_depth
    need = P.guard_thickness + P.guard_setback
    r.soft(lamina >= need, "guard-setback-lamina",
           f"front lamina {lamina:.1f} mm vs guard {P.guard_thickness}+setback "
           f"{P.guard_setback}={need:.1f} mm")

    # Driver dome DYNAMIC clearance: the grille must clear the dome's forward-most
    # (excursed) position, not just its rest height, or the diaphragm rubs at high
    # SPL. Both dome figures are ESTIMATES (MEASURE) → SOFT, not HARD, for now.
    dome_dynamic = P.driver_recess_depth + P.driver_dome_proud + P.driver_dome_excursion
    dome_need = dome_dynamic + P.guard_dome_clearance + 0.8   # + min printable guard rib
    r.soft(dome_need <= P.baffle_thickness, "guard-dome-excursion",
           f"excursed dome z{dome_dynamic:.1f} (seat+proud+excursion) + {P.guard_dome_clearance} clr "
           f"+ 0.8 rib = z{dome_need:.1f} ≤ baffle front z{P.baffle_thickness} (dome figures are estimates — MEASURE)")


    print(f"\n{'='*60}")
    print(f"HARD failures: {r.fails}   SOFT warnings: {r.warns}")
    if r.fails:
        print("GATE: FAIL — unprintable part(s); fix before printing.")
        return 1
    print("GATE: PASS — all hard checks clear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
