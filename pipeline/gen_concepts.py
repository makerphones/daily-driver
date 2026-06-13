# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Stage 1 — Concept / mood generation.

Generates N concept images from a CURATED visual-descriptor template (NOT a raw
dump of the brief — image models want short, visual, descriptor-style prompts).
Explores FORM only: silhouette, grille language, materials, finish, stance.
Nothing here has a dimension.

The brief (docs/industrial-design-brief.md) is the source of these descriptors
and is hashed into the manifest for provenance, but its prose, constraints, and
dimensions are deliberately NOT sent to the model. To steer the look, edit
BASE_STYLE / VISUAL_DESCRIPTORS below.

Output: design/_scratch/<UTC-timestamp>/ by default (raw, gitignored). Pass
--curated to write straight to design/explorations/<UTC-timestamp>/ (committed).
A manifest.json records prompt, model slug, seed(s), timestamp, and brief hash.

Usage:
    python pipeline/gen_concepts.py                 # 4 images -> _scratch
    python pipeline/gen_concepts.py --count 6
    python pipeline/gen_concepts.py --curated       # -> explorations (keepers)
    python pipeline/gen_concepts.py --seed 12345    # reproducible
"""

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

import config

# --- Editable prompt source --------------------------------------------------
# Curated from docs/industrial-design-brief.md. Short, visual, descriptor-style.
# Keep constraints / dimensions / manufacturing notes OUT of here.

BASE_STYLE = (
    "industrial design concept render, studio product photography, neutral "
    "background, soft even lighting, three-quarter front view"
)

VISUAL_DESCRIPTORS = (
    "open-back over-ear headphone, honest engineered maker aesthetic, "
    "pro-audio sensibility, 3D-print-native form language, "
    "circular cup with a legible open rear grille pattern, "
    "visible modular yoke and slider, spring-steel headband arc, "
    "matte charcoal finish with warm-orange accents, "
    "calm and considered, looks serviceable and modular, not glossy consumer plastic"
)


def build_prompt() -> str:
    return f"{BASE_STYLE}, {VISUAL_DESCRIPTORS}"


def brief_provenance() -> dict:
    """Hash the brief for provenance without sending its prose to the model."""
    brief = config.REPO_ROOT / "docs" / "industrial-design-brief.md"
    if not brief.exists():
        raise SystemExit(f"Brief not found: {brief}")
    data = brief.read_bytes()
    return {
        "path": str(brief.relative_to(config.REPO_ROOT)),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 1 — generate concept images")
    ap.add_argument("--count", type=int, default=config.DEFAULT_IMAGE_COUNT)
    ap.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    ap.add_argument("--model", default=config.IMAGE_MODEL)
    ap.add_argument(
        "--curated",
        action="store_true",
        help="write to design/explorations/ (committed) instead of _scratch/",
    )
    args = ap.parse_args()

    config.require_fal_key()
    import fal_client

    prompt = build_prompt()
    provenance = brief_provenance()
    stamp = config.utc_stamp()
    base = config.EXPLORATIONS_DIR if args.curated else config.SCRATCH_DIR
    out_dir = base / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    arguments = {
        "prompt": prompt,
        "image_size": config.DEFAULT_IMAGE_SIZE,
        "num_images": args.count,
    }
    if args.seed is not None:
        arguments["seed"] = args.seed

    print(f"Stage 1: {args.model} — {args.count} image(s) -> {out_dir}")
    try:
        result = fal_client.subscribe(args.model, arguments=arguments)
    except Exception as e:  # noqa: BLE001
        print(f"FAL call FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        print("  Check key / billing (FAL is pay-per-call) / model slug.", file=sys.stderr)
        return 1

    images = result.get("images") or []
    if not images:
        print(f"No images in result: {result}", file=sys.stderr)
        return 1

    saved = []
    for i, img in enumerate(images):
        url = img.get("url")
        if not url:
            continue
        fname = f"concept_{i:02d}.jpg"
        urllib.request.urlretrieve(url, out_dir / fname)
        saved.append(fname)

    manifest = {
        "stage": 1,
        "kind": "concept_images",
        "timestamp_utc": stamp,
        "model": args.model,
        "prompt": prompt,
        "requested_seed": args.seed,
        "result_seed": result.get("seed"),
        "image_count": len(saved),
        "images": saved,
        "brief": provenance,
        "note": "Form/mood exploration only — nothing here has a dimension.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Saved {len(saved)} image(s) + manifest.json to:\n  {out_dir}")
    if not args.curated:
        print("  (raw scratch — promote keepers into design/explorations/ to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
