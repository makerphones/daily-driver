# Daily Driver — Open-Back Headphone

### Design Specification · v0.3 · 2026-06-14

**Status:** Design phase — direction locked, CAD catching up. This document is the functional
spec the CAD is built against, and the reference behind the build guide, the parts list, and the
measurements.

> **🧊 Spin it in 3D** — inspect the assembly in your browser before you build:
> **[live 3D preview →](https://makerphones.github.io/daily-driver/)**

> **Every dimension below is a first-pass starting value pending measured parts.** Numbers are
> here so the geometry has something to build against, not because they're confirmed. They get
> replaced as real drivers, pads, and the bow are measured with calipers. Where a number depends
> on a part not yet in hand (the bow especially), it's marked **TBD from measured part**.

---

## Overview

The Daily Driver is the canonical first build: a 40 mm open-back headphone that's forgiving to
design and to assemble, buildable by a first-timer, and good enough to keep wearing once it's
done. It's fully parametric and built to be modified — change the driver, the pad, or the head
size and the model follows. A pre-sourced kit may be offered later; everything here is also
exactly what you need to build it yourself.

Honest sonic target: a **bright, open, detailed open-back** — strong mids and treble, modest
bass. That's the nature of a small driver in an open baffle, and the design leans into it
rather than chasing sub-bass the hardware can't make.

---

## Direction — DT880-family, around-ear

The form is locked to the **Beyerdynamic DT880 family**: a sprung-steel head **bow**, **sliders**
that ride it, and **fork-yokes** that straddle each cup. This is a deliberate choice between three
candidates the form pass explored:

- **DT880-family (chosen).** Spring-steel bow + fork-yoke + sliders. Around-ear, serviceable,
  honest pro-audio engineering — and the architecture decomposes cleanly into printed parts that
  bolt to a sourced steel bow. It reads exactly like what it is.
- **Grado-minimal (rejected).** On-ear, rod-block gimbals, exposed everything. Charming but small
  on the ear and fiddly to make comfortable; not the around-ear fit we want.
- **DCA thin-metal (rejected).** Dan Clark-style folded thin-metal baffle/arc. Beautiful, but it
  only makes sense in metal fabrication, not FDM — it would be faking a process we don't have.

Everything downstream — the fork-yoke, the screw-pin pivot, the slider that reuses a real Beyer
bow — follows from picking the DT880 family.

---

## System architecture

Seven parts per side, printed or sourced, each interface independently iterable. Top of the head
down to the ear:

```
SPRING-STEEL BOW         (bought: Beyerdynamic Metal Head Bow  |  or DIY 1095 to same geometry)
        │  ← slider rides the bow
SLIDER  × 2              (printed) — height adjust + swivel; clamps the bow
        │  ← fork-yoke carried by the slider
FORK-YOKE × 2            (printed) — DT880-style fork straddling the cup; ±20° tilt
        │  ← screw-pin pivot into the cup
CUP × 2                  (printed) — shell + integral rear grille; perimeter-wall screw bosses; earpad lip on the outer rim
        │  ← baffle front-mounts into the cup
BAFFLE × 2               (printed) — front-mount driver-mount plate; integral driver guard
        │
DRIVER × 2               (bought) — ~40 mm dynamic, damped, with rear air space
        │
PAD × 2                  (bought) — Dekoni Universal 100 mm (Beyer-type); slips over the cup-rim lip
```

Keeping each interface separate means any one part can be reprinted and iterated without touching
the others. The three real joints are detailed under **Interfaces** below.

→ See **[drawings/assembly.svg](drawings/assembly.svg)** for the exploded stack with the three
joints called out.

---

## Parts table

| Part | Printed / bought | Key dims (first-pass) | Status |
|---|---|---|---|
| Head bow | **Bought** (Beyer Metal Head Bow) or DIY 1095 | width ~10 mm; arc + length **TBD from measured part** | Sourcing target; geometry from real part |
| Slider ×2 | Printed | rides bow; height + swivel | Concept (CAD stub) — see [drawings/slider.svg](drawings/slider.svg) |
| Fork-yoke ×2 | Printed | straddles cup; ±20° tilt; M3 screw-pin | Concept (CAD stub) — see [drawings/yoke.svg](drawings/yoke.svg) |
| Cup ×2 | Printed | ID 78 · **depth 20** (DT880/770 ref; rear ~96 cc) · OD 90 (pad-driven) · wall 6; earpad lip on the rim | First-pass geometry; grille authored — see [drawings/cup.svg](drawings/cup.svg) |
| Baffle ×2 | Printed | OD ~77 · **stepped 6 (driver/guard hub) / 4 (outer ring)** · aperture ⌀35 · **open arc-slot vents + glued acoustic paper** | First-pass geometry — see [drawings/baffle.svg](drawings/baffle.svg) |
| Driver ×2 | Bought | ~40 mm dynamic, 32 Ω | Candidate: Peerless HPD-40N16 |
| Pad ×2 | Bought | Dekoni Universal 100 mm (Beyer-type); outer foam ⌀100, ear opening ⌀60 | Pad target locked |
| M3 heat-set inserts | Bought | M3 brass | Convention (`parts/features.py`) |
| M3 screws (rim + pivot) | Bought | M3 — rim: socket/button; pivot: shoulder screw | Convention |
| Damping pack | Bought | felt / foam / fiberfill | Tune by ear |

---

## Interfaces — the three joints

Three real joints hold the headphone together. Each is an independently iterable interface with a
resolved decision; exact dimensions are first-pass pending the mating parts.

### 1 · Cup ↔ Baffle — front-mount plate

The baffle (OD ~77) drops into the front of the cup (interior ID 78) and **front-mounts**: four
M3 screws pass through the baffle rim, **counterbored from the front**, into four heat-set inserts
in the cup's **perimeter-wall bosses**. The screw heads sit under the pad and are hidden once the
pad is on.

- **Decision:** front-mount, screws hidden under the pad; baffle is removable for driver swaps and
  tuning.
- **Not a hard seal.** The interface allows **controlled venting** plus a deliberate
  **damping-material spot** — the open-back wants some leakage here, not a gasketed seal.
- Supersedes v0.2's rear-ledge gasket-sealed baffle and its 70%-radius free-standing insert posts.

### 2 · Yoke ↔ Cup — screw-pin pivot

A DT880-style **fork-yoke straddles the cup**. Each fork arm pivots on a **screw-pin**: an M3
**shoulder screw** through the fork arm into a **heat-set insert** in the cup. Tilt is **±20°**.

- **Decision:** screw-pin pivot (shoulder screw + heat-set insert), one per side of the fork.
- Supersedes v0.2's "project's own 6 mm pivot post" interface — the pivot now lives at the
  yoke↔cup joint as a serviceable screw-pin, not a moulded post.

### 3 · Yoke ↔ Bow — slider

The **slider** clamps and **rides the bow** for height adjustment and provides the **swivel**
(cup rotation to meet the head); the fork-yoke is carried by the slider. Together: slider = height
+ swivel, fork-yoke = tilt.

- **Decision:** printed clamp on the bow; the bow is a **Beyerdynamic Metal Head Bow drop-in** (or
  DIY 1095 to the same geometry).
- **Open:** friction vs. detent on the height adjust is still undecided — with a real Beyer bow in
  hand there's the option to **reuse Beyer's metal wiper** rather than print the clamp spring.

---

## Acoustic approach (open-back)

- **Open rear.** The back of the cup is an integral open **grille**, not a sealed chamber — that's
  what makes the design forgiving and gives the open, airy character.
- **Front cavity = pad depth.** Driver-to-ear distance is set by pad thickness. Deeper is more
  comfortable and slightly warmer; shallower is more present and brighter. This is the main tuning
  lever, and it's why the pad choice is locked into the spec.
- **Light damping.** Acoustic felt / thin open-cell foam at the rear grille and a damping spot at
  the baffle interface tame cone breakup and reflections. Start light, tune by ear and measurement.
- **Rear air space.** The driver mounts with a deliberate rear air space behind it (cup depth),
  not pressed against the back.
- **No sealed volume to get right** — the reason an open-back is the right first build.
- **Expected response:** forward mids, extended/airy treble, gentle rolloff in the low bass.

---

## Design decisions

### Cup shell

→ **[drawings/cup.svg](drawings/cup.svg)**

- **Shell + integral grille** — the rear face *is* the grille, modelled into the cup (not a
  separate vented disc). Grille = a center **hub** + **2 concentric rings** + **8 radial spokes**,
  ~**40% open** area, every member **≥ 2 mm** for FDM printability.
- **Perimeter-wall screw bosses** — the four M3 heat-set bosses for the baffle are **blended into
  the perimeter wall**, *not* free-standing posts in the field of the back. Front-mount, and
  **clocked off the pivot axis** so they don't collide with the fork pivots.
- **Earpad retaining lip on the outer rim** — a raised ring at the cup's front **outer** edge
  (DT770-style); the earpad slips **over** it and its skirt wraps the lip. Retention lives on the
  structural cup, *not* the baffle. The lip OD = the cup OD, so it sizes with the cup.
- **Envelope** — interior **ID 78 mm × depth 30 mm**; **OD 90 mm** — a **pad-driven** outer
  diameter set to the earpad's cup-mount opening, so the cup's actual wall falls out at **6 mm**
  (`wall_thickness` 3 mm is now just the min-wall floor). The interior is unchanged at 78 mm —
  this is a pad/mounting change, not an acoustic one — so the ~143 cc internal volume holds
  (⌀78 × 30 mm ≈ π·39²·30 ≈ 143 cc; the old "~90 cc" was an arithmetic slip).
  Parameterized; **cup OD is now SET at 91.44 mm** (4 in overall − 2× pad lip), back-solved from the
  Beyer/Dekoni stretch-ring grip range — no caliper needed (see the build-readiness plan).
- **Symmetric** — identical left and right; L/R marked in the surface only.
- **Print orientation** — open face down / grille flat, no supports.
- **Material** — PLA+ for prototyping, PETG for durable/kit parts.

> **Engineering-pass note.** The current CAD still carries the June-14 grille where the outer ring
> sits on the old 70%-radius boss circle (bosses as ring nodes). This direction **moves the bosses
> out to the perimeter wall**, which decouples the grille's outer ring from the boss radius. The
> clean grille + wall-boss relocation + driver guard land together in the next engineering pass —
> this docs pass only records the target.

### Baffle plate

→ **[drawings/baffle.svg](drawings/baffle.svg)**

- **Front-mount plate**, OD **~77 mm**, **~4 mm** thick — drops into the cup front and screws from
  the front (see Interface 1).
- **Aperture ⌀35 mm with an integral printed driver guard** — thin spokes / grid printed across
  the aperture to protect the driver, in the same logo-evocative language as the rear grille.
- **No pad lip on the baffle** — the earpad retaining lip now lives on the **cup's outer rim**
  (DT770-style; see the Cup shell section); the baffle is a clean **driver-mount plate**. The
  front venting is now **open arc-slots** in the ring (between the 3 clamp-standoff sectors),
  **backed by a glued acoustic paper/mesh** in a shallow front depression — the paper sets the
  back→front resistance (open area large + parametric; paper grade measurement-gated).
- **Driver pocket ⌀42 mm on the back** — the driver frame seats into a pocket on the rear face;
  the aperture is the acoustic opening it fires through.
- **4 M3 rim screws**, counterbored from the front, into the cup's perimeter-wall bosses (see
  Interface 1). Heads hidden under the pad.
