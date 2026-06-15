"""
Headless multi-view renders for the Daily Driver build.
Loads a binary STL and writes front/iso/side PNGs with simple directional
shading -- no display, no GL, no VTK. Deps: numpy + matplotlib only.
    python render.py output/cup.stl --out renders --name cup
"""
import sys, struct, argparse, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

CHARCOAL = "#2d3748"
ORANGE   = "#ea580c"

VIEWS = {"front": (0, -90), "side": (0, 0), "iso": (28, -55)}

def load_binary_stl(path):
    with open(path, "rb") as f:
        f.read(80)
        (n,) = struct.unpack("<I", f.read(4))
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    return data[:, 12:48].copy().view("<f4").reshape(n, 3, 3)

def render(stl_path, out_dir, name, size=900):
    tris = load_binary_stl(stl_path)
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    nrm = np.cross(v1 - v0, v2 - v0)
    nlen = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, nlen, out=np.zeros_like(nrm), where=nlen != 0)
    light = np.array([0.3, 0.4, 0.85]); light = light / np.linalg.norm(light)
    shade = np.clip(0.35 + 0.65 * (nrm @ light), 0.15, 1.0)
    base = np.array([0.55, 0.60, 0.66])
    facecolors = np.clip(shade[:, None] * base, 0, 1)
    allpts = tris.reshape(-1, 3); ctr = allpts.mean(axis=0)
    span = (allpts.max(axis=0) - allpts.min(axis=0)).max() / 2 * 1.1
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for view, (elev, azim) in VIEWS.items():
        fig = plt.figure(figsize=(size/100, size/100), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        ax.add_collection3d(Poly3DCollection(
            tris, facecolors=facecolors, edgecolors=(0, 0, 0, 0.08), linewidths=0.2))
        ax.set_xlim(ctr[0]-span, ctr[0]+span); ax.set_ylim(ctr[1]-span, ctr[1]+span)
        ax.set_zlim(ctr[2]-span, ctr[2]+span)
        try: ax.set_box_aspect((1, 1, 1))
        except Exception: pass
        ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
        ax.set_title(f"{name} · {view}", color=CHARCOAL, fontsize=13, pad=4)
        out = os.path.join(out_dir, f"{name}_{view}.png")
        fig.savefig(out, transparent=True, bbox_inches="tight", pad_inches=0.1)
        plt.close(fig); paths.append(out)
    return paths

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("stl"); ap.add_argument("--out", default="renders")
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    name = a.name or os.path.splitext(os.path.basename(a.stl))[0]
    made = render(a.stl, a.out, name)
    print("rendered:", *("\n  " + p for p in made))
