# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Coarse single-start joint thread — the frame↔module twist-lock (Stage 2).

Convention helper (like features.py / hardware.py), NOT a part. Wraps cq_warehouse's
IsoThread so the cup's shiplap lap faces can carry a real printable thread: the
removable MODULE gets the EXTERNAL (male) thread on its spigot, the front FRAME gets
the INTERNAL (female) thread in its socket. Single-start, coarse (FDM-printable).

GUARDED: cq_warehouse is an OPTIONAL dev dependency (requirements-dev.txt). If it's
absent — or a thread fails to build — these return (None, None) and the caller falls
back to the plain slip register, so build.py + gate.py stay importable on the core
deps and never break. The gate's frame/module one-valid-solid manifold checks are the
real go/no-go for whether the threaded joint ships (else the slip register / a bayonet).
"""

import cadquery as cq


def _thread(major_diameter, pitch, length, external):
    """(workplane, min_radius) for an ISO thread, or (None, None) if unavailable.

    min_radius is the ROOT (external) / CREST (internal) radius — the caller sizes the
    spigot core just past the external root for a clean, single-solid fuse.
    """
    try:
        from cq_warehouse.thread import IsoThread
        t = IsoThread(
            major_diameter=major_diameter, pitch=pitch, length=length,
            external=external, end_finishes=("fade", "fade"), hand="right",
        )
        # Re-wrap as a PLAIN cq.Solid (not the IsoThread subclass): OCC transforms
        # re-invoke self.__class__(shape), which IsoThread's __init__ rejects (it
        # wants major/pitch). Same pattern hardware.py uses for the heat-set nut.
        return cq.Workplane(obj=cq.Solid(t.wrapped)), float(t.min_radius)
    except Exception as e:  # noqa: BLE001 — not installed / version drift / build fail
        kind = "external" if external else "internal"
        print(f"  [warn] thread: {kind} IsoThread unavailable ({e}); "
              "joint falls back to the plain slip register.")
        return None, None


def external_thread(major_diameter, pitch, length):
    """Male thread for the module spigot. Returns (workplane, root_radius) | (None, None)."""
    return _thread(major_diameter, pitch, length, external=True)


def internal_thread(major_diameter, pitch, length):
    """Female thread for the frame socket. Returns (workplane, crest_radius) | (None, None)."""
    return _thread(major_diameter, pitch, length, external=False)