- **Open front venting + acoustic paper/mesh** (resistance-controlled), not a hard seal.
- **Print orientation** — flat, no supports.

### Fork-yoke

→ **[drawings/yoke.svg](drawings/yoke.svg)**

- **DT880-style fork** that straddles the cup.
- **Screw-pin pivot** — M3 shoulder screw through each fork arm into a heat-set insert in the cup
  (see Interface 2).
- **Tilt ±20°**, with hard stops in the geometry to protect the cable.
- **Carried by the slider** at the top; the slider provides swivel and height.
- **Left/right** — mirror images, two files.

### Slider

→ **[drawings/slider.svg](drawings/slider.svg)**

- **Printed clamp that rides the bow** — provides **height adjustment** and **swivel**.
- **Adjustment mechanism open** — friction (a printed spring arm pressing the steel) vs. detent
  (punched holes in the bow for click-fit) is undecided; with a real Beyer bow there's also the
  option to **reuse Beyer's metal wiper** instead of printing the spring.
- **Carries the fork-yoke** below it.

### Headband / bow

→ **[drawings/bow.svg](drawings/bow.svg)**

- **Primary: Beyerdynamic Metal Head Bow as a drop-in.** Sourced ready-made (~$11). Design the
  slider/mount to accept it directly.
  Source: <https://north-america.beyerdynamic.com/p/metal-head-bow>
