# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Baffle plate — front-mount driver-mount plate with an integral guard (v0.3).

Local frame: BACK face at z=0, FRONT face at z=baffle_thickness. The driver
mounts cup-side (recess on the BACK) and fires forward through the aperture; the
guard sits recessed below the front face. In assembly the whole part is lifted to
baffle_seat_z so its front is flush with the cup rim. Pad retention is a lip on
the CUP's outer rim now (DT770-style), NOT on the baffle — the baffle front is a
clean plate.

All dimensions are ESTIMATES flagged in params.py.
"""

import math

import cadquery as cq
from params import P


def make_baffle() -> cq.Workplane:
    r = P.baffle_outer_diameter / 2
    t = P.baffle_thickness
    ap_r = P.driver_aperture / 2

    # Aperture SHAPE hook — only round is authored today (see params + DESIGN-LOG).
    # Non-round (oval / planar-magnetic) is a future variant: fail loudly rather
    # than silently building a round hole when something else was asked for.
    if P.driver_aperture_shape != "round":
        raise NotImplementedError(
            f"driver_aperture_shape={P.driver_aperture_shape!r}: only 'round' is "
            "built today. Author the non-round aperture/recess/guard before enabling."
        )

    # 1. Round plate (z=0 back → z=t front).
    baffle = cq.Workplane("XY").circle(r).extrude(t)

    # 2. Acoustic aperture — through-hole.
    aperture = cq.Workplane("XY").workplane(offset=-0.5).circle(ap_r).extrude(t + 1.0)
    baffle = baffle.cut(aperture)

    # 3. Driver SEAT on the BACK: a shallow pocket (driver_recess_diameter) cut
    #    driver_recess_depth up from the back face. The driver frame rim registers
    #    into it and seats on the ledge at z=driver_recess_depth; the narrower
    #    aperture carries on to the front. Shallow (1 mm) on purpose — the dome then
    #    stays low, clear of the front guard; the COLLAR below adds lateral location.
    recess = (
        cq.Workplane("XY")
        .workplane(offset=-0.5)
        .circle(P.driver_recess_diameter / 2)
        .extrude(P.driver_recess_depth + 0.5)
    )
    baffle = baffle.cut(recess)

    # 3b. Driver locating COLLAR — a short wall around the driver on the BACK,
    #    continuing the seat wall proud of the back face (z = -collar_height .. 0).
    #    Secures the driver laterally; SHORTER than the driver's behind-baffle
    #    protrusion (body_depth − seat) so the clamp ring still reaches the rear rim
    #    and presses the driver forward to seal (room for a foam gasket, per maker).
    collar = (
        cq.Workplane("XY")
        .workplane(offset=-P.driver_collar_height)
        .circle(P.driver_recess_diameter / 2 + P.driver_collar_wall)
        .circle(P.driver_recess_diameter / 2)
        .extrude(P.driver_collar_height)
    )
    baffle = baffle.union(collar)

    # 4. Integral driver GUARD across the aperture — concentric RINGS tied by radial
    #    SPOKES (a classic driver grille: far stronger than bare spokes, still airy).
    #    It lives in the front lamina (z = recess_depth .. t) — the only solid aperture
    #    wall, since the back recess eats the inner plate below recess_depth.
    #    DOME CLEARANCE: the driver dome is a cone, tallest at the centre, peaking at
    #    z = recess_depth + dome_proud. The guard floor sits guard_dome_clearance ABOVE
    #    that peak so the diaphragm never touches the grille. The lamina is thin
    #    (t − recess_depth), so the rib is auto-thinned to fit under the front face and
    #    the build WARNS the true clearances rather than silently floating the guard.
    #    NB driver_dome_proud is still a REF estimate — measure it; if the real dome is
    #    near/over estimate the baffle needs more depth (the lamina can't be cheated).
    lamina = t - P.driver_recess_depth
    dome_tip = P.driver_recess_depth + P.driver_dome_proud      # cone peak (centre), baffle frame
    g_bot = dome_tip + P.guard_dome_clearance                   # guard floor just above the dome
    g_th = max(0.8, min(P.guard_thickness, t - g_bot - 0.2))    # fit under the front face; keep a printable rib
    g_top = g_bot + g_th
    dome_clear = g_bot - dome_tip
    pad_setback = t - g_top
    if pad_setback < P.guard_setback - 1e-6:
        print(
            f"  [warn] baffle: guard squeezed in the {lamina:.1f} mm lamina — dome "
            f"clearance {dome_clear:.2f} mm, pad setback {pad_setback:.2f} mm (wanted "
            f"{P.guard_setback:.1f}). dome_proud is a REF estimate ({P.driver_dome_proud}); "
            f"measure it and deepen the baffle if the real dome is near/over estimate."
        )
    w = P.guard_member_width
    hub_r = P.guard_hub_diameter / 2
    # Spokes/rings embed 1 mm past the aperture wall so they FUSE into the plate
    # rather than meeting it on a coincident (non-merging) face.
    spoke_len = 2 * (ap_r + 1.0)
    guard = cq.Workplane("XY").workplane(offset=g_bot).circle(hub_r).extrude(g_th)  # central hub
    for k in range(P.guard_ring_count):                         # concentric rings
        rk = hub_r + (ap_r - hub_r) * (k + 1) / (P.guard_ring_count + 1)
        ring = (
            cq.Workplane("XY").workplane(offset=g_bot)
            .circle(rk + w / 2).circle(rk - w / 2).extrude(g_th)
        )
        guard = guard.union(ring)
    for i in range(P.guard_spoke_count):                        # radial spokes
        ang = i * 360.0 / P.guard_spoke_count
        spoke = (
            cq.Workplane("XY").workplane(offset=g_bot)
            .transformed(rotate=(0, 0, ang)).rect(spoke_len, w).extrude(g_th)
        )
        guard = guard.union(spoke)
    baffle = baffle.union(guard)

    # 5. Four M3 clearance holes on the bolt circle (diagonals), counterbored
    #    from the FRONT (heads sink below the front face, hidden under the pad).
    bcr = P.baffle_screw_radius
    for i in range(P.baffle_screw_count):
        a = math.radians(45 + i * 360 / P.baffle_screw_count)
        cx, cy = bcr * math.cos(a), bcr * math.sin(a)
        through = (
            cq.Workplane("XY").workplane(offset=-0.5)
            .center(cx, cy).circle(P.m3_clearance_hole / 2).extrude(t + 1.0)
        )
        cbore = (
            cq.Workplane("XY").workplane(offset=t - P.baffle_counterbore_depth)
            .center(cx, cy).circle(P.baffle_counterbore_diameter / 2).extrude(P.baffle_counterbore_depth + 0.5)
        )
        baffle = baffle.cut(through).cut(cbore)

    # 6. Controlled venting — a few small holes through the plate (NOT a hard
    #    seal), in the flat ring between the aperture and the bolt circle (the pad
    #    lip lives on the cup now, not here). vent_r DERIVES (midway in that ring)
    #    so it tracks driver_od; flag if the growing aperture crowds the bolt circle.
    ring_outer_r = P.baffle_screw_radius
    vent_r = (ap_r + ring_outer_r) / 2
    if ap_r + P.baffle_vent_diameter / 2 >= ring_outer_r:
        print(f"  [warn] baffle: at driver_od={P.driver_od} the aperture crowds the "
              "bolt circle — revisit venting for this driver.")
    for i in range(P.baffle_vent_count):
        a = math.radians(i * 360 / P.baffle_vent_count + 30)
        vx, vy = vent_r * math.cos(a), vent_r * math.sin(a)
        vent = (
            cq.Workplane("XY").workplane(offset=-0.5)
            .center(vx, vy).circle(P.baffle_vent_diameter / 2).extrude(t + 1.0)
        )
        baffle = baffle.cut(vent)

    # 7. Driver-clamp STANDOFFS — 3 bosses on the BACK face (z=0) at the clamp bolt
    #    circle that reach BACK to meet the clamp ring at the driver's rear depth, each
    #    with an M3 heat-set bore. At r30 (between the vents and the mount holes) at
    #    0/120/240, interleaving with the 6 vents (offset 30°) so they don't collide.
    #    Standoff ≈ driver_body_depth − driver_recess_depth (the driver depth behind
    #    the baffle back, where the clamp ring's shoulder bears on the frame rim).
    cbr = P.driver_clamp_bolt_circle / 2
    boss_h = P.driver_clamp_standoff
    for i in range(P.driver_clamp_count):
        a = math.radians(i * 360.0 / P.driver_clamp_count)   # 0 / 120 / 240
        cx, cy = cbr * math.cos(a), cbr * math.sin(a)
        boss = (cq.Workplane("XY").workplane(offset=-boss_h).center(cx, cy)
                .circle(P.insert_boss_diameter / 2).extrude(boss_h))   # on the BACK (−z)
        baffle = baffle.union(boss)
        bore = (cq.Workplane("XY").workplane(offset=-boss_h - 0.5).center(cx, cy)
                .circle(P.m3_insert_hole_diameter / 2).extrude(P.insert_boss_depth + 0.5))
        baffle = baffle.cut(bore)

    return baffle


if __name__ == "__main__":
    cq.exporters.export(make_baffle(), "output/baffle.stl")
    print("wrote output/baffle.stl")
