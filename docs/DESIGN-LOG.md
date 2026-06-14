# Daily Driver — Design Log

For an open design, the log *is* part of the product. Every decision, every
measurement, every iteration goes here so anyone can follow the reasoning, not
just the result. Newest entries at the top.

---

## 2026-06-14 — Concepts moved to a 3D-printed maker direction

Retuned `VISUAL_DESCRIPTORS` (a human taste call, encoded as written) to aim the
concept exploration at a **high-quality 3D-printed object** — precisely printed
and well-finished, explicitly neither injection-molded polish nor a crude
prototype. Print quality is expressed positively (clean, precise, even,
well-finished); no negative prompt.

- **Printed-maker surface + form.** Matte charcoal printed parts with a fine,
  even, intentional printed texture (described as fine-layer sintered nylon, not
  by acronym); designed-for-print cues: generous fillets, chamfered edges,
  uniform walls, monolithic forms.
- **Architecture cues.** A slim **exposed spring-steel metal band** anchored into
  printed sliders (bright metal contrasting the matte printed parts); **printed**
  yoke/gimbal arms with rounded filleted edges and visible pivot screws (not thin
  wire, not a blocky molded gimbal); maker/serviceable detail — exposed stainless
  socket-head fasteners, brass heat-set inserts, intentional seams, openable.
- **Grille tuning.** Open back is a printed spoked concentric grille: central hub
  + two **bold concentric rings** joined by a **small number of thick radial
  spokes**, coarse/open enough to see the driver — explicitly not a fine
  turbine/fan.
- **Orange restraint.** Matte charcoal throughout with a **single small**
  warm-orange accent (grille hub or a small yoke tag); never painted across whole
  parts.

Ran one default Stage-1 set (4 images) into gitignored `design/_scratch/`. Reads
clearly printed-maker now (matte, filleted, monolithic, visible fasteners), a
strong shift away from the molded-consumer look. Partial on the finer asks: the
grille landed as concentric rings on most views but still drifted to a fine
turbine on one, the spring-steel band read matte rather than bright metal, and
one cup's pad interior came through fully orange. Useful steer for the next
iteration; left in scratch for me to curate.

---

## 2026-06-14 — Open-back descriptor tuning; scripts now default to _scratch

Two refinements to Stage 1 after the first run read **closed-back**.

- **Open-back is now described, not named.** "Open-back" is category jargon, not
  an appearance, so the model rendered a solid shell. `VISUAL_DESCRIPTORS` now
  spells out the visual signature (a human taste call, encoded as written — not
  reinterpreted): the entire rear of each cup is an open metal grille with the
  driver visible behind it; a spoked concentric grille (center hub, two rings,
  radial spokes, echoing the brand mark); see-through and airy; matte charcoal
  with a single warm-orange accent and visible fasteners. The words "open-back"
  stay, paired with the look.
- **Camera view is varied across the N images.** A front-only batch reads closed
  regardless of wording, so `gen_concepts.py` now makes one call per image and
  cycles a `VIEWS` list (rear / front / side) with the **rear/grille view first
  so it's always present**. No negative prompt — FLUX.1 [dev] doesn't reward
  negation; concrete positive description is the lever. Re-ran (4 images): both
  rear views now read clearly open-back.
- **Scripts default to `_scratch`; curation is manual.** Reconciled the code with
  the scratch-vs-curated convention: `gen_concepts.py` and `gen_reference_mesh.py`
  now always write raw runs to gitignored `design/_scratch/<timestamp>/`. The
  `--curated` flag is gone — promoting keepers into `design/explorations/` and
  `design/reference-meshes/` is a manual curation step. Doc layout/how-to-run
  lines updated to match. The earlier `explorations/2026-06-13T214426Z/` run is
  left in place as history.

---

## 2026-06-13 — AI-assisted design pipeline set up (FAL Stages 1 & 2)

Stood up the AI design pipeline that feeds the form pass. It generates **options
and references** — it never produces engineered CAD.

