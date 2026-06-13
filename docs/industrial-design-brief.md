# Daily Driver — Industrial Design Brief

**v0.1 · for the form / industrial-design pass**

This is the brief for the *form* of the Daily Driver — what it looks like and feels like.
It exists because the functional skeleton (parametric CAD, build pipeline) is proven, and the
form is the next pass. Output of this pass is 3–5 form directions to choose from; the chosen
direction then gets translated back into the parametric CadQuery model, respecting everything
under "Locked" below. Renders give appearance, not manufacturable geometry — the CAD is still
built by hand from the chosen direction.

---

## What it is

An open-back, over-ear (circumaural) DIY headphone — the flagship "build in the open" design
for makerphones (a Warren Labs project). 3D-printed, fully parametric, open source (MIT), meant
to be downloaded, forked, and modified. It's the canonical first build: a forgiving ~40 mm
open-back. Sonic character is bright, open, detailed — and the form should feel like that too.

## Who it's for / how it should read

DIY makers and hobbyist builders. The form should read as **honest engineering — pro-audio
sensibility through a maker lens** — not glossy consumer product. Credibility comes from looking
considered, functional, and serviceable, not flashy. If it looks like it was designed by someone
who knows audio and respects the person building it, it's working.

## Design intent (the feeling)

- Honest, engineered, considered. Calm, not loud.
- **3D-print-native** form language — embrace what FDM does well; don't fake injection-molded smoothness.
- The openness should be **legible in the form** — it should look open, modular, and serviceable.
- Brand palette: charcoal `#2d3748` + warm orange `#ea580c`. Wordmark: makerphones by Warren Labs (lowercase makerphones).

## Locked — the form must respect these

These are hard constraints. Design freely *around* them, never through them.

- **Four-part architecture per side:** cup (shell + separate bolt-on baffle plate) → yoke (±20° tilt) → slider → spring-steel arc. Each interface stays independently iterable.
- **The project's own 6 mm pivot interface** between yoke and slider (deliberately not cross-compatible with commercial yokes).
- **Cup envelope:** interior ~78 mm dia × ~30 mm deep, outer ~84 mm; circumaural.
- **Ear pad:** Brainwavz HM5 oval velour (~90 mm); pad mounts on a lip of 61–62 mm OD.
- **Driver + grille:** baffle holds a ~40 mm-class driver; the rear grille must protect the driver.
- **Headband:** exposed 1095 spring-steel arc, 0.7 mm × 10 mm, ~100 mm radius — a visible structural ribbon, not hidden.
- **Cable:** dual entry (one exit per cup), standard 3.5 mm connector.
- **Open-back:** the rear is vented, never sealed.

## Open — the form playground

- **Cup outer profile and overall form.**
- **Rear vent pattern — the signature look.** Working direction: echo the makerphones logo (a
  center dot + two concentric rings) as a spoked concentric grille — as open as possible while
  staying structurally sound (continuous rings + radial spokes, no fragile webs).
- **Yoke / slider styling** within the 6 mm pivot and friction-clamp constraints.
- **Color, finish, and overall aesthetic language.**

## Design opportunities / hooks

- The rear grille as the brand signature (the logo motif).
- The exposed spring-steel ribbon as an intentional feature — industrial honesty, not something to hide.
- Modularity and serviceability as aesthetic: visible fasteners, removable baffle, "you can see how it's made."
- Print-native detailing (chamfers, layer-friendly surfaces) rather than faux-molded forms.

## Manufacturing reality (this constrains the form)

- FDM 3D-printed in PLA+ / PETG on a desktop printer.
- Overhangs ≤45° where possible; parts designed to print support-free in a sensible orientation.
- Parts print individually and bolt together; the form must slice and print, not just render.
- Not injection-molded — avoid forms that only make sense in molded plastic.

## Deliverables from this pass

- 3–5 distinct form directions, each shown in 3/4 and side views, covering cup + headband.
- Rear-grille pattern options (logo-evocative, varying openness).
- 2–3 color / finish directions in the brand palette.
- Pick one → translate it into the parametric model, respecting "Locked."

---

## Appendix — starter render / mood prompts

Starting points, not final. Keep the threads constant across iterations: charcoal + warm
orange, the concentric-ring rear grille, the exposed steel headband, the honest-maker character.

**Concept / mood (text-to-image, e.g. Midjourney):**

```
open-back over-ear headphones, industrial design concept, matte charcoal 3D-printed
earcups, circular rear grille of two concentric rings and radial spokes around a center
hub, thin exposed spring-steel headband ribbon, warm orange accent details, oval velour
ear pads, honest engineered maker aesthetic, pro-audio not consumer, studio product
render, soft neutral background, three-quarter view --ar 4:3
```

**Finish / material direction (e.g. Vizcom modify on a sketch, or as a style addendum):**

```
matte charcoal PLA earcups, warm orange anodized-look accent ring, brushed spring-steel
headband, black velour pads, soft studio lighting, clean neutral backdrop, realistic
3D-printed surface texture (subtle layer lines), product photography
```

*v0.1 — update as directions come back and one is chosen.*
