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
from parts.cup import make_cup, pivot_stop_pins
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.adapter_ring import make_adapter_ring
from parts.headband_pad import make_headband_pad
from parts.grille_dot import make_grille_dot
from parts.hardware import shoulder_screw_envelope, heatset_insert_envelope

# ---- Thresholds (named + transparent; not new checks, just the limits) -------
MIN_WALL = 2.0          # mm — FDM floor for any load-bearing wall (design wall 3)
MIN_BOSS_WALL = 1.0     # mm — material around a heat-set insert bore
MIN_PIVOT_PROUD = 2.0   # mm — pivot boss must stand proud of the cup wall
OPEN_MIN = 0.30         # grille open-area band (acoustic + structural) ...
OPEN_MAX = 0.50         # ... around the 0.40 target; outside = out of range
MIN_THREAD_ENGAGE = 0.95  # frac of screw thread that must sit inside the insert
MAX_TILT_EXTRA_FRAC = 0.20  # tilted cup∩yoke may exceed the 0° bearing overlap by ≤20%
STOP_OVER_ANGLE = 35.0  # deg — the over-rotation stop MUST block the cup by here
STOP_EPS = 0.05         # mm³ — pin∩yoke above this = stop engaged (vs free in slot)
STOP_REST_CLOCK = 90.0  # deg — cup↔yoke relative clock at the worn rest (pad ⟂ arch);
                        # the pin (cup −Y) lands at the slot (yoke −Z) here. Tilt is ± this.
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


def _stop_engagement(yoke_origin):
    """Probe the over-rotation hard stop: (working_vol, over_vol, first_blocked_deg).

    Tests at the WORN rest clocking: the assembly mounts the cup 90° clocked vs the
    yoke (pad ⟂ arch), so the pin (cup −Y) lands at the slot (yoke −Z) at rest. We
    apply that STOP_REST_CLOCK base rotation, then sweep the tilt around it. ~0 =
    pin riding free in the slot; a jump = a slot end (the hard stop) engaged.
    Isolated to the pins, so the eye/boss bearing overlap doesn't pollute it.
    """
    pins = pivot_stop_pins()
    yoke = yoke_origin.translate((0, 0, P.pivot_boss_z))
    zc = P.pivot_boss_z

    def vol(tilt):  # tilt is measured from the worn rest; base clock aligns pin↔slot
        p = pins.rotate((0, 0, zc), (1, 0, zc), STOP_REST_CLOCK + tilt)
        try:
            return _solid_volume(p.intersect(yoke))
        except Exception:  # noqa: BLE001
            return 0.0

    working = max(vol(P.pivot_tilt_degrees), vol(-P.pivot_tilt_degrees))
    over = min(vol(STOP_OVER_ANGLE), vol(-STOP_OVER_ANGLE))
    first_blocked = next((a for a in range(int(P.pivot_tilt_degrees), 91)
                          if vol(a) > STOP_EPS), None)
    return working, over, first_blocked


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
    parts = {"cup": cup, "baffle": baffle, "yoke": yoke, "slider": slider,
             "adapter_ring": adapter, "headband_pad": headband_pad,
             "grille_dot": grille_dot}

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

    # 3. Grille members >= printability floor (thinnest of ring/ring/spoke).
    grille_min_member = min(P.grille_outer_ring_width, P.grille_inner_ring_width,
                            P.grille_spoke_width)
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

    # 6a. Shoulder must span the yoke eye so the eye pivots on the SMOOTH shoulder,
    #     not the thread.
    r.hard(P.shoulder_screw_shoulder_length >= P.yoke_arm_thickness,
           "pivot-shoulder-spans-eye",
           f"shoulder {P.shoulder_screw_shoulder_length} mm >= eye {P.yoke_arm_thickness} mm")

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

    # 6e. Over-rotation HARD STOP: the working ±tilt range must ride free, and the
    #     stop must engage before STOP_OVER_ANGLE so the cup can't be forced over
    #     and shear the M3 shoulder screw. (Re-derived from Open-Omega's limiter.)
    working, over, first_blocked = _stop_engagement(yoke)
    r.hard(working < STOP_EPS and over > STOP_EPS, "pivot-overrotation-stop",
           f"free through ±{P.pivot_tilt_degrees:.0f}° ({working:.2f} mm³), "
           f"blocked by ±{STOP_OVER_ANGLE:.0f}° ({over:.2f} mm³); "
           f"engages ≈ ±{first_blocked}°")

    # --- Yoke structural floor — load-bearing sections held to the 4 mm
    #     STRUCTURAL floor, not the 2 mm wall floor (Openmod's v1→Mk2 lesson:
    #     thin yoke sections snap). ---
    yoke_arm_min = min(P.yoke_arm_thickness, P.yoke_arm_width, P.yoke_arm_hub_width)
    r.hard(yoke_arm_min >= MIN_YOKE_STRUCTURAL, "yoke-arm-structural",
           f"arm thinnest(t,w,hub) {yoke_arm_min} mm >= {MIN_YOKE_STRUCTURAL} mm structural")

    eye_web = (P.yoke_pivot_eye_diameter - P.yoke_pivot_hole_diameter) / 2
    r.hard(eye_web >= MIN_YOKE_STRUCTURAL, "yoke-eye-web",
           f"eye bearing web {eye_web:.1f} mm >= {MIN_YOKE_STRUCTURAL} mm structural")

    hub_wall = (P.yoke_swivel_hub_diameter - P.yoke_swivel_bore) / 2
    r.hard(hub_wall >= MIN_YOKE_STRUCTURAL, "yoke-hub-wall",
           f"swivel-hub wall {hub_wall:.1f} mm >= {MIN_YOKE_STRUCTURAL} mm structural")

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

    # The slider rides the measured 33 mm band: its channel must clear the strap
    # width and the block must wall the channel. (The bow's end mounting holes
    # raise a ride-vs-bolt-on mechanism question — flagged in DESIGN-LOG.)
    r.hard(P.slider_bow_channel_width >= P.bow_width + 0.5, "slider-channel-fits-bow",
           f"channel {P.slider_bow_channel_width} mm >= bow {P.bow_width} + 0.5 clr")
    r.hard(P.slider_block_width >= P.slider_bow_channel_width + 2 * MIN_WALL,
           "slider-channel-walls",
           f"block {P.slider_block_width} mm >= channel {P.slider_bow_channel_width} "
           f"+ 2×{MIN_WALL} wall")

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

    # The Task-1 over-rotation stop slot notches the eye; the web between the slot
    # and the pivot bore is below the 2 mm print floor. It's a non-load-path
    # clearance notch at the unloaded eye bottom, but thin/fragile — FLAGGED, not
    # silently accepted: a slot in a ⌀12 eye can't keep a ≥2 mm bore web (would
    # need a much larger eye or relocating the stop off the eye). Open decision;
    # confirm on a test print.
    slot_web = (P.pivot_stop_radius - (P.pivot_stop_pin_diameter / 2 + P.pivot_stop_slot_clearance)
                - P.yoke_pivot_hole_diameter / 2)
    r.soft(slot_web >= MIN_WALL, "yoke-stop-slot-web",
           f"stop-slot↔bore web {slot_web:.1f} mm vs {MIN_WALL} mm print floor "
           f"(non-load-path notch; FLAGGED for test print / relief)")

    print(f"\n{'='*60}")
    print(f"HARD failures: {r.fails}   SOFT warnings: {r.warns}")
    if r.fails:
        print("GATE: FAIL — unprintable part(s); fix before printing.")
        return 1
    print("GATE: PASS — all hard checks clear.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
