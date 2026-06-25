# Daily Driver

An open-source **40 mm open-back headphone** you can build yourself, modify, and
make your own. Parametric CAD — change a driver, a pad, or a head size and the
model follows. A project of [MakerPhones](https://makerphones.com) / Warren Labs.

> **🧊 Spin it in 3D** — inspect the assembly in your browser before you build:
> **[live 3D preview →](https://makerphones.github.io/daily-driver/)**

> **Status: early / in active development.** The cup and baffle are first-pass
> geometry; the headband parts (yoke, slider) are stubs. Nothing has been
> print-verified yet. Follow along — and fork freely.

Honest sonic target: a bright, open, detailed open-back — strong mids and
treble, modest bass. That's the nature of a small driver in an open baffle, and
the design leans into it rather than chasing bass the hardware can't make.

## How it's made

The parts are defined in code with [CadQuery](https://cadquery.readthedocs.io)
(Python). That means the whole design is plain text you can read, diff, and
modify — and it exports both **STL** (ready to print) and **STEP** (to edit in
other CAD).

### Build the parts

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build.py                 # all parts → output/
python build.py baffle          # just one
```

STLs and STEPs land in `output/`.

For the live VS Code [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer)
(`python show.py`), also install the viewer-only deps and point VS Code's Python
interpreter at this `.venv`:

```bash
pip install -r requirements-dev.txt
```

### Modify it

Open `params.py` — every dimension lives there with a comment. Common changes:

- **Different driver?** Measure it with calipers, update `driver_od` and
  `driver_aperture`, rebuild the baffle.
- **Different pad?** Adjust `pad_lip_od` to your pad's inner-ring diameter.
- **Bigger/smaller head?** Adjust the cup and headband parameters.

The build log in [`docs/DESIGN-LOG.md`](docs/DESIGN-LOG.md) explains the
reasoning behind the design and tracks the open questions. The full functional
spec is in [`docs/design-spec.md`](docs/design-spec.md).

## Bill of materials (build-it-yourself)

| Component | Source | Est. cost |
|---|---|---|
| 2× 40 mm driver, 32 Ω | Parts Express / Madisound | $8–18 |
| 1× Dekoni Universal 100 mm pads (Beyer-type) | Dekoni Audio | $30–45 |
| 1× spring steel arc (laser-cut, formed) | SendCutSend + form | $8–15 |
| 8× M3 heat-set inserts | hardware / online | $1 |
| 8× M3×8 mm button-head screws | hardware / online | $1 |
| Foam gasket tape | hardware | $1 |
| Damping pack (foam + felt + fiberfill) | Parts Express | $3–5 |
| Cable + Y-split + 3.5 mm TRS plug | online | $8–15 |
| Printed parts | own printer or print service | $3–25 |
| **Approx. total** | | **~$55–105** |

No printer? FDM print services (JLCPCB, Xometry) will print the set cheaply.

## License

**This project is open source under the [MIT License](LICENSE).** You are free
to use, modify, build, and **sell** the Daily Driver — commercially or
otherwise. No "personal use only" restriction, no fee. One license over the
whole repo, code and docs alike; full text in [`LICENSE`](LICENSE).

**Attribution requested:** when you share or build on it, credit *makerphones by
Warren Labs (makerphones.com)*.

The **makerphones** and **Warren Labs** names and brands are *not* covered by
the license and are protected separately by trademark — it covers the design
and code, not the names.

## Contributing

This is a learning-in-public project. Builds, measurements, and fixes are
welcome — open an issue with what you tried and what happened.
