# Daily Driver — Build-Readiness Plan

Canonical plan for the push to a buildable prototype. Captures the 2026-06-27 readiness
assessment + the maker's decisions + the work plan. **Source of truth for this push — update
the checkboxes as items close.** (A fresh session can resume from here.)

## Readiness verdict (2026-06-27)

**~50% to true prototype-ready.** The CAD is sound *where the gate covers it* (16/16 build,
gate 0 HARD/0 SOFT, the pivot-bore bug caught + fixed); **what's left is mostly MEASUREMENT +
one real print, not redesign.** Weakest area: **acoustics (45/100)** — it's intention, not
geometry yet. Per-lens: printability 62, fit 52, acoustics 45, hardware/BOM 45.

## Maker decisions (2026-06-27)

- **Driver = Kingstate 40 mm.** Maker has several Kingstate 40 mm drivers, all ~same height.
  Supersedes the HPD-40N16 candidate. → set the driver family to Kingstate 40 mm; **measure exact
  OD / dome-proud / excursion / DCR / Fs-Qts when bench-testing** (params stay parametric).
- **Printer: not yet in hand.** Do NOT let print-verification BLOCK the work; do NOT drop it
  either. When the printer arrives the maker will ask what to print first (answer: the two
  coupons, then one cup). Keep all print-verify items flagged, not gating.
- **Pads: DEFAULT = Beyerdynamic** (maker has them now). **Dekoni = premium alternative + a
  tuning option** (incoming). `cup_outer_diameter` (91.44) back-solves from the pad cup-mount
  skirt Ø → **MEASURE the Beyer pad** (skirt/tension-ring ID + pad depth) and set MEASURED.
  Maker offered to caliper them — take him up on it.
- **Headband / fit (the worn-fit fix):** add **THREE reference heads (S / M / L)** to the viewer
  to compare how the band lands; make the **bow simulate SPRING STEEL** — flex/compress per head
  (conserve developed length) so the clamp adjustment is *visible*; tie the slider travel so
  **FULL EXTENSION = the LARGEST head**. Reconsider the ~30 mm post range in that light (if the
  cup/post can raise in the slider, the usable range shrinks — size it to S↔L head span, not a
  guessed 30 mm).
- **Fasteners: pin real SKUs + part numbers + lengths now** (BOM gets a part-number column).

## Blockers to a first prototype (maker-gated — tracked, not all doable now)

1. **Lock the driver** — Kingstate 40 mm; measure OD/dome/excursion/Fs-Qts when in hand.
2. **Print the coupons** (`driver_coupon`, `pad_coupon`) — *when the printer arrives*. Converts
   slip/friction/heat-set/pad-grip clearances ESTIMATE→MEASURED. Highest-leverage single action.
3. ~~Measure the Beyer pad~~ **RESOLVED from published dims** (no caliper needed): Beyer DT770/880/990
   = Dekoni/Brainwavz interchangeable, **elastic stretch-ring mount** → pad **OD 100, opening ~58,
   depth ~22–25 mm**. The ring stretches over ~88–95 mm, so **`cup_outer_diameter` 91.44 is fine as-is
   — keep it** (REF it, no longer a back-solve blocker). Only change: set the pad mockup **depth ~24 mm**
   (front-cavity acoustics) — fold into the acoustic-geometry task. (Optional later: caliper the cup-rim
   snug fit; not gating.)
4. **Fix the worn headband fit** (band floats ~35 mm above the crown) — via the head-models +
   sprung-bow + slider-range work below.
5. **Pin fastener SKUs** — doing now.

## Work plan — proceed NOW (no parts needed)

Ordered; tick as done. Each = build→gate→log→commit→push, sync promote until v1.0.

- [x] **1. Fastener SKUs + part numbers** — DONE (16c1b10). `bom.py` rewritten with a linked
  **Part #** column + flags; every number read off a live supplier page (no invented McMaster
  numbers). Post=Mädler 619806050, pivot=Accu 49844-SKH-M3-8-A2, knob=Grand Brass SCK35,
  bow=Beyer 917017/973361, heat-sets=Ruthex RX-M3x5.7/M5x9.5/8-32x4.7, SHCS=FMW 2170021/2170020,
  wave=BelMetric WW3BSS, nylon=Accu HPW-3-2-7-0-5-N, cable=Parts Express 240-1032. Fit fixes:
  8-32 bore 5.0→5.6; 5⁄8″ all-metal knob is non-stock (½″ SCK35, flagged). Driver→Kingstate,
  pads→Beyer default.
- [x] **2. Close gate gaps** — DONE. Added `slider_shoe`, `headband_clamp`, `driver_coupon`,
  `pad_coupon` to the manifold loop (all 1 valid solid). Added 3 shoe checks
  (`shoe-saddle-reaches-post`, `shoe-saddle-cradles-post`, `shoe-fits-pocket`). guard-dome stays
  SOFT — precondition sharpened to `driver_dome_excursion` measured (the one remaining estimate).
  Gate covers 12 parts + shoe interface, 0 HARD / 0 SOFT.
- [ ] **3. Stale-doc sweep + AUTO-UPDATE.** Fix now: `print-guide.md` (removed over-rotation stop,
  '8/8'→16 build, Ø8→Ø6 post, dead SOFT-warn ref), `slider_shoe.py` + params Ø8→Ø6 comments,
  `hardware.py` "M4 thumbscrew"→8-32, and the **published manual spec** (`daily-driver-design-spec.mdx`,
  still v0.2 → v0.3: pads→Beyer default + Dekoni alt, vents, "~90 cc"→**143 cc**). THEN make the
  drift-prone bits **auto-generated** (build count, part list, orientation table from PartsGallery,
  the BOM) so they can't go stale — a `gen-docs` step run by build.py.
- [ ] **4. Acoustic geometry as params + shown in model.** Add: a removable **felt/damping seat**
  (ledge behind the grille), a **dimensioned front-seal gasket** + a **seal-squeeze gate check**
  (30–50 % compression), a few **pluggable rear/baffle vents** (openness = a measurable, reversible
  knob), and an **acoustic-volume helper** (fix the 143 cc; front-cavity tied to measured pad depth).
  **DESIGN FOR THE CLOSED-BACK CONVERSION NEXT:** the cup back + venting should toggle solid↔open
  (a `cup_open_back` param), so the same architecture yields the closed-back variant — keep the
  damping seat + gasket shared, the rear openings the only delta.
- [ ] **5. Head models S/M/L + sprung bow + slider range.** Three toggleable reference heads
  (parametrize `head_reference` by size: ear-to-ear ~140 / 147 / 155, height set); **bow flexes to
  each head** (re-pose worn radius/arc per head, conserve developed length — clamp shows); **full
  slider extension = largest head**; re-pose `bow_worn_radius` / trim `yoke_post_length` so the
  crown reaches the band across travel. **Closes blocker 4.**
- [ ] **6. Assembly sequence + explode refinement.** Write the Daily-Driver assembly order
  (heat-sets → driver seat + gasket + clamp ring → pivot **washer-stack** `[head|wave|nylon|eye|
  nylon|boss]` → shoe-drops-in-before-the-post → post/slider → band sandwich); **draw the washer
  stack in the render**; refine the **explode tool** to follow the assembly order/grouping (the
  explode currently flies parts out of frame + has no sequence semantics).

## Parking lot (revisit)

- Print-verify everything (printer pending) — coupons first, then one full cup + a baseline REW sweep.
- Kingstate driver specs — measure when bench-testing.
- Dekoni pads — incoming; premium/tuning alternative.
- After v1.0 lock: stop the beta↔current auto-sync (see `website-publish-channels` memory).
