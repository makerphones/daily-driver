# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Pipeline configuration — the single place to change models, dirs, and defaults.

Swapping a model = editing THIS file only. The Stage scripts (gen_concepts.py,
gen_reference_mesh.py) read everything from here.

Model slugs confirmed against fal.ai (June 2026). Alternatives are listed in
comments so a swap is a one-line edit.
"""

import os
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Models (FAL endpoint ids)
# --------------------------------------------------------------------------

# Stage 1 — text-to-image. Default: FLUX.1 [dev] — stable, good quality/cost,
# well-understood arg schema (prompt / image_size / num_images / seed).
# Swap-ins:
#   "fal-ai/flux/schnell"     cheapest/fastest (1-4 steps) — good for bulk scratch
#   "fal-ai/flux-pro/v1.1"    higher fidelity, pricier
#   "fal-ai/flux-2"           FLUX.2 [dev] — newest family (verify args if used)
IMAGE_MODEL = "fal-ai/flux/dev"

# Stage 2 — image-to-3D. Default: Trellis — ~$0.02/call, fine for a REFERENCE
# BODY (proportion/silhouette only). Input key is `image_url`; output is a GLB.
# Swap-ins (higher quality, pricier):
#   "fal-ai/hunyuan3d/v2"
#   "fal-ai/hunyuan3d-v3/image-to-3d"
MESH_MODEL = "fal-ai/trellis"

# --------------------------------------------------------------------------
# Output directories (relative to the repo root)
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"

DESIGN_DIR = REPO_ROOT / "design"
SCRATCH_DIR = DESIGN_DIR / "_scratch"            # raw bulk runs — GITIGNORED
EXPLORATIONS_DIR = DESIGN_DIR / "explorations"   # Stage 1 curated picks — committed
REFERENCE_MESH_DIR = DESIGN_DIR / "reference-meshes"  # Stage 2 curated picks — committed

# --------------------------------------------------------------------------
# Generation defaults
# --------------------------------------------------------------------------

DEFAULT_IMAGE_COUNT = 4
DEFAULT_IMAGE_SIZE = "square_hd"   # product-shot framing; e.g. landscape_4_3 also fine

# Seed handling: None => let the model choose (recorded in the manifest from the
# response when the model returns it). Set an int for reproducible runs.
DEFAULT_SEED = None

# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------


def load_env(path: Path = ENV_PATH) -> None:
    """Minimal .env loader (no external dependency). KEY=VALUE per line."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def require_fal_key() -> str:
    """Load .env and return FAL_KEY, or raise a clear error if it's missing."""
    load_env()
    key = os.environ.get("FAL_KEY")
    if not key:
        raise SystemExit(
            f"FAL_KEY is not set. Put it in {ENV_PATH} as:  FAL_KEY=your-key-here\n"
            "(.env is gitignored; never commit the key.)"
        )
    return key


def utc_stamp() -> str:
    """UTC timestamp safe for directory names, e.g. 2026-06-13T154233Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
