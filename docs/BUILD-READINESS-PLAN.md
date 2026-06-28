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
- [x] **3. Stale-doc sweep + AUTO-UPDATE.** DONE. Fixed active-code comments (Ø8→Ø6 in slider_shoe.py
  + params; M4/4-40→8-32 in hardware.py/slider.py/assembly.py). `print-guide.md`: removed the
  over-rotation stop, build-count→"all green (see PARTS.md)", M3→M3/M5/8-32 inserts, dead SOFT ref
  → driver-excursion note, +orientation rows for the new parts. Template docs '8/8'→'N/N'.
  **Auto-gen:** new `gen_parts_doc()` in build.py writes `docs/PARTS.md` (live inventory + 16/16 count,
  derived from the part dicts) alongside the already-auto-gen BOM.md. Website spec + local design-spec:
  corrected the actively-wrong facts (90→**143 cc**, pads→Beyer default) + an honest status note.
  **Parked:** a FULL website/local design-spec architecture refresh (it still describes the old
  spring-steel-arc/old-pivot architecture) — do after items 4-5 settle acoustics + headband, so it's
  rewritten once. (DESIGN-LOG could one day be auto-summarized too, but it's append-only history.)
- [x] **4. Acoustic geometry as params + shown in model.** DONE. `cup_open_back` toggle (open grille /
  solid back + pluggable tuning ports — closed-back verified to build as 1 solid). New `parts/vent_plug.py`
  (reversible openness knob). Damping retaining ring (felt-disc seat) in the cup. Dimensioned front-seal
  gasket + HARD `front-seal-squeeze` check (30–50 %). Acoustic-volume helpers fix the 143 cc IN CODE
  (`cup_interior_volume_cc` 143.4, `front_cavity_volume_cc` 67.9). `earpad_depth 24` (pad mockup
  Z-scaled). New gate checks `front-seal-squeeze` + `closed-back-ports-clear`; vent_plug in manifold.
  Build 17/17, gate 0/0. Parked: gasket/damping in the assembly VIZ; real vent open-area vs a REW sweep.
- [~] **5. Head models S/M/L + sprung bow + slider range.** DONE: three toggleable reference heads
  (S/M/L, uniform-scaled, ears aligned; `head_ref_s/m/l` — 3 viewer toggles, off by default); sprung-bow
  helper `bow_radius_for_ear_half` (conserves developed length, `bow_worn_radius_s/l`); viewer/render
  renames handled. Build 17/17, gate 0/0. **REMAINING (the actual blocker fix, scoped follow-up):** the
  bow apex floats ~34 mm above the crown and that exceeds the 32 mm slider travel — the yoke+post stack is
  ~2 cm too TALL. Trim `yoke_fork_height`/post ~20 mm + map slider travel S↔L (full extension = largest)
  so the band lands. The 3 heads now make the gap visible to calibrate against. (Its own careful pass —
  ripples through yoke geometry + gate + renders.)
- [~] **6. Assembly sequence + explode refinement.** DONE: wrote **`docs/ASSEMBLY.md`** — the full
  ordered build (Stage 0 heat-sets → driver+gasket+clamp → baffle+damping into cup → pivot
  **washer-stack** `[head|wave|nylon|eye|nylon|boss]` → shoe-before-post → post/slider/knob → band
  sandwich → finish), grounded in the real interfaces + BOM part numbers, and named as the explode's
  intended step order. **REMAINING (viz polish, scoped):** (a) draw the pivot washer stack in the
  assembly render (currently insert+screw only — "a manual nicety", DESIGN-LOG); (b) refine the
  explode tool to step through the ASSEMBLY.md stages in order + clamp offsets so parts stay in frame
  (the doc now defines the order to follow). Both iterative "as we go" per the maker.

## Parking lot (revisit)

- **Worn-fit RE-POSE (head-driven, per head) — the next focused build.** Head + ears DONE (live);
  the fit is diagnosed (see DESIGN-LOG 2026-06-28): earpad buried ~24 mm (modeled uncompressed +
  bow-driven cup spacing too narrow), band doesn't flex (vertical-only auto-fit). FIX: re-derive the
  worn pose head-driven — head ear → compressed worn-earpad (~12 mm) flush → cup position → bow flexes
  (`bow_radius_for_ear_half`) to span → band height to crown; per head; then the viewer re-poses on
  selection (swap a pre-flexed bow + per-head transforms, or per-head GLBs). Also: optionally make the
  KU100 face a touch more defined; the current nose/brow are subtle.

- ~~Worn-fit STACK TRIM~~ **BAND-FLOAT RESOLVED 2026-06-27 — it was the head model + pose, not the
  stack.** The ovoid had the ear at its centre (ear→crown 114, ~15 mm short) and the slider was posed
  mid-travel. Fixed: `head_ref_height_half 121` + `head_ref_z 8` (ear→crown 129, S/M/L 123/129/135) and
  `assembly_worn_slider_frac 0.9` (near-retracted = average head; big cup forces the block high). The
  stock 9.3″ Beyer bow now LANDS (pad contacts the M crown). Stack trim NOT needed. *Optional minor
  polish remaining:* the post travel is biased to the retracted end (average ≈ near-retracted) — a small
  post/fork trim could centre it so M sits mid-travel, but it's cosmetic, not a blocker.
- **Assembly viz polish** — (a) draw the pivot washer stack `[head|wave|nylon|eye|nylon|boss]` in the
  render (assembly.py currently shows insert+screw only); (b) refine the explode tool to step through
  the `ASSEMBLY.md` stages in order and clamp the per-part offsets so nothing flies out of frame.
- **Full design-spec refresh (website `.mdx` + local `design-spec.md`)** — both still describe the
  pre-bow "spring-steel-arc" architecture, the old pivot, Dekoni-default pads. Item 3 fixed only the
  actively-wrong facts (143 cc, pad default) + a status note. Do the full v0.4 reconciliation AFTER
  items 4-5 land (acoustics + headband), so it's rewritten once, not three times.
- Print-verify everything (printer pending) — coupons first, then one full cup + a baseline REW sweep.
- Kingstate driver specs — measure when bench-testing.
- Dekoni pads — incoming; premium/tuning alternative.
- After v1.0 lock: stop the beta↔current auto-sync (see `website-publish-channels` memory).
