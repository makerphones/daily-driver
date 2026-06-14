# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Stage 2 — Image -> rough 3D REFERENCE BODY.

!!! REFERENCE BODY ONLY — NOT A MANUFACTURABLE PART. !!!
The mesh this produces is a blobby proportion/silhouette reference for eyeballing
stance in 3D. It has no dimensions, no features, no manufacturability, and is
NEVER built from. Engineered geometry is authored by hand in CadQuery (Stage 3).
See docs/design-pipeline.md for why there is no render->engineered-CAD step.

Takes ONE chosen concept image (local path or URL), calls the configured
image-to-3D model, and downloads the mesh (GLB/STL) into
design/_scratch/<UTC-timestamp>/ with a manifest.json. Promoting a keeper into
design/reference-meshes/ is a manual curation step (see docs/design-pipeline.md).

Usage:
    python pipeline/gen_reference_mesh.py design/_scratch/<ts>/concept_00.jpg
    python pipeline/gen_reference_mesh.py https://example.com/chosen.jpg
"""

import argparse
import json
import sys
import urllib.request
from pathlib import Path

import config


def resolve_image_url(image_arg: str, fal_client) -> str:
    """Return a URL for the image: pass URLs through, upload local files."""
    if image_arg.startswith(("http://", "https://")):
        return image_arg
    path = Path(image_arg)
    if not path.exists():
        raise SystemExit(f"Image not found: {path}")
    print(f"Uploading local image to FAL: {path}")
    return fal_client.upload_file(str(path))


def find_mesh_url(result: dict):
    """Locate the mesh file URL in the model response (defensive across models)."""
    for key in ("model_mesh", "mesh", "model", "glb"):
        val = result.get(key)
        if isinstance(val, dict) and val.get("url"):
            return val["url"]
        if isinstance(val, str) and val.startswith("http"):
            return val
    # Fallback: any nested dict with a mesh-like url
    for val in result.values():
        if isinstance(val, dict) and isinstance(val.get("url"), str):
            if val["url"].lower().endswith((".glb", ".stl", ".ply", ".obj")):
                return val["url"]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Stage 2 — image -> reference mesh")
    ap.add_argument("image", help="path or URL to ONE chosen concept image")
    ap.add_argument("--model", default=config.MESH_MODEL)
    args = ap.parse_args()

    config.require_fal_key()
    import fal_client

    image_url = resolve_image_url(args.image, fal_client)
    stamp = config.utc_stamp()
    # Raw output always lands in scratch (gitignored). Promoting a keeper into
    # design/reference-meshes/ is a manual curation step.
    out_dir = config.SCRATCH_DIR / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Stage 2: {args.model} -> {out_dir}")
    try:
        result = fal_client.subscribe(args.model, arguments={"image_url": image_url})
    except Exception as e:  # noqa: BLE001
        print(f"FAL call FAILED: {type(e).__name__}: {e}", file=sys.stderr)
        print("  Check key / billing / model slug.", file=sys.stderr)
        return 1

    mesh_url = find_mesh_url(result)
    if not mesh_url:
        print(f"No mesh URL found in result: {result}", file=sys.stderr)
        return 1

    ext = Path(mesh_url.split("?")[0]).suffix or ".glb"
    mesh_name = f"reference{ext}"
    urllib.request.urlretrieve(mesh_url, out_dir / mesh_name)

    manifest = {
        "stage": 2,
        "kind": "reference_mesh",
        "REFERENCE_BODY_ONLY": True,
        "warning": "Reference body only — NOT a manufacturable part. Never build from this.",
        "timestamp_utc": stamp,
        "model": args.model,
        "source_image": args.image,
        "source_image_url": image_url,
        "mesh_file": mesh_name,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"Saved {mesh_name} + manifest.json to:\n  {out_dir}")
    print("  REFERENCE BODY ONLY — proportion/silhouette check, not a part.")
    print("  (raw scratch — promote into design/reference-meshes/ to commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