- **Option: DIY 1095 spring steel** to the **same geometry** — laser-cut a flat developed profile
  (e.g. SendCutSend), form cold over a printed radius jig. For builders who'd rather make it than
  buy it, or where the Beyer part isn't available.
- **Exact bow dimensions are TBD from the measured part** — width is ~10 mm class; arc radius,
  developed length, and the wiper/detent interface all come from a real bow on the bench.

### Cable

- **Dual entry** — each cup has its own exit; Y-split at chin level. No routing through the bow.
- **Strain relief** — raised ring at the entry; jacket clamped before it enters the cup.

---

## Component specifications

### Driver (parametric)

Design the baffle around named parameters, not a fixed part. Confirm the real numbers with
calipers and print a baffle test piece (a ~20-minute print) before committing a full cup set.

| Parameter | Starting value | Notes |
|---|---|---|
| Outer frame diameter (`driver_od`) | 42 mm | 38–42 mm class; **measure your actual driver** |
| Acoustic aperture (`driver_aperture`) | 35 mm | Driver fires through this; guard printed across it |
| Driver pocket (baffle back) | 42 mm | Frame seats into the rear pocket |
| Driver depth | 10 mm | Sets minimum cup interior depth |
| Cutout tolerance | +0.3 mm | Actual cut ≈ 35.3 mm for fit |
| Impedance target | 32 Ω | Works from phones/laptops, no amp |

