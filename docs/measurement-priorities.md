# Measurement priorities — what to measure, when, and why

The design churns when measurements arrive out of order or get re-taken. This is
the ranked list of open measurements: **Tier 1 blocks the first print**, Tier 2 can
wait for the second print / acoustic loop. Each one says which param it sets, the
risk if it's wrong, and how to capture it. Measure Tier 1 with calipers + a photo
(scale reference in frame) before printing anything load-bearing.

> Rule of thumb: if a part **regenerates from** the number, it's Tier 1. If the
> number only **tunes** a part, it's Tier 2.

## Tier 1 — measure before the first print

| # | Measurement | Sets (param) | Risk if wrong | How |
|---|---|---|---|---|
| 1 | **Earpad cup-mount skirt Ø** (the diameter the pad's inner skirt stretches over — NOT the 60 mm ear hole, NOT the 100 mm foam OD) | `cup_outer_diameter` → cascades to lip, pivot bosses, `yoke_pivot_centres`, ear spacing | Pad won't seat, or the whole cup is the wrong size and everything downstream regenerates wrong | Turn the Dekoni pad inside-out; caliper the mounting opening / groove ID. Photo top-down with a ruler. |
| 2 | **Bow relaxed radius** + **developed (rolled-out) length** | `bow_radius`, `bow_developed_length` → ear spacing, slider height, arc angle | Wrong ear spacing → fit is off; worn-pose geometry wrong | Roll the bow across a ruler (length); lay it on paper, trace the arc, R = chord/sagitta or fit a circle. Photo with ruler. |
| 3 | **Driver OD** (40 / 42 / 50 mm class) + frame depth | `driver_od` → aperture, recess, guard all derive | Driver won't drop into the baffle recess; aperture wrong | Caliper the frame OD and the seat-flange depth. |

These three are the spine: pad → cup size, bow → fit, driver → baffle. Lock them
and most of `params.py` regenerates coherently.

## Tier 2 — measure before the second print or the REW/acoustic loop

| Measurement | Tunes (param) | How |
|---|---|---|
| Pad flange/groove depth + skirt thickness | `pad_lip_extension`, `pad_lip_thickness` (how far the lip sticks out / how thin) | Caliper the pad's mounting groove depth |
| Bow end-tab hole Ø + pitch | `bow_endtab_hole_*`, slider mount-bore pattern | Caliper hole Ø + centre-to-centre |
| Bow thickness + width confirm | `bow_thickness`, `bow_width` (33 mm looked wide — confirm flat-strap width) | Caliper the flat strap, not across a curve |
| Bow **worn** radius (on a head) | `bow_worn_radius` → ear spacing fine-tune | Pose on a head/form; note arc ≥180° for clamp |
| Baffle screw head height | insert/counterbore depth floor | Caliper the M3 head |
| Damping material + mass | acoustic tuning (later) | Scale + notes |

## What's currently a guess (so you know what you're de-risking)

From the DESIGN-LOG, these ship as `ESTIMATE`/`TBD` today and want Tier-1/2 numbers:
`cup_outer_diameter=90` (Tier 1, pad), the whole bow block (Tier 1/2),
`driver_od=42` (Tier 1), `pad_lip_extension=5`/`thickness=2` (Tier 2, reaches Ø100
so likely shrinks once the real groove is measured), `bow_worn_radius=78` (Tier 2).

## Capture standard (so a number is never ambiguous later)

- **Scale reference in every photo** — a steel ruler, or a printed Ø25 mm
  calibration disk you keep on the bench. Caliper readings beat photos; photos
  catch what you forgot to measure.
- **Record the number AND its confidence** in the brief / params comment:
  `MEASURED` / `ESTIMATE` / `TBD`. Never invent a number to make geometry "work".
- After measuring: set the param → `build.py` (N/N) → `gate.py` (0 HARD) →
  DESIGN-LOG entry → commit → push. The ESTIMATE is overwritten cleanly.
