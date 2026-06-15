# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Baffle plate — front-mount, with an integral pad lip and driver guard (v0.3).

Local frame: BACK face at z=0, FRONT face at z=baffle_thickness. The driver
mounts cup-side (recess on the BACK) and fires forward through the aperture; the
pad pushes over the raised lip on the FRONT; the guard sits recessed below the
front face. In assembly the whole part is lifted to baffle_seat_z so its front is
flush with the cup rim.

All dimensions are ESTIMATES flagged in params.py.
"""

import math

import cadquery as cq
from params import P


def make_baffle() -> cq.Workplane:
    r = P.baffle_outer_diameter / 2
    t = P.baffle_thickness
    ap_r = P.driver_aperture / 2

    # 1. Round plate (z=0 back → z=t front).
    baffle = cq.Workplane("XY").circle(r).extrude(t)

    # 2. Acoustic aperture — through-hole.
    aperture = cq.Workplane("XY").workplane(offset=-0.5).circle(ap_r).extrude(t + 1.0)
    baffle = baffle.cut(aperture)

    # 3. Driver recess on the BACK: a wider pocket (driver_recess_diameter) cut
    #    driver_recess_depth up from the back face. The driver frame drops into
    #    it from behind and seats on the ledge at z=driver_recess_depth; the
    #    narrower aperture carries on to the front.
    recess = (
        cq.Workplane("XY")
        .workplane(offset=-0.5)
        .circle(P.driver_recess_diameter / 2)
        .extrude(P.driver_recess_depth + 0.5)
    )
    baffle = baffle.cut(recess)

    # 4. Raised integral pad lip on the FRONT — an annulus the HM5 pad pushes
    #    over. od = pad_lip_outer_diameter, wall = pad_lip_wall, height above the
    #    front face = pad_lip_height.
    lip_or = P.pad_lip_outer_diameter / 2
    lip_ir = lip_or - P.pad_lip_wall
    lip = (
        cq.Workplane("XY")
        .workplane(offset=t)
        .circle(lip_or)
        .circle(lip_ir)
        .extrude(P.pad_lip_height)
    )
    baffle = baffle.union(lip)

    # 5. Integral driver guard across the aperture — guard_spoke_count thin
    #    spokes + a small hub, RECESSED guard_setback below the front face so it
    #    clears the pad on the front. Spoke ends meet the aperture wall, so the
    #    guard ties into the plate.
    #    TODO (fit, measured driver): the REF dome stands ~dome_proud (1.5) proud
    #    and driver_recess_depth (3) puts the frame front near z=3, so a proud
    #    dome can reach the guard plane (z≈2.5). Verify guard-to-diaphragm
    #    clearance against the real driver; may need a deeper recess or a
    #    peripheral-only guard. NOT resolved here.
    # The only solid aperture wall is the front lamina (z = recess_depth .. t),
    # because the driver recess eats the inner plate below recess_depth. So the
    # guard must live in that lamina to be supported. baffle_thickness=6 with
    # recess_depth=3 leaves a 3 mm lamina, enough to hold guard_thickness (1.5)
    # AND the requested guard_setback (1.5). The clamp below stays parametric: if
    # a measured driver forces a deeper recess and the lamina shrinks, the setback
    # is held to what fits and the build WARNS rather than floating the guard.
    lamina = t - P.driver_recess_depth
    g_th = min(P.guard_thickness, lamina)
    setback = min(P.guard_setback, lamina - g_th)
    if setback < P.guard_setback - 1e-6:
        print(
            f"  [warn] baffle: guard setback held to {setback:.2f} mm (asked "
            f"{P.guard_setback:.2f}); front lamina is only {lamina:.2f} mm "
            f"(recess {P.driver_recess_depth}/{t}). Flagged for the measured driver."
        )
    g_top = t - setback
    g_bot = g_top - g_th
    # Spokes run slightly past the aperture wall (embed 1 mm) so they FUSE into
    # the plate rather than meeting it on a coincident (non-merging) face.
    spoke_len = 2 * (ap_r + 1.0)
    guard = (
        cq.Workplane("XY").workplane(offset=g_bot).circle(P.guard_hub_diameter / 2).extrude(P.guard_thickness)
    )
    for i in range(P.guard_spoke_count):
        ang = i * 360.0 / P.guard_spoke_count
        spoke = (
            cq.Workplane("XY")
            .workplane(offset=g_bot)
            .transformed(rotate=(0, 0, ang))
            .rect(spoke_len, P.guard_member_width)
            .extrude(P.guard_thickness)
        )
        guard = guard.union(spoke)
    baffle = baffle.union(guard)

    # 6. Four M3 clearance holes on the bolt circle (diagonals), counterbored
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

    # 7. Controlled venting — a few small holes through the plate (NOT a hard
    #    seal). Placed in the flat ring just outside the aperture.
    vent_r = ap_r + 5.5  # ESTIMATE: between aperture and pad-lip inner wall
    for i in range(P.baffle_vent_count):
        a = math.radians(i * 360 / P.baffle_vent_count + 30)
        vx, vy = vent_r * math.cos(a), vent_r * math.sin(a)
        vent = (
            cq.Workplane("XY").workplane(offset=-0.5)
            .center(vx, vy).circle(P.baffle_vent_diameter / 2).extrude(t + 1.0)
        )
        baffle = baffle.cut(vent)

    return baffle


if __name__ == "__main__":
    cq.exporters.export(make_baffle(), "output/baffle.stl")
    print("wrote output/baffle.stl")
