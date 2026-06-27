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

    # ---- Cable exit (bottom of each earcup) ----------------------------------
    # A hole through the cup's −Y wall — the BOTTOM when worn (T_cup maps cup −Y to
    # global −Z) — for the driver cable to exit. One per cup; sized for a cable +
    # optional grommet/strain relief (TBD). Placed at the pivot mid-height (depth).
    cable_exit_diameter: float = 5.0      # ESTIMATE  cable passthrough (cable + grommet TBD)

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
    baffle_screw_count: int = 4           # SET  4 (maker's choice). The baffle's 6
                                          #   OTHER small holes are VENTS, not screws.
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

    # ---- Pivot over-rotation hard stop — REMOVED 2026-06-26 ------------------
    # The cup now rotates FREELY in the yoke (Grado-style — free pivot, no detent or
    # hard stop). The old pin-on-cup + arc-slot-in-yoke-eye stop was dropped: the pin
    # was a snap-off risk and the slot notch weakened the eye, and free rotation is a
    # non-issue in practice (cf. Grado). The shoulder screw is the only tilt joint.

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
    driver_recess_depth: float = 1.0      # SET  shallow seat the driver rim registers into (on BACK).
                                          #   Was 3 — a deep recess that pushed the dome up into the thin
                                          #   front lamina (cone poked the guard). Now a 1 mm seat + a
                                          #   locating COLLAR (below) hold the driver, dropping the dome
                                          #   ~2 mm clear of the guard with NO extra baffle thickness, and
                                          #   leaving a lip for a foam seal the clamp compresses.
    # Driver locating COLLAR — a short wall around the driver on the baffle BACK,
    # continuing the seat wall proud of the back face. Secures/locates the driver
    # laterally; kept SHORTER than the driver's behind-baffle protrusion so the clamp
    # ring still presses the rear rim (good seal + room for foam), per the maker.
    driver_collar_height: float = 2.5     # SET  collar height proud of the baffle back (< driver protrusion)
    driver_collar_wall: float = 2.0       # SET  collar radial wall thickness
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
    # The maker's prototype: a 3-ear ring that slips over the BACK of the driver and
    # retains it by the PERIMETER. The driver nests SLIGHTLY into a RECESS in the ring
    # (not pressed by a proud lip) — the recess wall captures the driver's outer edge
    # and the recess floor (an inner shoulder) bears on the back of the frame rim,
    # pressing the driver forward into the baffle's recess. The magnet/back clears
    # through the open centre. Bolts to 3 inserts on the baffle BACK at bcd 60 (between
    # the vents ~r26 and the frame holes r35; the 3 ears interleave with the 6 vents).
    # Standoff bosses on the baffle reach back to the ring at the driver's back depth.
    # (Driver-fit dims are REF / driver-measured-pending.)
    driver_clamp_count: int = 3              # SET  3-ear clamp (matches the prototype)
    driver_clamp_bolt_circle: float = 60.0   # SET  bcd (r30): between vents (r26) + frame holes (r35)
    driver_clamp_inner_diameter: float = 34.0  # SET  open centre — clears the magnet; shoulder catches the rim
    driver_clamp_recess_clearance: float = 0.4  # SET  driver OD ↔ ring recess (the driver nests in)
    driver_clamp_recess_depth: float = 2.0   # SET  how far the driver nests into the ring
                                             #   (≈ the basket that protrudes behind the baffle)
    driver_clamp_floor_thickness: float = 2.5  # SET  shoulder floor behind the recess
    driver_clamp_wall: float = 2.5           # SET  wall around the recess
    driver_clamp_ear_diameter: float = 9.0   # SET  ear pad dia around each M3 hole
    driver_clamp_post_width: float = 6.0     # SET  post width (< ear pad 9 → post↔pad shoulders fillet cleanly)
    # driver_clamp_standoff is DERIVED below (= body_depth − seat depth) so it tracks the seat.
    driver_clamp_fillet: float = 0.8         # SET  blend at the post↔ring / post↔pad junctions. 0.8 is this OCC
                                             #   build's CEILING here — 0.9–1.1 silently invalidate, ≥1.2 hard-fail
                                             #   (clamp fillet probe). Bigger radii want the build123d port.
    driver_clamp_edge_round: float = 0.6     # SET  roundover on the ear-plate perimeter (softens the 90° rim corners)

    # ---- Integral driver guard (concentric RINGS + radial SPOKES, on the baffle) -
    # A classic driver grille: concentric rings tie the radial spokes, far stronger
    # than bare spokes while staying airy. It sits in the front lamina just ABOVE the
    # driver dome (the diaphragm must never touch it). The lamina is thin, so the rib
    # is auto-thinned to fit and the build WARNS the true clearances (see baffle.py).
    guard_spoke_count: int = 6            # ESTIMATE  radial spokes (hub → aperture wall)
    guard_ring_count: int = 2             # SET  concentric rings tying the spokes (the rings+spokes grille)
    guard_member_width: float = 2.0       # ESTIMATE  spoke / ring width
    guard_setback: float = 0.5            # ESTIMATE  DESIRED pad setback below the front face. The guard sits in
                                          #   the pad's OPEN centre, so a small setback is fine (warned if below)
    guard_dome_clearance: float = 0.5     # SET  safety gap from the guard floor to the dome's DYNAMIC (excursed)
                                          #   forward-most position — i.e. margin BEYOND driver_dome_excursion
    guard_thickness: float = 1.5          # ESTIMATE  guard rib thickness (Z); thinned to fit the lamina
    guard_hub_diameter: float = 6.0       # ESTIMATE  small center hub to tie the spokes

    # ---- Driver (MEASURED 2026-06-26) ---------------------------------------
    driver_od: float = 39.5               # MEASURED  outermost frame dia (the "40 mm" driver)
    driver_diaphragm_diameter: float = 34.0  # ESTIMATE  diaphragm/dome (< the 39.5 frame; guard clears it)
    driver_body_depth: float = 5.0        # MEASURED  driver height on the outside (the basket)
    driver_dome_proud: float = 1.5        # REF  dome stands proud of the frame (at REST)
    driver_dome_excursion: float = 1.0    # ESTIMATE  forward DYNAMIC travel of the dome in play — MEASURE.
                                          #   The grille must clear the dome's forward-most (excursed) position,
                                          #   not just its rest height, or it rubs at high SPL. 1.0 is a
                                          #   conservative 40 mm-driver placeholder until measured.
    # Driver MOCKUP dims (parts/driver.py) — a representative driver shown in the
    # assembly so the driver↔baffle↔clamp fit reads. The magnet sits behind the basket.
    driver_magnet_diameter: float = 27.0  # MEASURED  rear magnet OD
    driver_magnet_depth: float = 3.0      # MEASURED  rear magnet height
    driver_cutout_tolerance: float = 0.3  # ESTIMATE  fit allowance on the recess
    driver_seat_ledge: float = 2.5        # ESTIMATE  radial frame seat (per side); aperture =
                                          #   od − 2·this = 34.5, so the 34 diaphragm clears it
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
    yoke_arm_corner_radius: float = 2.0   # SET  corner-round of the LOFTED arm section (the de-blocky form;
                                          #   2.0 adversarially verified, 2.5 also builds — taste knob). NOT a
                                          #   3D fillet: the rounding is in the swept 2D section.
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
    yoke_post_length: float = 52.0        # SET  post length above the arm junction. >= slider block (26) +
                                          #   adjust travel (18) + grip margin, so the slider stays fully
                                          #   engaged across the whole head-size range (34 was too short).
    slider_post_clearance: float = 0.4    # SET  slide fit, post↔slider bore (FDM)
    slider_adjust_travel: float = 18.0    # ESTIMATE  vertical size-adjust range (reference)
    slider_thumbscrew_diameter: float = 3.0      # SET  M3 LOCK shaft — friction-locks the post (no load → small)
    slider_thumbscrew_insert_hole: float = 4.0   # SET  M3 brass heat-set bore (the lock)
    slider_thumbscrew_boss: float = 7.0   # SET  boss OD hosting the M3 insert (1.5 wall; small on the Ø14 barrel)
    slider_thumbscrew_boss_proud: float = 6.0  # SET  how far the boss/head stands proud of the barrel (finger purchase)
    slider_thumbscrew_boss_z: float = 5.0      # SET  boss lifted toward the crown so the Ø12 head clears the gusset
                                          #   band (z±7) for a clean two-finger side-pinch. On the +Y OUTBOARD face: in
                                          #   the worn pose local +Y → global +X (straight out the side of the head) =
                                          #   the natural reach with the phones ON, and it drives the post into the FULL
                                          #   lozenge backing (firm lock) vs the thin 2.8 mm barrel ring on the old +X.
    # Thumbscrew MOCKUP (parts/hardware.py) — the height lock, shown in the assembly so the
    # Grado-style post+thumbscrew mechanism reads. BIG knurled head (grip) on the small M3
    # shaft — keeps the hand grip while the boss stays slim.
    thumbscrew_head_diameter: float = 12.0   # REF  knurled hand-grip head OD (mockup)
    thumbscrew_head_height: float = 5.0      # REF  head height
    thumbscrew_shaft_length: float = 14.0    # REF  shaft from the post surface out through the boss

    # ---- Slider = CLAMP COLLAR (replaced the box block) ----------------------
    # A slim rounded BARREL around the post + a slim 2-bolt mount tab for the bow's
    # end tab + the side thumbscrew. The round post sliding/turning in the barrel bore
    # is the SWIVEL + height bearing in ONE robust interface (no separate weak joint);
    # the thumbscrew clamps both. Far less bulk than the old 42×26×18 block. The bow
    # end tab (33 mm, 2 holes at bow_endtab_hole_spacing) bolts to the mount tab.
    slider_collar_diameter: float = 14.0      # SET  barrel OD around the post bore (Ø8.4 bore + 2.8 wall)
    slider_collar_height: float = 18.0        # SET  barrel height (post grip + travel feel)
    slider_collar_rim_round: float = 2.0      # constructed 45° chamfer on the barrel end rims (fillet pass)
    slider_bore_chamfer: float = 1.0          # countersink lead-in at each post-bore mouth (post entry + clean print)
    slider_boss_chamfer: float = 0.8          # small countersink at the thumbscrew insert-bore mouth (1.5 mm boss wall)
    slider_tube_gusset: float = 5.0           # SET  gusset run that fairs the tube into the lozenge (grown-in)
    slider_tube_gusset_z: float = 14.0        # SET  gusset extent along the tube height (Z)
    # Headband CLAMP (Beyer-style two-piece, OFFSET-OUTER layout). The post-bore TUBE
    # (the barrel) is the OUTER body — the band attaches on the barrel's INNER (−Y,
    # head-side) face, so the rod + tube ride OUTSIDE the metal band (maker's call). The
    # band's two prongs drop into a RECESS in the clamp plate; a RIB enters the bow's open
    # CHANNEL (between the rails) for anti-rotation; a separate COVER plate
    # (parts/headband_clamp.py) sits on the band's inner face and sandwiches the metal with
    # two M3 screws through the prong-tip holes. The clamp is centred on the barrel mid
    # (z=0); the post slides the full barrel height and may poke past it (nothing stacks on
    # the post). slider_clamp_hole_z / rib_z are now relative to the barrel mid.
    # The clamp body is a flat rounded LOZENGE (Beyerdynamic end-cap look): a stadium outline
    # (rounded ends) BEVELED toward the barrel, sitting on the barrel's INNER (head-side) face
    # so the rod + tube ride OUTSIDE the band. Sleek + low-profile. The band's prongs drop
    # into a RECESS in its inner face; a short COVER (grip region only) lets the band sweep out
    # cleanly above. Z values are relative to the barrel mid (z=0).
    slider_clamp_width: float = 44.0       # SET  lozenge length (X) — band width + rounded ends
    slider_clamp_height: float = 22.0      # SET  lozenge height (Z)
    slider_clamp_corner_r: float = 9.0     # SET  lozenge corner radius (the rounded ends)
    slider_clamp_bevel: float = 2.0        # SET  perimeter bevel inner→outer face (the sleek "angle")
    slider_clamp_bevel_head: float = 3.0   # SET  HEAD-side relief: the inner (-Y) face is INSET this much so its
                                           #   perimeter RECEDES from the temple (eased pillow, not a proud square
                                           #   lip). Widest section sits this far behind the contact face. Ergo pass.
    slider_clamp_standoff: float = 6.0     # SET  lozenge depth (Y) proud of the barrel; hosts the inserts
    slider_clamp_z_lo: float = -6.0        # SET  recess/cover bottom Z (holds the prong tip)
    slider_clamp_hole_z: float = 0.0       # SET  Z of the 2 bolt inserts (= prong-tip holes)
    slider_clamp_rib_z: float = 1.5        # SET  Z of the anti-rotation rib (in the channel)
    slider_clamp_rib_height: float = 3.0   # SET  rib Z extent (short — registers, doesn't block the exit)
    slider_clamp_rib_depth: float = 3.0    # SET  rib protrusion into the channel (−Y past the recess floor)
    slider_clamp_cover_thickness: float = 3.0  # SET  the inner cover plate thickness
    # Finger SCALLOPS — a shallow concave dish down each of the lozenge's ±X (front/back) ENDS
    # so the hand has a DEFINED pinch to slide the block up/down on the post (the adjust motion).
    # Vertical channels, outboard of the inserts (x=±13) and recess (x=±17), so gate-neutral.
    slider_grip_scallop_r: float = 6.0     # SET  scallop cutter radius (sets dish width)
    slider_grip_scallop_depth: float = 1.2 # SET  how deep the dish bites the end face (subtle, not a hole)
    slider_clamp_cover_ease: float = 1.2   # SET  the cover (first thing to touch the head) drafts inward this much
                                           #   on its head-side face → a soft central crown, rim off the skin. Ergo pass.

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
    bow_endtab_hole_inset: float = 5.0     # SET  hole set-in from the prong TIP (near the very end, per photo)
    bow_endtab_hole_spacing: float = 26.0  # SET  pitch of the 2 end holes = the two RAIL CENTRES
                                           #   (= bow_width − bow_rail_width). The real band's end is two
                                           #   separate PRONGS (the rails), one hole near each prong tip,
                                           #   with the big open gap between — NOT a solid tab. Slider follows.
    bow_endtab_width: float = 33.0        # ESTIMATE/REF  band strap width
    # End structure (real band, maker's photo): the two outer RAILS run all the way out
    # to the ends as separate PRONGS — a big open gap between them, a screw hole near each
    # prong tip — and are braced only by a CENTRAL cut-out (no solid end tab).
    bow_endtab_length: float = 28.0       # ESTIMATE  bare prong region at each end (no pad/bracing there)
    bow_rail_width: float = 7.0           # SET  rail/prong width (Y) — wide enough to host the end hole
    bow_strut_width: float = 3.5          # ESTIMATE  X-brace diagonal strut width
    # Central X cut-out matching the real metal bow (maker's photo): the X cells live
    # in a CENTRAL region (developed length bow_pattern_length), NOT across the whole
    # band — solid rails run out to the solid end tabs that carry the mounting holes.
    bow_pattern_enabled: bool = True      # SET  the real Beyer-style bow has the central X cut-out
    bow_pattern_length: float = 110.0     # ESTIMATE  developed length the X pattern spans (centred)
    bow_pattern_bays: int = 2             # ESTIMATE  number of X cells in the pattern
    # bow_arc_degrees / bow_worn_arc_degrees are DERIVED (helpers below): both
    # conserve bow_developed_length, so the relaxed and flexed bands are one strap.

    # ---- Headband pad (ROUGH DRAFT — crown cushion under the bow) -------------
    # Soft comfort pad (foam / printed TPU) hugging the bow's concave underside at
    # the crown. First pass — a simple arc band; form/retention refined later. All
    # ESTIMATE. One shared pad at the crown (not per-ear).
    # Full-arc cushion that WRAPS the band: a head-side cushion (thickness) plus a lip
    # OVER the top (wrap), spanning the band BETWEEN the end tabs. The band nests in a
    # channel and the pad wraps its underside, both edges, and over the top. (was an
    # 80° crown-only band on the bow's inner face.)
    headband_pad_thickness: float = 8.0          # ESTIMATE  head-side cushion depth (radial, below the band)
    headband_pad_wrap: float = 4.0               # SET  cushion lip OVER the top of the band (the wrap)
    headband_pad_width: float = 40.0             # ESTIMATE  total width (> 33 mm band → wraps the edges)
    headband_pad_channel_clearance: float = 1.0  # SET  band↔pad slot clearance (the bow nests in)
    # Leather-cushion look (à la a Beyerdynamic headband pad, but NO snap buttons —
    # generic, not a specific product): transverse PLEAT seams quilt the underside.
    headband_pad_pleats: int = 7                  # SET  transverse pleat seams across the cushion
    headband_pad_pleat_radius: float = 2.5        # SET  pleat-seam groove radius (rounded)
    headband_pad_pleat_depth: float = 1.2         # SET  how deep each pleat seam cuts the cushion

    # ---- Earpad (generalised round cushion MOCKUP — bought, the user's choice) -
    # A representative round earpad so the assembly + website read like a finished
    # headphone. Users fit their OWN from the Beyerdynamic range or aftermarket
    # (Brainwavz, Dekoni); these are a generic round-pad ESTIMATE — measure/refine.
    earpad_outer_diameter: float = 100.0  # ESTIMATE  cushion OD
    earpad_inner_diameter: float = 60.0   # ESTIMATE  ear-opening ID
    earpad_base_flat: float = 1.5         # SET  flat mounting base (seats on the cup front rim)

    # ---- Fit coupons (printable QA pieces; lock tolerances vs real hardware) --
    # Small parts that ISOLATE a toleranced interface so it's checked against the
    # real driver / clamp ring / pad BEFORE committing a full cup or baffle print.
    # Every fit dimension DERIVES from the real interface params above
    # (driver_recess_diameter, driver_clamp_*, cup_outer_diameter, pad_lip_*), so a
    # coupon CAN'T drift from the part it validates — only the coupon's own
    # scaffolding lives here. ACCESSORIES (STL+STEP), not in the assembly/gallery.
    coupon_driver_puck_margin: float = 4.0   # radial wall around the back recess (puck OD = recess + 2×)
    coupon_driver_tab_width: float = 10.0    # width of each spoke carrying a standoff boss out to the clamp BCD
    coupon_pad_ring_wall: float = 3.0        # coupon ring wall — rigidity only (NOT the real ~6.72 cup wall)
    coupon_pad_ring_height: float = 15.0     # grip-wall height below the lip (>= a typical pad mount-skirt depth)

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
    def driver_clamp_standoff(self) -> float:
        # baffle-back boss height = how far the driver protrudes behind the back face
        # = body_depth − the shallow seat. Derived so it tracks driver_recess_depth.
        return self.driver_body_depth - self.driver_recess_depth

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
        # one-piece cup: bosses stand on the interior back floor (solid) and run up to
        # the baffle underside — a full-height buttressed column tied to the floor + wall.
        return self.cup_interior_floor_z

    @property
    def baffle_boss_height(self) -> float:
        # boss columns run from the interior back floor up to the baffle underside
        return self.baffle_seat_z - self.baffle_boss_floor_z

    @property
    def pivot_boss_z(self) -> float:
        # yoke pivot bosses sit at cup mid-height (balanced clamp; one-piece cup).
        return self.cup_total_height / 2

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
