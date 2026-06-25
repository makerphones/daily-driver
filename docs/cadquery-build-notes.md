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
5. **Accept square + flag it.** The wraparound yoke stays a flat bar because every
   rounded-tube construction (incremental union, batch `combine()`, per-arm
   `combine()`, swept circle) fragmented when fused with the eyes/hub + bore cuts.
   Logged in DESIGN-LOG; hand-finish the print or round that one part in another
   tool if it matters.

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
