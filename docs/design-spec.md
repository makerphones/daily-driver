# Daily Driver — Open-Back Headphone

### Design Specification · v0.2 · 2026-06-12

**Status:** Design phase — CAD in progress. This document is the functional spec the CAD is
built against, and the reference behind the build guide, the parts list, and the measurements.

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

## System architecture

Four printed/sourced parts per side, each interface independently iterable:

```
SPRING STEEL ARC  (sourced, laser-cut flat, formed over a jig)
        |
SLIDER × 2  (printed) — adjusts length, wraps the arc, carries the yoke pivot post
        |
YOKE × 2  (printed) — connects slider to cup, allows ±20° tilt
        |
CUP ASSEMBLY × 2  (printed: cup shell + separate baffle plate)
```

Keeping each interface separate means any one part can be reprinted and iterated without
touching the others.

---

## Acoustic approach (open-back)

- **Open rear.** The back of the cup is an open vent pattern, not a sealed chamber — that's
  what makes the design forgiving and gives the open, airy character.
- **Front cavity = pad depth.** Driver-to-ear distance is set by pad thickness. Deeper is
  more comfortable and slightly warmer; shallower is more present and brighter. This is the
  main tuning lever, and it's why the pad choice is locked into the spec.
- **Light rear damping.** A disc of acoustic felt or thin open-cell foam across the rear vent
  tames cone breakup and reflections. Start light, tune by ear and measurement.
- **No sealed volume to get right** — the reason an open-back is the right first build.
- **Expected response:** forward mids, extended/airy treble, gentle rolloff in the low bass.

---

## Design decisions

### Cup shell
- **Symmetric** — identical left and right; L/R marked in the surface only.
- **~90 cc internal acoustic volume** — starting point, parameterized for easy adjustment.
- **Open-back vent** — ring of 6–8 oval slots on the rear face, ~40% open area.
- **Pad attachment** — tension-ring lip, 61–62 mm OD to accept Brainwavz HM5 and compatible
  pads.
- **Walls** — 3 mm minimum shell, 4 mm at structural points (baffle flange, yoke boss).
- **Print orientation** — open face down, no supports.
- **Material** — PLA+ for prototyping, PETG for durable/kit parts.

### Baffle plate
- **Separate from the cup** — 4× M3 screws into heat-set inserts; removable for driver swaps
  and tuning.
- **Driver cutout** — acoustic aperture only; the driver sits on a ledge (the frame doesn't
  pass through).
- **Gasket channel** — 2 mm wide × 1.5 mm deep around the driver cutout.
- **Insert placement** — 4 inserts, symmetric, ~70% of radius from center.
- **Cable entry** — 6–7 mm hole near one edge, toward the headband side.
- **Print orientation** — flat, no supports.

### Yoke
- **Separate from the cup** — lets the cup and yoke iterate independently.
- **Own pivot spec** — a 6 mm-diameter post, deliberately *not* cross-compatible with
  commercial (e.g. Beyerdynamic) yokes; this is the project's own interface.
- **Pivot post** — 6 mm diameter, 8 mm tall, one flat face, M3 through-hole for a retention
  screw.
- **Rotation** — ±20° tilt, with hard stops in the geometry to protect the cable.
- **Single axis** — tilt only; no fold mechanism on v1.
- **Left/right** — mirror images, two files.

### Slider
- **Wraps the spring steel arc** on three sides.
- **Adjustment** — friction clamp: a printed spring arm presses on the steel face.
- **Detent-ready** — the boss geometry also works with punched holes in the steel for a
  click-fit upgrade.
- **Carries the pivot post** — 6 mm post matching the yoke bore, M3 retention screw.

### Cable
- **Dual entry** — each cup has its own exit; Y-split at chin level. No routing through the
  headband arc — simpler wiring, easier assembly.
- **Strain relief** — raised ring at the entry; jacket clamped before it enters the cup.

---

## Component specifications

### Driver (parametric)

Design the baffle around named parameters, not a fixed part. Confirm the real numbers with
calipers and print a baffle test piece (a ~20-minute print) before committing a full cup set.

| Parameter | Starting value | Notes |
|---|---|---|
| Outer frame diameter (`driver_od`) | 42 mm | 38–42 mm class; **measure your actual driver** |
| Acoustic aperture (`driver_aperture`) | 35 mm | Driver sits on the ledge inside this |
| Gasket ledge width | 3.5 mm/side | (`driver_od` − `driver_aperture`) / 2 |
| Driver depth | 10 mm | Sets minimum cup interior depth |
| Cutout tolerance | +0.3 mm | Actual cut ≈ 35.3 mm for fit |
| Impedance target | 32 Ω | Works from phones/laptops, no amp |

**Selecting a driver.** Look for: 40 mm nominal, 32 Ω, neodymium magnet, a *smooth* response
without aggressive peaks above ~3 kHz, and ideally a published measurement from another
builder. Good options sit in the $12–18 range at Parts Express or Madisound.

> **Budget option, with a caveat.** The Dayton CE38MB-32 (~$3.49, 40 mm frame, 32 Ω, Ø35.5 mm
> opening, ~5.6 mm deep) is the cheapest way in, but it has a peaky upper midrange that takes
> extra damping work to tame — workable, but not the easiest first-build driver. Choose it
> only if cost is the priority, and expect to spend more time on damping.

### Ear pads
- Brainwavz HM5 velour, 90 mm oval (widely available; the design is built to this pad).
- Friction-ring attachment — pushes over the cup's pad lip.
- Confirm the HM5 inner ring diameter with calipers before finalizing the lip OD (nominal
  ~60 mm; cup lip OD target 61–62 mm).

### Spring steel arc

