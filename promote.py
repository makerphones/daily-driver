#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Promote the live BETA build to the STABLE channel.

Two channels are published to the daily-driver GitHub Pages (which serves `docs/`):

  • BETA / live   — `docs/models/`        + `docs/renders/`        (rebuilt by build.py
                    on EVERY push; the website's *beta* page shows this)
  • CURRENT build — `docs/models-stable/` + `docs/renders-stable/` (a frozen snapshot;
                    the website's main *current build* page shows this)

`build.py` only ever touches the beta dirs. When the live build is good enough to be the
"current build" everyone sees, run this to copy beta → stable, then commit + push:

    .venv/bin/python promote.py
    git add -A && git commit -m "Promote build <sha> to current" && git push

Idempotent: re-running just refreshes the snapshot. Nothing here rebuilds geometry —
run build.py + gate.py first and be happy with the beta page.
"""

import datetime
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
PAIRS = [("docs/models", "docs/models-stable"),
         ("docs/renders", "docs/renders-stable")]


def main() -> None:
    for src, dst in PAIRS:
        s, d = ROOT / src, ROOT / dst
        if not s.exists():
            raise SystemExit(f"missing {src} — run build.py first")
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(s, d)
        n = sum(1 for _ in d.rglob("*") if _.is_file())
        print(f"  promoted {src} -> {dst}  ({n} files)")

    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT).decode().strip()
    except Exception:  # noqa: BLE001
        sha = "unknown"
    stamp = f"Current build promoted from {sha} on {datetime.date.today().isoformat()}\n"
    (ROOT / "docs" / "STABLE.txt").write_text(stamp)
    print(f"  wrote docs/STABLE.txt  ({stamp.strip()})")
    print("\nNow: git add -A && git commit -m 'Promote build to current' && git push")


if __name__ == "__main__":
    main()
