# Daily Driver — Design Log

For an open design, the log *is* part of the product. Every decision, every
measurement, every iteration goes here so anyone can follow the reasoning, not
just the result. Newest entries at the top.

---

## 2026-06-14 — Engineering pass: CAD reconciled to v0.3, all parts authored

Full engineering pass — the CAD now matches the v0.3 spec and every part has real
geometry. We are **not** waiting on measured parts: every dimension is an
ESTIMATE flagged in `params.py` (with `REF` for bought-part references and `TODO`
for genuine unknowns) so a measured value overwrites cleanly later. Worked part
by part, building and verifying after each; `python build.py` is green
(cup/baffle/yoke/slider STL+STEP, bow STEP-only reference, + assembly).

- **params.py** reorganised to the v0.3 stack with an explicit ESTIMATE policy
  banner. Grille **decoupled** from the bosses (its own `grille_outer_ring_radius`);
  bolt circle is now explicit (`baffle_bolt_circle_diameter=70`), not a fraction.
- **Cup.** Bosses moved OFF the grille and BLENDED into the perimeter wall
  (`baffle_boss_diameter=10` so each reaches the inner wall at the bolt circle and
  merges). Grille cleaned (hub 16 / rings 24+32 / 8 spokes). Two **pivot bosses**
  added at 0/180 on the side walls (mid-height), each a through-wall radial boss
  housing an M3 heat-set insert for the fork shoulder screw. Verified: single
  connected solid; **measured open fraction 0.398** (target 0.40).
  - *Deviation flagged:* spec listed `member_w=3`, but at the new ring radii 3.0
    gives 0.51 open. Tuned to **4.0** to hit the 0.40 target (still ≫ 2 mm floor),
    per the standing "size member width to the open-area target" rule. Documented
    in `params.py`, not silently changed.
- **Baffle.** Front-mount plate (od 77, th 4): back driver recess (42×3), raised
  front pad lip (od 62, h 3.5), 4 M3 holes counterbored from the front, controlled
  vent holes. Integral driver guard (6 spokes, 2 mm) across the aperture.
  - *Conflict flagged (not forced):* recess 3 of a 4 mm plate leaves only a ~1 mm
    front lamina — the only solid the guard can anchor to — so the requested
    1.5 mm guard setback can't fit. The guard seats in the lamina and the build
    **warns**; TODO to deepen the plate or shallow the recess once the driver is
    measured. The REF dome-proud vs recess-depth also suggests a dome/guard
    clearance check — flagged in `baffle.py`.
- **Fork-yoke.** DT880 wishbone: two arms from a top swivel hub (vertical bore,
  mates the slider) down to two pivot eyes (M3 clearance) at `yoke_pivot_centres`.
  Arms routed vertically past the cup then angled in — a straight eye→hub bar would
  pass through the cup. TODO: ±tilt clearance against the real cup pose.
- **Slider.** Clamp block with a vertical bow channel, a bottom swivel bore
  (mates the fork hub), and an M3 grub boss pressing a friction pad onto the bow.
