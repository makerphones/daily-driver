# Daily Driver — Design Log

For an open design, the log *is* part of the product. Every decision, every
measurement, every iteration goes here so anyone can follow the reasoning, not
just the result. Newest entries at the top.

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
