# Print guide — Daily Driver (first-prototype)

The parts build 8/8 and pass the gate (0 HARD), so they're geometrically printable.
This is the how-to-print layer: orientation, supports, material, and the order to
print so the **first set is a measurement jig**, not a finished product — several
dimensions are still `ESTIMATE`/`TBD` pending the Tier-1 measurements
(`measurement-priorities.md`).

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
| Inserts | M3 brass heat-set | bores are sized for them — install with a soldering iron |

## Per-part orientation + supports

| Part | Orient | Supports | Notes |
|---|---|---|---|
| **baffle** | flat, **back face down** | none | guard spokes bridge fine; counterbores face up (heads hide under the pad) |
| **cup** | **back/grille down**, axis vertical | **yes** — the 2 pivot bosses (radial overhangs) + a touch under the front flange | brim on a brim if the grille lifts; the rounded back edge prints clean on the bed |
| **yoke** | **flat in its plane** (bracket lying on the bed) | minimal (under the eyes if needed) | flat bracket = easy print. **Post-process:** the cross-section edges are square (kernel can't round them yet) — a quick sand softens them, or wait for the build123d port |
| **slider** | **swivel-bore axis vertical**, seat pocket facing sideways | light, in the swivel bore mouth | rounded block, mostly self-supporting; mount bores print across the seat floor |
| **grille_dot** | flat, proud face up | none | press-in accent cap |
| **headband_pad** | arch on its side or flat | light at the arch ends | **TPU**; rough draft — expect to iterate |
| **adapter_ring** | flat | none | accessory (only if stepping a smaller driver) |
| **bow** | — | — | **NOT printed** — bought Beyer metal bow or a DIY laser-cut/water-jet 1095 spring-steel blank to the modelled geometry |

## First-prototype order

1. **Baffle** + seat the real driver → confirm `driver_od`, aperture, recess. Measure.
2. **Cup** (one) → check the pivot bosses, the grille, and that your **earpad's mount
   skirt** actually grips the front flange. Measure the pad mount Ø → set
   `cup_outer_diameter`. (This is the Tier-1 number that moves everything.)
3. **Yoke + slider + hardware** → dry-fit the pivot (M3 shoulder screw + inserts) and
   the tilt range; confirm the over-rotation stop.
4. **Bow** (bought/cut) → measure relaxed radius + rolled-out length → set the bow
   params; check ear spacing on a head.
5. Re-build with the measured numbers → re-gate → reprint the parts that moved.

## Post-processing checklist

- [ ] Heat-set M3 inserts into the cup pivot bosses + baffle bosses + slider mount.
- [ ] Sand the yoke edges if you want the soft feel now (kernel limitation logged).
- [ ] Light chamfer/clean on the earpad flange so the skirt slips on.
- [ ] Note every real measurement back into `params.py` (overwrites the ESTIMATE),
      then **rebuild → gate → DESIGN-LOG → commit → push**.

## What's still TBD before a "final" (not prototype) print

From the DESIGN-LOG: the earpad mount Ø (→ cup OD), the bow geometry (→ ear spacing),
the driver OD, and the lip extension/thickness. The first prototype exists to nail
these — see `measurement-priorities.md` for which block printing vs which can wait.
