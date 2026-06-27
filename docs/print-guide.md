# Print guide — Daily Driver (DRAFT — NOT print-ready)

> ⚠️ **The Daily Driver is not ready to print or assemble.** All parts *build*
> green (see `PARTS.md`) and pass the *printability* linter (0 HARD), but that's a low bar — the
> DESIGN still needs significant work before a print-and-assemble: measurements,
> fit, acoustics, mechanism detail, the soft yoke, the headband pad, and the
> tweaks the maker is carrying (see "What's still open" below + the DESIGN-LOG).
> This file is a **forward reference** for when it gets there, not a green light.

When the design IS ready, this is the how-to-print layer — orientation, supports,
material, and order. Even the earliest useful step (a baffle to check a driver) is
gated on settling more than is settled today.

> STLs export to `output/` (gitignored) via `python build.py`; they ship to builders
> through tagged GitHub Releases, not the tree. STEP is exported alongside for
> editing elsewhere.

## Print the BAFFLE first (against a real driver)

Per the build's golden rule: **print the baffle alone, first, and seat your actual
driver in it** before committing to the rest. It's flat and fast, and it validates
`driver_od` / aperture / recess — the cheapest way to catch the #1 first-print risk.

## Baseline settings (tune to your printer)

| Setting | Start at | Why |
|---|---|---|
| Material | **PETG** (cups/yoke/slider), **TPU** (headband pad) | PETG = tough + a little flex for the snap/lip; TPU for the cushion |
| Layer height | 0.2 mm (0.16 for the grille/flange) | finer on thin features |
| Walls / perimeters | 4 (≥ the 3 mm design wall) | strength; the structural floor is 4 mm |
| Infill | 30–40 % gyroid | cups/yoke see real load |
| Inserts | M3 / M5 / 8-32 brass heat-set | bores are sized for them — install with a soldering iron (exact part #s in `BOM.md`) |

## Per-part orientation + supports

| Part | Orient | Supports | Notes |
|---|---|---|---|
| **baffle** | flat, **back face down** | none | guard spokes bridge fine; counterbores face up (heads hide under the pad) |
| **cup** | **back/grille down**, axis vertical | **yes** — the 2 pivot bosses (radial overhangs) + a touch under the front flange | brim on a brim if the grille lifts; the rounded back edge prints clean on the bed |
| **yoke** | **flat in its plane** (bracket lying on the bed) | minimal (under the eyes if needed) | flat bracket = easy print. **Post-process:** the cross-section edges are square (kernel can't round them yet) — a quick sand softens them, or wait for the build123d port |
| **slider** | **post-bore axis vertical**, lozenge + thumbscrew boss facing sideways | light, in the post-bore mouth | rounded lozenge, mostly self-supporting; the shoe pocket + 8-32 boss bore print across the +Y face |
| **slider_shoe** | **saddle axis vertical** (concave face sideways) | none | tiny — print a few spares; drops into the slider pocket through the bore |
| **driver_clamp** | flat, ring face down | none | 3 ears; the M3 clamp holes + standoff bosses face up |
| **headband_clamp** | flat, plate face down | none | small inner cover; the rib slot faces up |
| **grille_dot** | flat, proud face up | none | press-in accent cap |
| **headband_pad** | arch on its side or flat | light at the arch ends | **TPU**; rough draft — expect to iterate |
| **adapter_ring** | flat | none | accessory (only if stepping a smaller driver) |
| **driver_coupon / pad_coupon** | as the part each validates (baffle-back / cup front down) | as that part | **QA fit coupons** — print these *first* against your real driver + pad |
| **bow** | — | — | **NOT printed** — bought Beyer metal bow (917017/973361) or a DIY laser-cut/water-jet 1095 spring-steel blank to the modelled geometry |

## First-prototype order

1. **Baffle** + seat the real driver → confirm `driver_od`, aperture, recess. Measure.
2. **Cup** (one) → check the pivot bosses, the grille, and that your **earpad's mount
   skirt** actually grips the front flange. Measure the pad mount Ø → set
   `cup_outer_diameter`. (This is the Tier-1 number that moves everything.)
3. **Yoke + slider + hardware** → dry-fit the pivot (M3 shoulder screw + inserts) and
   the **free tilt range** (Grado-style — no over-rotation stop), and the post + 8-32
   knob → shoe height lock.
4. **Bow** (bought/cut) → measure relaxed radius + rolled-out length → set the bow
   params; check ear spacing on a head.
5. Re-build with the measured numbers → re-gate → reprint the parts that moved.

## Post-processing checklist

- [ ] Heat-set inserts: **M3** (cup pivot + baffle + driver-clamp bosses), **M5** (fork → post
      shoulder screw), **8-32** (slider knob). Part #s in `BOM.md`.
- [ ] Sand the yoke edges if you want the soft feel now (kernel limitation logged).
- [ ] Light chamfer/clean on the earpad flange so the skirt slips on.
- [ ] Note every real measurement back into `params.py` (overwrites the ESTIMATE),
      then **rebuild → gate → DESIGN-LOG → commit → push**.

## What's still open (why this isn't print-ready)

A design in progress, not a finished product. Known work before a real
print-and-assemble — and the maker is carrying more:

- **Measurements** — pad mount Ø (→ cup OD), bow geometry (→ fit), driver OD: all
  still `ESTIMATE`/`TBD`.
- **Earpad lip** — extension/thickness provisional (5 mm reaches ⌀100 = pad foam);
  resize once the real pad groove is measured.
- **Fit** — worn ear spacing / clamp / tilt unverified on a head.
- **Acoustics** — driver choice (40 vs 50), damping, vent open-area: nothing tuned
  or measured.
- **Yoke** — stays a flat bracket; the soft round version waits on the build123d port.
- **Headband pad** — explicitly a rough draft.
- **Mechanism detail** — slider bolt-on + bow end-tab hole specs need calipers + a
  real hardware fit.
- **Driver dome excursion** — still an `ESTIMATE`; the guard↔dome clearance gate check stays
  SOFT until it's measured on the real Kingstate driver (then it promotes to HARD).
- **…and the maker's tweak list** — the items that prompted this note.

See `measurement-priorities.md` for the measurement order once we're closer.
