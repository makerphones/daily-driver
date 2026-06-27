# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Yoke adjustment ROD — the bought Ø6 metal shaft the slider rides on. REFERENCE body (not printed).

This replaced the old printed integral post. It's a Ø6 mm 304-stainless GROUND SHAFT (TGP):
centreless-ground for a smooth, straight, durable bearing surface that the printed/Delrin slider
barrel SLIDES and SWIVELS on (the plastic is the sacrificial wear surface). Bonded (epoxy) into a
blind socket in the fork-yoke; the exposed length rises as the height-adjust post. The top end is
faced + tapped M3 for a small screw-on TOP-STOP knob (so the cup can't slide out when the lock is
loose). Buy ~70 mm and trim the SOCKET (bonded) end to length, leaving the tapped end clean.

Total length = socket engagement + exposed post (params). Built along +Z from z=0 (socket floor).
"""

import cadquery as cq
from params import P


def make_yoke_rod() -> cq.Workplane:
    length = P.yoke_rod_socket_depth + P.yoke_post_length
    rod = cq.Workplane("XY").circle(P.yoke_post_diameter / 2).extrude(length)
    # Tapped M3 lead-hole in the top face for the screw-on top-stop knob (viz of the bought feature).
    try:
        rod = rod.faces(">Z").workplane().hole(P.m3_clearance_hole, 6.0)
    except Exception:  # noqa: BLE001 — cosmetic; never fail the reference body
        pass
    return rod


if __name__ == "__main__":
    cq.exporters.export(make_yoke_rod(), "output/yoke_rod.step")
    print("wrote output/yoke_rod.step")