- **Toolchain.** Official FAL Python client (`fal-client`, import `fal_client`,
  reads `FAL_KEY`) confirmed from fal.ai docs and pinned in `requirements.txt`.
  `FAL_KEY` lives in a gitignored `.env`; the key is never committed. Smoke test
  (`pipeline/smoke_test.py`, one minimal `flux/schnell` call) passed — auth +
  connectivity good.
- **Scripts (config-driven, swappable models).** All under `pipeline/`:
  `config.py` is the single place model slugs, output dirs, counts, and seed
  handling live — swapping a model is a one-line edit. `gen_concepts.py`
  (Stage 1) and `gen_reference_mesh.py` (Stage 2) read everything from it.
  Confirmed current slugs: Stage 1 default `fal-ai/flux/dev` (FLUX.1 [dev]);
  Stage 2 default `fal-ai/trellis` (~$0.02/call). Hunyuan3D and FLUX.2 noted as
  documented swap-ins.
- **Stage 1 verified.** Ran one curated generation (3 images, `flux/dev`) →
  `design/explorations/2026-06-13T214426Z/` with a manifest (prompt, model,
  resolved seed, brief hash). Output is on-brief (charcoal + orange, modular).
  Prompts are built from a **curated visual-descriptor template**, not a raw
  dump of the brief.

### The boundary this pipeline encodes

- **No render → engineered-CAD step.** Meshes (Stage 2) are triangle soup, not
  B-rep; and engineered features (screw locations, cup depth, vent area) are
  decisions and measurements, not pixels. Stage 3 — the real parts — is authored
  by hand in CadQuery, on purpose.
- **Taste is human, encoded in code.** Some taste is a number (→ `params.py`),
  some is form (vent shape, grille, cup profile → parametric geometry in
  `parts/*.py`). AI informs taste by showing options; it never sets a dimension
  or authors a part.
- **Convention is reused, not regenerated.** Mechanical primitives (boss, post,
  fillet, thread, snap) live in `parts/features.py`, authored once from
  established practice and reused across parts.
- **Scratch vs. curated.** Raw bulk runs go to gitignored `design/_scratch/`;
  only curated picks land in `design/explorations/` and
  `design/reference-meshes/` and get committed (the open-design story).

### Carry-forward

- **Migrate primitives into `parts/features.py`.** `features.py` is a stub
  (signatures only). `cup.py` step 3 still inlines its baffle-mounting boss +
  insert-bore logic; that convention should move into `features.py` and be
  reused once the primitives are implemented. Not done now (no refactor this
  session) — flagged for a future step. Joins the earlier carry-forwards
  (floating baffle bosses, first-pass vent grille).

---

## 2026-06-13 — Entering the form / industrial-design pass

The functional skeleton is proven — parametric CAD, build pipeline, four parts
exporting as valid solids — so the next pass is **form**. Added
`docs/industrial-design-brief.md`, built from the spec's locked-vs-open section:
it defines what the Daily Driver should look and feel like and frames the form
exploration (cup profile, rear grille, yoke/slider styling, finish) as 3–5
directions to choose from before any more geometry work. The chosen direction
then gets translated back into the parametric model, respecting everything the
brief locks.

**Carry-forward issues to fix when the chosen form goes back into the model**
(noting now so they aren't lost — not fixing here, no geometry changes this
session):

1. **Floating baffle bosses.** The four baffle-mounting bosses are currently
   posts that aren't anchored to the cup wall — they need to tie into the wall
   when the form is rebuilt.
2. **Clunky first-pass vent grille.** The rear vent array is the crude
   area-driven placeholder; the real grille is a form decision (it's the
   signature look) and gets designed in this pass.

---

## 2026-06-13 — First build runs; all four parts export; cup fillet was masking a failure

First time the toolchain ran against the geometry kernel. Set up a venv and
installed CadQuery, then ran `python build.py`.

