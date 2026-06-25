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
an arc band curving over the top (+Z) in the XZ plane, width along Y. Radius,
developed length, and width are MEASURED off the real Beyer band; the arc derives
from them (params helper). Two end-tab mounting holes per end model where the
slider mechanism fastens (their exact dia/pitch are TBD from the real part).
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


def make_bow(radius: float = None, arc_degrees: float = None) -> cq.Workplane:
    """Reference band. Defaults to the MEASURED at-rest geometry (params); the
    assembly passes the flexed (worn) radius/arc so the same strap can be posed
    opened-out on a head. Width + developed length are invariant under flex.
    """
    R = P.bow_radius if radius is None else radius
    th = P.bow_thickness
    arc = P.bow_arc_degrees if arc_degrees is None else arc_degrees
    half_arc = arc / 2

    # 1. Band: thin arc (thickness th, radial) × width (along Y), over the top.
    #    A clean strap — the real band's relief/cutout styling (cf. the maker's
    #    X-pattern band) is a separate pass and not modelled into the bought part.
    band = _arc_band(R - th / 2, R + th / 2, half_arc, P.bow_width)

    # 2. End-tab MOUNTING HOLES — where the slider mechanism fastens. Two per end,
    #    marching INBOARD from each tip along the band, centred across the width
    #    (matches the measured Beyer end tab). Drilled radially through the band
    #    thickness. Hole dia + along-band pitch are ESTIMATE; the count (2/end) +
    #    along-band layout are inferred from the real part / the maker's reference
    #    band — confirm all of it with a caliper read.
    hole_r = P.bow_endtab_hole_diameter / 2
    margin = math.degrees(6.0 / R)                       # first hole, in from the tip
    pitch = math.degrees(P.bow_endtab_hole_spacing / R)  # along-band hole pitch
    for end_sign in (+1, -1):
        a_tip = 90 + end_sign * half_arc                 # the band tip
        for k in (0, 1):                                 # both holes land on the band
            phi = math.radians(a_tip - end_sign * (margin + k * pitch))
            radial = cq.Vector(math.cos(phi), 0, math.sin(phi))
            base = cq.Vector(R * math.cos(phi), 0, R * math.sin(phi)) - radial * 2
            drill = cq.Solid.makeCylinder(hole_r, 4.0, base, radial)
            band = band.cut(cq.Workplane(obj=drill))

    return band


if __name__ == "__main__":
    cq.exporters.export(make_bow(), "output/bow.step")
    print("wrote output/bow.step  (REFERENCE BODY ONLY)")
