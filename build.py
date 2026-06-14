# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Build all parts to output/.

Each part is exported as both STL (ready to print) and STEP (clean B-rep for
editing in other CAD). One failing part won't stop the others — you get a clear
per-part status so you can iterate on just the part you're working on.

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

PARTS = {
    "cup": make_cup,
    "baffle": make_baffle,
    "yoke": make_yoke,
    "slider": make_slider,
}

OUT = "output"


def build(names):
    os.makedirs(OUT, exist_ok=True)
    ok, failed = [], []
    for name in names:
        try:
            model = PARTS[name]()
            cq.exporters.export(model, os.path.join(OUT, f"{name}.stl"))
            cq.exporters.export(model, os.path.join(OUT, f"{name}.step"))
            print(f"  [ok]   {name}.stl + {name}.step")
            ok.append(name)
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed.append(name)

    # Cup + baffle assembly (the parts with real geometry), isolated like a part.
    if {"cup", "baffle"} <= set(names):
        try:
            from assembly import make_assembly
            make_assembly().export(os.path.join(OUT, "assembly.step"))
            print("  [ok]   assembly.step (cup + baffle)")
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
