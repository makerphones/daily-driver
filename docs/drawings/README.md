# Daily Driver — drawings

Schematic 2D part sheets (SVG) for the Daily Driver, in the DT880-family
direction (see `../design-spec.md`). These are **Resolve-phase schematics** — not
CAD projections. They capture intent, key joints, and first-pass dimensions so
the spec and the eventual `parts/*.py` geometry agree on what each part *is*.

| Sheet | Part | Referenced from spec section |
|---|---|---|
| `assembly.svg` | Exploded stack + the 3 joints | System architecture / BOM |
| `cup.svg`      | Cup shell + integral grille | Cup shell |
| `baffle.svg`   | Front-mount baffle          | Baffle plate |
| `yoke.svg`     | DT880-style fork-yoke       | Fork-yoke |
| `slider.svg`   | Bow slider (height + swivel)| Slider |
| `bow.svg`      | Spring-steel head bow       | Headband / bow |

**Every dimension on these sheets is a first-pass starting value pending measured
parts** — the bow especially is TBD from the real Beyer Metal Head Bow. Sheets
are schematic, dimensions are not to scale.
