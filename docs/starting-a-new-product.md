# Starting a new product (the template)

The "template" for product #2+ is **this repo** — fork it copy-on-write. There is no
separate skeleton to maintain (a parallel skeleton drifts from the live code; a fork
is always current). The value here is the **checklist of what to change**, so a new
product starts clean instead of half-edited.

> Hold until product #2 is actually greenlit. When it is, this is the cold-start.

## 1. Fork

```bash
cp -r builds/daily-driver builds/<new-product>        # copy-on-write from the reference
cd builds/<new-product>
rm -rf .git && git init                               # its own standalone repo (like daily-driver)
rm -rf docs/DESIGN-LOG.md output/ docs/models/ docs/renders/   # start a fresh log + artifacts
```

Then run **`/headphone-intake`** → fill `BRIEF.md` → translate the brief into
`params.py`. See `new-build-intake.md` (pipeline), `decision-tree.md` (the order),
`measurement-priorities.md` (what blocks the first print).

## 2. Reset product-TASTE params, keep ARCHITECTURE params

`params.py` is ~60% reusable architecture, ~40% product taste. Reset the taste to
the new brief; leave the architecture unless the brief changes it.

| Keep (architecture / convention) | Reset to the new brief (taste / fit) |
|---|---|
| insert/screw dims, `m3_*`, `heatset_*` | `driver_od`, aperture/recess rules |
| structural floors (`wall_thickness*`) | `cup_interior_diameter`, `cup_outer_diameter` |
| pivot/insert mechanics, `pivot_boss_*` | `pad_*` (the earpad + lip) |
| gate thresholds (mostly) | `bow_*` (the chosen band) |
| the build→gate→log ritual | grille pattern, accents, `*_fillet`, signature |
| | `yoke_*`, `slider_*` if the mechanism changes |

Every dimension stays in `params.py` (single source of truth); parts stay
independently buildable.

## 3. The cross-cutting things that bite if you forget them

These live outside `params.py` and won't error — they just come out wrong:

- [ ] **`assembly.py` → `SUBASSEMBLIES`** — the node names (`cup_R`, `baffle_L`, …)
      are a public contract for the manual's parts viewer. Keep them or update the
      viewer's manifest to match.
- [ ] **`build.py` → `PRINTED` / `ACCESSORY` / `REFERENCE` sets** — re-classify any
      added/removed parts so the STL/STEP/render outputs are right.
- [ ] **`assembly.py` transforms** — if the cup/pad/mechanism orientation changes,
      the worn-pose transforms (`T_cup`, `T_yoke`, mirror) need re-deriving.
- [ ] **`bom.py`** — swap the driver / pad / bow rows + sources to the new brief.
- [ ] **GLB / Pages** — if the new product gets a web preview, wire its GitHub Pages
      `/docs` the same way (CORS `*`), and point the manual at the new origin.
- [ ] **README + license** — restate scope; confirm the prior-art boundary (credit
      adopted ideas; never copy non-permissive files/geometry).

## 4. First build

`python build.py` (N/N) → `python gate.py` (0 HARD) → first DESIGN-LOG entry →
commit → **push**. Treat the first print as a measurement jig for the Tier-1
unknowns (`measurement-priorities.md`).

## When to extract a real code skeleton

After product #2 ships, you'll know what's *truly* reusable (vs Daily-Driver-
specific). That's the moment to lift the shared architecture into a `platform/`
base + a `parts/primitives/` library and turn this fork-guide into a thin skeleton.
Doing it now — from a sample size of one, mid-WIP — would just bake in guesses.
