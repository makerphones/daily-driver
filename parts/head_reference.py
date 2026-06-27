# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Reference HEAD — a translucent, deliberately non-real ovoid for worn-fit context. VIZ ONLY.

Not a printed part and not part of the build. It exists so the 3D parts viewer can show the
headphone on an abstract average head (toggleable, OFF by default, and held OUT of the explode
motion by the viewer). Sized to an average adult head: ear-to-ear ~147 mm, length ~194 mm,
ear→crown ~120 mm. The ellipsoid is a non-uniformly scaled sphere (revolve is dead on this OCC
build, so `transformGeometry` with a scaling matrix builds the ovoid). The assembly positions it
so the ears land at the cups and the crown sits up under the band.
"""

import cadquery as cq
from params import P


def make_head_reference(ear_half: float = None) -> cq.Workplane:
    """A translucent reference-head ovoid. `ear_half` = ear-to-ear HALF breadth; the
    MEDIUM ovoid (head_ref_*) is scaled UNIFORMLY by ear_half / medium so S/M/L share a
    shape and only differ in size (a bigger head is wider AND taller-crowned). Defaults
    to the medium head."""
    eh = P.head_ref_ear_half if ear_half is None else ear_half
    s = eh / P.head_ref_ear_half                         # uniform scale vs the medium ovoid
    sphere = cq.Solid.makeSphere(1.0, angleDegrees1=-90, angleDegrees2=90, angleDegrees3=360)
    scale = cq.Matrix([[eh, 0, 0, 0],
                       [0, P.head_ref_depth_half * s, 0, 0],
                       [0, 0, P.head_ref_height_half * s, 0]])
    return cq.Workplane(obj=sphere.transformGeometry(scale))


if __name__ == "__main__":
    cq.exporters.export(make_head_reference(), "output/head_reference.step")
    print("wrote output/head_reference.step")