| Parameter | Value | Notes |
|---|---|---|
| Material | 1095 high-carbon spring steel | Standard headband material |
| Thickness | 0.7 mm | 0.6 mm lighter/gentler, 0.8 mm firmer |
| Width | 10 mm | Standard headband width |
| Target inside arc radius | ~100 mm | Needs prototype iteration (see Open questions) |
| Developed (flat) length | ~370 mm | ~100 mm radius × ~90° arc + 30 mm terminations each end |
| Detent holes (optional) | 3 mm dia., 6 mm spacing | Punched at cut time for click-adjust |

**Sourcing the steel — the clever part.** Draw the arc as a *flat developed profile* (imagine
the arc unrolled), export a DXF, and order it laser-cut in 1095 spring steel from a service
like SendCutSend (~$10–15 delivered at low quantity). They ship flat precision blanks; you
form the curve cold over a printed radius jig. No metal shop, no minimum orders. (Builders on
a tighter budget can salvage spring steel from a cheap fashion headset — functional, but
imprecise.) The DXF ships alongside the STLs so anyone can order their own.

---

## 3D-print guidance

- **Material:** PETG (durable, slight flex — good for cups and the stressed gimbal/headband
  parts) or PLA+ (easy, rigid, fine for prototypes). Avoid brittle plain PLA on any stressed
  part.
- **Tolerances:** start 0.2 mm clearance for a friction fit, 0.3–0.4 mm for a slip fit; tune
  to your printer.
- **Heat-set inserts:** M3 brass inserts in printed bosses for any joint opened and closed
  (driver retention, gimbal) — far more durable than screwing into plastic.
- **Orientation:** put the best surface on visible faces; print the grille flat; orient the
  yoke so stress runs *along* layer lines, not across them (layer adhesion is the weak axis).
- **Supports:** designed to be support-free where possible (overhangs ≤45° chamfered).

---

## Parametric setup (for builders who want to modify it)

The model is driven by named parameters so it can be adapted without re-modeling. Starting
values:

```
cup_interior_diameter = 78 mm
cup_depth             = 30 mm
wall_thickness        = 3 mm
driver_od             = 42 mm     ← update when driver confirmed
driver_aperture       = 35 mm     ← update when driver confirmed
gasket_channel_width  = 2 mm
gasket_channel_depth  = 1.5 mm
pad_lip_od            = 62 mm
pivot_post_diameter   = 6 mm
vent_slot_count       = 7
vent_open_fraction    = 0.40
```

**Cup approach — interior first.** Model the acoustic void as the primary geometry (revolve
the half-profile of the interior, then shell outward to `wall_thickness`), then add the pad
lip, baffle flange, yoke boss, and vent array. Build order: cup → baffle → yoke → slider, each
constrained by the part before it.

---

## Printing the parts without your own printer

If you don't have a printer, FDM print services (e.g. JLCPCB, Xometry) will print the part set
inexpensively — order a few iterations at once to batch the shipping wait. For a show finish
on the cups, an SLA service gives a smoother surface. Once a design is stable and you're
iterating often, an inexpensive desktop printer pays for itself quickly.

---

## Bill of materials (build-it-yourself)

| Component | Source | Est. cost |
|---|---|---|
| 2× 40 mm driver, 32 Ω | Parts Express / Madisound | $8–18 |
| 1× Brainwavz HM5 velour pads | Brainwavz | $20–25 |
| 1× spring steel arc (laser-cut, formed) | SendCutSend + form | $8–15 |
| 8× M3 heat-set inserts | hardware/online | $1 |
| 8× M3×8 mm button-head screws | hardware/online | $1 |
| Foam gasket tape (small roll) | hardware | $1 |
| Damping pack (foam + felt + fiberfill) | Parts Express | $3–5 |
| Cable + Y-split + 3.5 mm TRS plug | online | $8–15 |
| Printed parts (2× cup, baffle, yoke, slider) | own printer or service | $3–25 |
| **Approx. total** | | **~$55–105** |

Own-printer build lands near the low end (filament only); print-service sourcing near the high
end.

---

## Open design questions

These are the live problems still being worked — documented as the design develops.

**Spring steel arc radius.** Arc radius and steel thickness together set clamping force: too
tight is uncomfortable, too loose falls off. Approach: print forming jigs at 95 / 105 / 115 mm
inside radius, form a blank over each, test across head sizes before committing. Cold-formed
spring steel springs back ~10–15% when released, so cut the jig radius 10–15% *smaller* than
the target. If the best radius gives the wrong clamping force, change thickness (0.6 mm
lighter, 0.8 mm firmer) before changing geometry.

**Driver confirmation.** The baffle is parametric specifically so the production driver can be
locked late — update `driver_od` / `driver_aperture` and the baffle follows. Confirm a
specific driver against the selection criteria above, ideally one with published measurements.

---

## Locked vs. open — for the form/industrial-design work

**Locked (the design must respect these):**

- The four-part architecture and the project's own 6 mm pivot interface
- Driver seat parametric to `driver_od`; baffle aperture to `driver_aperture`; grille protects
  the driver
- Pad lip sized to the Brainwavz HM5 (61–62 mm OD)
- Circumaural fit; spring steel headband, 1095 / 0.7 mm / 10 mm
- Standard cable connector

**Open (the form playground):**

- Cup profile and outer form
- Rear vent geometry and pattern — the signature look
- Yoke / slider styling within the pivot and clamp constraints
- Color, finish, and overall aesthetic language

---

*v0.2 · 2026-06-12 · Reconciled from the earlier Daily Driver brief and the driver-grounded
acoustic spec. Update as the form lands and the first prototype is measured. Open decisions:
specific production driver, final pad confirmation, connector choice, file license.*
