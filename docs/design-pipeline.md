# Daily Driver — AI-Assisted Design Pipeline

**v0.1 · for the form / industrial-design pass**

This describes how AI assists the Daily Driver's design and, just as importantly,
**where it stops**. The pipeline generates *options* and *references*. It never
produces engineered CAD. The headphone you can actually build is authored by hand
in CadQuery, from human decisions — the AI helps you see and choose, it does not
design the part.

---

## The three stages

```
Stage 1  CONCEPT / MOOD          Stage 2  IMAGE -> ROUGH 3D         Stage 3  ENGINEERED GEOMETRY
  text -> images (FAL)             image -> mesh (FAL)                 human + CadQuery
  explores FORM                    reference body ONLY                 real parts, dims, screws
        │                                  │                                   │
  design/explorations/             design/reference-meshes/            params.py + parts/*.py
        │                                  │                                   │
        └────────── pick a concept ───────┘                                    │
                            └──────── eyeball proportion/silhouette ───────────┘
                                          (then DECIDE the numbers by hand)
```

### Stage 1 — Concept / mood generation

Read `docs/industrial-design-brief.md` and generate N concept images via FAL's
text-to-image model, exploring **form** — silhouette, stance, grille language,
how "open and serviceable" reads visually.

**Prompt construction matters.** `gen_concepts.py` does **not** dump the raw
brief into the prompt. Image models want short, visual, descriptor-style prompts
— not prose carrying constraints and dimensions. So the script builds the prompt
from a **curated, editable visual-descriptor template** (silhouette, grille
language, materials, finish, stance) drawn from the brief, and deliberately
leaves out constraints, dimensions, and manufacturing notes. Edit that template
to steer the look.

- Output: raw run to `design/_scratch/<UTC-timestamp>/` (gitignored) + a
  `manifest.json` recording per-image prompt/view/seed, model slug, and
  timestamp. Promote keepers into `design/explorations/` by hand.
- The camera view is varied across the N images so the set doesn't read closed;
  a rear/grille view is always included.
- These are mood/appearance only. Nothing here has a dimension.

### Stage 2 — Image → rough 3D reference

Take **one chosen** concept image and generate a 3D mesh via FAL. The result is
a **reference body only**: a blobby mesh for checking proportion and silhouette
in 3D. It is **not a part** — no dimensions, no features, no manufacturability.
You hold it next to the real model to judge stance and proportion; you do not
build from it.

**Use it sparingly.** For something as readable-from-renders as a headphone, an
auto-generated mesh often adds little over a good set of multi-angle 2D concepts
— and it costs a call. Reach for Stage 2 only when 3D proportion is genuinely
unclear from the 2D, not by default.

- Output: raw run to `design/_scratch/<UTC-timestamp>/` (GLB/STL, gitignored) +
  a `manifest.json` recording the source image, model slug, and timestamp.
  Promote a keeper into `design/reference-meshes/` by hand.
- The mesh file's header/manifest says, in words: **REFERENCE BODY ONLY, not a
  manufacturable part.**

### Stage 3 — Engineered geometry

Authored by hand in CadQuery (`params.py` + `parts/*.py`). This is where the real
industrial-design files live — actual dimensions, separate parts, screw bosses,
fillets, tolerances. **No API does render → engineered CAD.** That translation is
human + code, on purpose (see the boundary below).

---

## The boundary: no render → engineered CAD

There is deliberately **no automated step from a Stage-2 mesh to a Stage-3 part.**
Two reasons, and they're not going away:

1. **Meshes vs. B-rep.** Stage 2 produces a *mesh* — a soap-film of triangles
   approximating a surface, with no notion of a hole, a thread, a flat mating
   face, or a wall thickness. Engineered CAD is *B-rep*: exact analytic faces and
   edges with real topology you can dimension, offset, and bolt to. You cannot
   reliably auto-convert one into the other; a "watertight STL" is not a designed
   part. The mesh tells you what it should *look* like, not what it *is*.

2. **Engineered features are decisions, not pixels.** Where the screws go, how
   deep the cup is, how the baffle seats, the vent open area — these are
   functional choices with consequences (fit, acoustics, print success). They are
   reasoned and measured, not inferred from an image. An image can't know your
   driver's caliper measurements or your printer's tolerance.

