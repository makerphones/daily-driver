# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Slider — rides the bow, carries the fork (v0.3 engineering pass).

A clamp block with a vertical channel that rides the bow (height adjust), a
vertical swivel bore at the bottom that mates the fork's swivel hub (the swivel
joint), and an M3 grub-screw boss on the back that presses a friction pad onto
the bow to set the height.

Frame: block centred on the origin. The bow channel is on the -Y face (head
side); the grub boss on the +Y face (back). All dimensions ESTIMATES (params.py).
"""

import cadquery as cq
from params import P


def make_slider() -> cq.Workplane:
    w = P.slider_block_width      # X — wide enough to wall the 33 mm bow channel
    d = P.slider_block_depth      # Y
    h = P.slider_block_height     # Z

    slider = cq.Workplane("XY").box(w, d, h)

    # Vertical bow channel on the -Y face: bow runs vertically (Z) for height
    # adjust. Width = slider_bow_channel_width (X), depth = channel_depth (Y).
    ch_w = P.slider_bow_channel_width
    ch_d = P.slider_bow_channel_depth
    channel = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(0, -d / 2 + ch_d / 2)          # sit against the -Y face
        .box(ch_w, ch_d + 0.2, h + 2, centered=(True, True, True))
    )
    slider = slider.cut(channel)

    # Swivel bore at the bottom (axis Z) — takes the fork swivel-hub pin.
    swivel = (
        cq.Workplane("XY")
        .workplane(offset=-h / 2 - 1)
        .circle(P.slider_swivel_bore / 2)
        .extrude(h * 0.75)                      # up from the bottom, not through
    )
    slider = slider.cut(swivel)

    # M3 grub-screw boss on the +Y face, set high enough to clear the swivel bore
    # below. The grub threads in and presses a friction pad onto the bow. Built
    # with explicit Y-axis cylinders (named-plane normals are easy to get wrong).
    grub_z = h / 2 - 6.0                         # ESTIMATE: upper third, clears swivel
    boss_len = 4.0
    boss = cq.Solid.makeCylinder(
        3.5, boss_len, cq.Vector(0, d / 2, grub_z), cq.Vector(0, 1, 0)
    )
    slider = slider.union(cq.Workplane(obj=boss))
    grub_len = d / 2 + boss_len + ch_d + 0.5     # through boss + block into channel
    grub = cq.Solid.makeCylinder(
        P.slider_grub_hole_diameter / 2, grub_len,
        cq.Vector(0, d / 2 + boss_len, grub_z), cq.Vector(0, -1, 0)
    )
    slider = slider.cut(cq.Workplane(obj=grub))

    return slider


if __name__ == "__main__":
    cq.exporters.export(make_slider(), "output/slider.stl")
    print("wrote output/slider.stl")
