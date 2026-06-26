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
a measurement before it's trustworthy. `MEASURED` is a confirmed caliper reading.
`SET` marks a dimension the maker has fixed by DESIGN DECISION — a target to build
to (e.g. the overall cup size), distinct from a guess (ESTIMATE) or a measured part
(MEASURED). Do not treat any ESTIMATE as confirmed.
"""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    # ---- Cup shell -----------------------------------------------------------
    cup_interior_diameter: float = 78.0   # ESTIMATE  cup_id — acoustic void dia (ear cavity)
    cup_depth: float = 30.0               # ESTIMATE  interior depth (driver→back)
    wall_thickness: float = 3.0           # ESTIMATE  min shell wall (floor). NB the cup's
                                          #   own wall is thicker now — see cup_outer_diameter.
    wall_thickness_structural: float = 4.0  # ESTIMATE  at bosses / structural pts
    # OVERALL OD is now the maker-set MASTER dimension: the cup measures 4 in
    # (101.6 mm) across the very outside, INCLUDING the retaining lip (maker decision
    # 2026-06-25). cup_outer_diameter below is the CUP-BODY OD — the dia the pad skirt
    # grips, behind the lip — and BACK-SOLVES from that target:
    #   cup_outer_diameter = 101.6 − 2·pad_lip_extension(5.08) = 91.44.
    # The earpad mounts OVER this rim and hooks behind the lip. TARGET PAD: Dekoni
    # Universal 100 mm (Beyer-type) — outer foam ⌀100, ear opening ⌀60; OPEN: confirm
    # the pad's cup-mount opening actually grips ~91.4 when measured (was ESTIMATE 90).
    # The wall falls out as (od−id)/2 = (91.44−78)/2 = 6.72 mm: a roomy pad seat that
    # also fully houses the pivot bosses.
    cup_outer_diameter: float = 91.44     # SET  cup-body OD = 4 in overall − 2× lip (back-solved)
    # ---- Form pass: chamfered back (direction "A", 2026-06-24) ----------------
    # The closed (grille) back is thickened past the side wall so a 45° outer
    # bevel reads without thinning the 3 mm side wall (the bevel lives entirely in
    # this back band). The acoustic air space behind the baffle is unchanged — only
    # the grille substrate gets deeper and the cup ~3 mm taller. See DESIGN-LOG.
    cup_back_thickness: float = 6.0       # ESTIMATE  closed-back depth (grille substrate)
    cup_back_round: float = 5.5           # soft-form ROUNDOVER radius on the back-outer edge
                                          #   (was a 45° chamfer; a fillet is a softer transition)

    # ---- Rear vent grille (DECOUPLED from the baffle bosses, v0.3) -----------
    # Remaining material = center hub + concentric rings + radial spokes; the
    # gaps open to the driver. The outer ring is now its OWN radius (no longer
    # pinned to the boss circle) — bosses moved out to the perimeter wall.
    # LOGO rings + dot echo the makerphones mark (src DriverMark.astro): a center DOT
    # + two concentric rings, the OUTER ring ~2× the inner's weight. Radii/widths from
    # the logo's 64-grid proportions (outer r24/stroke5, inner r13.5/stroke2.5, dot
    # r4.2) scaled into the grille zone. As of Stage 1b these ride FLUSH on top of a
    # structural triangular lattice (below) — they are decoration, not structure.
    grille_hub_diameter: float = 10.0     # ESTIMATE  the center DOT (logo dome dot)
    grille_ring_count: int = 2            # ESTIMATE  two concentric LOGO rings (the mark)
    grille_inner_ring_radius: float = 17.0  # ESTIMATE  inner ring (logo 13.5/24 of outer)
    grille_outer_ring_radius: float = 30.0  # ESTIMATE  outer ring (rim left for the chamfered back)
    grille_outer_ring_width: float = 6.0  # ESTIMATE  outer ring weight (the heavier ring)
    grille_inner_ring_width: float = 3.0  # ESTIMATE  inner ring weight (~½ outer, per the mark)
    grille_member_min_width: float = 2.0  # HARD FLOOR — FDM printability minimum
    grille_target_open_fraction: float = 0.40  # ESTIMATE  target_open (~40%)
    # Structural LATTICE (Stage 1b) — the grille is now a rigid TRIANGULAR ×3 mesh:
    # three opposing bar layers at 0/60/120° that carry the protection + stiffness,
    # with the logo rings + dot (above) riding FLUSH on top (single colour, co-planar,
    # same material). This INVERTS the old logo-as-structure grille (which read as
    # fragile yet bulky at once): the mesh is the structure; the logo is decoration,
    # so it can be bold without being load-bearing and prints self-supporting (built
    # face-down). Member 2.2 / pitch 11.5 are the settings the maker dialed in on the
    # interactive pattern explorer ("landed behind the logo nicely").
    grille_lattice_member_width: float = 2.2  # SET  triangular lattice bar width (explorer)
    # Explorer value was 11.5, but against the real BOLD logo (the rings alone cover
    # ~45% of the zone) that gave only 0.274 open — below the 0.30 floor. Opened to 16
    # → ~0.385 gate-measured (near the 0.40 target), keeping the bold logo. Denser mesh
    # later is possible by thinning the logo rings to free up open area (maker's call).
    grille_lattice_pitch: float = 16.0        # SET  bar pitch (tuned to the open-area floor)
    grille_lattice_angles: tuple = (0.0, 60.0, 120.0)  # 3 opposing layers (triangular)
    grille_open_min: float = 0.30         # gate band lower bound (see gate.py OPEN_MIN)
    # Orange ACCENT dot — a press-in cap at the grille center (the mark's only
    # accent, printed in the warm orange). Seats on the grille hub, stands proud
    # on the outboard face.
    grille_dot_diameter: float = 9.0      # ESTIMATE  accent dot (<= hub dia, seats on it)
    grille_dot_proud: float = 1.5         # ESTIMATE  stands proud of the grille face

    # ---- Baffle-mounting bosses in the cup (wall-blended) --------------------
    # Four heat-set bosses on the diagonals (45/135/225/315), blended into the
    # perimeter inner wall near the front — NOT free-standing posts. Bore faces
    # front; the baffle screws into them from the front.
    baffle_screw_count: int = 3           # SET  3 (was 4) — lighter, 3 is a stable
                                          #   plane + matches the 3-fold driver clamp.
                                          #   (The baffle's 6 OTHER holes are VENTS.)
    baffle_bolt_circle_diameter: float = 70.0  # ESTIMATE  bolt_circle_dia (bcd)
    baffle_boss_diameter: float = 12.0    # SET  10 → 12: deeper wall embedment (reach
                                          #   r41 > inner wall r39) + a thicker bore wall.
                                          #   Stays < the female-thread crest (~41.7).
    # Boss BUTTRESS — a base flare merging the boss into the cup wall so it can't snap
    # off at the thin wall lens (maker flagged the bare columns as fragile). Built as a
    # wider base step then bored, so it adds real support material at the junction.
    baffle_boss_flare_diameter: float = 15.0  # SET  base flare OD (reach r42.5 < thread valley)
    baffle_boss_flare_height: float = 3.0     # SET  flare height at the base

    # ---- Yoke pivot bosses in the cup (external, side walls) -----------------
    # Two bosses at 0/180 on the cup's OUTER side wall, at mid-height, each with
    # an M3 heat-set bore (radial, outward-facing) for the fork shoulder-screw.
    pivot_boss_count: int = 2             # ESTIMATE  count (0/180)
    pivot_boss_diameter: float = 12.0     # ESTIMATE  external boss OD
    # yoke_pivot_centres=98 puts the boss outer face ~4 mm proud of cup_od (90)
    # per side — room for the boss + insert + fork-arm seat. The boss spans the
    # 6 mm wall + 4 mm proud (9 mm total); with the thicker wall its inner end now
    # stops IN the wall (no lug into the cavity) while still housing the insert.
    pivot_boss_through_span: float = 9.0  # ESTIMATE  radial length across the wall

    # ---- Modular split: permanent FRONT FRAME + removable REAR MODULE --------
    # Architecture "D / forward split, NO ribs" (maker decision 2026-06-25, after a
    # 5-lens adversarial eval). The cup is built WHOLE as a reference shell
    # (cup.make_cup) and SPLIT at parting_z into two PRINTED parts:
    #   • make_frame  — front: baffle seat, pad lip, the YOKE PIVOTS (forward, on the
    #                   frame), and the joint socket. The permanent structural frame;
    #                   the hinge load path lives here, intact.
    #   • make_module — rear: the cavity + grille; swaps for damping / open↔sealed.
    # GEOMETRY CONSTRAINT (why the split is mid, not behind the baffle): with no ribs
    # the Ø12 pivot boss must sit on the frame, and pivot(12) + lap + baffle-boss(6)
    # must fit between parting_z and the 36 mm rim → parting_z + lap ≤ 24. So the
    # most-forward no-rib parting is ~18 (a clean MID split ≈ architecture B). A truly
    # forward parting (module owns most of the cavity) needs the hybrid-D ribs to move
    # the pivot off the frame — the documented upgrade path. See DESIGN-LOG 2026-06-25.
    # JOINT = a telescoping SHIPLAP: the frame's outer wall sleeves DOWN over the
    # module's inner spigot (continuous 91.44 OD, no external collar). The spigot top
    # bottoms on the frame wall (the seat). The coarse single-start THREAD + axial
    # O-ring GASKET are deferred to Stage 2/3 — Stage 1 is a simple slip register.
    parting_z: float = 18.0               # SET  split height z (mid; max-forward w/o ribs)
    joint_register_lap: float = 6.0       # ESTIMATE  lap / thread engagement length (axial)
    # joint_interface_radius is the THREAD MAJOR radius (crest) AND the plain-register
    # interface. Ø86 (r43), pitch 3 is the wall-budget sweet spot for the 6.7 mm wall:
    # male core (root−cavity) ≈ 2.4 mm and frame outer wall (body−female valley) ≈ 2.4
    # mm both clear the 2 mm floor, and the female crest (~41.7) clears the baffle
    # bosses (reach r40). (Ø84/pitch4 from the eval collapsed the male core to ~0.8 mm
    # in THIS shiplap; coarser-but-shallower pitch 3 at Ø86 fixes it — see DESIGN-LOG.)
    joint_interface_radius: float = 43.0  # SET  thread major radius (Ø86) = lap interface
    joint_register_clearance: float = 0.35  # SET  radial thread/slip clearance (FDM)
    # Stage 2: a single-start coarse thread on the lap faces (cq_warehouse IsoThread —
    # module = external/male, frame = internal/female). Import-guarded: if cq_warehouse
    # is absent or a thread won't build, the joint DEGRADES to the plain slip register
    # (still one valid solid). The gate's frame/module manifold checks are the go/no-go.
    joint_thread: bool = True             # SET  thread the lap (else plain slip register)
    joint_thread_pitch: float = 3.0       # SET  coarse single-start pitch (FDM-printable)
    # Stage 3: hard bottoming SHOULDER + axial O-ring SEAL. The seal SQUEEZE is set by
    # GEOMETRY, not thread torque: a local COLLAR bulges both parts at the joint band
    # (OD <= 101.6 lip) to make a seal face OUTBOARD of the thread; the O-ring GROOVE is
    # on the MODULE's up-facing flange (printed floor-up = the only FDM-airtight face),
    # and the frame collar bottoms plastic-to-plastic on the lands either side of it,
    # capping the squeeze. The spigot top is held ~joint_seat_clearance short of the
    # socket ceiling so the z=parting SHOULDER is the hard stop. The OPEN (lattice)
    # module just omits the O-ring; the SEALED module fits it. (Eval Stage 3.)
    joint_collar_diameter: float = 98.0   # SET  collar OD at the joint band (<= 101.6 lip)
    joint_oring_cross_section: float = 2.62  # SET  AS568 dash-2xx O-ring cord dia
    joint_seal_mean_diameter: float = 92.0  # SET  O-ring mean seal Ø (groove centre, outboard of thread)
    joint_groove_depth: float = 2.1       # SET  groove depth at bottomed (~20% squeeze)
    joint_groove_width: float = 3.3       # SET  groove width (<= 85% fill, no hydraulic lock)
    joint_seat_clearance: float = 0.3     # SET  spigot-top↔socket-ceiling gap so the shoulder bottoms

    # ---- Heat-set inserts / screws (M3) -------------------------------------
    m3_insert_hole_diameter: float = 4.0  # ESTIMATE  M3 brass insert bore
    m3_clearance_hole: float = 3.4        # M3 free-fit through-hole (standard)
    insert_boss_diameter: float = 7.0     # ESTIMATE  generic insert-boss OD
    insert_boss_depth: float = 6.0        # ESTIMATE  insert/bore depth

    # ---- Pivot hardware: M3 shoulder screw + heat-set insert ----------------
    # Real fastener geometry for the yoke↔cup pivot, so the gate validates fit
    # against actual parts (see parts/hardware.py + the pivot gate checks).
    # Insert dims are REF, VERIFIED against cq_warehouse 0.8.0 HeatSetNut
    # "M3-0.5-Standard" / "McMaster-Carr" (measured OD 4.70, length 5.70).
    # NOTE: m3_insert_hole_diameter (4.0) is the UNDERSIZED thermal-install bore for
    # this 4.70 OD insert — correct by design (the brass melts/knurls into it), not
    # a mismatch. Boss-wall checks use the 4.70 INSTALLED OD (conservative).
    heatset_insert_diameter: float = 4.70   # REF  M3 insert installed OD (verified)
    heatset_insert_length: float = 5.70     # REF  M3 insert length (verified)
    # cq_warehouse has NO ShoulderScrew class, so the screw is composed from
    # primitives; these are ESTIMATE / caliper-pending (measure the part you buy).
    shoulder_screw_thread_diameter: float = 3.0    # M3 thread major dia
    shoulder_screw_shoulder_diameter: float = 4.0  # ESTIMATE  smooth shoulder OD (≈4 on M3)
    shoulder_screw_shoulder_length: float = 8.0    # ESTIMATE  bearing length the eye rides
    shoulder_screw_thread_length: float = 5.0      # ESTIMATE  thread into insert (<= insert len)
    shoulder_screw_head_diameter: float = 6.5      # ESTIMATE  head OD
    shoulder_screw_head_height: float = 3.0        # ESTIMATE  head height

    # ---- Pivot over-rotation hard stop --------------------------------------
    # A pin on each cup pivot boss rides an arc slot in the mating yoke eye; the
    # slot ENDS are hard stops that bound cup tilt just past the ±20° working
    # range, so the cup can't be forced over and shear the M3 shoulder screw.
    # Primary purpose: protect the pivot/screw. Cable routing isn't designed yet,
    # so cable protection is a SECONDARY benefit once routing exists (flagged).
    # Re-derived from Open-Omega's separate "cup rotation limiter" (CERN-OHL-P) —
    # nothing copied. The effective engagement angle is MEASURED by the gate.
    # Stop lives at the BOTTOM of the eye (−Z), clear of the arm bar that joins at
    # the top (+Z). Slot radius is set so it clears both the pivot bore and the eye
    # rim (no fragmentation). Effective engagement ≈ halfangle − pin's angular half.
    pivot_stop_slot_halfangle: float = 22.0  # ESTIMATE  arc-slot half-span; engages ~28° (past ±20°)
    pivot_stop_radius: float = 3.6           # ESTIMATE  pin/slot radius from the pivot axis
    pivot_stop_pin_diameter: float = 1.6     # ESTIMATE  stop-pin dia (rides the slot)
    pivot_stop_slot_clearance: float = 0.4   # ESTIMATE  radial slip clearance, pin↔slot

    # ---- Baffle plate (front-mount) -----------------------------------------
    baffle_outer_diameter: float = 77.0   # ESTIMATE  baffle_od (drops into id 78)
    baffle_thickness: float = 6.0         # ESTIMATE  baffle_th — 6 (was 4) leaves a
                                          #   solid front lamina (th − recess_depth)
                                          #   for the driver guard to anchor in, so
                                          #   guard_setback fits. recess_depth and
                                          #   guard_setback stay driver-measured.
    # driver_aperture and driver_recess_diameter now DERIVE from driver_od (see the
    # derived helpers), so the baffle aperture/guard/vents stay coherent when the
    # driver size changes — "different baffle plates" is a regenerate, not a redesign.
    driver_recess_depth: float = 3.0      # ESTIMATE  driver_recess_depth (on BACK)
    # Earpad retaining FLANGE — a thin brim at the CUP's front OUTER edge that
    # extends the perimeter OUTWARD (DT770-style "extension of the circumference"),
    # so the earpad's skirt wraps over it and hooks behind. It sticks OUT radially,
    # NOT up toward the head, so the baffle stays flush (not recessed). Exact size is
    # TBD — measure the Dekoni pad's mounting skirt/groove.
    pad_lip_extension: float = 5.08       # SET  lip radial extension = 0.2 in (maker 2026-06-25);
                                          #   cup_outer_diameter + 2× this = the 4 in overall OD
    pad_lip_thickness: float = 2.0        # ESTIMATE  flange thickness (axial) — thin printed lip
    pad_lip_round: float = 0.8            # soft-form roundover on the brim edges (eases the pad + feel)
    baffle_counterbore_diameter: float = 6.0  # ESTIMATE  M3 socket head clearance
    baffle_counterbore_depth: float = 2.5     # ESTIMATE  head sinks below front
    baffle_vent_count: int = 6            # ESTIMATE  small controlled-vent holes
    baffle_vent_diameter: float = 2.0     # ESTIMATE  not a hard seal
    # baffle bolt circle reuses baffle_bolt_circle_diameter (aligned to the cup).
    # NOTE: cable entry is cup-side per v0.3 (dual entry) — NOT on the baffle.

    # ---- Driver clamp ring (3-bolt, holds the driver to the baffle) ----------
    # The maker's prototype: a 3-ear ring (like an exhaust flange) that presses the
    # driver into the baffle's back recess, bolted to 3 heat-set inserts in the
    # baffle BACK. Independent of the baffle→frame mount. The bolt circle sits at
    # r30 — BETWEEN the vents (~r26) and the frame-mount holes (r35) — and the 3 ears
    # (0/120/240) interleave with the 6 vents (offset 30°) so they don't collide.
    # A raised front LIP presses the driver's mounting flange. Light: a thin eared
    # ring, open centre. (Driver-fit dims are REF/driver-pending.)
    driver_clamp_count: int = 3              # SET  3-ear clamp (matches the prototype)
    driver_clamp_bolt_circle: float = 60.0   # SET  bcd (r30): between vents (r26) + frame holes (r35)
    driver_clamp_inner_diameter: float = 34.0  # SET  open centre (clears the driver magnet/dome)
    driver_clamp_ring_outer: float = 46.0    # SET  ring body OD (just past the driver od 42)
    driver_clamp_thickness: float = 3.0      # SET  ring/ear thickness (light)
    driver_clamp_ear_diameter: float = 9.0   # SET  ear pad dia around each M3 hole
    driver_clamp_lip_height: float = 2.0     # ESTIMATE  front lip standoff to the seated flange (driver-pending)

    # ---- Integral driver guard (across the aperture, on the baffle) ----------
    guard_spoke_count: int = 6            # ESTIMATE  guard_spoke_count
    guard_member_width: float = 2.0       # ESTIMATE  guard_member_w
    guard_setback: float = 1.5            # ESTIMATE  recessed below front face so
                                          #   it clears the pad AND the diaphragm
    guard_thickness: float = 1.5          # ESTIMATE  guard rib thickness (Z)
    guard_hub_diameter: float = 6.0       # ESTIMATE  small center hub to tie spokes

    # ---- Driver (REFERENCE — candidate Peerless HPD-40N16) ------------------
    driver_od: float = 42.0               # REF  outer frame dia. 40 mm class LOCKED
                                          #   (2026-06-25, not 50). 42 = generic 40 mm frame;
                                          #   confirm against the chosen driver's measured frame.
    driver_diaphragm_diameter: float = 40.0  # REF  diaphragm — guard must clear
    driver_body_depth: float = 8.0        # REF  frame depth behind the baffle
    driver_dome_proud: float = 1.5        # REF  dome stands proud of the frame
    driver_cutout_tolerance: float = 0.3  # ESTIMATE  fit allowance on the recess
    driver_seat_ledge: float = 3.5        # ESTIMATE  radial frame seat (per side);
                                          #   driver_aperture derives as od − 2·this
    # Aperture SHAPE hook: only "round" is authored today. "oval"/"planar" (e.g. a
    # planar-magnetic driver) is a FUTURE variant — baffle.py raises if not round.
    # See DESIGN-LOG. Kept here so the param surface is ready before the geometry is.
    driver_aperture_shape: str = "round"  # ESTIMATE  only "round" is built today

    # ---- Step-down adapter ring (accessory; "design big, adapt down") --------
    # A printed ring so a baffle built for a LARGER driver can host a smaller one
    # with NO reprint — a real driver-testing workflow. Worked example: a 50 mm-
    # class host hosting the 40 mm reference driver. INDEPENDENT of the reference
    # build (driver_od stays 42). All ESTIMATE. NOTE: a step-down ring changes the
    # front cavity / adds a step — NOT acoustically neutral; ring variants are
    # REW-loop items (see DESIGN-LOG), not a free swap.
    adapter_host_diameter: float = 50.0     # ESTIMATE  host baffle recess the ring drops into
    adapter_target_driver_od: float = 42.0  # ESTIMATE  smaller driver it adapts to (40 mm class)
    adapter_height: float = 6.0             # ESTIMATE  ring height (shims the driver-depth delta)
    adapter_seat_thickness: float = 2.0     # ESTIMATE  front seat floor the driver rests on

    # ---- Fork / yoke ---------------------------------------------------------
    yoke_pivot_centres: float = 98.0      # ESTIMATE  pivot_centres (hole-to-hole);
                                          #   98 (was 92) so the boss stays ~4 mm proud of
                                          #   the wider 90 mm cup. TODO: verify ±tilt on a print.
    yoke_arm_width: float = 9.0           # ESTIMATE  arm_w (at the eye / load end)
    yoke_arm_hub_width: float = 6.0       # ESTIMATE  arm_w at the hub end — gentle taper
                                          #   (slims toward the hub; >= structural floor)
    yoke_arm_thickness: float = 6.0       # ESTIMATE  arm_th (beefier for print strength)
    yoke_fork_height: float = 55.0        # ESTIMATE  fork_height (pivot → hub)
    yoke_pivot_hole_diameter: float = 3.4  # ESTIMATE  pivot_hole (M3 clearance)
    yoke_pivot_eye_diameter: float = 12.0  # ESTIMATE  pad around pivot hole (12 hosts the stop slot)
    pivot_tilt_degrees: float = 20.0      # ESTIMATE  tilt_range (±)

    # ---- Yoke↔slider vertical adjustment (Grado HP1000-style: post + thumbscrew) -
    # The yoke carries a round vertical POST that slides up/down in the slider block
    # for HEIGHT (head-size) adjustment, locked by a side THUMBSCREW pressing the post
    # — no detent, like Joe Grado's HP1/HP1000. The round post in a round bore also
    # lets the cup SWIVEL (fore-aft seal conform) when the screw is loose; tightening
    # locks both height + swivel by friction. (Replaces the old fixed swivel hub/bore;
    # Beyer's friction-clip in the block is the alternative, noted in the LOG.)
    yoke_post_diameter: float = 8.0       # SET  round adjustment post OD (slide + swivel)
    yoke_post_length: float = 34.0        # SET  post length above the arm junction (travel + grip)
    slider_post_clearance: float = 0.4    # SET  slide fit, post↔slider bore (FDM)
    slider_adjust_travel: float = 18.0    # ESTIMATE  vertical size-adjust range (reference)
    slider_thumbscrew_diameter: float = 4.0      # SET  M4 thumbscrew (bigger for hand grip)
    slider_thumbscrew_insert_hole: float = 5.6   # SET  M4 brass heat-set bore (the lock)
    slider_thumbscrew_boss: float = 9.0   # SET  boss OD on the +Y face hosting the insert

    # ---- Slider (BOLTS to the bow end tab) ----------------------------------
    # MECHANISM (decided): the band's end tab bolts to the slider's inside (-Y)
    # face with two M3 screws (the bow's 2 holes/end), not a friction clamp-ride.
    # The block + tab seat are sized for the measured 33 mm band (were 22/17 for a
    # 16 mm bow). The 2 mount bores sit above the swivel bore and straddle X.
    slider_block_width: float = 42.0      # ESTIMATE  block w (X) — hosts the 33 mm tab + bores
    slider_block_height: float = 26.0     # ESTIMATE  block h (Z) — the post slides through this
    slider_block_depth: float = 18.0      # SET  block d (Y) — 16→18 for the central post bore
                                          #   wall (post bore ↔ bow-tab seat) to clear the floor
    slider_tab_seat_width: float = 34.0   # ESTIMATE  tab-seat width (measured bow 33 + 1 clr)
    slider_tab_seat_depth: float = 2.0    # ESTIMATE  tab-seat depth (registers the tab)
    slider_mount_bore_z: float = 9.0      # ESTIMATE  height of the 2 tab-mount bores (off-centre, clears the central post bore)
    slider_block_fillet: float = 2.5      # soft-form roundover on the block edges (hand feel)

    # ---- Bow (BOUGHT Beyer Metal Head Bow / DIY 1095 — INTERFACE ONLY) ------
    # Reference body for assembly + a DIY template. NOT a printed part. The first
    # three are MEASURED off the real Beyerdynamic metal head bow (2026-06-25):
    # the relaxed band is a 5 in circle (→ R 63.5), it rolls out to 9.3 in
    # (→ 236.2 mm developed), strap width 1.3 in (→ 33 mm). The at-rest arc DERIVES
    # from R + developed length (helper below) and lands >180° — the ends sit past
    # the half-circle, exactly as observed. It's spring steel: at rest it's this
    # tight 5 in circle; on a head it flexes OPEN to bow_worn_radius (the assembly
    # poses it flexed, conserving developed length). Thickness + the end-hole specs
    # are still ESTIMATE/REF — no caliper reading yet.
    bow_radius: float = 63.5              # MEASURED  relaxed/at-rest arc radius (5 in dia)
    bow_developed_length: float = 236.2   # MEASURED  rolled-out band length (9.3 in)
    bow_width: float = 33.0               # MEASURED  strap width (1.3 in, top-down)
    bow_thickness: float = 0.8            # ESTIMATE/REF  bow_th (no caliper reading yet)
    bow_worn_radius: float = 78.0         # ESTIMATE  flexed-on-head radius; sets ear spacing
                                          #   (~156 mm cups). The band springs open from the
                                          #   63.5 at-rest; developed length is conserved.
    bow_endtab_hole_diameter: float = 3.2  # ESTIMATE/REF  end-tab mounting-hole dia (M3 clr)
    bow_endtab_hole_spacing: float = 14.0  # ESTIMATE/REF  along-band pitch of the 2 end holes
    bow_endtab_width: float = 33.0        # ESTIMATE/REF  end-tab width (= strap width)
    # X-truss cutout (the maker's reference band): two outer rails braced by
    # crossing diagonal struts over the central span; solid end tabs carry the holes.
    bow_endtab_length: float = 28.0       # ESTIMATE  solid end-tab arc length (holds the 2 holes)
    bow_rail_width: float = 4.0           # ESTIMATE  outer rail width (Y) flanking the truss
    bow_strut_width: float = 3.5          # ESTIMATE  X-brace diagonal strut width
    bow_truss_bays: int = 6               # ESTIMATE  number of X cells along the central span
    # bow_arc_degrees / bow_worn_arc_degrees are DERIVED (helpers below): both
    # conserve bow_developed_length, so the relaxed and flexed bands are one strap.

    # ---- Headband pad (ROUGH DRAFT — crown cushion under the bow) -------------
    # Soft comfort pad (foam / printed TPU) hugging the bow's concave underside at
    # the crown. First pass — a simple arc band; form/retention refined later. All
    # ESTIMATE. One shared pad at the crown (not per-ear).
    headband_pad_arc_degrees: float = 80.0   # ESTIMATE  contact arc at the crown
    headband_pad_thickness: float = 8.0      # ESTIMATE  cushion depth (radial)
    headband_pad_width: float = 40.0         # ESTIMATE  wider than the 33 mm bow, for comfort
    headband_pad_channel_depth: float = 3.0  # ESTIMATE  bow nests this deep; side rails grip it

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
    def driver_aperture(self) -> float:
        # front acoustic opening = frame od − a seat ledge each side; derives from
        # driver_od so the baffle regenerates coherently for any driver size.
        return self.driver_od - 2 * self.driver_seat_ledge

    @property
    def driver_recess_diameter(self) -> float:
        # back recess the driver frame drops into = od + fit tolerance.
        return self.driver_od + self.driver_cutout_tolerance

    @property
    def adapter_target_aperture(self) -> float:
        # the adapter's front opening, by the same seat-ledge rule as the baffle.
        return self.adapter_target_driver_od - 2 * self.driver_seat_ledge

    @property
    def cup_wall_thickness(self) -> float:
        # the cup's ACTUAL radial wall = (od − id)/2; thicker than wall_thickness
        # because the OD is pad-driven (gives the pad seat + houses the pivot bosses).
        return (self.cup_outer_diameter - self.cup_interior_diameter) / 2

    @property
    def cup_total_height(self) -> float:
        # interior depth plus the closed (grille) back band (thickened for the
        # chamfered-back form pass; the air space behind the baffle is unchanged)
        return self.cup_depth + self.cup_back_thickness

    @property
    def baffle_screw_radius(self) -> float:
        # bolt circle the cup bosses AND the baffle holes share (aligned)
        return self.baffle_bolt_circle_diameter / 2

    @property
    def cup_interior_floor_z(self) -> float:
        # top of the interior back floor (now the thickened back band)
        return self.cup_back_thickness

    @property
    def baffle_seat_z(self) -> float:
        # baffle underside / boss-top height: baffle sits flush with the front rim
        return self.cup_total_height - self.baffle_thickness

    @property
    def baffle_boss_floor_z(self) -> float:
        # baffle bosses are FRAME-only now: they floor at the top of the joint lap
        # band (parting_z + lap) so the lap socket never cuts them, and run up to the
        # baffle underside. (Was the interior back floor, which the split would sever.)
        return self.parting_z + self.joint_register_lap

    @property
    def baffle_boss_height(self) -> float:
        # boss columns run from the joint-lap top up to the baffle underside
        return self.baffle_seat_z - self.baffle_boss_floor_z

    @property
    def pivot_boss_z(self) -> float:
        # FORWARD pivot (on the frame, no ribs): the boss bottom sits at the parting
        # plane, so its centre is parting_z + the boss radius. The boss spans
        # parting_z .. parting_z+diameter, attached to the frame's intact outer wall
        # (the shiplap removes only the INNER wall over the lap). (Was mid-height.)
        return self.parting_z + self.pivot_boss_diameter / 2

    @property
    def pivot_boss_outer_radius(self) -> float:
        # external boss outer face seats the fork eye at pivot_centres/2
        return self.yoke_pivot_centres / 2

    @property
    def bow_arc_degrees(self) -> float:
        # at-rest arc span — DERIVES from the measured radius + rolled-out length
        # (θ = L / R). With 236.2 / 63.5 this lands ~213°, i.e. >180°: the ends sit
        # past the half-circle, matching the observed relaxed band.
        return math.degrees(self.bow_developed_length / self.bow_radius)

    @property
    def bow_worn_arc_degrees(self) -> float:
        # flexed-on-head arc span — the SAME strap (same developed length) opened
        # out to bow_worn_radius: θ = L / R_worn (~173° at R 78). < at-rest arc.
        return math.degrees(self.bow_developed_length / self.bow_worn_radius)

    @property
    def ear_half_spacing(self) -> float:
        # worn cup-centre half-spacing = where the flexed band's ends land
        # (R_worn · sin(half-arc)). ~78 mm → cups ~156 mm apart.
        return self.bow_worn_radius * math.sin(math.radians(self.bow_worn_arc_degrees / 2))


# Importable singleton used by every part module.
P = Params()