So the pipeline hands you **vision and reference**, and you do the engineering.

---

## Taste vs. convention — the split that decides what AI touches

Two different kinds of work, handled two different ways:

**TASTE is human and manual.** Cup depth, vent form, where the screws go,
proportions, stance, finish. These are judgment calls — you decide them from
concepts/references **plus real measurements**. Taste is encoded two ways, and
both are authored by you, in code: some taste is a **number** (cup depth → a
value in `params.py`), and some taste is **form** (vent shape, grille pattern,
cup profile) authored as parametric **geometry in `parts/*.py`** and driven by
those params. Either way it's a human decision expressed in code. AI may
*inform* taste (by showing options); it never *sets* it, never writes a
dimension, and never authors a part.

**ESTABLISHED MECHANICAL CONVENTIONS are not reinvented.** A screw boss, a
fillet, a standard thread, a snap fit — these are solved by decades of practice.
They live as **reusable parametric helpers**, authored once from convention in
`parts/features.py`, and **reused** across parts — never regenerated per part by
AI, and never re-derived by hand each time. Convention is a library, not a
creative act.

| | Who/what | Where it lives |
|---|---|---|
| **Taste** | Human decision, informed by concepts/refs + measurement | `params.py` (numbers) + `parts/*.py` (form), authored by human |
| **Convention** | Standard practice, authored once | `parts/features.py` (reusable helpers) |
| **Form options** | FAL image gen | `design/explorations/` |
| **Proportion refs** | FAL image→3D | `design/reference-meshes/` |
| **Engineered parts** | Human + CadQuery | `parts/*.py` |

`parts/features.py` is the home for mechanical primitives (`boss()`,
`screw_post()`, etc.): authored once from established practice and reused, never
regenerated per part. (Status: stubbed; primitives currently inline in
`parts/cup.py` migrate here later — see DESIGN-LOG.)

---

## Layout

```
docs/industrial-design-brief.md   the form brief Stage 1 reads
docs/design-pipeline.md           this file
pipeline/
  config.py                       model slugs, output dirs, counts, seeds (swap a model here)
  gen_concepts.py                 Stage 1: brief -> images
  gen_reference_mesh.py           Stage 2: image -> reference mesh
  smoke_test.py                   one minimal FAL call, confirms auth+connectivity
design/
  _scratch/                       raw bulk runs — GITIGNORED, not part of the record
  explorations/<timestamp>/       Stage 1 CURATED PICKS (committed)
  reference-meshes/<timestamp>/   Stage 2 CURATED PICKS (committed)
parts/features.py                 reusable mechanical primitives (convention)
.env                              FAL_KEY (gitignored, never committed)
```

**Curated keepers are committed; raw scratch is not.** `design/explorations/`
and `design/reference-meshes/` hold only the **curated picks** you choose to keep
— those are committed on purpose, because the exploration history is part of an
open design's story. Raw bulk runs land in `design/_scratch/`, which is
**gitignored**: generate freely there, then promote the keepers into the curated
dirs. The API key is **never** committed.

---

## How to run

> _To be filled in once the scripts land (steps 2–3 of setup). Placeholder so the
> shape is clear:_

```bash
# one-time: env + auth
source .venv/bin/activate
pip install -r requirements.txt        # includes the FAL client
# put FAL_KEY=... in .env (gitignored); FAL is pay-per-call — billing required

# confirm connectivity
python pipeline/smoke_test.py

# Stage 1 — generate concepts from the brief (raw -> gitignored _scratch)
python pipeline/gen_concepts.py        # -> design/_scratch/<timestamp>/

# Curate: copy the keepers into design/explorations/<timestamp>/ by hand, commit

# Stage 2 — turn ONE chosen concept into a reference mesh (raw -> _scratch)
python pipeline/gen_reference_mesh.py <path-or-url-to-chosen-image>
                                       # -> design/_scratch/<timestamp>/
# Curate: copy a keeper into design/reference-meshes/<timestamp>/ by hand, commit

# Stage 3 — engineer it by hand (no command; this is you + CadQuery)
```

---

*v0.1 · 2026-06-13 · Written as the form pass opens. Update the "how to run"
section and model slugs as the scripts and FAL's model lineup evolve.*
