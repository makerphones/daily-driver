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
BASE_STYLE / VISUAL_DESCRIPTORS below. The camera view is varied across the N
images (VIEWS) so the set doesn't read closed — the rear/grille view is always
included.

Output: ALWAYS design/_scratch/<UTC-timestamp>/ (raw, gitignored). Promoting
keepers into design/explorations/ is a manual curation step (see
docs/design-pipeline.md). A manifest.json records per-image prompt/view/seed,
model slug, timestamp, and brief hash.

Usage:
    python pipeline/gen_concepts.py                 # 4 images -> _scratch
    python pipeline/gen_concepts.py --count 6
    python pipeline/gen_concepts.py --seed 12345    # reproducible
"""

import argparse
import hashlib
import json
import sys
import urllib.request

import config

# --- Editable prompt source --------------------------------------------------
# Curated from docs/industrial-design-brief.md. Short, visual, descriptor-style.
# Keep constraints / dimensions / manufacturing notes OUT of here.

BASE_STYLE = (
    "industrial design concept render, studio product photography, neutral "
    "background, soft even lighting"
)

# "open-back" is category jargon, not an appearance — so describe the visual
# signature explicitly AND keep the words "open-back". Positive, concrete
# description is the lever here; do NOT add a negative prompt (FLUX.1 [dev]
# doesn't reward negation). Direction: a HIGH-QUALITY 3D-PRINTED maker object —
# precisely printed and well-finished, not injection-molded polish and not a
# crude prototype. Print quality is expressed positively (clean, precise, even).
VISUAL_DESCRIPTORS = (
    "open-back over-ear headphone, a high-quality 3D-printed object — looks "
    "precisely printed, clean and well-finished, not injection-molded and not a "
    "rough prototype; "
    "matte charcoal printed parts with a fine, even, intentional printed surface "
    "texture, like well-made fine-layer sintered nylon; "
    "designed for printing: generous fillets, chamfered edges, uniform wall "
    "thickness, monolithic printed forms; "
    "the open back is a printed spoked concentric grille — a central hub and two "
    "bold concentric rings joined by a small number of thick radial spokes, "
    "coarse and open enough to see the driver through it (not a fine turbine or "
    "fan); "
    "a slim exposed spring-steel metal headband band anchored into printed "
    "sliders, the bright metal band contrasting the matte printed parts; "
    "printed yoke and gimbal arms with rounded, filleted edges and visible pivot "
    "screws, not thin metal wire and not a blocky molded gimbal; "
    "maker and serviceable detail: exposed stainless socket-head fasteners and "
    "brass heat-set inserts, intentional assembly seams, clearly openable and "
    "repairable; "
    "matte charcoal throughout with a single small warm-orange accent at the "
    "grille hub or a small yoke tag, orange kept minor, never painted across "
    "whole parts"
)

# Vary the camera across the N images so the set doesn't read closed. The REAR
# view is first, so a rear shot showing the open grille is always present (even
# at --count 1). Views cycle if N exceeds the list.
VIEWS = [
    "three-quarter rear view that clearly shows the entire open grille back, "
    "with the driver visible through the grille",
    "three-quarter front view",
    "side profile view",
]


def build_prompt(view: str) -> str:
    return f"{BASE_STYLE}, {view}, {VISUAL_DESCRIPTORS}"


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
    args = ap.parse_args()

    config.require_fal_key()
    import fal_client

    provenance = brief_provenance()
    stamp = config.utc_stamp()
    # Raw bulk runs always land in scratch (gitignored). Promoting keepers into
    # design/explorations/ is a manual curation step — see docs/design-pipeline.md.
    out_dir = config.SCRATCH_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    # One call per image so the camera view can vary across the set (a
    # front-only batch reads closed regardless of wording).
    print(f"Stage 1: {args.model} — {args.count} image(s) -> {out_dir}")
    saved = []
    for i in range(args.count):
        view = VIEWS[i % len(VIEWS)]
        prompt = build_prompt(view)
        arguments = {
            "prompt": prompt,
            "image_size": config.DEFAULT_IMAGE_SIZE,
            "num_images": 1,
        }
        if args.seed is not None:
            arguments["seed"] = args.seed + i  # vary so images differ but stay reproducible

        try:
            result = fal_client.subscribe(args.model, arguments=arguments)
        except Exception as e:  # noqa: BLE001
            print(f"FAL call {i} FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            print("  Check key / billing (FAL is pay-per-call) / model slug.", file=sys.stderr)
            return 1

        images = result.get("images") or []
        if not images or not images[0].get("url"):
            print(f"No image in result {i}: {result}", file=sys.stderr)
            return 1

        fname = f"concept_{i:02d}.jpg"
        urllib.request.urlretrieve(images[0]["url"], out_dir / fname)
        saved.append({
            "file": fname,
            "view": view,
            "prompt": prompt,
            "requested_seed": (args.seed + i) if args.seed is not None else None,
            "result_seed": result.get("seed"),
        })
        print(f"  [{i}] {fname}  ({view.split(' that')[0].split(' view')[0]} view)")

    manifest = {
        "stage": 1,
        "kind": "concept_images",
        "timestamp_utc": stamp,
        "model": args.model,
        "base_style": BASE_STYLE,
        "visual_descriptors": VISUAL_DESCRIPTORS,
        "image_count": len(saved),
        "images": saved,
        "brief": provenance,
        "note": "Form/mood exploration only — nothing here has a dimension. "
        "Raw scratch run; promote keepers into design/explorations/ to commit.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Saved {len(saved)} image(s) + manifest.json to:\n  {out_dir}")
    print("  (raw scratch — promote keepers into design/explorations/ to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