- **Bow (REFERENCE only).** Bought Beyer / DIY 1095 — modelled as a reference
  body (arc band + relief slot + end-tab holes), STEP only, excluded from the
  printed-STL set. NOTE: this OCP build's `revolve` fails outright (`BRep_API:
  command not done`) even on a textbook offset revolve — built the band from
  **extruded annular sectors** instead. Bow dims are TBD from the measured part.
- **assembly.py / build.py / show.py.** Assembly now poses the full one-side chain
  (cup → baffle → yoke → slider → bow ref); the bow pose is representative
  (full head-size kinematics TBD). build.py splits PRINTED (STL+STEP) from
  REFERENCE (STEP only). Assembly loads and exports (5 parts).

Carried-forward `[warn]`s unchanged: cup outer-edge comfort fillet (no-op on the
cylinder) and the yoke junction fillet (OCC declines it) — both best-effort and
caught, geometry is unaffected.

---

## 2026-06-14 — Off EOL Python 3.9 → 3.13; stack updated; ocp_vscode matches the extension

Moved the repo's environment off end-of-life Python 3.9 (EOL Oct 2025) to
**Python 3.13.14**, and updated the CAD stack to match the installed OCP CAD
Viewer extension (3.4.0) — chosen over downgrading the extension now that we're
on a current Python.

- **Why 3.13.** Newest Python with prebuilt macOS-arm64 wheels across the whole
  stack: `cadquery-ocp` ships arm64 wheels for cp310–cp313 (no cp314 yet), so
  3.13 is the ceiling. `ocp_vscode` 3.4.0 and `cadquery` 2.7.0 both need >=3.10.
- **Interpreter source.** The Homebrew `python@3.13` bottle was unusable on
  macOS 26.2 — its `pyexpat` failed to load (`Symbol not found:
  _XML_SetAllocTrackerActivationThreshold` vs the system libexpat), which breaks
  pip bootstrap. Switched to the **python.org 3.13.14 universal2 installer**
  (`/Library/Frameworks/Python.framework/Versions/3.13`), which bundles its own
  libexpat — `pyexpat`/pip/ssl all clean.
- **New stack.** Python 3.13.14 · CadQuery **2.7.0** · cadquery-ocp
  **7.8.1.1.post1** · ocp_vscode **3.4.0** (matches the 3.4.0 extension —
  resolves the viewer mismatch by upgrading) · fal-client 1.0.0.
- **Verified.** `build.py` exports all four parts + assembly.step on 3.13 (same
  pre-existing fillet [warn]s, unchanged). `show.py` now gets past port discovery
  ("Using port 3939") with no TypeError and no `find_port()` ValueError — the
  3.4.0 package fixed that; full connect just needs the live panel.
- **Env swap.** New env built at `.venv-new`, then swapped into `.venv` (the path
  VS Code points at) with relocated script paths fixed; the old 3.9 env is kept
  as `.venv-old` (backup, not deleted until confirmed working).
- **Pins.** `requirements.txt` → `cadquery>=2.7,<2.8`; `requirements-dev.txt` →
  `ocp_vscode==3.4.0`. Both verified to resolve against the new env with no
  changes needed.

---

## 2026-06-14 — Direction locked: DT880-family, around-ear (docs-only pass)

Settled the Daily Driver's direction and rewrote the spec to match — **docs only, no CAD/geometry
touched** (no `params.py`, no `parts/*.py`). The form is the **Beyerdynamic DT880 family**:
spring-steel **bow** → printed **slider** (height + swivel) → printed **fork-yoke** (±20° tilt) →
printed **cup** → printed **baffle** → driver → pad. Explicitly **not** Grado-minimal (on-ear,
too small/fiddly) and **not** DCA thin-metal (only makes sense in metal fab, not FDM).

Resolved decisions captured in `design-spec.md` (→ **v0.3**):

- **Headband.** Design the slider/mount to accept the **Beyerdynamic Metal Head Bow as a drop-in**
  (~$11, sourced); DIY 1095 spring steel to the same geometry stays as the maker option. Exact bow
  dims are **TBD from the measured part** — slider + jig geometry derive from a real bow on the bench.
- **Pivot (yoke↔cup).** **Screw-pin** — M3 shoulder screw through the fork arm into a heat-set
  insert in the cup. **Supersedes** the old "project's own 6 mm pivot post" interface.
- **Baffle.** **Front-mount** plate (OD ~77, ~4 mm); **integral raised pad lip ⌀62** (pad-lip
  location now resolved to the baffle, not the cup); **⌀35 aperture with an integral printed driver
  guard**; **⌀42 driver pocket** on the back; 4 M3 rim screws **counterbored from the front, hidden
  under the pad**; controlled venting + a damping spot, **not a hard seal**.
- **Cup.** Shell + integral grille (hub + 2 rings + 8 spokes, ~40% open, members ≥ 2 mm). The 4 M3
  bosses move to **blended-into-the-perimeter-wall**, clocked off the pivot axis — **supersedes** the
  free-standing 70%-radius posts, and decouples the grille's outer ring from the boss radius.
- **Driver.** ~40 mm dynamic, **candidate Peerless HPD-40N16** (not locked — baffle stays
  parametric), damped with a rear air space. **Pad:** Brainwavz HM5 oval velour ~90 mm.
- Every dimension flagged as a **first-pass starting value pending measured parts.**

Added three sections to the spec — **Parts table**, **Interfaces** (the 3 joints: cup↔baffle
front-mount, yoke↔cup screw-pin, yoke↔bow slider), and an updated **BOM** with the bow sourcing
link. Created **`docs/drawings/`** with schematic SVG sheets (assembly + cup/baffle/yoke/slider/bow),
each referenced from its spec section; all six render clean. Added a reconciliation banner to
`industrial-design-brief.md` so its older "Locked" bullets point to the resolved spec.

**Deferred to the next engineering pass (NOT this pass):** clean grille, relocating the cup bosses
to the perimeter wall, the integral driver guard, and real yoke/slider/bow geometry — the current
CAD still reflects the older boss placement and stubbed yoke/slider.

---

## 2026-06-14 — Design-pipeline doc: one workflow (Diverge → Resolve → Engineer)

Captured the refined workflow in `docs/design-pipeline.md` (→ v0.2). Added a
top-level **Diverge → Resolve → Engineer** section near the start and folded the
old "three stages" under it as tooling detail, so the doc now has ONE model, not
two competing ones. **Resolve** was the missing layer: developing a picked
direction into a buildable design in chat (parts/fit/fasteners + the
engineering-taste calls — connector, acoustics, wall, weight, cross-part design
language), via schematic SVG sketches and reasoning, before any geometry. Diverge
= old Stage 1 (Stage 2 image→3D is an optional sub-tool); Engineer = old Stage 3.
Handoffs: picked screenshots into chat (Diverge→Resolve), a precise CC prompt
carrying resolved intent (Resolve→Engineer). The boundary (no render →
engineered CAD) and taste-vs-convention sections were reconciled to read
alongside it (taste is decided in Resolve, only encoded in Engineer).

---

## 2026-06-14 — Real concentric-ring grille authored (replaces placeholder vents)

Authored the real rear grille into the cup, replacing the placeholder slot ring
entirely. This **closes the "first-pass vent grille" carry-forward** (#2 in the
2026-06-13 form-direction entry).

**Structure (v1, fully parametric so it tunes after we see it).** Remaining
material = a center hub + two concentric rings + 8 radial spokes; the gaps
between them open to the driver. Spokes: 4 aligned to the baffle-boss positions,
4 between them. Built as an annular CUTTER (zone disc minus the kept members)
cut from the closed back, *before* the bosses are added so no boss column is
sliced.

**Boss/vent collision resolved.** The outer ring's centerline lands on the
baffle-boss radius — `P.grille_outer_radius` is a property that returns
`P.baffle_screw_radius`, so it references the boss radius instead of duplicating
it. The 4 bosses now sit as NODES on the outer ring (verified: back plate is
solid under each boss, columns intact), so the screws reinforce the grille
rather than colliding with a slot. The outer ring's outer edge meets the solid
rim, so the grille is continuous with the shell.

**Open area.** New params in `params.py` (all flagged): `grille_ring_count=2`,
`grille_spoke_count=8`, `grille_hub_diameter=12`, `grille_inner_ring_radius=15`,
`grille_member_width=3.8`, `grille_member_min_width=2.0` (FDM floor),
`grille_target_open_fraction=0.40`. Member width was sized by area-sampling the
2D pattern to hit ~0.40 open; 3.8 mm lands it and every member stays well above
the 2 mm print floor (no need to hold the floor and report a worse number).
**Measured open fraction from the built solid = 0.401** over the grille zone
(radius 29.2 mm) — on target.

**Verified.** `python build.py` green (cup/baffle/yoke/slider + assembly all
export). Cup body is a single connected solid with the grille. (The separate
2nd solid is the pre-existing floating yoke boss — confirmed it was already
detached on HEAD; untouched this pass per scope.) The pre-existing fillet
[warn]s are unchanged and unrelated.

Not touched this pass: yoke/slider form, the floating-yoke-boss carry-forward,
boss screw direction, pad-lip interface — all still open.

---

## 2026-06-14 — Pin the VS Code viewer extension to 2.6.x (match the package)

Reconciled the OCP CAD Viewer mismatch the low-risk way: **downgrade the VS Code
extension to match the Python package**, not the reverse. The package stays
`ocp_vscode==2.6.2` and the env is untouched (Python 3.9.6 / CadQuery 2.5.2 /
OCP 7.7.2).

- **Why not bump the package.** `ocp_vscode` 3.4.0 declares `requires_python
  >=3.10` (confirmed via PyPI); 2.6.2 is `>=3.9`. Bumping to 3.4 would force a
  Python upgrade off the working 3.9.6 and likely reinstalls of OCP/CadQuery —
  exactly the disruption to avoid for a viewer convenience.
- **Action.** Pin the `bernhard-42.ocp-cad-viewer` extension to **2.6.2** (exact
  match; 2.6.1/2.6.3/2.6.4 also exist on the Marketplace, major.minor 2.6 is what
  must match). The `code` CLI isn't on PATH, so it's installed manually via the
  Extensions panel → "Install Specific Version…" → 2.6.2, then disable auto-update
  for that extension so it can't jump back to 3.4.0.
- **Unchanged:** ocp_vscode, CadQuery, OCP, Python, and requirements-dev.txt
  (pin stays 2.6.2).

---

## 2026-06-14 — Fix show.py for the ocp_vscode 2.6.2 API

`show.py` was written against an older API and crashed with
`TypeError: show() got an unexpected keyword argument 'name'`. In 2.6.2 the
signature is `show(*cad_objs, names=None, ...)` — `names` is a list, no singular
`name=`. Fixed to `show(make_assembly(), names=["daily_driver_cup_baffle"])`;
`show()` is the only ocp_vscode call in the repo. Confirmed it now runs past the
`show()` call with no TypeError.

Noted for later (NOT fixed): with no viewer running it then fails in
`find_port()` with a `ValueError` (port discovery), and there's a likely
version mismatch — VS Code extension `bernhard-42.ocp-cad-viewer` is **3.4.0**
while the `ocp_vscode` package is pinned to **2.6.2**. Line these up to clear the
port/`--backend measure-tool` errors in a later pass.

---

## 2026-06-14 — Viewer dev-deps split out

Split the live-viewer dependency from the core build deps: `ocp_vscode==2.6.2`
now lives in a new `requirements-dev.txt` (which pulls in `requirements.txt` via
`-r`), not in `requirements.txt` — `build.py` doesn't need it. README and a
`requirements.txt` comment point to it. Confirmed `.vscode/` is gitignored so a
machine-specific interpreter path never gets committed.

---

## 2026-06-14 — Stage 3 opened: convention primitives, floating-boss fix, cup+baffle assembly

First real-geometry pass. Foundation + convention only — the grille and the
yoke/slider **form** are deliberately untouched (taste passes).

- **Mechanical primitives implemented (`parts/features.py`).** `boss()` (cylinder
  + central blind bore for a brass heat-set insert) and `screw_post()` (same, but
  the bore is a screw clearance/pilot) — both stand on a host plane, merge into
  the host, and fillet the base junction so features are tied and printable.
  Shared `_studs()` body; these are convention, reused, not regenerated per part.
  Verified on a clean host: 1 valid solid with 4 base-fillet faces.
- **Params added (flagged defaults).** `boss_base_fillet` (1.0), `screw_post_diameter`
  (7.0), `screw_post_pilot_diameter` (2.5, FLAGGED — confirm vs real screw); plus
  derived `cup_interior_floor_z`, `baffle_seat_z`, `baffle_boss_height`. The
  baffle **flush-seat** at the front rim is a flagged PROVISIONAL assumption (the
  front/pad-lip interface is still open).
- **Floating-boss bug fixed + migrated (`parts/cup.py`).** The inline boss code is
  gone; the cup now calls `features.boss()`. The old bosses were short cylinders
  near the rim touching nothing (unioned as disconnected solids). They're now
  columns standing on the interior back floor, merged + filleted into it — the
  cup (excluding the provisional yoke boss, below) is a single connected solid.
  Vents are now cut **before** the bosses so the cut never slices the columns.
- **Flagged — boss/vent ring collision.** `baffle_screw_radius` (~70% R, 27.3 mm)
  nearly coincides with the placeholder vent ring (~62% R, 26 mm), so the boss
  bases overlap vent slots and the base fillet skips there (it works fine on a
  clean host). The bosses are still merged/connected. To resolve in the **grille
  taste pass**: pattern the real grille around the four boss footprints.
- **Flagged — provisional yoke boss is barely connected.** The cup-side yoke-mount
  placeholder (a cylinder tangent to the curved wall) only touches along a line,
  so the cup currently reports **2 disjoint solids** (cup body + that boss). Left
  untouched on purpose — cup-side yoke attachment is an open question and yoke
  **form** is deferred. Resolve when the yoke-to-cup interface is designed.
- **Basic assembly added (`assembly.py`, `show.py`).** Cup + baffle in their real
  relationship: the baffle flipped so its driver recess faces into the cup, seated
  flush at the front rim on the boss tops. `build.py` exports `output/assembly.step`
  (error-isolated); `python show.py` opens it in OCP CAD Viewer. Assembly verified
  valid and exporting; open it in the viewer to check proportions.
- **Build.** `python build.py` → 4/4 parts export + `assembly.step`. Yoke/slider
  still stubs.

### Carry-forward

- Grille **form** (and patterning it around the boss footprints) — taste pass.
- Yoke/slider **form** + the cup-side yoke mount (fix its connectivity then) —
  taste pass.
- Confirm `screw_post_pilot_diameter` and the provisional baffle flush-seat once
  the real screws and front/pad-lip interface are settled.

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
