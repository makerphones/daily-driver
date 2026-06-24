# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Headband pad — ROUGH DRAFT (crown cushion under the bow).

A soft comfort pad (foam, or printed TPU) that hugs the concave underside of the
bow at the crown, where the headband rests on the head. This is a first pass: an
arc band on the bow's inner radius, wider than the steel band for comfort. Its
form, retention (how it clips/slots to the bow), and material are all TBD — the
point here is to put a credible cushion in the assembly so it reads as a real
headphone. Every dimension is an ESTIMATE (params.py).

Built from an extruded annular sector (same approach as the bow — this OCC build's
`revolve` is unusable). Apex at the top (+Z) in the XZ plane, width along Y, so it
takes the bow's assembly transform directly.
"""

import math

import cadquery as cq
from params import P


def make_headband_pad() -> cq.Workplane:
    ro = P.bow_radius - P.bow_thickness / 2          # hug the bow's inner (concave) face
    ri = ro - P.headband_pad_thickness
    half = P.headband_pad_arc_degrees / 2
    a0, am, a1 = 90 - half, 90, 90 + half

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
        .extrude(P.headband_pad_width / 2, both=True)
    )


if __name__ == "__main__":
    cq.exporters.export(make_headband_pad(), "output/headband_pad.stl")
    print("wrote output/headband_pad.stl")
