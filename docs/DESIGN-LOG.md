# Daily Driver — Design Log

For an open design, the log *is* part of the product. Every decision, every
measurement, every iteration goes here so anyone can follow the reasoning, not
just the result. Newest entries at the top.

---

## 2026-06-24 — Settled decisions from the prior-art review (no geometry)

Recorded rulings from the clean-room prior-art review (Open-Omega CERN-OHL-P;
Capra/Variable Openmod). Logging + parking only — no params, parts, or gate
touched. Each is a decision, not a maybe.

- **DECISION — treble is the unit-to-unit variance budget.** Open-Omega's
  multi-unit FR overlay shows bass/mids clustered to ~±1.5 dB but the treble
  (>3 kHz) fanning to ~±5 dB across nominally identical printed units. So for a
  build-in-public design: **lock the near-ear variables that drive treble** — pad
  seat, baffle-to-ear distance, driver seating, and vent consistency — and
  **publish an FR *band*, not a single "golden" curve.** This shapes the REW loop
  (measure the spread, not one unit) and the eventual FR-publication format in the
  manual. Credit Open-Omega.
- **DECISION — headband is a SOURCED metal bow.** The Beyerdynamic Metal Head Bow
  is the **recommended** part; DIY 1095 spring steel is the metal fallback. A
  printable headband *may* be documented later but is **explicitly not
  recommended** — printed spring arms creep/snap under sustained clamp load
  (Capra's own PETG-arm "breaks if under-printed" warning is the evidence). The
  printed parts are the cup / yoke / baffle / adapter; **the spring stays metal.**
  (The BOM already encodes this: Beyer bow as REF, DIY 1095 as the alt.)
- **DECISION — reference pad locked to Brainwavz HM5 (large velour).** The DIY
  community default (Openmod also uses HM5; ~10 cm velour is the open-back norm).
  Already carried in the BOM and the baffle pad-lip params.
- **PARKED — laser-cut baffle + bonded stainless mesh variant.** Open-Omega's
  approach gives finer treble control, but it **adds a fabrication method (laser
  cut + adhesive bond) that cuts against first-timer buildability.** Keep
  everything printable or easily purchasable for the reference build. Revisit only
  **after the printed baffle is measured** and if treble control demands it.
- **OPEN (do not resolve in CAD) — 40 mm vs 50 mm reference driver.** Held at
  40 mm for identity + first-build forgiveness; the baffle is now parametric so
  the lock is a one-line change. **Resolve by REW measurement, not a spec guess.**
  (Full rationale in the driver-parametric entry below.)

---

## 2026-06-24 — Driver size is now a parameter + a step-down adapter ring

Made driver size a regenerate, not a commitment, and added an accessory ring so
one baffle can host several drivers without a reprint. Build **6/6** (adapter_ring
joins), gate PASS — 21 hard checks, 1 soft (the carried-over stop-slot flag).
Credit: prior-art review (Open-Omega driver-specific vs Openmod's "most 40–52 mm"
+ 52 mm adapter) — re-derived, nothing copied.

- **Parametric baffle.** `driver_aperture` and `driver_recess_diameter` now DERIVE
  from `driver_od` (new `driver_seat_ledge=3.5`: aperture = od − 2·ledge; recess =
  od + cutout_tolerance). The guard spans the derived aperture and the vent ring
  `vent_r` now derives midway between aperture and pad lip, so all of
  aperture/guard/vents stay coherent when `driver_od` changes. **Verified** by
  regenerating at od = 42/50/58: aperture 35/43/51, recess 42.3/50.3/58.3, guard
  span 37/45/53 — baffle stays one valid solid throughout. At od = 64 the new
  **coherence flag fires** (aperture crowds the pad lip → vent ring gone) rather
  than silently breaking — exactly the "FLAG it" ask.
- **Reference build unchanged where it matters.** `driver_od` stays 42 (40 mm
  class, HPD-40N16 candidate); the acoustic aperture stays **35** (unchanged). The
  only delta: the back recess now applies the documented 0.3 mm fit tolerance
  (42 → 42.3) — a coherence fix, not a redesign.
- **Step-down adapter ring** (`parts/adapter_ring.py`, accessory — STL+STEP, NOT
  in the assembly). Worked example: a **50 mm-class host hosting the 40 mm
  reference driver** (params `adapter_*`, independent of `driver_od`). Gated:
  `adapter-ring-wall` 4.0 ≥ 2, `adapter-seat-ledge` 3.5 ≥ 2, manifold 1 solid.
  **Acoustic honesty (flagged):** a step-down ring lengthens/steps the front
  cavity — NOT acoustically neutral. Ring variants are **REW-loop items**, not a
  free swap.
- **Non-round / planar future (hook + TODO).** Added `driver_aperture_shape`
  ("round" only today); `baffle.py` raises `NotImplementedError` for anything
  else. Round-only is built now; an oval / planar-magnetic aperture is a future
  variant — the param surface is ready before the geometry is.
- **Open decision (flagged, do NOT resolve in CAD): 40 mm vs 50 mm reference
  driver.** Community converges on the Peerless/Tymphany HPD family — the 50 mm
  HPD-50N25 is the open-back favorite (Kennerton Vali), while the 40 mm HPD-40N16
  leans closed-back. Held at 40 mm for identity + first-build forgiveness; the
  baffle is now parametric so the lock is a one-line change. **Resolve by REW
  measurement, not by spec guess.**

---

## 2026-06-24 — Yoke structural-floor gate checks (credit: Openmod v1→Mk2)

Codified that the load-bearing yoke can't regress into under-thickness — the
lesson behind Variable Openmod's v1→Mk2 fix (a 1 mm section snapped, thickened to
2 mm) and Open-Omega's analogue. No geometry change; build 5/5, gate **0 hard /
1 soft** (the soft is an intended flag, below). Now 18 hard checks.

- **Current floors (reported) + flagged conflict.** The gate's load-bearing wall
  floor is `MIN_WALL=2.0`; the spec calls for **4.0 mm at structural points**
  (`wall_thickness_structural`). The yoke is load-bearing but had **no dimensional
  gate check at all** (only manifold). Flagged and resolved by adding yoke checks
  at the **4 mm structural floor** (not 2 mm). Did **not** lower the cup's 2 mm
  `MIN_WALL` — that's correct for the 3 mm cup wall.
- **New HARD checks** (`MIN_YOKE_STRUCTURAL = wall_thickness_structural = 4`):
  `yoke-arm-structural` (min arm t/w 5.0 ≥ 4), `yoke-eye-web` (bearing ring 4.3 ≥
  4), `yoke-hub-wall` ((14−6)/2 = **4.0, exactly at the floor** — flagged as
  no-margin; a measured slider pin or any hub shrink would breach it).
