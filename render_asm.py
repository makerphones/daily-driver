"""Colored multi-view render of the full assembly (per-part colors) + a junction zoom."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cadquery as cq
from assembly import make_assembly

asm = make_assembly()
LIGHT = np.array([0.3, 0.4, 0.85]); LIGHT = LIGHT / np.linalg.norm(LIGHT)

parts = []  # (name, tris Mx3x3, rgb)
for child in asm.children:
    obj = child.obj
    if obj is None:
        continue
    comp = cq.Compound.makeCompound(obj.vals()) if isinstance(obj, cq.Workplane) else obj
    if child.loc is not None:
        comp = comp.located(child.loc)
    verts, idx = comp.tessellate(0.25)
    if not idx:
        continue
    V = np.array([[v.x, v.y, v.z] for v in verts])
    T = np.array(idx)
    rgb = np.array(child.color.toTuple()[:3]) if child.color is not None else np.array([0.6, 0.6, 0.6])
    parts.append((child.name, V[T], rgb))

allpts = np.vstack([p[1].reshape(-1, 3) for p in parts])


def draw(out, views, lim=None, title="", use=None):
    plist = parts if use is None else use
    n = len(views)
    fig = plt.figure(figsize=(7 * n, 7), dpi=110)
    for i, (vname, elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, n, i + 1, projection="3d")
        for _, tri, rgb in plist:
            nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            nl = np.linalg.norm(nrm, axis=1, keepdims=True)
            nrm = np.divide(nrm, nl, out=np.zeros_like(nrm), where=nl != 0)
            shade = np.clip(0.4 + 0.6 * (nrm @ LIGHT), 0.2, 1.0)
            fc = np.clip(shade[:, None] * rgb, 0, 1)
            ax.add_collection3d(Poly3DCollection(tri, facecolors=fc,
                                edgecolors=(0, 0, 0, 0.05), linewidths=0.15))
        if lim is None:
            c = allpts.mean(0); s = (allpts.max(0) - allpts.min(0)).max() / 2 * 1.05
            ax.set_xlim(c[0]-s, c[0]+s); ax.set_ylim(c[1]-s, c[1]+s); ax.set_zlim(c[2]-s, c[2]+s)
        else:
            (xl, xh), (yl, yh), (zl, zh) = lim
            ax.set_xlim(xl, xh); ax.set_ylim(yl, yh); ax.set_zlim(zl, zh)
        try: ax.set_box_aspect((1, 1, 1))
        except Exception: pass
        ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
        ax.set_title(f"{title} {vname}", fontsize=12)
    fig.savefig(out, transparent=False, facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", out)


# Full assembly: front (look along Y, shows inner↔outer), side (along X), iso.
draw("renders/asm_full.png",
     [("front", 0, -90), ("side", 0, 0), ("iso", 22, -60)], title="assembly ·")

# Junction zoom on the RIGHT ear (band inner / tube outer). Find the slider bbox.
sl = [p for p in parts if p[0] == "slider_R"][0][1].reshape(-1, 3)
cx, cz = sl[:, 0].mean(), sl[:, 2].mean()
r = 38
lim = ((cx - r, cx + r), (-r, r), (cz - r, cz + r))
# Hide the pad + earpads so the metal band, recess, cover and tube/post read clearly,
# and recolor the junction parts so the inner→outer stack is unmistakable.
HIDE = {"headband_pad", "earpad_R", "earpad_L"}
RECOLOR = {
    "bow_ref":           (0.90, 0.20, 0.20),   # metal BAND — red
    "headband_clamp_R":  (0.95, 0.75, 0.10),   # COVER (inner, head-side) — gold
    "slider_R":          (0.20, 0.50, 0.90),   # clamp plate + post-bore TUBE — blue
    "thumbscrew_R":      (0.85, 0.30, 0.85),   # thumbscrew — magenta
    "yoke_R":            (0.45, 0.47, 0.50),   # yoke + post (rod) — gray
}
bare = [(nm, tri, np.array(RECOLOR.get(nm, tuple(rgb)))) for nm, tri, rgb in parts if nm not in HIDE]
draw("renders/asm_junction.png",
     [("front (head|<-  ->|out)", 0, -90), ("iso", 18, -62)],
     lim=lim, title="junction ·", use=bare)
