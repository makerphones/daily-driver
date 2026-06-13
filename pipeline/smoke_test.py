# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
FAL smoke test — confirm auth + connectivity with ONE minimal image call.

This is the cheapest possible check that the FAL pipeline is wired up: it loads
FAL_KEY from .env, makes a single small `flux/schnell` (fast/cheap) generation,
and prints the resulting image URL. It does NOT save anything into the repo.

NOTE: FAL is pay-per-call. This makes one real (small) billable request.

Usage:
    source .venv/bin/activate
    python pipeline/smoke_test.py
"""

import os
import sys
from pathlib import Path

# Cheapest current Flux text-to-image variant — fine for a connectivity check.
# (The real pipeline's model slugs live in pipeline/config.py.)
SMOKE_MODEL = "fal-ai/flux/schnell"

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"


def load_env(path: Path) -> None:
    """Minimal .env loader (no external dependency). KEY=VALUE per line."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key.strip(), value)


def main() -> int:
    load_env(ENV_PATH)

    if not os.environ.get("FAL_KEY"):
        print(
            "ERROR: FAL_KEY is not set.\n"
            f"  Put it in {ENV_PATH} as a line:  FAL_KEY=your-key-here\n"
            "  (.env is gitignored; never commit the key.)",
            file=sys.stderr,
        )
        return 1

    try:
        import fal_client
    except ImportError:
        print(
            "ERROR: fal_client not installed. Run:  pip install -r requirements.txt",
            file=sys.stderr,
        )
        return 1

    print(f"Calling {SMOKE_MODEL} (one small billable image)...")
    try:
        result = fal_client.subscribe(
            SMOKE_MODEL,
            arguments={
                "prompt": "a single matte charcoal sphere on a plain background, "
                "studio product photo",
                "image_size": "square",
                "num_images": 1,
            },
        )
    except Exception as e:  # noqa: BLE001 — surface any auth/network/billing error
        print(f"FAL call FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        print(
            "  Common causes: bad/expired key, or billing/credits not set up "
            "(FAL is pay-per-call).",
            file=sys.stderr,
        )
        return 1

    images = result.get("images") or []
    if not images:
        print(f"Call returned but no images in result: {result}", file=sys.stderr)
        return 1

    print("SUCCESS — FAL auth + connectivity confirmed.")
    print(f"  image URL: {images[0].get('url')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
