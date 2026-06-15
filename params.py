# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Daily Driver — parametric values.

This is the single source of truth for every dimension in the model. Change a
value here and the affected parts follow. All values are in millimetres.

Reconciled to design-spec.md v0.3 (DT880-family: bow → slider → fork-yoke → cup
→ baffle → driver → pad).

>>> ESTIMATE POLICY <<<
We are NOT waiting on measured parts. Every value tagged `ESTIMATE` is a working
guess chosen so the geometry builds and the interfaces line up — it is here to be
OVERWRITTEN by a measured value later, cleanly, because nothing downstream hard-
codes it. `REF` marks a reference dimension of a bought part (driver, bow) used
only for fit/clearance. `TODO` flags a real uncertainty that needs a decision or
a measurement before it's trustworthy. Do not treat any ESTIMATE as confirmed.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # ---- Cup shell -----------------------------------------------------------
    cup_interior_diameter: float = 78.0   # ESTIMATE  cup_id — acoustic void dia
    cup_depth: float = 30.0               # ESTIMATE  interior depth (driver→back)
    wall_thickness: float = 3.0           # ESTIMATE  wall — 3 mm min shell
    wall_thickness_structural: float = 4.0  # ESTIMATE  at bosses / structural pts
    # cup_od = 84 is derived (cup_outer_diameter property = id + 2*wall).

    # ---- Rear vent grille (DECOUPLED from the baffle bosses, v0.3) -----------
    # Remaining material = center hub + concentric rings + radial spokes; the
    # gaps open to the driver. The outer ring is now its OWN radius (no longer
    # pinned to the boss circle) — bosses moved out to the perimeter wall.
    grille_hub_diameter: float = 16.0     # ESTIMATE  hub_dia — center disc
    grille_ring_count: int = 2            # ESTIMATE  ring_count
    grille_inner_ring_radius: float = 24.0  # ESTIMATE  inner_ring_r
    grille_outer_ring_radius: float = 32.0  # ESTIMATE  outer_ring_r (decoupled)
    grille_spoke_count: int = 8           # ESTIMATE  spoke_count
    # member_w: spec suggested 3.0, but with these ring radii (inner 24 / outer 32)
    # 3.0 yields ~0.51 open. Sized UP to 4.0 to hit grille_target_open_fraction
    # (0.40, measured 0.40) while staying well above the 2 mm floor. Per the
    # standing rule, member width is tuned to the open-area target, not fixed.
    grille_member_width: float = 4.0      # ESTIMATE  member_w (tuned to 0.40 open)
    grille_member_min_width: float = 2.0  # HARD FLOOR — FDM printability minimum
    grille_target_open_fraction: float = 0.40  # ESTIMATE  target_open (~40%)

    # ---- Baffle-mounting bosses in the cup (wall-blended) --------------------
    # Four heat-set bosses on the diagonals (45/135/225/315), blended into the
    # perimeter inner wall near the front — NOT free-standing posts. Bore faces
    # front; the baffle screws into them from the front.
    baffle_screw_count: int = 4           # ESTIMATE  count
    baffle_bolt_circle_diameter: float = 70.0  # ESTIMATE  bolt_circle_dia (bcd)
    baffle_boss_diameter: float = 10.0    # ESTIMATE  > insert dia so it reaches
                                          #   the inner wall (r=35 + 5 = 40 > 39)
                                          #   and merges → "blended into the wall"

    # ---- Yoke pivot bosses in the cup (external, side walls) -----------------
    # Two bosses at 0/180 on the cup's OUTER side wall, at mid-height, each with
    # an M3 heat-set bore (radial, outward-facing) for the fork shoulder-screw.
    pivot_boss_count: int = 2             # ESTIMATE  count (0/180)
    pivot_boss_diameter: float = 12.0     # ESTIMATE  external boss OD
    # TODO: yoke_pivot_centres (88) sits only ~2 mm proud of cup_od (84) per side,
    # so the boss spans THROUGH the wall (inside lug + outside seat) to fully
    # house a 6 mm insert. Revisit boss form once the real fork is in hand.
    pivot_boss_through_span: float = 9.0  # ESTIMATE  radial length across the wall

    # ---- Heat-set inserts / screws (M3) -------------------------------------
    m3_insert_hole_diameter: float = 4.0  # ESTIMATE  M3 brass insert bore
    m3_clearance_hole: float = 3.4        # M3 free-fit through-hole (standard)
    insert_boss_diameter: float = 7.0     # ESTIMATE  generic insert-boss OD
    insert_boss_depth: float = 6.0        # ESTIMATE  insert/bore depth

    # ---- Baffle plate (front-mount) -----------------------------------------
    baffle_outer_diameter: float = 77.0   # ESTIMATE  baffle_od (drops into id 78)
    baffle_thickness: float = 4.0         # ESTIMATE  baffle_th
    driver_aperture: float = 35.0         # ESTIMATE  acoustic opening (front-back)
    driver_recess_diameter: float = 42.0  # ESTIMATE  driver_recess_dia (on BACK)
    driver_recess_depth: float = 3.0      # ESTIMATE  driver_recess_depth (on BACK)
    pad_lip_outer_diameter: float = 62.0  # ESTIMATE  pad_lip_od — Brainwavz HM5
    pad_lip_height: float = 3.5           # ESTIMATE  pad_lip_h (raised, FRONT)
    pad_lip_wall: float = 2.0             # ESTIMATE  lip wall thickness
    baffle_counterbore_diameter: float = 6.0  # ESTIMATE  M3 socket head clearance
    baffle_counterbore_depth: float = 2.5     # ESTIMATE  head sinks below front
    baffle_vent_count: int = 6            # ESTIMATE  small controlled-vent holes
    baffle_vent_diameter: float = 2.0     # ESTIMATE  not a hard seal
    # baffle bolt circle reuses baffle_bolt_circle_diameter (aligned to the cup).
    # NOTE: cable entry is cup-side per v0.3 (dual entry) — NOT on the baffle.

    # ---- Integral driver guard (across the aperture, on the baffle) ----------
    guard_spoke_count: int = 6            # ESTIMATE  guard_spoke_count
    guard_member_width: float = 2.0       # ESTIMATE  guard_member_w
    guard_setback: float = 1.5            # ESTIMATE  recessed below front face so
                                          #   it clears the pad AND the diaphragm
    guard_thickness: float = 1.5          # ESTIMATE  guard rib thickness (Z)
    guard_hub_diameter: float = 6.0       # ESTIMATE  small center hub to tie spokes

    # ---- Driver (REFERENCE — candidate Peerless HPD-40N16) ------------------
    driver_od: float = 42.0               # REF  outer frame dia
    driver_diaphragm_diameter: float = 40.0  # REF  diaphragm — guard must clear
    driver_body_depth: float = 8.0        # REF  frame depth behind the baffle
    driver_dome_proud: float = 1.5        # REF  dome stands proud of the frame
    driver_cutout_tolerance: float = 0.3  # ESTIMATE  fit allowance on the recess

    # ---- Fork / yoke ---------------------------------------------------------
    yoke_pivot_centres: float = 88.0      # ESTIMATE  pivot_centres (hole-to-hole)
    yoke_arm_width: float = 8.0           # ESTIMATE  arm_w
    yoke_arm_thickness: float = 5.0       # ESTIMATE  arm_th
    yoke_fork_height: float = 55.0        # ESTIMATE  fork_height (pivot → hub)
    yoke_pivot_hole_diameter: float = 3.4  # ESTIMATE  pivot_hole (M3 clearance)
    yoke_pivot_eye_diameter: float = 11.0  # ESTIMATE  pad around each pivot hole
    yoke_swivel_hub_diameter: float = 14.0  # ESTIMATE  swivel_hub_dia
    yoke_swivel_bore: float = 6.0         # ESTIMATE  swivel_bore (vertical pin)
    yoke_swivel_hub_height: float = 12.0  # ESTIMATE  hub height (along the pin)
    pivot_tilt_degrees: float = 20.0      # ESTIMATE  tilt_range (±)

    # ---- Slider (rides the bow) ---------------------------------------------
    slider_block_width: float = 22.0      # ESTIMATE  block w (X)
    slider_block_height: float = 26.0     # ESTIMATE  block h (Z)
    slider_block_depth: float = 16.0      # ESTIMATE  block d (Y)
    slider_bow_channel_width: float = 17.0  # ESTIMATE  bow_channel_w (bow ≈16 + clr)
    slider_bow_channel_depth: float = 2.0   # ESTIMATE  bow_channel_d
    slider_swivel_bore: float = 6.0       # ESTIMATE  mates the fork swivel hub
    slider_grub_hole_diameter: float = 2.5  # ESTIMATE  M3 grub tap (friction)

    # ---- Bow (BOUGHT Beyer Metal Head Bow / DIY 1095 — INTERFACE ONLY) ------
    # Reference body for assembly + a DIY template. Dimensions are TBD from the
    # measured Beyer part; these are placeholders so the slider channel and end
    # interface have something to mate. NOT a printed part.
    bow_radius: float = 100.0             # ESTIMATE/REF  bow_radius (arc)
    bow_width: float = 16.0               # ESTIMATE/REF  bow_width
    bow_thickness: float = 0.8            # ESTIMATE/REF  bow_th
    bow_endtab_hole_diameter: float = 3.2  # ESTIMATE/REF  endtab_hole_dia
    bow_endtab_hole_spacing: float = 14.0  # ESTIMATE/REF  endtab_hole_spacing
    bow_endtab_width: float = 16.0        # ESTIMATE/REF  endtab_w
    bow_arc_degrees: float = 150.0        # ESTIMATE  modelled arc span (reference)

    # ---- Mechanical primitives (convention; see parts/features.py) ----------
    boss_base_fillet: float = 1.0         # fillet tying a boss to its host (print)
    screw_post_diameter: float = 7.0      # socket-head fastener post OD
    screw_post_pilot_diameter: float = 2.5  # thread-form pilot; confirm per screw

    # ---- Print / fit ---------------------------------------------------------
    fit_clearance_friction: float = 0.2   # friction fit
    fit_clearance_slip: float = 0.35      # slip fit
    edge_fillet: float = 1.5              # general comfort/print fillet

    # ---- Derived helpers -----------------------------------------------------
    @property
    def cup_outer_diameter(self) -> float:        # cup_od = 84
        return self.cup_interior_diameter + 2 * self.wall_thickness

    @property
    def cup_total_height(self) -> float:
        # interior depth plus one wall thickness for the closed (grille) back
        return self.cup_depth + self.wall_thickness

    @property
    def baffle_screw_radius(self) -> float:
        # bolt circle the cup bosses AND the baffle holes share (aligned)
        return self.baffle_bolt_circle_diameter / 2

    @property
    def cup_interior_floor_z(self) -> float:
        # top of the interior back floor (the closed back is one wall thick)
        return self.wall_thickness

    @property
    def baffle_seat_z(self) -> float:
        # baffle underside / boss-top height: baffle sits flush with the front rim
        return self.cup_total_height - self.baffle_thickness

    @property
    def baffle_boss_height(self) -> float:
        # boss columns run from the interior back floor up to the baffle underside
        return self.baffle_seat_z - self.cup_interior_floor_z

    @property
    def pivot_boss_z(self) -> float:
        # yoke pivot bosses sit at cup mid-height
        return self.cup_total_height / 2

    @property
    def pivot_boss_outer_radius(self) -> float:
        # external boss outer face seats the fork eye at pivot_centres/2
        return self.yoke_pivot_centres / 2


# Importable singleton used by every part module.
P = Params()
