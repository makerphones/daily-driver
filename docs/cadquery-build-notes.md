# CadQuery / OCC build notes — what this kernel can and can't do

The Daily Driver CAD runs on a CadQuery + OCP/OCC build whose **boolean and
finishing operations are fragile**. This file is the hard-won map of what works,
so future parts (and future headphones) don't re-discover it the slow way. If a
fillet "doesn't show up" or a part comes out as several invalid solids, it is
almost always one of the limits below — not a logic bug in the part.

## The one rule that matters most

**Round (fillet/chamfer) on CLEAN geometry, BEFORE you cut pockets/bores.**

`.fillet()` and `.chamfer()` raise `Standard_Failure: BRep_API: command not done`
on any solid that already has pockets, bores, or unioned features. They succeed on
a fresh primitive (a plain box, a clean disc) or a single isolated edge.

```python
# WORKS — round the box, then cut into it
slider = cq.Workplane("XY").box(w, d, h).edges().fillet(2.5)
slider = slider.cut(pocket).cut(bore)        # cuts after the fillet are fine

# FAILS — cut first, then try to round
slider = cq.Workplane("XY").box(w, d, h).cut(pocket)
slider = slider.edges("|Z").fillet(2.5)      # BRep_API: command not done
```

## What works / what fails (measured 2026-06-25)

| Operation | Status | Notes |
|---|---|---|
| `.fillet()` on a clean box/disc | ✅ | any/all edges |
| `.fillet()` after a cut/pocket | ❌ | `BRep_API: command not done` |
| `.chamfer()` after a cut | ❌ | same failure as fillet |
| `.fillet()` on one isolated outer edge of a complex part | ⚠️ | sometimes (cup front rim `>Z` worked; cup back `<Z` failed) — test it |
| `revolve` | ❌ | unusable — build arcs from extruded annular sectors or fans of cylinders (see `parts/bow.py`, the yoke stop slot) |
| `sweep` a profile along a path | ✅ | **but** `moveTo(start)` the path first — a bare `.spline(pts)` runs from the origin and mis-places the result |
| union of a FEW clean solids | ✅ | |
| `combine()` / union of MANY solids (~30+) | ❌ | fragments into invalid pieces; unioning rounded arms + eyes/hub then cutting bores also fails |
| extrude / cut / simple union | ✅ | the dependable core |

## Workarounds, in order of preference

1. **Round before cut.** Fillet the blank/primitive, then cut features into it.
2. **Sketch-level (2D) rounding.** Build a rounded profile and extrude it, instead
   of filleting the 3D solid.
3. **Annular sectors / cylinder fans** for arcs (revolve substitute).
4. **Chamfer** where a fillet won't take and the edge is exposed/clean.
5. **Perpendicular-section LOFT for a smooth swept form.** (SUPERSEDES the old "yoke
   stays a flat bar" note.) The wraparound yoke arm is now a single
   `cq.Solid.makeLoft(wires, ruled=False)` through rounded-rectangle sections placed
   perpendicular to the path tangent — a continuous organic tube, ROUNDED with no sharp
   edges along it, in pure cadquery. The key: build each section's rounded-rect wire BY
   HAND (4 line segments + 4 tangent `threePointArc` corners), NOT with `Sketch().fillet()`
   (fillet2D is unreliable on complex faces here). Loft the arm first; union eyes/hub/post
   with each end overlapping DEEP (a tangent kiss → two disjoint solids); cut bores/slots
   LAST. This rounds the form WITHOUT a 3D fillet and WITHOUT the build123d port. (The
   earlier failures — incremental union, `combine()`, swept circle fused with eyes/hub +
   bores — were all trying to round AFTER assembly; lofting the smooth section up front
   sidesteps it. See parts/yoke.py.)

## How to probe quickly

Before committing to a finishing approach on a new part, trial it in isolation and
check `len(v.Solids()) == 1 and v.isValid()`:

```python
def trial(name, fn):
    try:
        v = fn().val()
        print(name, len(v.Solids()), v.isValid())
    except Exception as e:
        print(name, "FAIL", str(e)[:60])
```

A part that builds as `1 solid, valid=True` is sound; `>1 solids` or `valid=False`
means a boolean fragmented — back off to a simpler construction.

## build123d evaluation (2026-06-25) — the path off these limits

Spiked `build123d` 0.11 in an isolated venv to see if it dodges the limits above.
It rides the **same OCCT kernel**, so it is not a magic wand — but it handles the
geometry that fragments cadquery here:

| Test (the cadquery pain points) | cadquery/OCC | build123d |
|---|---|---|
| Small fillet (r ≤ 0.8) after a pocket cut | ❌ any radius (`BRep_API`) | ✅ works |
| Larger fillet (r ≥ 1.5) after a cut | ❌ | ❌ but errors clearly ("try a smaller value") |
| `sweep` a circle along the wrap arc | ⚠️ mis-places the profile | ✅ clean, 1 solid |
| **Full round-tube yoke** — 2 swept tubes + 2 eyes + hub fused, then a bore cut | ❌ **fragments to invalid solids** | ✅ **1 valid solid, 0.7 s** |

**Verdict:** build123d builds the rounded yoke that this cadquery/OCC build can't,
its `sweep` works, and its errors are actionable. It's the realistic path to (a) the
**soft round-section yoke** and (b) fewer boolean surprises generally.

**Recommendation — a planned port, not a mid-stream scramble.** `params.py` (the
single source of truth) stays; the work is porting the part builders + `build.py`,
`gate.py`, `assembly.py` from the cadquery API to build123d's. Do it as a dedicated
effort (good moment: alongside the product-template/platform work, or sooner if the
rounded yoke jumps the queue). Until then **product #1's yoke stays the flat
bracket** — already shipped and gate-clean. Don't half-migrate one part into the
cadquery pipeline; the APIs don't mix cleanly.
