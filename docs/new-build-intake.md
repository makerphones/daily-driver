# New headphone intake → brief → build

The Daily Driver is product #1. This is the repeatable pipeline for starting the
next one without a blank page: a structured **intake** that produces a **brief**,
which seeds a parametric **build** you iterate on. The intake captures exactly the
decisions that ended up driving `params.py` and the styling passes for the Daily
Driver — so it's grounded in what actually mattered, not a generic survey.

Run it interactively with the **`/headphone-intake`** skill (it asks the questions
below and writes a `BRIEF.md`), or fill the template by hand.

## The pipeline

```
INTAKE  →  BRIEF.md  →  params.py + parts/  →  build.py → gate.py → DESIGN-LOG  →  iterate  →  release
(ask)      (decisions)   (single source)        (N/N)      (0 HARD)   (one entry)    (re-measure)  (tag)
```

- **Intake**: answer the questionnaire; gather reference photos + any measurements.
  Unknowns are fine — mark them `TBD` / `ESTIMATE`, don't invent numbers.
- **Brief**: the frozen-enough set of decisions + targets. Lives in the build dir.
- **Build**: translate the brief into `params.py` values (the single source of
  truth) and any new part geometry. Reuse the Daily Driver skeleton + ritual.
- **Gate every change**: `python build.py` (N/N) then `python gate.py` (0 HARD).
- **Log + commit + push** every real decision/iteration (newest DESIGN-LOG entry
  on top; one commit per task; **always push**).
- **Iterate on real parts**: measurements from printed parts / the actual pad/bow
  overwrite ESTIMATEs cleanly → rebuild → gate → log.

See `cadquery-build-notes.md` for the kernel limits (round before cut, etc.) before
you reach for fillets, and `design-pipeline.md` for the taste-vs-convention boundary.

## The questionnaire (what a brief must answer)

Each block maps to params/decisions. Capture the answer **and** its confidence
(`MEASURED` / `ESTIMATE` / `TBD`).

1. **Use-case & vibe** — open- or closed-back? studio / commute / desk / gaming?
   The feel: soft & rounded vs. angular & technical? Reference headphones/images.
2. **Driver** — size (e.g. 40/50 mm), impedance, model or "generic class". Aperture
   and recess derive from `driver_od`, so this sets the baffle family.
3. **Earpad** — brand/model + the four numbers: outer Ø, ear-opening ID, **mounting
   skirt Ø** (what the cup lip wraps — NOT the ear opening), and depth. Drives the
   cup OD and the retaining lip. (Daily Driver: Dekoni Universal 100 mm.)
4. **Headband / bow** — bought spring band (e.g. Beyer metal bow) or DIY blank?
   Relaxed radius, developed (rolled-out) length, width, end-tab hole pattern. The
   band flexes; the worn radius sets ear spacing.
5. **Cup–yoke–slider mechanism** — pivot + swivel gimbal? How does the band attach
   to the slider — **bolt-on at end tabs** or telescoping clamp? (Daily Driver:
   bolt-on, screws on the inside face.)
6. **Fit** — target head width / ear spacing, clamp feel, tilt range.
7. **Aesthetic** — grille pattern + open-area target, accent color, edge treatment
   (roundovers vs chamfers — within the kernel's limits), any signature mark.
8. **Constraints** — print bed size, material (PLA/PETG/ABS/TPU pads?), hardware
   you'll stock (M3 inserts/screws), license, budget per unit.
9. **Prior-art boundary** — list reference designs studied; note their licenses.
   Credit adopted ideas in DESIGN-LOG; **never copy files/geometry** from
   non-permissively-licensed projects.

## BRIEF.md template

```markdown
# <Headphone name> — design brief
Status: DRAFT · <date>

## 1. Use-case & vibe
- ...
- References: <links / image filenames>

## 2. Driver
- Size / impedance / model: <…>  [MEASURED|ESTIMATE|TBD]

## 3. Earpad
- Model: <…>
- Outer Ø: <…> | Ear ID: <…> | Mount skirt Ø: <…> | Depth: <…>  [confidence each]

## 4. Headband / bow
- Type: <bought | DIY>  | Relaxed R: <…> | Developed length: <…> | Width: <…>
- End-tab holes: <count / pitch>  [confidence each]

## 5. Mechanism
- Cup pivot / swivel: <…>
- Band ↔ slider attach: <bolt-on | clamp>, screws on <inside|outside>

## 6. Fit
- Ear spacing target: <…> | Tilt range: <…> | Clamp: <…>

## 7. Aesthetic
- Grille: <pattern>, open-area target <…>
- Accent: <…> | Edge treatment: <…> | Signature: <…>

## 8. Constraints
- Bed: <…> | Material: <…> | Hardware: <…> | License: <…> | Target cost: <…>

## 9. Prior-art studied (look-don't-copy)
- <project> — <license> — <idea adopted, credited in DESIGN-LOG>

## Open questions / next measurements
- [ ] <…>
```

## Turning a brief into a build

- New cup OD / pad → set `cup_outer_diameter`, `pad_lip_*`; the lip + pivot bosses
  + yoke regenerate.
- New driver → `driver_od`; aperture/recess/guard derive.
- New bow → `bow_radius`, `bow_developed_length`, `bow_width`, `bow_worn_radius`.
- Styling → grille params, accents, edge treatments (mind the kernel limits).
- Everything flows from `params.py`; parts stay independently buildable.

## Bigger picture (not built yet)

A public intake **form on makerphones.com** that collects design suggestions is the
natural extension. Caveat: an LLM-backed form burns API credits per submission, so
prove the value with this here-only `/headphone-intake` skill first, then decide
between (a) a plain structured web form that emails a brief draft, and (b) a
hosted assistant. Start cheap.