**Candidate driver: Peerless HPD-40N16** — a ~40 mm dynamic that fits the class and the sonic
target. Treated as a **candidate**, not locked: the baffle stays parametric so the production
driver is confirmed late (smooth response without aggressive peaks above ~3 kHz, ideally with a
published measurement from another builder). Mount with damping and a rear air space.

### Ear pads

- **Dekoni Audio Universal 100 mm** (Beyer-type) — outer foam **⌀100 mm**, ear opening **⌀60 mm**
  (the ⌀60 is the *ear* hole, **not** the cup mount). The design is built to this pad. Price
  **~$30–45 (ESTIMATE)**.
- **Slips over the cup-rim lip** — the pad's skirt wraps a raised retaining ring at the cup's outer
  front edge (DT770-style); the lip is part of the structural cup, not the baffle.
- **Pad-mount = cup OD.** Set `cup_outer_diameter` to the Dekoni pad's actual cup-mount opening and
  the cup-rim lip follows. Current value **90 mm is ESTIMATE/TBD** — measure the pad's mounting lip
  with calipers before finalizing (don't confuse it with the ⌀100 foam OD or the ⌀60 ear hole).

### Head bow

| Parameter | Value | Notes |
|---|---|---|
| Primary part | Beyerdynamic Metal Head Bow | Drop-in, ~$11 — [source](https://north-america.beyerdynamic.com/p/metal-head-bow) |
| DIY alternative | 1095 high-carbon spring steel | Laser-cut flat profile, formed cold over a jig |
| Width | ~10 mm | Standard headband width; **confirm from the measured bow** |
| Thickness | ~0.7 mm class | 0.6 mm lighter, 0.8 mm firmer (DIY route) |
| Arc radius / length | **TBD from measured part** | Slider + jig geometry derive from the real bow |

**DIY sourcing (the clever part).** Draw the arc as a *flat developed profile*, export a DXF, and
order it laser-cut in 1095 spring steel (e.g. SendCutSend, ~$10–15 at low quantity). They ship
flat blanks; form the curve cold over a printed radius jig — no metal shop, no minimums. The DXF
ships alongside the STLs. Cold-formed spring steel springs back ~10–15%, so cut the jig radius
10–15% *smaller* than target.

---

## 3D-print guidance

- **Material:** PETG (durable, slight flex — good for cups and the stressed yoke/slider) or PLA+
  (easy, rigid, fine for prototypes). Avoid brittle plain PLA on any stressed part.
- **Tolerances:** start 0.2 mm clearance for a friction fit, 0.3–0.4 mm for a slip fit; tune to
  your printer.
- **Heat-set inserts:** M3 brass inserts in printed bosses for any joint opened and closed (baffle
  rim, pivot) — far more durable than screwing into plastic.
- **Orientation:** best surface on visible faces; print the grille flat; orient the yoke so stress
  runs *along* layer lines, not across them (layer adhesion is the weak axis).
- **Supports:** designed to be support-free where possible (overhangs ≤45° chamfered).

---

## Parametric setup (for builders who want to modify it)

The model is driven by named parameters so it can be adapted without re-modeling. **All values are
first-pass starting points** (`params.py` is the single source of truth):

```
cup_interior_diameter = 78 mm
cup_depth             = 30 mm
wall_thickness        = 3 mm
driver_od             = 42 mm     ← update when driver confirmed
driver_aperture       = 35 mm     ← update when driver confirmed
cup_outer_diameter    = 90 mm     ← pad-driven; earpad lip on the cup rim (Dekoni ~90, TBD)
baffle_thickness      = 6 mm     ← driver/guard HUB (dome-gated); outer ring 4 mm (front recessed)
grille_ring_count     = 2
grille_spoke_count    = 8
grille_target_open_fraction = 0.40
grille_member_width   = 3.8 mm    ← held ≥ 2 mm for printability
pivot_tilt_degrees    = 20        ← ±20° fork tilt
```

**Cup approach — interior first.** Model the acoustic void as the primary geometry (revolve the
half-profile of the interior, then shell outward to `wall_thickness`), then add the integral
grille, the perimeter-wall bosses, and the pivot insert bosses. Build order: cup → baffle → yoke →
slider, each constrained by the part before it.

---

## Printing the parts without your own printer

If you don't have a printer, FDM print services (e.g. JLCPCB, Xometry) will print the part set
inexpensively — order a few iterations at once to batch the shipping wait. For a show finish on
the cups, an SLA service gives a smoother surface. Once a design is stable and you're iterating
often, an inexpensive desktop printer pays for itself quickly.

---

## Bill of materials (build-it-yourself)

Mirrors the assembly sheet ([drawings/assembly.svg](drawings/assembly.svg)).

| Component | Source | Est. cost |
|---|---|---|
| 1× Beyerdynamic Metal Head Bow | [beyerdynamic](https://north-america.beyerdynamic.com/p/metal-head-bow) | ~$11 |
| — or DIY 1095 spring-steel bow (laser-cut, formed) | SendCutSend + form | $8–15 |
| 2× ~40 mm driver, 32 Ω (candidate Peerless HPD-40N16) | Parts Express / Madisound | $8–25 |
| 1× Dekoni Universal 100 mm pads (Beyer-type) | Dekoni Audio | $30–45 |
| M3 heat-set inserts (baffle rim + pivots) | hardware/online | $1–2 |
| M3 screws — rim (socket/button) + pivot (shoulder) | hardware/online | $1–2 |
| Damping pack (foam + felt + fiberfill) | Parts Express | $3–5 |
| Cable + Y-split + 3.5 mm TRS plug | online | $8–15 |
| Printed parts (2× cup, baffle, fork-yoke, slider) | own printer or service | $3–25 |
| **Approx. total** | | **~$55–110** |

Own-printer build lands near the low end (filament only); print-service sourcing near the high end.

---

## Open design questions

These are the live problems still being worked — documented as the design develops.

**Bow geometry from the measured part.** The slider clamp, swivel, and (if DIY) the forming jig
all derive from the real Beyer Metal Head Bow's cross-section, arc radius, and length. Get one on
the bench and measure before committing slider geometry.

**Slider adjustment: friction vs. detent.** Printed spring-arm friction clamp, punched-hole
detents in the bow, or reuse of Beyer's metal wiper. Decide with a real bow in hand.

**Driver confirmation.** The baffle is parametric specifically so the production driver can be
locked late — update `driver_od` / `driver_aperture` and the baffle follows. Confirm the Peerless
HPD-40N16 (or alternative) against the selection criteria, ideally one with published measurements.

**Venting balance.** How much controlled leakage at the baffle interface vs. how much damping —
tuned by ear and measurement once a driver is in.

---

## Locked vs. open — for the form/industrial-design work

**Locked (the design must respect these):**

- **DT880-family architecture:** spring-steel bow → slider (height + swivel) → fork-yoke (±20°
  tilt) → cup → baffle → driver → pad. Each interface independently iterable.
- **Screw-pin pivot** at the yoke↔cup joint (M3 shoulder screw into a heat-set insert) — supersedes
  the old 6 mm post interface.
- **Front-mount baffle** — a clean driver-mount plate with the driver guard integral to it (no pad
  lip); rim screws into perimeter-wall cup bosses, hidden under the pad.
- Driver seat parametric to `driver_od`; baffle aperture to `driver_aperture`; integral guard
  protects the driver.
- **Earpad retaining lip on the cup's outer rim** (DT770-style); pad-mount = cup OD (Dekoni
  Universal 100 mm → ~90 mm, exact **TBD** — measure the pad's mounting lip).
- Circumaural fit; Beyerdynamic Metal Head Bow drop-in (or DIY 1095 to the same geometry).
- Standard 3.5 mm cable connector, dual entry.

**Open (the form playground / still to resolve):**

- Cup outer profile and overall form.
- Final rear-grille geometry within the hub + 2 rings + 8 spokes language (the signature look).
- Fork-yoke and slider styling within the pivot and clamp constraints.
- Slider adjustment mechanism (friction / detent / Beyer wiper).
- Color, finish, and overall aesthetic language.

---

*v0.3 · 2026-06-14 · Direction locked to the DT880 family (around-ear; spring-steel bow + fork-yoke
+ sliders). Resolved the pivot (screw-pin), the driver-guard location (baffle), the baffle mount
(front-mount, hidden screws), the cup bosses (blended into the perimeter wall), and the bow sourcing
(Beyer drop-in / DIY 1095). All dimensions first-pass pending measured parts. Geometry changes —
clean grille, wall bosses, driver guard, real yoke/slider/bow — come in the next engineering pass.
Open: bow geometry from the measured part, slider adjustment, production driver, venting balance.*

*Update (2026-06-25) · Earpad target switched to the **Dekoni Universal 100 mm** (Beyer-type); the
retaining lip moved from the baffle to the **cup's outer rim** (DT770-style), making the baffle a
clean driver-mount plate; the cup OD is now a **pad-driven 90 mm** (interior held at 78 mm, wall
6 mm). Cup OD is **ESTIMATE/TBD** pending a caliper read of the pad's cup-mount opening. See the
DESIGN-LOG for the full reasoning.*
