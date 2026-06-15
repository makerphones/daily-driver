# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Build all parts to output/.

Printed parts (cup, baffle, fork-yoke, slider) export as both STL (ready to
print) and STEP (clean B-rep). The BOW is a REFERENCE body (bought Beyer part /
DIY blank) — STEP only, never in the printed-STL set. One failing part won't stop
the others; you get a per-part status so you can iterate on just one part.

Usage:
    python build.py            # build everything
    python build.py cup baffle # build only named parts
"""

import sys
import os
import cadquery as cq

from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.bow import make_bow

# Printed parts → STL + STEP.
PRINTED = {
    "cup": make_cup,
    "baffle": make_baffle,
    "yoke": make_yoke,
    "slider": make_slider,
}
# Reference bodies → STEP only (NOT printed).
REFERENCE = {
    "bow": make_bow,
}
PARTS = {**PRINTED, **REFERENCE}

OUT = "output"


def build(names):
    os.makedirs(OUT, exist_ok=True)
    ok, failed = [], []
    for name in names:
        try:
            model = PARTS[name]()
            cq.exporters.export(model, os.path.join(OUT, f"{name}.step"))
            if name in PRINTED:
                cq.exporters.export(model, os.path.join(OUT, f"{name}.stl"))
                print(f"  [ok]   {name}.stl + {name}.step")
            else:
                print(f"  [ok]   {name}.step  (REFERENCE — not printed)")
            ok.append(name)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed.append(name)

    # Full side assembly (cup + baffle + yoke + slider + bow ref), isolated.
    if PRINTED.keys() <= set(names):
        try:
            from assembly import make_assembly
            make_assembly().export(os.path.join(OUT, "assembly.step"))
            print("  [ok]   assembly.step (cup + baffle + yoke + slider + bow ref)")
        except Exception as e:
            print(f"  [FAIL] assembly: {e}")

    print(f"\nBuilt {len(ok)}/{len(names)}: {', '.join(ok) or 'none'}")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    requested = sys.argv[1:] or list(PARTS.keys())
    unknown = [n for n in requested if n not in PARTS]
    if unknown:
        print(f"Unknown part(s): {', '.join(unknown)}")
        print(f"Available: {', '.join(PARTS)}")
        sys.exit(2)
    print("Building Daily Driver parts...\n")
    build(requested)