- **Discovered + FLAGGED — the Task-1 stop slot is itself a thin section.** The
  over-rotation slot notches the ⌀12 eye; the web between the slot and the pivot
  bore is **~0.7 mm**, below the 2 mm print floor. New SOFT check
  `yoke-stop-slot-web` surfaces it. It's a non-load-path clearance notch at the
  *unloaded* eye bottom, but it's thin/fragile and **a slot in a ⌀12 eye can't
  keep a ≥2 mm bore web** (would need a much larger eye, or relocating the stop
  off the eye entirely). **Open decision for the human:** accept pending a test
  print, enlarge the eye, or relocate the stop. Not silently resolved.

---

## 2026-06-24 — Pivot over-rotation hard stop (credit: Open-Omega)

Added a physical hard stop to the yoke↔cup pivot so the cup can't be forced past
its range and shear the M3 shoulder screw. The ±20° tilt *clearance* was already
verified; this is the *stop*. Build 5/5, gate PASS (0/0) — now 15 hard checks.
**Re-derived independently from Open-Omega's separate `cup rotation limiter`
(CERN-OHL-P); nothing was copied** — different mechanism, our own geometry.

- **Mechanism:** a small pin on each cup pivot boss (`pivot_stop_pins()` in
  `cup.py`) rides an arc slot cut in the mating yoke eye (`yoke.py`); the slot
  **ends** are the hard stop. Placed at the **bottom of the eye (−Z)**, clear of
  the arm bar that joins at the top — a first attempt at the top (+Z) buried the
  pin in the bar and fragmented the yoke into 13 solids. Slot built from a fan of
  cylinders (this OCP build's `revolve` is unusable — see bow.py).
- **Tuned empirically via the gate probe:** engagement angle ≈ `slot_halfangle +
  deg(clearance/rp)`. Set `pivot_stop_slot_halfangle=22°` → **free through the
  full ±20° working range (0.00 mm³ pin∩yoke), engages ≈ ±29°** (blocked well by
  ±35°). ~9° margin past the working range; never interferes with normal tilt.
- **Gate check `pivot-overrotation-stop`** (new): asserts the working ±tilt rides
  free AND the stop engages before `STOP_OVER_ANGLE` (35°). Uses the shared
  `pivot_stop_pins()` so it verifies exactly what ships; isolated to the pins so
  the eye/boss bearing overlap doesn't pollute the reading.
- **Side change (flagged):** bumped `yoke_pivot_eye_diameter` 11 → 12 so the slot
  clears both the pivot bore and the eye rim without fragmenting (ESTIMATE). The
  tilt-clearance baseline shifted 494 → 515 mm³ accordingly, still well within
  the +20% bound.
- **Scope (flagged):** primary purpose is protecting the pivot/screw. **Cable
  routing isn't designed yet**, so cable protection is a *secondary* benefit to
  revisit once routing exists. All stop dims are ESTIMATE; the engagement angle
  is geometric and should be re-confirmed on a test print (and re-checked once the
  pre-existing eye/boss bearing fit is cleaned up — it currently interferes by
  design as a representative first pass).

---

## 2026-06-24 — build.py emits a hardware BOM (BOM.md)

`build.py` now writes `BOM.md` (new `bom.py`) on a full build — part of the open
product, like the DESIGN-LOG: what a forker needs to source the build. Build 5/5,
gate PASS (0/0), no geometry change.

- **Quantities derived from the design, not hand-typed.** Counts come from
  `params.py` × 2 ears (`baffle_screw_count=4` → 8 baffle screws + 8 inserts;
  `pivot_boss_count=2` → 4 M3 shoulder screws + 4 inserts → 12 inserts total), so
  the BOM tracks the model automatically.
- **Flags carried through:** the Beyer Metal Head Bow is `REF` (~$11,
  north-america.beyerdynamic.com); the shoulder screws, inserts, driver, pads,
  cable, damping, and printed parts are `ESTIMATE` — starting points, with the
  header repeating the project rule to verify prices against the live supplier
  page (never present a guessed price as confirmed). The driver carries the widest
  estimate since it's still unlocked (candidate Peerless HPD-40N16).
- Emitted in the full-build block (a partial `build.py cup` won't rewrite it);
  guarded so the BOM never fails the build. Committed alongside the model.

---

## 2026-06-24 — Real pivot hardware + geometric fit checks (cq_warehouse)

Replaced the placeholder pivot arithmetic with REAL fastener geometry and wired it
into the gate, so the yoke↔cup pivot fit is validated against actual parts. Build
5/5, gate PASS (0 hard / 0 soft) — now 14 hard checks (was 10).

- **cq_warehouse — evaluated, partially adopted (flagged).** It's **git-only**
  (not on PyPI), **dormant since 2023** (gumyr moved to build123d/bd_warehouse),
  and has **NO `ShoulderScrew` class** (confirmed by introspection). But it
  installs `--no-deps` and **imports + builds cleanly on our cadquery 2.7 / OCP
  7.8 stack**, and `HeatSetNut("M3-0.5-Standard","McMaster-Carr")` measures
  **OD 4.70 / length 5.70** — now the REF insert dims. Added to
  `requirements-dev.txt` as an OPTIONAL visualisation dep (declares no runtime
  deps, so it won't disturb the pinned cadquery). The shoulder screw is composed
  from primitives instead (no library class).
- **`parts/hardware.py`** — geometry source of truth is **pure-cadquery primitive
  envelopes** (`shoulder_screw_envelope`, `heatset_insert_envelope`), always
  available on core deps, so the gate + STL build never need cq_warehouse (CI stays
  core-deps-only — verified the gate path doesn't import it). `make_heatset_insert`
  uses the accurate cq_warehouse `HeatSetNut` for the ASSEMBLY VIZ when present,
  else the primitive at the same envelope — so a clearance result never depends on
  which path ran.
- **`params.py`** — added the pivot-hardware block. Insert dims REF (verified);
  shoulder-screw dims ESTIMATE / caliper-pending. **Clarified, not "fixed":**
  `m3_insert_hole_diameter` (4.0) is the *correct undersized thermal-install bore*
  for the 4.70 OD insert (the brass melts/knurls in) — not a mismatch. Wall checks
  use the 4.70 INSTALLED OD (conservative).
- **Gate — 4 new pivot checks, 2 of them geometric:** `pivot-shoulder-spans-eye`
  (8≥5), `pivot-thread-engages-insert` (thread∩insert = 1.00, no bottoming),
  `pivot-insert-wall` (3.65 mm around the 4.70 OD ≥ 1.0), and
  **`pivot-tilt-clearance`** — rotating the cup through the full ±20° about the
  pivot axis adds <1% to the 0° bearing overlap (497 vs 494 mm³). **This resolves
  the open yoke `TODO (tilt clearance)` in-CAD**: the cup shell (≤42 mm) never
  reaches the arms (at x=46) and the boss is coaxial with the tilt axis, so the
  bearing is invariant. A test print should still confirm friction/feel, but
  geometric collision is ruled out. Updated the yoke comment to match.
- **`assembly.py`** — places the shoulder screw + heat-set insert at both pivot
  bosses (viz), guarded so the build never fails on hardware.

---

## 2026-06-24 — Filesystem MCP groundwork (chat-side read access)

Config + docs only — **no geometry change**, build still 5/5, gate PASS (0/0).
Goal: let a chat-side review session read this live working tree, since the
GitHub MCP connector is platform-blocked on this account.

- **No move needed.** `daily-driver` is its own repo nested at
  `~/Projects/makerphones/builds/daily-driver` (gitignored by the parent website
  repo), so it is *already* under `~/Projects`. Verified there are no absolute
  paths baked into the tree (`git grep /Users/...` → none). Added a convenience
  top-level alias `~/Projects/daily-driver -> makerphones/builds/daily-driver`
  (symlink resolves within `~/Projects`, so it stays in-scope for a `~/Projects`
  server).
- **Read-only is a client-side lockdown, not a server flag — flagged finding.**
  Checked the installed `@modelcontextprotocol/server-filesystem` (v2026.1.14)
  source directly rather than guessing: it has **no `--readonly` flag**, takes
  allowed dirs as positional args, and always registers the write tools
  (`write_file`/`edit_file`/`create_directory`/`move_file`). The `readOnly`
  strings in it are only advisory `readOnlyHint` annotations. So the setup doc
  enforces read-only by **denying those four write tools client-side**, and
  documents that "switch to read-write" = drop the deny list. Did not invent a
  flag that doesn't exist.
- Wrote `docs/filesystem-mcp-setup.md` (scoped to `~/Projects` only, the config
  snippet, the read-only mechanism, and the exact manual enable step) + a one-line
  pointer in `CLAUDE.md`. **Nothing is enabled by the repo** — adding the
  connector is a manual step the human takes in the Claude app.

---

## 2026-06-15 — Embed the 3D preview in the manual (keep it on-site)

Follow-up to the entry below. The manual's link-out card sent readers to the
GitHub Pages viewer with no navigation back to makerphones.com. Switched the
manual's Daily Driver page to an **inline `<model-viewer>` embed** so the preview
renders within the site (sidebar/nav intact). To keep it fully on-site the GLB is
now also **hosted on makerphones.com** at `public/models/daily-driver.glb`
(served `/models/daily-driver.glb`); the model-viewer script loads via per-page
Starlight frontmatter `head` (only that page). Verified the Astro build serves
the GLB and injects the viewer + script.

- **Cross-repo artifact — RESOLVED (same day).** Initially copied the GLB into
  the manual's `public/models/`, but that meant re-syncing on every geometry
  change. Switched the manual's `<model-viewer src>` to load the GLB
  **cross-origin** from this repo's GitHub Pages
  (`makerphones.github.io/daily-driver/models/daily-driver.glb`) — a single
  source of truth, no duplicate, nothing to re-sync. Verified the URL is live
  (HTTP 200, `model/gltf-binary`, `access-control-allow-origin: *`, so CORS
  permits the fetch from makerphones.com). Trade-off accepted: the manual's
  preview now depends on this repo's Pages staying up — fine, since this repo IS
  the canonical home for the design files.
- The README + design-spec callouts (this repo, viewed on GitHub — which strips
  custom elements/scripts) stay as **links** to the Pages viewer; embedding only
  works on the manual.

---

## 2026-06-15 — Surface the live 3D preview from the docs

Linked the published viewer (<https://makerphones.github.io/daily-driver/>, the
`docs/` Pages build page from the prior entry) from the three places people land:

- **README.md** and **docs/design-spec.md** — a blockquote callout near the top
  ("🧊 Spin it in 3D → live 3D preview"), so GitHub readers can inspect before they
  build.
- **The manual's Daily Driver page** (`learn/daily-driver-design-spec.md`, in the
  separate Astro repo) — a branded HTML callout card (charcoal `#2d3748` / orange
  `#ea580c` accent) at the top of the page. Verified the Astro build renders it
  (51 pages built, card + link present in the output HTML); committed in the
  manual repo, noted here.

No geometry change.

---

## 2026-06-14 — Renders, in-browser 3D viewer, and a committed CI gate

Three pieces of build infrastructure so the open design is inspectable and
unprintable parts can't slip through.

**1 · Headless multi-view renders.** New `render.py` parses a binary STL with
numpy and writes front/iso/side PNGs via matplotlib's Agg backend — no display,
no GL, no VTK, so it can't reintroduce the OCP-viewer port/version problems.
`build.py` calls it behind a guarded import (`_HAVE_RENDER`): after each STL
export it renders, wrapped so a render failure never fails the build, and a
forker with only the core deps still builds parts (rendering just skips).
`matplotlib>=3.8` is **render-only** — it lives in `requirements-dev.txt`, not
`requirements.txt`, keeping the core build pure. Renders land in `renders/`
(repo root, NOT gitignored — they ship with the design). Sample:

![cup · iso](../renders/cup_iso.png)

**2 · In-browser 3D viewer.** `build.py` now also exports the assembly to
`docs/models/daily-driver.glb` via CadQuery's glTF exporter
(`asm.export(..., exportType="GLTF")`). **GLB export worked first try** (valid
`glTF` binary, ~1.6 MB) — no three.js/STLLoader fallback needed. A branded
`docs/index.html` build page embeds it with Google `<model-viewer>` (orbit,
auto-rotate, AR) so anyone can spin the assembly before downloading, from any
device. The GLB is an **intentional published artifact**, so it's committed
(unlike the gitignored working STL/STEP); `docs/.nojekyll` serves the GLB + HTML
statically.

**3 · Printability gate → committed CI linter.** The verification ritual we'd
been running by hand is now `gate.py`: it builds the printed parts in-process and
asserts they're printable, exiting non-zero on any HARD failure. Checks are
unchanged, just enforceable — manifold/single-solid (all 4 parts), wall ≥ floor,
grille member ≥ 2 mm, grille open area in range (measured 0.397), pivot clearance,
pivot-insert depth, boss-wall blend, boss-bore wall. Cosmetic/deferred items
(fillets, guard-setback-vs-lamina) are SOFT — they print but don't fail.
Confirmed it passes clean (0 hard, 0 soft) AND fails (exit 1) when a check is
violated. `.github/workflows/gate.yml` runs `build.py` then `gate.py` on push +
PR (incl. forks) with **core deps only** — no render/viewer extras in CI.

**Decisions (logged, not silently resolved):**
- *Where the site lives.* This CAD repo has no web site of its own and the Astro
  manual is a separate repo; `build.py` writes relative paths within this repo.
  The task's example path (`docs/models/…`) and relative embed `src` both fit
  **this repo's `docs/` as the GitHub Pages source**. So the GLB + build page
  live here. **One-time human step:** set the repo's Pages source to
  *Deploy from branch → `main` → `/docs`* for the viewer to go live.
- *"The gate" didn't exist as a file* — it was the inline verification I'd run
  each session. Promoted to `gate.py` without changing any check.

Build stays green (5/5 + assembly + GLB + 12 renders); the only `[warn]`s are the
two carried-forward cosmetic fillet deferrals.

---

## 2026-06-14 — Two flagged fits resolved (baffle lamina, pivot clearance)

Cleared the two real fit flags from the engineering pass, both as ESTIMATE param
bumps (still driver-/print-measured later):

- **Baffle guard lamina.** `baffle_thickness` 4 → **6**, so the front lamina
  (`th − recess_depth`) is now 3 mm — enough to hold the 1.5 mm guard plus the
  full **1.5 mm guard_setback**. The guard-setback `[warn]` is gone (verified:
  guard recessed 1.5 below the front face, baffle still one solid). `recess_depth`
  and `guard_setback` stay parametric; the clamp still warns if a measured driver
  later forces a deeper recess than the lamina can hold.
- **Pivot clearance.** `yoke_pivot_centres` 88 → **92**, putting the boss outer
  face ~4 mm proud of the cup wall (was ~2 mm) — room for boss + insert + fork-arm
  seat. Cup and yoke both still one solid; eyes and bosses align at r=46. **±20°
  tilt clearance is left as a TODO to verify on a test print.**

`build.py` green (5/5 + assembly). Left as-is per scope: grille open fraction
(0.398), the bow extruded-sector workaround (revolve still broken), and the two
cosmetic best-effort fillet `[warn]`s (cup outer edge, yoke junction).

---

## 2026-06-14 — Engineering pass: CAD reconciled to v0.3, all parts authored

Full engineering pass — the CAD now matches the v0.3 spec and every part has real
geometry. We are **not** waiting on measured parts: every dimension is an
ESTIMATE flagged in `params.py` (with `REF` for bought-part references and `TODO`
for genuine unknowns) so a measured value overwrites cleanly later. Worked part
by part, building and verifying after each; `python build.py` is green
(cup/baffle/yoke/slider STL+STEP, bow STEP-only reference, + assembly).

- **params.py** reorganised to the v0.3 stack with an explicit ESTIMATE policy
  banner. Grille **decoupled** from the bosses (its own `grille_outer_ring_radius`);
  bolt circle is now explicit (`baffle_bolt_circle_diameter=70`), not a fraction.
- **Cup.** Bosses moved OFF the grille and BLENDED into the perimeter wall
  (`baffle_boss_diameter=10` so each reaches the inner wall at the bolt circle and
  merges). Grille cleaned (hub 16 / rings 24+32 / 8 spokes). Two **pivot bosses**
  added at 0/180 on the side walls (mid-height), each a through-wall radial boss
  housing an M3 heat-set insert for the fork shoulder screw. Verified: single
  connected solid; **measured open fraction 0.398** (target 0.40).
  - *Deviation flagged:* spec listed `member_w=3`, but at the new ring radii 3.0
    gives 0.51 open. Tuned to **4.0** to hit the 0.40 target (still ≫ 2 mm floor),
    per the standing "size member width to the open-area target" rule. Documented
    in `params.py`, not silently changed.
- **Baffle.** Front-mount plate (od 77, th 4): back driver recess (42×3), raised
  front pad lip (od 62, h 3.5), 4 M3 holes counterbored from the front, controlled
  vent holes. Integral driver guard (6 spokes, 2 mm) across the aperture.
  - *Conflict flagged (not forced):* recess 3 of a 4 mm plate leaves only a ~1 mm
    front lamina — the only solid the guard can anchor to — so the requested
    1.5 mm guard setback can't fit. The guard seats in the lamina and the build
    **warns**; TODO to deepen the plate or shallow the recess once the driver is
    measured. The REF dome-proud vs recess-depth also suggests a dome/guard
    clearance check — flagged in `baffle.py`.
- **Fork-yoke.** DT880 wishbone: two arms from a top swivel hub (vertical bore,
  mates the slider) down to two pivot eyes (M3 clearance) at `yoke_pivot_centres`.
  Arms routed vertically past the cup then angled in — a straight eye→hub bar would
  pass through the cup. TODO: ±tilt clearance against the real cup pose.
- **Slider.** Clamp block with a vertical bow channel, a bottom swivel bore
  (mates the fork hub), and an M3 grub boss pressing a friction pad onto the bow.
- **Bow (REFERENCE only).** Bought Beyer / DIY 1095 — modelled as a reference
  body (arc band + relief slot + end-tab holes), STEP only, excluded from the
  printed-STL set. NOTE: this OCP build's `revolve` fails outright (`BRep_API:
  command not done`) even on a textbook offset revolve — built the band from
  **extruded annular sectors** instead. Bow dims are TBD from the measured part.
- **assembly.py / build.py / show.py.** Assembly now poses the full one-side chain
  (cup → baffle → yoke → slider → bow ref); the bow pose is representative
  (full head-size kinematics TBD). build.py splits PRINTED (STL+STEP) from
  REFERENCE (STEP only). Assembly loads and exports (5 parts).

Carried-forward `[warn]`s unchanged: cup outer-edge comfort fillet (no-op on the
cylinder) and the yoke junction fillet (OCC declines it) — both best-effort and
caught, geometry is unaffected.

---

## 2026-06-14 — Off EOL Python 3.9 → 3.13; stack updated; ocp_vscode matches the extension

Moved the repo's environment off end-of-life Python 3.9 (EOL Oct 2025) to
**Python 3.13.14**, and updated the CAD stack to match the installed OCP CAD
Viewer extension (3.4.0) — chosen over downgrading the extension now that we're
on a current Python.

- **Why 3.13.** Newest Python with prebuilt macOS-arm64 wheels across the whole
  stack: `cadquery-ocp` ships arm64 wheels for cp310–cp313 (no cp314 yet), so
  3.13 is the ceiling. `ocp_vscode` 3.4.0 and `cadquery` 2.7.0 both need >=3.10.
- **Interpreter source.** The Homebrew `python@3.13` bottle was unusable on
  macOS 26.2 — its `pyexpat` failed to load (`Symbol not found:
  _XML_SetAllocTrackerActivationThreshold` vs the system libexpat), which breaks
  pip bootstrap. Switched to the **python.org 3.13.14 universal2 installer**
  (`/Library/Frameworks/Python.framework/Versions/3.13`), which bundles its own
  libexpat — `pyexpat`/pip/ssl all clean.
- **New stack.** Python 3.13.14 · CadQuery **2.7.0** · cadquery-ocp
  **7.8.1.1.post1** · ocp_vscode **3.4.0** (matches the 3.4.0 extension —
  resolves the viewer mismatch by upgrading) · fal-client 1.0.0.
- **Verified.** `build.py` exports all four parts + assembly.step on 3.13 (same
  pre-existing fillet [warn]s, unchanged). `show.py` now gets past port discovery
  ("Using port 3939") with no TypeError and no `find_port()` ValueError — the
  3.4.0 package fixed that; full connect just needs the live panel.
- **Env swap.** New env built at `.venv-new`, then swapped into `.venv` (the path
  VS Code points at) with relocated script paths fixed; the old 3.9 env is kept
  as `.venv-old` (backup, not deleted until confirmed working).
- **Pins.** `requirements.txt` → `cadquery>=2.7,<2.8`; `requirements-dev.txt` →
  `ocp_vscode==3.4.0`. Both verified to resolve against the new env with no
  changes needed.

---

## 2026-06-14 — Direction locked: DT880-family, around-ear (docs-only pass)

Settled the Daily Driver's direction and rewrote the spec to match — **docs only, no CAD/geometry
touched** (no `params.py`, no `parts/*.py`). The form is the **Beyerdynamic DT880 family**:
spring-steel **bow** → printed **slider** (height + swivel) → printed **fork-yoke** (±20° tilt) →
printed **cup** → printed **baffle** → driver → pad. Explicitly **not** Grado-minimal (on-ear,
too small/fiddly) and **not** DCA thin-metal (only makes sense in metal fab, not FDM).

Resolved decisions captured in `design-spec.md` (→ **v0.3**):

- **Headband.** Design the slider/mount to accept the **Beyerdynamic Metal Head Bow as a drop-in**
  (~$11, sourced); DIY 1095 spring steel to the same geometry stays as the maker option. Exact bow
  dims are **TBD from the measured part** — slider + jig geometry derive from a real bow on the bench.
- **Pivot (yoke↔cup).** **Screw-pin** — M3 shoulder screw through the fork arm into a heat-set
  insert in the cup. **Supersedes** the old "project's own 6 mm pivot post" interface.
- **Baffle.** **Front-mount** plate (OD ~77, ~4 mm); **integral raised pad lip ⌀62** (pad-lip
  location now resolved to the baffle, not the cup); **⌀35 aperture with an integral printed driver
  guard**; **⌀42 driver pocket** on the back; 4 M3 rim screws **counterbored from the front, hidden
  under the pad**; controlled venting + a damping spot, **not a hard seal**.
- **Cup.** Shell + integral grille (hub + 2 rings + 8 spokes, ~40% open, members ≥ 2 mm). The 4 M3
  bosses move to **blended-into-the-perimeter-wall**, clocked off the pivot axis — **supersedes** the
  free-standing 70%-radius posts, and decouples the grille's outer ring from the boss radius.
- **Driver.** ~40 mm dynamic, **candidate Peerless HPD-40N16** (not locked — baffle stays
  parametric), damped with a rear air space. **Pad:** Brainwavz HM5 oval velour ~90 mm.
- Every dimension flagged as a **first-pass starting value pending measured parts.**

Added three sections to the spec — **Parts table**, **Interfaces** (the 3 joints: cup↔baffle
front-mount, yoke↔cup screw-pin, yoke↔bow slider), and an updated **BOM** with the bow sourcing
link. Created **`docs/drawings/`** with schematic SVG sheets (assembly + cup/baffle/yoke/slider/bow),
each referenced from its spec section; all six render clean. Added a reconciliation banner to
`industrial-design-brief.md` so its older "Locked" bullets point to the resolved spec.

**Deferred to the next engineering pass (NOT this pass):** clean grille, relocating the cup bosses
to the perimeter wall, the integral driver guard, and real yoke/slider/bow geometry — the current
CAD still reflects the older boss placement and stubbed yoke/slider.

---

## 2026-06-14 — Design-pipeline doc: one workflow (Diverge → Resolve → Engineer)

Captured the refined workflow in `docs/design-pipeline.md` (→ v0.2). Added a
top-level **Diverge → Resolve → Engineer** section near the start and folded the
old "three stages" under it as tooling detail, so the doc now has ONE model, not
two competing ones. **Resolve** was the missing layer: developing a picked
direction into a buildable design in chat (parts/fit/fasteners + the
engineering-taste calls — connector, acoustics, wall, weight, cross-part design
language), via schematic SVG sketches and reasoning, before any geometry. Diverge
= old Stage 1 (Stage 2 image→3D is an optional sub-tool); Engineer = old Stage 3.
Handoffs: picked screenshots into chat (Diverge→Resolve), a precise CC prompt
carrying resolved intent (Resolve→Engineer). The boundary (no render →
engineered CAD) and taste-vs-convention sections were reconciled to read
alongside it (taste is decided in Resolve, only encoded in Engineer).

---

## 2026-06-14 — Real concentric-ring grille authored (replaces placeholder vents)

Authored the real rear grille into the cup, replacing the placeholder slot ring
entirely. This **closes the "first-pass vent grille" carry-forward** (#2 in the
2026-06-13 form-direction entry).

**Structure (v1, fully parametric so it tunes after we see it).** Remaining
material = a center hub + two concentric rings + 8 radial spokes; the gaps
between them open to the driver. Spokes: 4 aligned to the baffle-boss positions,
4 between them. Built as an annular CUTTER (zone disc minus the kept members)
cut from the closed back, *before* the bosses are added so no boss column is
sliced.

**Boss/vent collision resolved.** The outer ring's centerline lands on the
baffle-boss radius — `P.grille_outer_radius` is a property that returns
`P.baffle_screw_radius`, so it references the boss radius instead of duplicating
it. The 4 bosses now sit as NODES on the outer ring (verified: back plate is
solid under each boss, columns intact), so the screws reinforce the grille
rather than colliding with a slot. The outer ring's outer edge meets the solid
rim, so the grille is continuous with the shell.

**Open area.** New params in `params.py` (all flagged): `grille_ring_count=2`,
`grille_spoke_count=8`, `grille_hub_diameter=12`, `grille_inner_ring_radius=15`,
`grille_member_width=3.8`, `grille_member_min_width=2.0` (FDM floor),
`grille_target_open_fraction=0.40`. Member width was sized by area-sampling the
2D pattern to hit ~0.40 open; 3.8 mm lands it and every member stays well above
the 2 mm print floor (no need to hold the floor and report a worse number).
**Measured open fraction from the built solid = 0.401** over the grille zone
(radius 29.2 mm) — on target.

**Verified.** `python build.py` green (cup/baffle/yoke/slider + assembly all
export). Cup body is a single connected solid with the grille. (The separate
2nd solid is the pre-existing floating yoke boss — confirmed it was already
detached on HEAD; untouched this pass per scope.) The pre-existing fillet
[warn]s are unchanged and unrelated.

Not touched this pass: yoke/slider form, the floating-yoke-boss carry-forward,
boss screw direction, pad-lip interface — all still open.

---

## 2026-06-14 — Pin the VS Code viewer extension to 2.6.x (match the package)

Reconciled the OCP CAD Viewer mismatch the low-risk way: **downgrade the VS Code
extension to match the Python package**, not the reverse. The package stays
`ocp_vscode==2.6.2` and the env is untouched (Python 3.9.6 / CadQuery 2.5.2 /
OCP 7.7.2).

- **Why not bump the package.** `ocp_vscode` 3.4.0 declares `requires_python
  >=3.10` (confirmed via PyPI); 2.6.2 is `>=3.9`. Bumping to 3.4 would force a
  Python upgrade off the working 3.9.6 and likely reinstalls of OCP/CadQuery —
  exactly the disruption to avoid for a viewer convenience.
- **Action.** Pin the `bernhard-42.ocp-cad-viewer` extension to **2.6.2** (exact
  match; 2.6.1/2.6.3/2.6.4 also exist on the Marketplace, major.minor 2.6 is what
  must match). The `code` CLI isn't on PATH, so it's installed manually via the
  Extensions panel → "Install Specific Version…" → 2.6.2, then disable auto-update
  for that extension so it can't jump back to 3.4.0.
- **Unchanged:** ocp_vscode, CadQuery, OCP, Python, and requirements-dev.txt
  (pin stays 2.6.2).

---

## 2026-06-14 — Fix show.py for the ocp_vscode 2.6.2 API

`show.py` was written against an older API and crashed with
`TypeError: show() got an unexpected keyword argument 'name'`. In 2.6.2 the
signature is `show(*cad_objs, names=None, ...)` — `names` is a list, no singular
`name=`. Fixed to `show(make_assembly(), names=["daily_driver_cup_baffle"])`;
`show()` is the only ocp_vscode call in the repo. Confirmed it now runs past the
`show()` call with no TypeError.

Noted for later (NOT fixed): with no viewer running it then fails in
`find_port()` with a `ValueError` (port discovery), and there's a likely
version mismatch — VS Code extension `bernhard-42.ocp-cad-viewer` is **3.4.0**
while the `ocp_vscode` package is pinned to **2.6.2**. Line these up to clear the
port/`--backend measure-tool` errors in a later pass.

---

## 2026-06-14 — Viewer dev-deps split out

Split the live-viewer dependency from the core build deps: `ocp_vscode==2.6.2`
now lives in a new `requirements-dev.txt` (which pulls in `requirements.txt` via
`-r`), not in `requirements.txt` — `build.py` doesn't need it. README and a
`requirements.txt` comment point to it. Confirmed `.vscode/` is gitignored so a
machine-specific interpreter path never gets committed.

---

## 2026-06-14 — Stage 3 opened: convention primitives, floating-boss fix, cup+baffle assembly

First real-geometry pass. Foundation + convention only — the grille and the
yoke/slider **form** are deliberately untouched (taste passes).

- **Mechanical primitives implemented (`parts/features.py`).** `boss()` (cylinder
  + central blind bore for a brass heat-set insert) and `screw_post()` (same, but
  the bore is a screw clearance/pilot) — both stand on a host plane, merge into
  the host, and fillet the base junction so features are tied and printable.
  Shared `_studs()` body; these are convention, reused, not regenerated per part.
  Verified on a clean host: 1 valid solid with 4 base-fillet faces.
- **Params added (flagged defaults).** `boss_base_fillet` (1.0), `screw_post_diameter`
  (7.0), `screw_post_pilot_diameter` (2.5, FLAGGED — confirm vs real screw); plus
  derived `cup_interior_floor_z`, `baffle_seat_z`, `baffle_boss_height`. The
  baffle **flush-seat** at the front rim is a flagged PROVISIONAL assumption (the
  front/pad-lip interface is still open).
- **Floating-boss bug fixed + migrated (`parts/cup.py`).** The inline boss code is
  gone; the cup now calls `features.boss()`. The old bosses were short cylinders
  near the rim touching nothing (unioned as disconnected solids). They're now
  columns standing on the interior back floor, merged + filleted into it — the
  cup (excluding the provisional yoke boss, below) is a single connected solid.
  Vents are now cut **before** the bosses so the cut never slices the columns.
- **Flagged — boss/vent ring collision.** `baffle_screw_radius` (~70% R, 27.3 mm)
  nearly coincides with the placeholder vent ring (~62% R, 26 mm), so the boss
  bases overlap vent slots and the base fillet skips there (it works fine on a
  clean host). The bosses are still merged/connected. To resolve in the **grille
  taste pass**: pattern the real grille around the four boss footprints.
- **Flagged — provisional yoke boss is barely connected.** The cup-side yoke-mount
  placeholder (a cylinder tangent to the curved wall) only touches along a line,
  so the cup currently reports **2 disjoint solids** (cup body + that boss). Left
  untouched on purpose — cup-side yoke attachment is an open question and yoke
  **form** is deferred. Resolve when the yoke-to-cup interface is designed.
- **Basic assembly added (`assembly.py`, `show.py`).** Cup + baffle in their real
  relationship: the baffle flipped so its driver recess faces into the cup, seated
  flush at the front rim on the boss tops. `build.py` exports `output/assembly.step`
  (error-isolated); `python show.py` opens it in OCP CAD Viewer. Assembly verified
  valid and exporting; open it in the viewer to check proportions.
- **Build.** `python build.py` → 4/4 parts export + `assembly.step`. Yoke/slider
  still stubs.

### Carry-forward

- Grille **form** (and patterning it around the boss footprints) — taste pass.
- Yoke/slider **form** + the cup-side yoke mount (fix its connectivity then) —
  taste pass.
- Confirm `screw_post_pilot_diameter` and the provisional baffle flush-seat once
  the real screws and front/pad-lip interface are settled.

---

## 2026-06-14 — Concepts moved to a 3D-printed maker direction

Retuned `VISUAL_DESCRIPTORS` (a human taste call, encoded as written) to aim the
concept exploration at a **high-quality 3D-printed object** — precisely printed
and well-finished, explicitly neither injection-molded polish nor a crude
prototype. Print quality is expressed positively (clean, precise, even,
well-finished); no negative prompt.

- **Printed-maker surface + form.** Matte charcoal printed parts with a fine,
  even, intentional printed texture (described as fine-layer sintered nylon, not
  by acronym); designed-for-print cues: generous fillets, chamfered edges,
  uniform walls, monolithic forms.
- **Architecture cues.** A slim **exposed spring-steel metal band** anchored into
  printed sliders (bright metal contrasting the matte printed parts); **printed**
  yoke/gimbal arms with rounded filleted edges and visible pivot screws (not thin
  wire, not a blocky molded gimbal); maker/serviceable detail — exposed stainless
  socket-head fasteners, brass heat-set inserts, intentional seams, openable.
- **Grille tuning.** Open back is a printed spoked concentric grille: central hub
  + two **bold concentric rings** joined by a **small number of thick radial
  spokes**, coarse/open enough to see the driver — explicitly not a fine
  turbine/fan.
- **Orange restraint.** Matte charcoal throughout with a **single small**
  warm-orange accent (grille hub or a small yoke tag); never painted across whole
  parts.

Ran one default Stage-1 set (4 images) into gitignored `design/_scratch/`. Reads
clearly printed-maker now (matte, filleted, monolithic, visible fasteners), a
strong shift away from the molded-consumer look. Partial on the finer asks: the
grille landed as concentric rings on most views but still drifted to a fine
turbine on one, the spring-steel band read matte rather than bright metal, and
one cup's pad interior came through fully orange. Useful steer for the next
iteration; left in scratch for me to curate.

---

## 2026-06-14 — Open-back descriptor tuning; scripts now default to _scratch

Two refinements to Stage 1 after the first run read **closed-back**.

- **Open-back is now described, not named.** "Open-back" is category jargon, not
  an appearance, so the model rendered a solid shell. `VISUAL_DESCRIPTORS` now
  spells out the visual signature (a human taste call, encoded as written — not
  reinterpreted): the entire rear of each cup is an open metal grille with the
  driver visible behind it; a spoked concentric grille (center hub, two rings,
  radial spokes, echoing the brand mark); see-through and airy; matte charcoal
  with a single warm-orange accent and visible fasteners. The words "open-back"
  stay, paired with the look.
- **Camera view is varied across the N images.** A front-only batch reads closed
  regardless of wording, so `gen_concepts.py` now makes one call per image and
  cycles a `VIEWS` list (rear / front / side) with the **rear/grille view first
  so it's always present**. No negative prompt — FLUX.1 [dev] doesn't reward
  negation; concrete positive description is the lever. Re-ran (4 images): both
  rear views now read clearly open-back.
- **Scripts default to `_scratch`; curation is manual.** Reconciled the code with
  the scratch-vs-curated convention: `gen_concepts.py` and `gen_reference_mesh.py`
  now always write raw runs to gitignored `design/_scratch/<timestamp>/`. The
  `--curated` flag is gone — promoting keepers into `design/explorations/` and
  `design/reference-meshes/` is a manual curation step. Doc layout/how-to-run
  lines updated to match. The earlier `explorations/2026-06-13T214426Z/` run is
  left in place as history.

---

## 2026-06-13 — AI-assisted design pipeline set up (FAL Stages 1 & 2)

Stood up the AI design pipeline that feeds the form pass. It generates **options
and references** — it never produces engineered CAD.

- **Toolchain.** Official FAL Python client (`fal-client`, import `fal_client`,
  reads `FAL_KEY`) confirmed from fal.ai docs and pinned in `requirements.txt`.
  `FAL_KEY` lives in a gitignored `.env`; the key is never committed. Smoke test
  (`pipeline/smoke_test.py`, one minimal `flux/schnell` call) passed — auth +
  connectivity good.
- **Scripts (config-driven, swappable models).** All under `pipeline/`:
  `config.py` is the single place model slugs, output dirs, counts, and seed
  handling live — swapping a model is a one-line edit. `gen_concepts.py`
  (Stage 1) and `gen_reference_mesh.py` (Stage 2) read everything from it.
  Confirmed current slugs: Stage 1 default `fal-ai/flux/dev` (FLUX.1 [dev]);
  Stage 2 default `fal-ai/trellis` (~$0.02/call). Hunyuan3D and FLUX.2 noted as
  documented swap-ins.
- **Stage 1 verified.** Ran one curated generation (3 images, `flux/dev`) →
  `design/explorations/2026-06-13T214426Z/` with a manifest (prompt, model,
  resolved seed, brief hash). Output is on-brief (charcoal + orange, modular).
  Prompts are built from a **curated visual-descriptor template**, not a raw
  dump of the brief.

### The boundary this pipeline encodes

- **No render → engineered-CAD step.** Meshes (Stage 2) are triangle soup, not
  B-rep; and engineered features (screw locations, cup depth, vent area) are
  decisions and measurements, not pixels. Stage 3 — the real parts — is authored
  by hand in CadQuery, on purpose.
- **Taste is human, encoded in code.** Some taste is a number (→ `params.py`),
  some is form (vent shape, grille, cup profile → parametric geometry in
  `parts/*.py`). AI informs taste by showing options; it never sets a dimension
  or authors a part.
- **Convention is reused, not regenerated.** Mechanical primitives (boss, post,
  fillet, thread, snap) live in `parts/features.py`, authored once from
  established practice and reused across parts.
- **Scratch vs. curated.** Raw bulk runs go to gitignored `design/_scratch/`;
  only curated picks land in `design/explorations/` and
  `design/reference-meshes/` and get committed (the open-design story).

### Carry-forward

- **Migrate primitives into `parts/features.py`.** `features.py` is a stub
  (signatures only). `cup.py` step 3 still inlines its baffle-mounting boss +
  insert-bore logic; that convention should move into `features.py` and be
  reused once the primitives are implemented. Not done now (no refactor this
  session) — flagged for a future step. Joins the earlier carry-forwards
  (floating baffle bosses, first-pass vent grille).

---

## 2026-06-13 — Entering the form / industrial-design pass

The functional skeleton is proven — parametric CAD, build pipeline, four parts
exporting as valid solids — so the next pass is **form**. Added
`docs/industrial-design-brief.md`, built from the spec's locked-vs-open section:
it defines what the Daily Driver should look and feel like and frames the form
exploration (cup profile, rear grille, yoke/slider styling, finish) as 3–5
directions to choose from before any more geometry work. The chosen direction
then gets translated back into the parametric model, respecting everything the
brief locks.

**Carry-forward issues to fix when the chosen form goes back into the model**
(noting now so they aren't lost — not fixing here, no geometry changes this
session):

1. **Floating baffle bosses.** The four baffle-mounting bosses are currently
   posts that aren't anchored to the cup wall — they need to tie into the wall
   when the form is rebuilt.
2. **Clunky first-pass vent grille.** The rear vent array is the crude
   area-driven placeholder; the real grille is a form decision (it's the
   signature look) and gets designed in this pass.

---

## 2026-06-13 — First build runs; all four parts export; cup fillet was masking a failure

First time the toolchain ran against the geometry kernel. Set up a venv and
installed CadQuery, then ran `python build.py`.

- **Environment.** Only system Python (3.9.6) is available on this machine — no
  3.10–3.12 as the requirements note prefers. Tried 3.9 anyway since it's the
  empirical path, and it worked: `pip install -r requirements.txt` pulled
  **CadQuery 2.5.2** with **cadquery-ocp 7.7.2** (3.9 wheels exist), and import
  succeeded. No newer Python needed for now.
- **Result.** All four parts export to both STL and STEP, and all four are valid
  solids (`isValid() == True`): cup (65 faces), baffle (13), yoke (9, stub),
  slider (13, stub). The two flagged trouble spots that *did* hold up:
  - **Cup front-face shell** (`faces(">Z").shell(-wall_thickness)`) — works,
    clean open cup.
  - **Side yoke boss** (`Workplane("XZ")` boss union) — works, unions cleanly.
- **The real problem: the cup edge fillet was failing silently.** Step 6
  (`cup.edges("|Z").fillet(edge_fillet)`) raises `BRep_API: command not done`
  every run, and the old `except: pass` swallowed it — so the build printed
  `[ok]` while shipping a cup with **no fillet applied**. Diagnosed why:
  `"|Z"` selects all 51 vertical edges, but ~32 of those are the **vent-slot
  walls** and the rest are boss edges. A 1.5 mm fillet overruns the slot
  geometry and OCC aborts the whole operation. Scoping to the outer wall doesn't
  rescue it either — the cup is a **cylinder**, so its only outer vertical edges
  are the yoke-boss/cylinder intersection (a curved-on-curved saddle), which OCC
  refuses to fillet even at 0.5 mm.
- **Conclusion (not silently resolved).** A cylindrical first-pass form has no
  sharp outer vertical edges worth softening. **Which edges get a comfort fillet
  is a form-pass decision** that depends on the real outer profile — and the
  outer profile is an explicitly OPEN form question in the spec. So I did *not*
  invent a new filleting scheme.
- **Fix applied (cup.py step 6).** Scoped the fillet to the outer wall only (so
  it stops trying to fillet the vent slots — that was never the intent), and
  replaced the silent `except: pass` with a printed `[warn]` so a skipped fillet
  is **visible in the build**, not hidden behind `[ok]`. `edge_fillet` stays in
  `params.py`, flagged; the fillet activates once the form pass gives the cup
  real edges to soften. Build now reports the skip honestly and still produces
  all four valid solids.

### Repo location

The CAD repo now lives at `builds/daily-driver/` inside the MakerPhones working
tree (it had been dropped at the wrong path). It remains its own standalone git
repo (`github.com/makerphones/daily-driver`); the website repo gitignores
`builds/` so the two stay cleanly decoupled. Room for sibling builds later.

### Next

- Open `output/cup.stl` and `output/baffle.stl` in a viewer and sanity-check
  proportions (human review — not assessed here).
- Print the **baffle first** (flat, fast) against a real driver to confirm the
  cutout, seat, and gasket channel before committing a cup print.
- When the cup's outer **form pass** happens, decide which edges the comfort
  fillet should soften — the `[warn]` will clear once it has real edges.
- Stubs still TODO: `yoke` real gimbal geometry + cup-side mount, `slider`
  friction clamp — both gated on open questions (yoke-to-cup interface, headband
  arc radius).

---

## 2026-06-13 — Switched to a single MIT license

Replaced the split CERN-OHL-P-2.0 (source) + CC-BY-4.0 (docs) setup with one
**MIT** license over the whole repo.

- **Why MIT.** Simplicity — one short, universally understood license instead
  of two, and it's code-native, which fits a design that's *defined in code*
  rather than shipped as discrete hardware files.
- **Why permissive.** The whole point is for the design to spread — get used,
  forked, built, and sold freely. There's no moat here to defend with copyleft
  or a non-commercial clause.
- **Where the value actually lives.** Kits (sourced, matched parts in a box), a
  finished Warren Labs product for people who don't want to build, and merch.
  None of those depend on the design being closed — a published model doesn't
  make the kit or the assembled unit any less worth buying.
- **What stays protected.** The makerphones and Warren Labs *names and brands*
  are held back by trademark, separately from the code license. Anyone can build
  and sell the design; nobody can sell it *as* makerphones.

---

## 2026-06-13 — Licensed open, permissive with attribution

Picked the licenses and made the repo properly open.

- **Source / design files:** CERN-OHL-P-2.0 (CERN Open Hardware Licence v2,
  Permissive). **Docs** (spec, this log, README prose): CC-BY-4.0. SPDX headers
  on every `.py`; `LICENSE` + `LICENSE-docs` carry the full legal text.
- **Why permissive.** The whole point is for the design to spread — get built,
  forked, remixed, sold by whoever wants to. A copyleft or non-commercial clause
  would slow that down to protect a moat that isn't there. The design being open
  costs nothing, because the commercial value doesn't live in the geometry.
- **Where the value actually lives.** Kits (sourced, matched parts in a box), a
  finished Warren Labs product for people who don't want to build, and merch.
  None of those depend on the CAD being secret — a published STL doesn't make
  the kit or the assembled unit any less worth buying.
- **What stays protected.** The MakerPhones and Warren Labs *names and brands*
  are held back by trademark, separately from the design license. Anyone can
  build and sell the design; nobody can sell it *as* MakerPhones. Open design,
  protected brand — the two don't conflict.

---

## 2026-06-13 — Repo scaffolded, code-CAD toolchain chosen

Moved the Daily Driver from spec-only into a parametric CAD repo.

- **Toolchain:** CadQuery (code-based, B-rep, exports STL + STEP). Chosen over
  Fusion/MCP for this project specifically because the files are text — they
  version-control and diff naturally, and anyone can fork and modify. Trade-off
  (known going in): weaker at taste-driven surfaces and complex fillets than a
  GUI. Those get handled in the form pass; functional geometry lives in code.
- **Structure:** `params.py` is the single source of truth; one file per part
  in `parts/`; each part builds independently (matches the spec's modular,
  independently-iterable interface goal).
- **State:** `cup` and `baffle` are real first-pass geometry. `yoke` and
  `slider` are wired stubs (parameters exercised, real geometry TODO).

### Open questions carried from the spec (do NOT silently resolve)

1. **Pad lip vs. cup interior.** `pad_lip_od` = 62 sits well inside
   `cup_interior_diameter` = 78. The spec lists both but doesn't fully say
   where the lip lives — a raised ring on the cup front, or a feature of the
   baffle. Resolve cup + baffle together. Confirm HM5 inner-ring dia with
   calipers first.
2. **Baffle screw direction.** Current model puts heat-set inserts in the cup
   bosses and clearance holes in the baffle (screw from the front, into the
   cup). Spec lists "insert placement" under the baffle, which could mean the
   reverse. Pick one, note it here.
3. **Yoke-to-cup attachment.** Not specified. The cup currently has a
   placeholder boss on the +X side. Design the yoke and the cup mount together.
4. **Headband arc radius.** Spec's own open question — print jigs at 95/105/115
   mm inside radius, form blanks, test clamping force across head sizes before
   committing. Drives the slider and the whole fit.
5. **Production driver.** Baffle is parametric so the driver locks late. Update
   `driver_od` / `driver_aperture` in `params.py` once a specific driver with
   published measurements is chosen.
6. **Vent open area.** The rear vent slots are sized toward ~40% open with a
   crude area calc and a fixed 5 mm slot width. Exact open area + slot shape is
   both an acoustic tuning lever and the signature look — iterate by eye and by
   measurement.

### Next

- Run `python build.py` on the machine, open `output/cup.stl` and
  `output/baffle.stl` in a slicer/viewer, sanity-check proportions.
- Print the baffle first (flat, fast) against a real driver to confirm the
  cutout, seat, and gasket channel before committing a cup print.
