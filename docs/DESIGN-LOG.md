# Daily Driver — Design Log

For an open design, the log *is* part of the product. Every decision, every
measurement, every iteration goes here so anyone can follow the reasoning, not
just the result. Newest entries at the top.

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
