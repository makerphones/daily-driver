# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Hardware bill of materials — emitted by build.py to BOM.md.

This is part of the open product, same as the DESIGN-LOG: it's what a forker needs
to actually source the build. Quantities are DERIVED FROM params.py counts × 2
ears, so they track the design automatically (change baffle_screw_count or
pivot_boss_count and the BOM follows).

PART NUMBERS were researched against live supplier catalogs (2026-06-27) and each
is tagged with how confident we are. Per the project's accuracy rule we NEVER
invent a part number, supplier, or price — every catalog number below was read on
a real supplier page. Flags:

  VERIFIED — part # + spec read straight off the cited supplier page (price may
             still drift; confirm at cart). The default for the fasteners.
  REF      — a confirmed reference for a specific bought part (the Beyer bow).
  SPEC     — the SPEC is pinned, but the exact SKU is builder's choice / the
             small-qty source varies (commodity washers, cable) — verify live.
  MAKER    — maker-supplied; the maker already has these (Kingstate driver, Beyer
             pads). No SKU pinned by design.
  ESTIMATE — a working price/selection pending confirmation.

Source URLs live next to each part so a builder can click through. The ESTIMATE
rows are starting points, not quotes — verify against the live page when you source.
"""

from params import P

EARS = 2


def _pn(part, supplier, url=None):
    """Format a 'Part # — supplier' cell, linking the part number when we have a URL."""
    head = f"[{part}]({url})" if url else part
    return f"{head} — {supplier}"


def bom_rows():
    """Structured BOM rows (component, qty, spec/length, part#·supplier, price, flag).

    Counts come from params (× EARS) where the design fixes them; the part numbers
    are the researched best picks (see the module docstring + the Sourcing notes
    appended below the table for alternates and caveats)."""
    baffle_screws = P.baffle_screw_count * EARS          # M3×8, baffle → frame bosses
    clamp_screws = P.driver_clamp_count * EARS           # M3×6, driver clamp ring → baffle back
    pivot_screws = P.pivot_boss_count * EARS             # M3 shoulder screws (the tilt joint)
    pivot_nylon_washers = 2 * P.pivot_boss_count * EARS  # 2/joint: head-side + boss-side
    pivot_wave_washers = P.pivot_boss_count * EARS       # 1/joint: tilt-hold preload
    knobs = EARS                                         # 8-32 knurled knob, slider height lock (1/side)
    m3_inserts = (P.baffle_screw_count + P.driver_clamp_count + P.pivot_boss_count) * EARS
    ts_inserts = EARS                                    # one 8-32 heat-set per slider, for the knob
    shoes = EARS                                         # one pressure shoe per slider (printed/Delrin)
    rods = EARS                                          # shoulder screw = the adjustment post (1/side)
    m5_inserts = EARS                                    # M5 heat-set in the fork → shoulder screw (1/side)

    return [
        # --- Acoustic + soft goods (maker-supplied / builder's choice) -----------
        ("Kingstate 40 mm dynamic driver, ~32 Ω (common-40 mm assumption)", f"{EARS}",
         "Ø39.5 frame / ≤6 mm deep MEASURED; dome proud/excursion = common-40 mm ASSUMPTION until test "
         "drivers measured (drives baffle hub depth)",
         "Kingstate — maker-supplied (measure Fs/Qts/Z + dome/excursion when bench-testing)", "~$8–18", "MAKER"),
        ("Ear pads — Beyerdynamic DT 770/880/990 family (DEFAULT)", "1 pair",
         "OD ~100 / opening ~58 / depth ~22–25 mm, elastic stretch-ring mount",
         "Beyerdynamic EDT-series — maker-supplied; Dekoni / Brainwavz interchangeable (premium/tuning)",
         "~$25–45", "MAKER"),

        # --- Headband spring -----------------------------------------------------
        ("Metal head bow (spring band)", "1",
         "DT-family sprung bow; 5 in relaxed dia, 33 mm wide",
         _pn("917017 (std) / 973361 (PRO)", "Beyerdynamic NA",
             "https://north-america.beyerdynamic.com/p/metal-head-bow"),
         "~$11", "REF"),

        # --- Headband height: adjustment post + lock -----------------------------
        (f"Adjustment post — shoulder screw, ISO 7379 Ø{P.yoke_post_diameter:.0f} f9 × M5 × 50 mm, SS",
         f"{rods}", "Ø6 ground shoulder (slide+swivel bearing), M5 thread, head = top stop",
         _pn("619806050", "Mädler North America",
             "https://maedlernorthamerica.com/partshop/shoulder-screw-similar-to-iso-7379-o6f9-m5-50mm-stainless-steel-1-4301-pn-619806050/"),
         "$6.65 ea", "VERIFIED"),
        ("Slider height-lock knob — 8-32 knurled-head thumb screw, ½″ head × 3⁄8″ stud, brass",
         f"{knobs}", "8-32 × ~3⁄8″ stud; presses the captive shoe onto the post",
         _pn("SCK35", "Grand Brass",
             "https://grandbrass.com/3-8in-long-x-8-32-threaded-1-2in-diameter-knurled-head-thumb-screw/"),
         "$0.54 ea", "VERIFIED"),
        ("Slider pressure shoe — printed PETG or Delrin blank (screw → shoe → rod, no marring)",
         f"{shoes}", "own print / Delrin offcut", "own printer or Delrin scrap", "~$0", "SPEC"),

        # --- Yoke ↔ cup pivot (friction-tilt washer stack) -----------------------
        (f"Pivot shoulder screw — ISO 7379 Ø{P.shoulder_screw_shoulder_diameter:.0f} × M3 × {P.shoulder_screw_shoulder_length:.0f} mm, A2 SS",
         f"{pivot_screws}", "Ø4 smooth shoulder the fork eye rides; M3 into the cup heat-set",
         _pn("49844-SKH-M3-8-A2", "Accu",
             "https://accu-components.com/us/knurled-socket-shoulder-screws/49844-SKH-M3-8-A2"),
         "~$5 ea", "VERIFIED"),
        ("Nylon flat washer, M3 (DIN 125 / ISO 7089) — pivot tilt stack, protects PETG + adds drag",
         f"{pivot_nylon_washers}", "ID 3.2 / OD 7 / 0.5 mm, Nylon 6/6",
         _pn("465682-HPW-3-2-7-0-5-N", "Accu",
             "https://accu-components.com/us/metric-flat-washers/465682-HPW-3-2-7-0-5-N"),
         "~$0.10 ea", "SPEC"),
        ("Wave spring washer, M3 (DIN 137B) — pivot tilt PRELOAD (cup holds its angle, no detent)",
         f"{pivot_wave_washers}", "ID 3.2 / OD 8 / 0.5 mm, free height ~0.8 mm, SS",
         _pn("WW3BSS", "BelMetric",
             "https://belmetric.com/wave-washer-stainless-form-b-crinkled-din-137b/"),
         "~$0.09 ea", "VERIFIED"),

        # --- Baffle / driver-clamp screws ----------------------------------------
        ("M3 socket-head cap screw, 8 mm (DIN 912), 18-8/A2 SS — baffle → frame bosses",
         f"{baffle_screws}", "M3 × 8 mm",
         _pn("2170021", "FMW Fasteners",
             "https://www.fmwfasteners.com/products/m3-0-50-x-8-socket-cap-screw-din-912-18-8-a2-stainless-steel"),
         "$0.13 ea", "VERIFIED"),
        ("M3 socket-head cap screw, 6 mm (DIN 912), 18-8/A2 SS — driver clamp ring → baffle",
         f"{clamp_screws}", "M3 × 6 mm",
         _pn("2170020", "FMW Fasteners",
             "https://www.fmwfasteners.com/products/m3-0-50-x-6-socket-cap-screw-din-912-18-8-a2-stainless-steel"),
         "$0.13 ea", "VERIFIED"),

        # --- Heat-set inserts (brass, for FDM) -----------------------------------
        (f"M3 brass heat-set insert (install bore ⌀{P.m3_insert_hole_diameter:.1f}) — baffle/clamp/pivot bosses",
         f"{m3_inserts}", "M3×0.5, OD ~4.6, L 5.7 mm",
         _pn("RX-M3x5.7 (GE-M3x57-001)", "Ruthex / 3DJake",
             "https://www.3djake.com/ruthex/threaded-insert-m3-100-pieces"),
         "~$8.5 / 100", "VERIFIED"),
        (f"M5 brass heat-set insert (install bore ⌀{P.m5_insert_hole_diameter:.1f}) — fork → post shoulder screw",
         f"{m5_inserts}", "M5×0.8, OD ~7.1, L 9.5 mm",
         _pn("RX-M5x9.5 (GE-M5x95-001)", "Ruthex / 3DJake",
             "https://www.3djake.com/ruthex/threaded-inserts-m5-50-pieces"),
         "~$9.5 / 50", "VERIFIED"),
        (f"8-32 brass heat-set insert (SHORT, install bore ⌀{P.slider_thumbscrew_insert_hole:.1f}) — slider knob",
         f"{ts_inserts}", "8-32 UNC, ~4.7 mm long (fits the 5 mm boss)",
         _pn("RX-8-32x4.7", "Ruthex",
             "https://www.ruthex.de/en/products/ruthex-8-32-short-gewindeeinsatz-unc-50-stuck-ge-8-32x47-001"),
         "~$9 / 50", "VERIFIED"),

        # --- Cable + consumables -------------------------------------------------
        ("Cable + 3.5 mm TRS plug (builder's choice)", "1",
         "any cable terminated in a 3.5 mm (1⁄8″) TRS plug, ~1.2–1.8 m",
         _pn("240-1032", "Parts Express",
             "https://www.parts-express.com/3.5mm-Stereo-Male-to-Male-Audio-Cable-Dual-Shielded-with-Gold-Plated-Connectors-6-ft.-240-1032"),
         "~$2", "SPEC"),
        (f"Front-seal foam gasket — driver↔baffle ({int(P.front_gasket_squeeze*100)}% squeeze)",
         f"{EARS}",
         f"~{P.front_gasket_thickness} mm foam ring, ~{P.front_gasket_width} mm wide (clamp compresses to {P.front_gasket_compressed} mm)",
         "foam tape — builder-cut", "~$1", "ESTIMATE"),
        (f"Rear damping felt disc (⌀{int(P.damping_felt_diameter)} × {int(P.damping_felt_thickness)} mm)",
         f"{EARS}",
         "acoustic felt / open-cell — drops into the cup's damping ring over the grille",
         "Parts Express / craft felt", "$3–5", "ESTIMATE"),
        (f"Front acoustic paper / mesh — {P.baffle_vent_strip_count} arc STRIPS per ear (~{P.baffle_paper_thickness} mm)",
         f"{P.baffle_vent_strip_count * 2} strips ({P.baffle_vent_strip_count}/ear)",
         "cut as straight-ish strips (low waste); each glues into a baffle FRONT 'hot-dog' depression "
         "over its vent holes — the paper sets back→front resistance. GRADE (weight / mesh count) "
         "measurement-gated to the driver",
         "acoustic paper (speaker-cone paper) / metal mesh", "~$1", "ESTIMATE"),
        ("Vent plug — printed, CLOSED-BACK variant only (reversible openness tuning)",
         "as needed", f"press-fit ⌀{int(P.cup_port_diameter)} mm port; plug N of {P.cup_port_count}",
         "own printer (parts/vent_plug.py)", "~$0", "SPEC"),
        ("Printed parts (2× cup, baffle, yoke, slider, driver clamp, shoe per side)", "1 set",
         "PETG recommended", "own printer or print service", "$3–25", "ESTIMATE"),
    ]


# Sourcing notes — alternates, caveats, and the DIY routes that don't fit the table.
SOURCING_NOTES = [
    "**Metal head bow** — `917017` is the lower-clamp bow (DT 770/880/990 + Edition, T1/T5p/T70/T90); "
    "`973361` is the *PRO* bow (higher clamp; DT 770/880/990 PRO, DT 1770/1990, Custom One). "
    "DIY route: a ~33 mm × ~0.8 mm 1095 blue-tempered spring-steel strip (OnlineMetals PID 26230, "
    "0.032″) or a laser-cut + formed arc (SendCutSend).",
    "**Adjustment post** — Mädler `619806050` is 304 SS \"similar to ISO 7379\" (read-verified, $6.65, no MOQ). "
    "For a *strict* ISO 7379 A2 part the exact-size match is Accu `436268-SSH-M5-6-50-A2` (price not "
    "machine-readable — confirm live). Alloy 12.9 (cheaper in bulk): ASMC `0000-114004` (25-pc min).",
    "**Pivot shoulder screw** — Accu `49844-SKH-M3-8-A2` (knurled head) or plain-head `10379-SSH-M3-8-A2`; "
    "Accu's site blocks price scraping, so for a read-verified US price use Mädler `619804008` ($5.41 ea). "
    "Note: Ø4-M3 is below the official ISO 7379 size sheet, so all suppliers brand it \"similar to.\"",
    "**Slider knob** — a true ⌀5⁄8″ all-metal 8-32 knurled head appears to be non-stock; ½″ (SCK35) is the "
    "largest readily sourced all-metal head. If a bigger grip is wanted, the only 8-32 option ≥5⁄8″ is a "
    "*plastic*-handle control knob (Innovative Components GN82) — verify before ordering.",
    "**8-32 heat-set** — the design bore is reconciled to ⌀5.6 mm (the real Ruthex 8-32 install hole). The "
    "SHORT `RX-8-32x4.7` matches the 5 mm slider boss; the standard `RX-8-32x8.1` (GE-8-32x81-001) needs a "
    "deeper boss. US second source: CNC Kitchen 8-32 (cnckitchenus.store).",
    "**M3 heat-set** — Ruthex actual OD is 4.6 mm; params keep the McMaster 4.70 as the *conservative* "
    "wall-check reference (larger OD → stricter gate). CNC Kitchen `M3×5.7` is an equivalent US second source.",
    "**Nylon + wave washers** — small-quantity SKUs vary; Accu (no MOQ) and BelMetric (US, Amazon 200-pc "
    "ASIN B08FXFQZT8 for the wave washer) are the practical hobbyist buys. Aspen Fasteners has read-verified "
    "prices but only in bulk boxes.",
    "**Driver + pads are maker-supplied** — the Kingstate 40 mm driver specs get measured at bench-test; the "
    "Beyerdynamic pads are the default (Dekoni/Brainwavz are interchangeable premium/tuning swaps).",
]


def _markdown(rows):
    lines = [
        "# Daily Driver — hardware bill of materials",
        "",
        "**Generated by `build.py` — do not hand-edit; change `bom.py` / `params.py`.**",
        "",
        "Quantities are per complete headphone (2 ears) and are derived from the",
        f"design (`baffle_screw_count={P.baffle_screw_count}`, "
        f"`pivot_boss_count={P.pivot_boss_count}`, × {EARS} ears). Part numbers were",
        "read off live supplier pages (2026-06-27); prices drift, so confirm at cart.",
        "Flags: **VERIFIED** part#/spec read on the cited page · **REF** confirmed",
        "bought-part reference · **SPEC** spec pinned, SKU is builder's choice ·",
        "**MAKER** maker-supplied · **ESTIMATE** pending confirmation.",
        "",
        "| Component | Qty | Spec / length | Part # — supplier | Price | Flag |",
        "|---|---|---|---|---|---|",
    ]
    for item, qty, spec, partno, price, flag in rows:
        lines.append(f"| {item} | {qty} | {spec} | {partno} | {price} | {flag} |")
    lines += [
        "",
        "## Sourcing notes",
        "",
    ]
    lines += [f"- {n}" for n in SOURCING_NOTES]
    lines += [
        "",
        "Own-printer builds land near the low end (filament only); print-service",
        "sourcing near the high end. The driver is maker-supplied (Kingstate 40 mm,",
        "params MEASURED) — its price is the widest estimate.",
        "",
    ]
    return "\n".join(lines)


def write_bom(path="BOM.md"):
    with open(path, "w") as f:
        f.write(_markdown(bom_rows()))
    return path


if __name__ == "__main__":
    print("wrote", write_bom())
