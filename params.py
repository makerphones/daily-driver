# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Daily Driver — parametric values.

This is the single source of truth for every dimension in the model. Change a
value here and the affected parts follow. All values are in millimetres.

Transcribed from daily-driver-design-spec.md (v0.2). Where the spec gives a
range or flags an open question, the comment says so — do not silently resolve
those; they're tuned in the build loop and confirmed against real hardware.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # ---- Cup shell -----------------------------------------------------------
    cup_interior_diameter: float = 78.0   # acoustic void diameter (parametric)
    cup_depth: float = 30.0               # interior depth (driver-to-back)
    wall_thickness: float = 3.0           # 3 mm min shell
    wall_thickness_structural: float = 4.0  # at baffle flange / yoke boss

    # ---- Driver (parametric — CONFIRM against your actual driver with calipers)
    driver_od: float = 42.0               # outer frame dia; 38-42 mm class
    driver_aperture: float = 35.0         # acoustic opening; driver sits on ledge
    driver_depth: float = 10.0            # sets min interior depth
    driver_cutout_tolerance: float = 0.3  # actual cut ~= aperture + this

    # ---- Baffle plate --------------------------------------------------------
    baffle_thickness: float = 4.0
    gasket_channel_width: float = 2.0
    gasket_channel_depth: float = 1.5
    baffle_screw_count: int = 4           # M3
    baffle_screw_radius_fraction: float = 0.70  # of interior radius
    cable_hole_diameter: float = 6.5      # 6-7 mm, near one edge

    # ---- Pad interface -------------------------------------------------------
    # NOTE: pad_lip_od (62) sits well inside cup_interior_diameter (78). The
    # spec lists both but does not fully resolve where the lip lives (cup front
    # ring vs. baffle). Treated as an OPEN INTERFACE — see docs/DESIGN-LOG.md.
    # Confirm HM5 inner-ring dia with calipers before finalizing.
    pad_lip_od: float = 62.0              # Brainwavz HM5 target (61-62 mm)
    pad_lip_height: float = 4.0           # how far the lip stands proud
    pad_lip_wall: float = 2.0

    # ---- Heat-set inserts (M3) ----------------------------------------------
    m3_insert_hole_diameter: float = 4.0  # typical M3 brass insert bore
    m3_clearance_hole: float = 3.4        # M3 free-fit through-hole
    insert_boss_diameter: float = 7.0
    insert_boss_depth: float = 6.0

    # ---- Rear vent array -----------------------------------------------------
    vent_slot_count: int = 7              # 6-8 oval slots
    vent_open_fraction: float = 0.40      # ~40% open area target
    vent_ring_radius_fraction: float = 0.62  # slot centre, fraction of back radius

    # ---- Yoke / pivot --------------------------------------------------------
    pivot_post_diameter: float = 6.0      # project's own interface (not Beyer)
    pivot_post_height: float = 8.0
    pivot_tilt_degrees: float = 20.0      # +/- range
    # Cup-side yoke mount is NOT fully specified in the spec yet — provisional.
    yoke_mount_boss_diameter: float = 9.0

    # ---- Print / fit ---------------------------------------------------------
    fit_clearance_friction: float = 0.2   # friction fit
    fit_clearance_slip: float = 0.35      # slip fit
    edge_fillet: float = 1.5              # general comfort/print fillet

    # ---- Derived helpers -----------------------------------------------------
    @property
    def cup_outer_diameter(self) -> float:
        return self.cup_interior_diameter + 2 * self.wall_thickness

    @property
    def cup_total_height(self) -> float:
        # interior depth plus one wall thickness for the closed (vented) back
        return self.cup_depth + self.wall_thickness

    @property
    def baffle_diameter(self) -> float:
        # spans the front opening to reach the mounting bosses
        return self.cup_interior_diameter

    @property
    def driver_cutout_diameter(self) -> float:
        return self.driver_aperture + self.driver_cutout_tolerance

    @property
    def baffle_screw_radius(self) -> float:
        return (self.cup_interior_diameter / 2) * self.baffle_screw_radius_fraction


# Importable singleton used by every part module.
P = Params()
