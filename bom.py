# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Hardware bill of materials — emitted by build.py to BOM.md.

This is part of the open product, same as the DESIGN-LOG: it's what a forker needs
to actually source the build. Quantities are DERIVED FROM params.py counts × 2
ears, so they track the design automatically (change baffle_screw_count or
pivot_boss_count and the BOM follows). Prices/sources are flagged:

  REF      — a confirmed reference for a specific bought part (e.g. the Beyer bow).
  ESTIMATE — a working price/selection pending confirmation (per the project rule:
             never present a guessed price as confirmed; flag it).

Per the project's accuracy rule, verify prices against the live supplier page at
the time you source — the ESTIMATE rows are starting points, not quotes.
"""

from params import P

EARS = 2


def bom_rows():
    """Structured BOM rows. Counts come from params (× EARS) where the design
    fixes them; everything else is a flagged sourcing estimate."""
    baffle_screws = P.baffle_screw_count * EARS          # M3, baffle → frame bosses
    clamp_screws = P.driver_clamp_count * EARS           # M3, driver clamp ring → baffle back
    pivot_screws = P.pivot_boss_count * EARS             # M3 shoulder screws (the tilt joint)
    pivot_nylon_washers = 2 * P.pivot_boss_count * EARS  # 2/joint: head-side + boss-side
    pivot_wave_washers = P.pivot_boss_count * EARS       # 1/joint: tilt-hold preload
    thumbscrews = EARS                                   # 4-40 knurled thumbscrew, slider height lock (1/side)
    m3_inserts = (P.baffle_screw_count + P.driver_clamp_count + P.pivot_boss_count) * EARS
    ts_inserts = EARS                                    # one 8-32 heat-set per slider, for the thumbscrew
    shoes = EARS                                         # one pressure shoe per slider (printed/Delrin)
    rods = EARS                                          # shoulder screw = the adjustment post (1/side)
    m5_inserts = EARS                                    # M5 heat-set in the fork → shoulder screw (1/side)

    return [
        # item, qty, source, price, flag
        ("40 mm dynamic driver, 32 Ω", f"{EARS}",
         "Parts Express / Madisound", "$8–18", "ESTIMATE"),
        ("Dekoni Universal 100 mm ear pads (Beyer-type)", "1 pair",
         "Dekoni Audio", "$30–45", "ESTIMATE"),
        ("Beyerdynamic Metal Head Bow (or DIY 1095 spring steel)", "1",
         "north-america.beyerdynamic.com", "~$11", "REF"),
        (f"M3 shoulder screw — yoke↔cup pivot, ISO 7379 Ø{P.shoulder_screw_shoulder_diameter:.0f} shoulder × M3 (eye rides the shoulder)",
         f"{pivot_screws}", "McMaster-Carr / hardware", "~$1.50 ea (~$6)", "ESTIMATE"),
        ("Nylon flat washer, M3 — pivot tilt stack (head-side + boss-side; protects PETG + adds drag)",
         f"{pivot_nylon_washers}", "McMaster-Carr / hardware", "~$1 (set)", "ESTIMATE"),
        ("M3 wave/Belleville washer — pivot tilt preload (cup holds its angle, no detent)",
         f"{pivot_wave_washers}", "McMaster-Carr / hardware", "~$1 (set)", "ESTIMATE"),
        (f"M3 socket-head screw, ~{int(P.baffle_thickness)}–10 mm — baffle → frame",
         f"{baffle_screws}", "McMaster-Carr / hardware", "~$1 (set)", "ESTIMATE"),
        ("M3 socket-head screw, ~6–8 mm — driver clamp ring → baffle",
         f"{clamp_screws}", "McMaster-Carr / hardware", "~$1 (set)", "ESTIMATE"),
        ("Knurled knob / large-head thumb screw, 8-32, ⌀5/8\" head — slider height lock (presses the shoe)",
         f"{thumbscrews}", "McMaster-Carr (knurled knobs / thumb-screw knobs)", "~$2 ea", "ESTIMATE"),
        ("Slider pressure shoe — printed PETG or Delrin blank (screw → shoe → rod, no marring)",
         f"{shoes}", "own printer / Delrin offcut", "~$0", "ESTIMATE"),
        ("Shoulder screw — ISO 7379 Ø6 shoulder × M5 × 50 mm, 18-8 SS — the adjustment post (head = top stop, no rod machining)",
         f"{rods}", "McMaster-Carr (metric stainless socket shoulder screws)", "~$3 ea", "ESTIMATE"),
        ("M5 brass heat-set insert — fork → shoulder-screw thread",
         f"{m5_inserts}", "McMaster-Carr / Amazon", "~$1 (set)", "ESTIMATE"),
        (f"M3 brass heat-set insert (⌀{P.heatset_insert_diameter:.1f} OD × {P.heatset_insert_length:.1f})",
         f"{m3_inserts}", "McMaster-Carr / Amazon", "~$4–5 (set)", "ESTIMATE"),
        ("8-32 brass heat-set insert — slider thumbscrew",
         f"{ts_inserts}", "McMaster-Carr / Amazon", "~$1 (set)", "ESTIMATE"),
        ("Foam gasket tape (driver seal)", "small roll",
         "hardware", "~$1", "ESTIMATE"),
        ("Damping pack (felt + open-cell foam + fiberfill)", "1",
         "Parts Express", "$3–5", "ESTIMATE"),
        ("Cable + Y-split + 3.5 mm TRS plug", "1",
         "online", "$8–15", "ESTIMATE"),
        ("Printed parts (2× cup, baffle, yoke, slider, driver clamp, shoe per side)", "1 set",
         "own printer or print service", "$3–25", "ESTIMATE"),
    ]


def _markdown(rows):
    lines = [
        "# Daily Driver — hardware bill of materials",
        "",
        "**Generated by `build.py` — do not hand-edit; change `bom.py` / `params.py`.**",
        "",
        "Quantities are per complete headphone (2 ears) and are derived from the",
        f"design (`baffle_screw_count={P.baffle_screw_count}`, "
        f"`pivot_boss_count={P.pivot_boss_count}`, × {EARS} ears). Prices flagged",
        "`REF` are confirmed references; `ESTIMATE` are starting points pending",
        "confirmation — verify against the live supplier page when you source (the",
        "project rule: never present a guessed price as confirmed).",
        "",
        "| Component | Qty | Source | Est. price | Flag |",
        "|---|---|---|---|---|",
    ]
    for item, qty, source, price, flag in rows:
        lines.append(f"| {item} | {qty} | {source} | {price} | {flag} |")
    lines += [
        "",
        "Own-printer builds land near the low end (filament only); print-service",
        "sourcing near the high end. The driver is still parametric/unlocked",
        "(candidate Peerless HPD-40N16) — its price is the widest estimate.",
        "",
    ]
    return "\n".join(lines)


def write_bom(path="BOM.md"):
    with open(path, "w") as f:
        f.write(_markdown(bom_rows()))
    return path


if __name__ == "__main__":
    print("wrote", write_bom())
