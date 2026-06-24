# CLAUDE.md — working notes for Claude Code

This repo is the parametric CAD for the **Daily Driver**, an open-source
40 mm open-back headphone. It's a project of MakerPhones / Warren Labs. The
designs are meant to be downloaded, forked, and modified, so the repo is the
source of truth — not chat.

## What this is

Code-based CAD in **CadQuery** (Python). The model emits both STL (print-ready)
and STEP (clean B-rep for editing elsewhere). Code-CAD was chosen on purpose:
text files diff and version-control naturally, and anyone can fork and modify.

## How it's laid out

- `params.py` — **single source of truth** for every dimension. Change values
  here, not inside part files. Derived values are `@property` helpers on
  `Params`.
- `parts/` — one file per part, each exposing a `make_<part>()` that returns a
  CadQuery `Workplane`. Each part builds **independently** (the spec wants every
  interface independently iterable).
  - `cup.py` — real first-pass geometry
  - `baffle.py` — real first-pass geometry (flat; print this first)
  - `yoke.py`, `slider.py` — **stubs**: parameters wired, real geometry TODO
  - `features.py` — **reusable mechanical primitives** (screw boss, post,
    fillet, thread, snap): established convention, **authored once and reused —
    never regenerated per part**, never re-derived by hand each time. Currently
    a stub. (cup.py's inline bosses migrate here later — see DESIGN-LOG.)
- `build.py` — renders parts to `output/`. `python build.py` for all, or
  `python build.py cup baffle` for specific ones. Failures are isolated per part.
- `pipeline/` — AI-assisted **design** pipeline (FAL): Stage 1 text→concept
  images, Stage 2 image→reference mesh. It generates OPTIONS and REFERENCES; it
  never produces engineered CAD. See `docs/design-pipeline.md`.
- `docs/design-spec.md` — the functional spec the CAD is built against.
- `docs/design-pipeline.md` — the AI design pipeline + the taste-vs-convention
  boundary (taste → `params.py` + parametric form in `parts/*.py`; convention →
  `parts/features.py`).
- `docs/DESIGN-LOG.md` — the running record. **For an open design the log is
  part of the product.** Add an entry for every real decision or iteration.
- `docs/filesystem-mcp-setup.md` — how to give a chat-side review session
  read-only access to this repo via the filesystem MCP (config + manual enable step).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py
```

## Working rules (these matter)

1. **`params.py` is the only place dimensions live.** If you need a new
   dimension, add it there with a comment, don't hardcode it in a part.
2. **Don't silently resolve open questions.** The spec and DESIGN-LOG flag real
   unknowns (pad lip location, baffle screw direction, yoke-to-cup mount,
   headband radius, production driver, vent open area). If you make a call on
   one, it's because the human decided — record it in DESIGN-LOG with the
   reasoning. Never invent a driver, part, supplier, price, or spec to make
   geometry "work."
3. **Accuracy over plausibility.** If a dimension isn't known, say so and leave
   it parametric/flagged rather than guessing a number that looks right.
4. **Keep parts independently buildable.** Don't create cross-imports between
   part files; share only through `params.py`.
5. **Functional geometry in code; taste-driven form is a separate pass.** The
   outer profile, vent slot shape (the signature look), and yoke styling are
   refined deliberately, not auto-generated. Get fit and function right first.
6. **Log as you go.** New entry at the top of `DESIGN-LOG.md` each working
   session.

## Current state

`cup` and `baffle` produce valid first-pass solids. `yoke` and `slider` are
stubs. Nothing has been print-verified yet. Immediate next step is to build,
visually sanity-check proportions, then print the baffle against a real driver.

## Distribution

`output/` is gitignored — STL/STEP ship to builders via tagged GitHub Releases,
not committed to the tree. License is still an open decision (see README).
