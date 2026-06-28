"""Colored multi-view render of the full assembly (per-part colors) + a junction zoom."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import cadquery as cq
from assembly import make_assembly
from params import P
from parts.head_reference import make_head_reference

asm = make_assembly()
LIGHT = np.array([0.3, 0.4, 0.85]); LIGHT = LIGHT / np.linalg.norm(LIGHT)

parts = []  # (name, tris Mx3x3, rgb)
for child in asm.children:
    if child.name.startswith("head_ref"):
        continue  # the assembly's S/M/L reference heads are for the 3D viewer; render_asm draws its own
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

# The shoulder-screw HEAD (top stop) is a low socket-cap the same steel colour as the shaft, so it
# blends in. Split it out and colour it distinctly so it READS in the assembly render. The head sits
# at global z just below the rod top (yoke_fork_height + 4 + shoulder length).
_HEAD_Z = P.yoke_fork_height + 4 + P.yoke_post_length - 1.0
_HEAD_RGB = np.array([0.95, 0.55, 0.10])
_split = []
for nm, tri, rgb in parts:
    if nm.startswith("yoke_rod"):
        zc = tri[:, :, 2].mean(axis=1)
        if (zc > _HEAD_Z).any():
            _split.append((nm + "_head", tri[zc > _HEAD_Z], _HEAD_RGB))   # the head — orange
        _split.append((nm, tri[zc <= _HEAD_Z], rgb))                      # the Ø6 shoulder/shaft
    else:
        _split.append((nm, tri, rgb))
parts = _split

allpts = np.vstack([p[1].reshape(-1, 3) for p in parts])


def _ellipsoid(center, axes, nu=30, nv=18):
    """Triangulated ellipsoid (Mx3x3) — an abstract 'glass blob' head reference."""
    cx, cy, cz = center
    axx, axy, axz = axes
    u = np.linspace(0, 2 * np.pi, nu)
    v = np.linspace(0, np.pi, nv)

    def P(i, j):
        return (cx + axx * np.cos(u[i]) * np.sin(v[j]),
                cy + axy * np.sin(u[i]) * np.sin(v[j]),
                cz + axz * np.cos(v[j]))
    tris = []
    for i in range(nu - 1):
        for j in range(nv - 1):
            a, b, c2, d = P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)
            tris += [[a, b, c2], [a, c2, d]]
    return np.array(tris)


# Abstract reference HEAD (not real-looking — a translucent ovoid) so the worn fit reads at a
# glance: ears ≈ the cups, crown under the band. Sized to an average adult head and placed from
# the cup geometry (ear level = cup-centre z); deliberately NON-anatomical.
_cup = np.vstack([p[1].reshape(-1, 3) for p in parts if p[0] in ("cup_R", "cup_L")])
_ear_y, _ear_z = _cup[:, 1].mean(), _cup[:, 2].mean()
# Use the REAL reference-head geometry (parts/head_reference — KU100-style ovoid + pinna ears +
# nose/brow + neck), tessellated to triangles, so the poster shows the SAME head as the 3D viewer.
# Posed like the assembly: centred at x=0, lifted by head_ref_z so the ears land at the cups.
def _tessellate(wp, tol=0.4):
    shp = wp.val()
    vs, ts = shp.tessellate(tol)
    v = np.array([[p.x, p.y, p.z] for p in vs])
    return np.array([[v[a], v[b], v[c]] for (a, b, c) in ts])

HEAD = _tessellate(make_head_reference().translate((0, 0, P.head_ref_z)))
HEAD_RGB = np.array([0.55, 0.68, 0.85])   # cool glass tint


def draw(out, views, lim=None, title="", use=None, head=None):
    plist = parts if use is None else use
    n = len(views)
    fig = plt.figure(figsize=(7 * n, 7), dpi=110)
    for i, (vname, elev, azim) in enumerate(views):
        ax = fig.add_subplot(1, n, i + 1, projection="3d")
        if head is not None:
            # Draw the glass head FIRST (behind the opaque parts) so it fills the gaps without
            # muddying the hardware. Low alpha + a cool tint reads as a non-real reference blob.
            hn = np.cross(head[:, 1] - head[:, 0], head[:, 2] - head[:, 0])
            hnl = np.linalg.norm(hn, axis=1, keepdims=True)
            hn = np.divide(hn, hnl, out=np.zeros_like(hn), where=hnl != 0)
            hsh = np.clip(0.55 + 0.45 * (hn @ LIGHT), 0.35, 1.0)
            hfc = np.clip(hsh[:, None] * HEAD_RGB, 0, 1)
            ax.add_collection3d(Poly3DCollection(
                head, facecolors=np.c_[hfc, np.full(len(hfc), 0.16)],
                edgecolors=(0.45, 0.55, 0.7, 0.05), linewidths=0.1))
        for _, tri, rgb in plist:
            nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            nl = np.linalg.norm(nrm, axis=1, keepdims=True)
            nrm = np.divide(nrm, nl, out=np.zeros_like(nrm), where=nl != 0)
            shade = np.clip(0.4 + 0.6 * (nrm @ LIGHT), 0.2, 1.0)
            fc = np.clip(shade[:, None] * rgb, 0, 1)
            ax.add_collection3d(Poly3DCollection(tri, facecolors=fc,
                                edgecolors=(0, 0, 0, 0.05), linewidths=0.15))
        if lim is None:
            base = allpts if head is None else np.vstack([allpts, head.reshape(-1, 3)])
            c = base.mean(0); s = (base.max(0) - base.min(0)).max() / 2 * 1.05
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

# WORN FIT on the abstract glass-head reference — does the cup land at the ear and the band on the
# crown? (front + side + iso). The head is a non-real translucent ovoid, just a sanity gauge.
draw("renders/asm_worn.png",
     [("front", 0, -90), ("side", 0, 0), ("iso", 18, -62)], title="worn ·", head=HEAD)

# Junction zoom on the RIGHT ear (band inner / tube outer). Find the slider bbox.
sl = [p for p in parts if p[0] == "slider_R"][0][1].reshape(-1, 3)
cx, cz = sl[:, 0].mean(), sl[:, 2].mean()
r = 26
lim = ((cx - r, cx + r), (-r, r), (cz - r + 6, cz + r + 6))
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
     [("front (head|<-  ->|out)", 0, -90), ("side", 2, 0), ("iso", 16, -64)],
     lim=lim, title="junction ·", use=bare)
