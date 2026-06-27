# Decision tree — the order to lock choices

Eight iterations on the Daily Driver taught a dependency order: **lock the inputs,
derive the cup, derive the mechanism, build the chain, then style.** Following it
avoids the churn of re-deriving downstream parts when an upstream number changes.
Reusable for any new headphone (it's about dependencies, not this product).

```
0. FRAME          use-case & vibe ─────────────────────────────► colours every choice below
                       │
1. INPUTS         ┌────┴─────┬───────────────┐   (independent — measure/choose all three;
   (Tier 1)       ▼          ▼               ▼    see measurement-priorities.md)
              DRIVER      EARPAD           BOW
              (OD)     (mount skirt Ø)  (R, length, width)
                  │          │               │
2. DERIVE CUP     │          ▼               │
                  │   cup_outer_diameter      │   ◄── pad mount sets the cup OD
                  └──► cup_interior (ear      │
                       cavity + driver)       │
                            │                 │
3. DERIVE         ┌─────────┴────────┐        │
   MECHANISM      ▼                  ▼        ▼
            pivot bosses        band↔slider attach
            (proud of cup OD)   (bolt-on vs clamp)
                  │                  │
            yoke_pivot_centres   slider geometry
            → yoke wraps cup     ← bow width
                  │                  │
4. BUILD CHAIN    └──► cup → baffle → yoke → slider → bow → ASSEMBLY
                       (gate every part: build N/N, gate 0 HARD)
                            │
5. STYLE          ────────► grille / accents / edge treatments / signature
   (taste pass)             ◄── LAST, after fit + function are right
                            ◄── mind the kernel limits (cadquery-build-notes.md)
                            │
6. PROTOTYPE      ────────► print → measure real parts → overwrite ESTIMATEs → iterate
```

## The rules behind the arrows

- **Inputs gate everything.** Driver, earpad, and bow are independent givens —
  measure all three (Tier 1) before deriving anything. A wrong input regenerates
  the whole chain wrong.
- **Pad → cup OD → pivot → yoke is a hard chain.** The pad's mount Ø sets
  `cup_outer_diameter`; the cup OD sets how far the pivot bosses must stand proud,
  which sets `yoke_pivot_centres`, which sets how the yoke wraps. Change the pad and
  this all moves. (We re-walked it twice — once for the cup resize, once for the
  yoke.)
- **Mechanism before geometry.** Decide *bolt-on vs clamp* (band↔slider) and the
  pivot/swivel scheme before detailing the slider/yoke — the parts differ a lot.
- **Style last.** The grille, accents, and roundovers are a taste pass *after* fit
  and function gate clean. Styling first wastes work when a dimension moves. (And
  some roundovers aren't even possible on this kernel — check the build-notes before
  promising a finish.)
- **Don't invent inputs.** If a Tier-1 number isn't measured yet, mark it `TBD`,
  build with a flagged `ESTIMATE`, and treat the first print as a measurement jig —
  don't fabricate a spec to "finish" the design.

## Where it maps in the repo

`params.py` is the single source of truth, organised roughly in this order
(cup → baffle → driver → yoke → slider → bow → styling). The intake skill
(`/headphone-intake`) walks the inputs; `new-build-intake.md` is the full pipeline;
`measurement-priorities.md` says which inputs block the first print.
