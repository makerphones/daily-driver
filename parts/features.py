# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Reusable mechanical primitives — established convention, authored ONCE.

These are solved-by-practice mechanical features: screw bosses, posts, fillets,
threads, snaps. They are NOT taste and NOT regenerated per part by AI or
re-derived by hand each time. Author each one here from established practice,
then REUSE it across parts. Taste (proportions, vent form, where things go)
stays in params.py + the parametric geometry in parts/*.py. See
docs/design-pipeline.md, "Taste vs. convention".

STATUS: STUB. Signatures and intent only — no implementation yet.

MIGRATION NOTE (future step, do NOT do as part of pipeline setup):
parts/cup.py step 3 currently inlines the baffle-mounting boss + heat-set-insert
bore logic. That is exactly the kind of convention that belongs here. When these
primitives are implemented, refactor cup.py to call boss()/screw_post() instead
of building bosses inline, sharing only through params.py (no cross-part
imports). Flagged in DESIGN-LOG.
"""

import cadquery as cq


def boss(wp: cq.Workplane, diameter: float, height: float) -> cq.Workplane:
    """Add a cylindrical boss (e.g. for a heat-set insert or screw).

    STUB — not implemented. Intended to be the single, reused definition of a
    mounting boss, authored from convention (wall-tie, draft, fillet at base).
    """
    raise NotImplementedError("features.boss() is a stub — author from convention")


def screw_post(wp: cq.Workplane, diameter: float, height: float,
               bore: float) -> cq.Workplane:
    """Add a screw post: a boss with a clearance/insert bore down its axis.

    STUB — not implemented. Intended as the reused post primitive (pairs with
    a clearance hole on the mating part).
    """
    raise NotImplementedError("features.screw_post() is a stub — author from convention")
