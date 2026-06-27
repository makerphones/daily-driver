# Assembly sequence — Daily Driver

> ⚠️ Like the print guide, this is a **forward reference** for when the design is build-ready —
> not a green light. It's also the canonical **order** the 3D exploder should follow (the explode
> is grouped by these stages; refining it to step through them in order is tracked work).

Build **one earcup at a time**, then join the shared headband last. Part numbers + quantities are
in [`BOM.md`](../BOM.md); the part inventory is [`PARTS.md`](PARTS.md). Heat-set install bores are
sized for the inserts in the BOM — install them with a temperature-controlled soldering iron.

The order is chosen so nothing traps a part you still need to reach, and so every fastener threads
into a heat-set that's already seated:

## Stage 0 — Heat-set inserts (do all of them first)

Seat every brass insert before any screw goes in — you can't press an insert cleanly once parts
are stacked around it.

1. **M3** (Ruthex RX-M3x5.7) → the 4 baffle bosses (cup interior), the 3 driver-clamp standoffs
   (baffle back), and the 2 cup pivot bosses (cup side walls). 9 per ear.
2. **M5** (Ruthex RX-M5x9.5) → the fork boss (yoke), for the adjustment-post shoulder screw. 1 per ear.
3. **8-32** (Ruthex RX-8-32x4.7, short) → the slider thumbscrew boss. 1 per ear.

## Stage 1 — Driver into the baffle

The driver is captured between the baffle (front) and the clamp ring (back) — no glue.

4. Lay a **front-seal foam gasket** on the baffle's driver seat (the rim the driver frame lands on).
   It compresses ~33 % when clamped — that's the seal.
5. Drop the **driver** into the baffle's back recess (frame rim on the seat, dome firing forward
   through the guard). The locating collar keeps it centred.
6. Set the **driver-clamp ring** over the driver's back; its shoulder bears on the rear frame rim.
   Run **3× M3×6** (FMW 2170020) into the standoff heat-sets. Tighten evenly until the gasket seats.

## Stage 2 — Baffle + damping into the cup

7. Drop the **rear damping felt disc** (⌀38) into the cup's interior damping ring, over the grille.
   *(Closed-back variant: also press **vent plugs** into the tuning ports to taste — this is the
   reversible openness knob.)*
8. Lower the **baffle sub-assembly** into the cup front; align the 4 bolt holes to the baffle bosses.
   Run **4× M3×8** (FMW 2170021) from the front into the boss heat-sets. The heads sit under the pad.

## Stage 3 — Cup ↔ yoke pivot (the friction-tilt stack)

The cup hangs in the fork on one shoulder screw per side. The washer stack makes it a **friction
hinge** — the cup holds its tilt angle, no detent. Build the stack in this order, outside → in:

9. On the **pivot shoulder screw** (Accu 49844-SKH-M3-8-A2), thread on, in order:
   **`[ screw head | M3 wave washer | nylon flat washer | yoke eye | nylon flat washer | cup boss ]`**
   The wave washer is the preload; the nylon washers protect the printed PETG from the steel and add
   drag. The eye rides the **smooth Ø4 shoulder** (not the thread); the M3 thread takes the boss heat-set.
10. Tighten until the cup tilts with light friction and holds. Repeat for the other side. Free
    rotation otherwise (Grado-style — no over-rotation stop).

## Stage 4 — Adjustment post + slider (shoe goes in FIRST)

The captive shoe must be trapped in the slider **before** the post fills the bore — there's no way
to insert it afterward.

11. Drop the **pressure shoe** into the slider's side pocket (it sits in the wall, saddle facing the bore).
12. Thread the **adjustment post** (Mädler 619806050 shoulder screw) — M5 end — into the fork's M5
    heat-set. The Ø6 ground shoulder is the post; the head is the built-in **top stop**.
13. Slide the **slider** down onto the post (the shoe's saddle now cradles the post). The slider
    travels the post for height; the post also swivels in the bore for seal conform.
14. Run the **8-32 knurled knob** (Grand Brass SCK35) into the slider boss until its tip presses the
    **shoe** onto the post — that's the height lock. Never let the screw touch the post directly.

## Stage 5 — Headband (join both ears)

15. Drop each **bow** prong-tip into the recess in its slider's clamp lozenge; the slider's rib enters
    the bow's open channel (anti-rotation).
16. Set the **clamp cover plate** (`headband_clamp`) on the band's inner face; run **2× M3** through the
    prong-tip holes into the lozenge inserts. The band is now sandwiched.
17. Press/clip the **headband pad** onto the bow's underside at the crown.

## Stage 6 — Finish

18. Route the **cable** out each cup's bottom exit; solder to the driver tabs (observe polarity).
19. Stretch the **earpads** over the cup's outer rim; the elastic mount-ring hooks behind the lip.
20. Set height (slide), check tilt (friction holds), wear-test, then **measure** and feed real numbers
    back into `params.py`.

---

**Explode-tool note.** The 3D viewer groups parts by sub-assembly (earcup / earpad / gimbal /
headband / heads). Refining the explode to step through **these stages in order** (and to keep parts
in frame rather than flying them to infinity) is tracked in the build-readiness plan — the stages
above are the intended sequence.