- **Environment.** Only system Python (3.9.6) is available on this machine — no
  3.10–3.12 as the requirements note prefers. Tried 3.9 anyway since it's the
  empirical path, and it worked: `pip install -r requirements.txt` pulled
  **CadQuery 2.5.2** with **cadquery-ocp 7.7.2** (3.9 wheels exist), and import
  succeeded. No newer Python needed for now.
- **Result.** All four parts export to both STL and STEP, and all four are valid
  solids (`isValid() == True`): cup (65 faces), baffle (13), yoke (9, stub),
  slider (13, stub). The two flagged trouble spots that *did* hold up:
  - **Cup front-face shell** (`faces(">Z").shell(-wall_thickness)`) — works,
    clean open cup.
  - **Side yoke boss** (`Workplane("XZ")` boss union) — works, unions cleanly.
- **The real problem: the cup edge fillet was failing silently.** Step 6
  (`cup.edges("|Z").fillet(edge_fillet)`) raises `BRep_API: command not done`
  every run, and the old `except: pass` swallowed it — so the build printed
  `[ok]` while shipping a cup with **no fillet applied**. Diagnosed why:
  `"|Z"` selects all 51 vertical edges, but ~32 of those are the **vent-slot
  walls** and the rest are boss edges. A 1.5 mm fillet overruns the slot
  geometry and OCC aborts the whole operation. Scoping to the outer wall doesn't
  rescue it either — the cup is a **cylinder**, so its only outer vertical edges
  are the yoke-boss/cylinder intersection (a curved-on-curved saddle), which OCC
  refuses to fillet even at 0.5 mm.
- **Conclusion (not silently resolved).** A cylindrical first-pass form has no
  sharp outer vertical edges worth softening. **Which edges get a comfort fillet
  is a form-pass decision** that depends on the real outer profile — and the
  outer profile is an explicitly OPEN form question in the spec. So I did *not*
  invent a new filleting scheme.
- **Fix applied (cup.py step 6).** Scoped the fillet to the outer wall only (so
  it stops trying to fillet the vent slots — that was never the intent), and
  replaced the silent `except: pass` with a printed `[warn]` so a skipped fillet
  is **visible in the build**, not hidden behind `[ok]`. `edge_fillet` stays in
  `params.py`, flagged; the fillet activates once the form pass gives the cup
  real edges to soften. Build now reports the skip honestly and still produces
  all four valid solids.

### Repo location

The CAD repo now lives at `builds/daily-driver/` inside the MakerPhones working
tree (it had been dropped at the wrong path). It remains its own standalone git
repo (`github.com/makerphones/daily-driver`); the website repo gitignores
`builds/` so the two stay cleanly decoupled. Room for sibling builds later.

### Next

- Open `output/cup.stl` and `output/baffle.stl` in a viewer and sanity-check
  proportions (human review — not assessed here).
- Print the **baffle first** (flat, fast) against a real driver to confirm the
  cutout, seat, and gasket channel before committing a cup print.
- When the cup's outer **form pass** happens, decide which edges the comfort
  fillet should soften — the `[warn]` will clear once it has real edges.
- Stubs still TODO: `yoke` real gimbal geometry + cup-side mount, `slider`
  friction clamp — both gated on open questions (yoke-to-cup interface, headband
  arc radius).

---

## 2026-06-13 — Switched to a single MIT license

Replaced the split CERN-OHL-P-2.0 (source) + CC-BY-4.0 (docs) setup with one
**MIT** license over the whole repo.

- **Why MIT.** Simplicity — one short, universally understood license instead
  of two, and it's code-native, which fits a design that's *defined in code*
  rather than shipped as discrete hardware files.
- **Why permissive.** The whole point is for the design to spread — get used,
  forked, built, and sold freely. There's no moat here to defend with copyleft
  or a non-commercial clause.
- **Where the value actually lives.** Kits (sourced, matched parts in a box), a
  finished Warren Labs product for people who don't want to build, and merch.
  None of those depend on the design being closed — a published model doesn't
  make the kit or the assembled unit any less worth buying.
