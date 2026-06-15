# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Head bow — REFERENCE BODY ONLY (v0.3 engineering pass).

This is NOT a printed part. The real bow is the BOUGHT Beyerdynamic Metal Head
Bow (or a DIY 1095 spring-steel blank to the same geometry). This module models a
reference body so the assembly reads correctly and the slider channel + end
interface have something to mate. It exports to STEP only (build.py excludes it
from the printed-parts STL set).

Every dimension is an ESTIMATE/REF (params.py) — TBD from the measured Beyer part.

Built from EXTRUDED annular sectors (this OCP build's `revolve` is unusable):
an arc band curving over the top (+Z) in the XZ plane, width along Y. A central
relief slot and two end-tab hole pairs are modelled as interface markers (their
exact form is TBD from the real part — see flags below).
"""

import math

import cadquery as cq
from params import P


def _arc_band(ri, ro, deg_half, y_width):
    """Annular sector (ri..ro) centred on +Z (90°), ±deg_half, extruded ±Y."""
    a0, a1, am = 90 - deg_half, 90 + deg_half, 90

    def p(r, a):
        a = math.radians(a)
        return (r * math.cos(a), r * math.sin(a))

    Ao, Mo, Bo = p(ro, a0), p(ro, am), p(ro, a1)
    Bi, Mi, Ai = p(ri, a1), p(ri, am), p(ri, a0)
    return (
        cq.Workplane("XZ")
        .moveTo(*Ao).threePointArc(Mo, Bo)
        .lineTo(*Bi).threePointArc(Mi, Ai)
        .close()
        .extrude(y_width / 2, both=True)
    )


def make_bow() -> cq.Workplane:
    R = P.bow_radius
    th = P.bow_thickness
    half_arc = P.bow_arc_degrees / 2

    # 1. Band: thin arc (thickness th, radial) × width (along Y), over the top.
    band = _arc_band(R - th / 2, R + th / 2, half_arc, P.bow_width)

    # 2. Central relief slot — narrow (Y) full-depth cut over the central arc,
    #    leaving two rails + solid end tabs. ESTIMATE form.
    slot = _arc_band(R - th, R + th, half_arc - 30.0, 2.0)
    band = band.cut(slot)

    # 3. End-tab holes — 2 per end, drilled radially through the band thickness.
    #    TODO: spacing/orientation is an ESTIMATE (endtab_hole_spacing across the
    #    width); confirm the real Beyer end interface before relying on it.
    s = P.bow_endtab_hole_spacing / 2
    hole_r = P.bow_endtab_hole_diameter / 2
    for end_sign in (+1, -1):
        phi = math.radians(90 + end_sign * (half_arc - 6.0))   # just inside each end
        radial = cq.Vector(math.cos(phi), 0, math.sin(phi))
        for y in (+s, -s):
            base = cq.Vector(R * math.cos(phi), y, R * math.sin(phi)) - radial * 2
            drill = cq.Solid.makeCylinder(hole_r, 4.0, base, radial)
            band = band.cut(cq.Workplane(obj=drill))

    return band


if __name__ == "__main__":
    cq.exporters.export(make_bow(), "output/bow.step")
    print("wrote output/bow.step  (REFERENCE BODY ONLY)")