- **What stays protected.** The makerphones and Warren Labs *names and brands*
  are held back by trademark, separately from the code license. Anyone can build
  and sell the design; nobody can sell it *as* makerphones.

---

## 2026-06-13 — Licensed open, permissive with attribution

Picked the licenses and made the repo properly open.

- **Source / design files:** CERN-OHL-P-2.0 (CERN Open Hardware Licence v2,
  Permissive). **Docs** (spec, this log, README prose): CC-BY-4.0. SPDX headers
  on every `.py`; `LICENSE` + `LICENSE-docs` carry the full legal text.
- **Why permissive.** The whole point is for the design to spread — get built,
  forked, remixed, sold by whoever wants to. A copyleft or non-commercial clause
  would slow that down to protect a moat that isn't there. The design being open
  costs nothing, because the commercial value doesn't live in the geometry.
- **Where the value actually lives.** Kits (sourced, matched parts in a box), a
  finished Warren Labs product for people who don't want to build, and merch.
  None of those depend on the CAD being secret — a published STL doesn't make
  the kit or the assembled unit any less worth buying.
- **What stays protected.** The MakerPhones and Warren Labs *names and brands*
  are held back by trademark, separately from the design license. Anyone can
  build and sell the design; nobody can sell it *as* MakerPhones. Open design,
  protected brand — the two don't conflict.

---

## 2026-06-13 — Repo scaffolded, code-CAD toolchain chosen

Moved the Daily Driver from spec-only into a parametric CAD repo.

- **Toolchain:** CadQuery (code-based, B-rep, exports STL + STEP). Chosen over
  Fusion/MCP for this project specifically because the files are text — they
  version-control and diff naturally, and anyone can fork and modify. Trade-off
  (known going in): weaker at taste-driven surfaces and complex fillets than a
  GUI. Those get handled in the form pass; functional geometry lives in code.
- **Structure:** `params.py` is the single source of truth; one file per part
  in `parts/`; each part builds independently (matches the spec's modular,
  independently-iterable interface goal).
- **State:** `cup` and `baffle` are real first-pass geometry. `yoke` and
  `slider` are wired stubs (parameters exercised, real geometry TODO).

### Open questions carried from the spec (do NOT silently resolve)

1. **Pad lip vs. cup interior.** `pad_lip_od` = 62 sits well inside
   `cup_interior_diameter` = 78. The spec lists both but doesn't fully say
   where the lip lives — a raised ring on the cup front, or a feature of the
   baffle. Resolve cup + baffle together. Confirm HM5 inner-ring dia with
   calipers first.
2. **Baffle screw direction.** Current model puts heat-set inserts in the cup
   bosses and clearance holes in the baffle (screw from the front, into the
   cup). Spec lists "insert placement" under the baffle, which could mean the
   reverse. Pick one, note it here.
3. **Yoke-to-cup attachment.** Not specified. The cup currently has a
   placeholder boss on the +X side. Design the yoke and the cup mount together.
4. **Headband arc radius.** Spec's own open question — print jigs at 95/105/115
   mm inside radius, form blanks, test clamping force across head sizes before
   committing. Drives the slider and the whole fit.
5. **Production driver.** Baffle is parametric so the driver locks late. Update
   `driver_od` / `driver_aperture` in `params.py` once a specific driver with
   published measurements is chosen.
6. **Vent open area.** The rear vent slots are sized toward ~40% open with a
   crude area calc and a fixed 5 mm slot width. Exact open area + slot shape is
   both an acoustic tuning lever and the signature look — iterate by eye and by
   measurement.

### Next

- Run `python build.py` on the machine, open `output/cup.stl` and
  `output/baffle.stl` in a slicer/viewer, sanity-check proportions.
- Print the baffle first (flat, fast) against a real driver to confirm the
  cutout, seat, and gasket channel before committing a cup print.
