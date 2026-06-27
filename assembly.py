# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Assembly — one side of the Daily Driver in its correct relationship (v0.3).

Chain: cup → baffle (front-mounted) → fork-yoke (pivoted to the cup) → slider
(rides the fork's adjustment post) → bow (REFERENCE body). The cup/baffle/yoke/slider
poses
are the real kinematic chain; the bow is posed representatively so one end sits in
the slider channel and the arc sweeps over toward the other (mirror) side — the
full head-size kinematics are TBD from the measured bow (ESTIMATES, see params).

View it:  python show.py        (OCP CAD Viewer)
Export:   build.py writes output/assembly.step
"""

import math

import cadquery as cq

from params import P
from parts.cup import make_cup
from parts.baffle import make_baffle
from parts.yoke import make_yoke
from parts.slider import make_slider
from parts.bow import make_bow
from parts.headband_pad import make_headband_pad
from parts.driver import make_driver
from parts.driver_clamp import make_driver_clamp
from parts.earpad import make_earpad
from parts.headband_clamp import make_headband_clamp


# Sub-assembly groups for the manual's interactive parts viewer. The node NAMES
# below are a PUBLIC CONTRACT: the website viewer toggles/isolates parts by them
# (they match the asm.add(name=...) calls in make_assembly). Renaming a part there
# means updating this too (and the manual). build.py emits this to
# docs/models/daily-driver.groups.json next to the GLB; the viewer fetches it.
SUBASSEMBLIES = {
    "groups": [
        {"id": "earcup", "label": "Earcup",
         "nodes": ["cup_R", "cup_L", "baffle_R", "baffle_L",
                   "driver_R", "driver_L", "driver_clamp_R", "driver_clamp_L"]},
        {"id": "earpad", "label": "Earpads",
         "nodes": ["earpad_R", "earpad_L"]},
        {"id": "gimbal", "label": "Gimbal",
         "nodes": ["yoke_R", "yoke_L", "yoke_rod_R", "yoke_rod_L",
                   "insert_p_R", "insert_p_L", "insert_m_R",
                   "insert_m_L", "screw_p_R", "screw_p_L", "screw_m_R", "screw_m_L"]},
        {"id": "headband", "label": "Headband",
         "nodes": ["bow_ref", "slider_R", "slider_L", "thumbscrew_R", "thumbscrew_L",
                   "slider_shoe_R", "slider_shoe_L", "headband_clamp_R", "headband_clamp_L"]},
        {"id": "headband_pad", "label": "Headband pad",
         "nodes": ["headband_pad"]},
    ],
    "bought": ["bow_ref", "earpad_R", "earpad_L"],
}


def make_assembly() -> cq.Assembly:
    """Both ears + the shared headband, posed like a WORN headphone.

    Head frame (global): X = inter-ear (right ear at +Xe, pad facing −X inward),
    Z = up (bow over the crown), Y = front-back (the tilt-pivot axis). The cup and
    yoke are co-designed with pad ∥ arch (both +Z), which is why earlier the cup sat
    "face-up". Here they're mounted at the correct 90° relative clocking:
      • cup-group  T_cup : pad (cup +Z) → −X (inward), pivot (cup ±X) → ±Y,
                           up (cup +Y) → +Z;  pivot centre → (Xe, 0, 0).
      • yoke-group T_yoke: eyes (yoke ±X) → ±Y, arch (yoke +Z) stays +Z (up);
                           pivot centre → (Xe, 0, 0)  (90° clocked about Y vs the cup).
    The two pivots coincide at (±Xe, 0, 0); the LEFT ear is the mirror across x=0.
    The bow + crown pad are shared parts arcing between the two sliders, posed
    FLEXED to the worn radius (bow_worn_radius); ear spacing = where the flexed
    band's ends land (~156 mm). The bow's relaxed dims are MEASURED off the Beyer
    part; the worn radius (head fit) is still ESTIMATE (see params/bow).

    HEADBAND JUNCTION (v0.7, offset-outer): the metal band rides INSIDE (head-side) and
    the slider's post-bore tube rides OUTSIDE it, so the cups step outboard by
    (barrel R + clamp-plate depth) to keep the post under the band's clamp. Band end →
    recess in the slider's clamp plate → cover (inner) + 2 screws; rib through the bow
    channel; thumbscrew locks the post in the tube.
    """
    CHARCOAL = cq.Color(0.30, 0.32, 0.35)
    ORANGE = cq.Color(0.92, 0.45, 0.10)
    YOKE_C = cq.Color(0.36, 0.38, 0.42)
    SLIDER_C = cq.Color(0.42, 0.44, 0.48)
    STEEL = cq.Color(0.75, 0.76, 0.78)
    BRASS = cq.Color(0.80, 0.68, 0.30)
    SCREW_C = cq.Color(0.55, 0.57, 0.60)
    PAD_C = cq.Color(0.13, 0.13, 0.15)   # near-black foam/velour
    DRIVER_C = cq.Color(0.10, 0.10, 0.12)  # driver mockup (black)

    pbz = P.pivot_boss_z
    # Worn pose: the spring band flexes OPEN from its 63.5 mm at-rest circle to
    # bow_worn_radius on a head (developed length conserved → ~173° arc — note the
    # worn arc dips just under 180° while the measured at-rest arc is >180°). Ear
    # spacing = where the flexed band's ends land (~78 mm → cups ~156 mm apart).
    end_a = 90 - P.bow_worn_arc_degrees / 2
    Xe = P.bow_worn_radius * math.cos(math.radians(end_a))  # bow END x (where the band clamps)
    ez = P.bow_worn_radius * math.sin(math.radians(end_a))
    # Prong-tip HOLE position, set in from the tip up the arc (where the band bolts down).
    inset_deg = math.degrees(P.bow_endtab_hole_inset / P.bow_worn_radius)
    zh = P.bow_worn_radius * math.sin(math.radians(end_a + inset_deg))  # hole height (pre-pose)
    # OFFSET-OUTER junction: the metal band rides INSIDE (head-side) and the post-bore TUBE
    # rides OUTSIDE it. The barrel/post sit OUTBOARD of the band by (barrel R + clamp-plate
    # depth), so the cups step out that far and the clamp plate's inner face lands back at
    # the band end Xe.
    clamp_off = P.slider_collar_diameter / 2 + P.slider_clamp_standoff
    Xe_cup = Xe + clamp_off

    def T_cup(w):    # pad → −X, pivot → ±Y, up → +Z; pivot centre → (Xe_cup,0,0)
        return (w.rotate((0, 0, 0), (0, 1, 0), -90)
                 .rotate((0, 0, 0), (1, 0, 0), 90)
                 .translate((Xe_cup + pbz, 0, 0)))

    def T_yoke(w):   # eyes → ±Y, arch stays +Z (up); pivot centre → (Xe_cup,0,0)
        return w.rotate((0, 0, 0), (0, 0, 1), -90).translate((Xe_cup, 0, 0))

    def mirror_L(w):  # right ear → left ear (true mirror across the head centre)
        return w.mirror("YZ", (0, 0, 0))

    # ---- RIGHT ear ----
    cup = T_cup(make_cup())
    baffle = T_cup(make_baffle().translate((0, 0, P.baffle_seat_z)))
    # Driver (mockup) seated in the baffle's back recess, firing forward; the clamp
    # ring behind it retains the rear rim. ledge = where the flange seats; rear_rim =
    # the driver back where the clamp shoulder bears.
    ledge_z = P.baffle_seat_z + P.driver_recess_depth
    rear_rim_z = ledge_z - P.driver_body_depth
    driver = T_cup(make_driver().translate((0, 0, ledge_z)))
    driver_clamp = T_cup(make_driver_clamp().translate((0, 0, rear_rim_z)))
    # Earpad (mockup) on the cup front rim, ear opening facing the head (cup +Z → −X).
    earpad = T_cup(make_earpad().translate((0, 0, P.cup_total_height)))
    yoke = T_yoke(make_yoke())
    # Bought Ø6 adjustment ROD — epoxy-bonded into the fork socket, rising as the post. Built from
    # its socket floor (z=0); shift up so it seats in the socket, then ride with the yoke.
    # The post is a bought ISO 7379 shoulder screw: M5 thread into the fork boss, Ø6 shoulder is the
    # post, head is the top stop. Built from z=0 = the shoulder seat (boss top); ride with the yoke.
    from parts.yoke_rod import make_yoke_rod
    rod = T_yoke(make_yoke_rod().translate((0, 0, P.yoke_fork_height + 4)))
    # Slider rides the yoke post; the post slides + swivels the full barrel height and may
    # poke past it (nothing stacks on the post now). Barrel TOP at post_top → barrel CENTRE
    # (the slider frame's z=0, where the clamp sits) at post_top − h/2.
    post_top = P.yoke_fork_height + 4 + P.yoke_post_length
    post_base = P.yoke_fork_height + 4                      # hub top = the barrel's bottom stop
    # WORN pose: slide the barrel down the post to a realistic mid-travel position (average head),
    # not the fully-extended extreme. frac 0 → barrel at the post top (biggest head); frac 1 →
    # barrel at the hub stop (smallest head, rod pokes up most). The band/cover/knob ride with it.
    sz_hi = post_top - P.slider_collar_height / 2           # barrel at the post top (extended)
    sz_lo = post_base + P.slider_collar_height / 2          # barrel at the hub (retracted)
    slider_z = sz_hi - P.assembly_worn_slider_frac * (sz_hi - sz_lo)   # barrel / clamp centre
    slider = T_yoke(make_slider().translate((0, 0, slider_z)))
    # Pressure SHOE — rides in the slider's +Y pocket, saddle cradling the post (the thumbscrew
    # presses it, not the post). Built at the origin, shifted +Y so its saddle is post-coaxial.
    from parts.slider_shoe import make_slider_shoe, shoe_offset_y
    shoe = T_yoke(make_slider_shoe().translate((0, shoe_offset_y(), slider_z)))

    # ---- Shared headband: bow + crown pad, arcing between the two sliders ----
    # Pose so the band's prong-tip HOLE lands at the clamp centre (slider z=0 + hole_z=0).
    bow_xf = (0, 0, slider_z - zh)
    bow = make_bow(radius=P.bow_worn_radius,
                   arc_degrees=P.bow_worn_arc_degrees).translate(bow_xf)
    pad = make_headband_pad(radius=P.bow_worn_radius,
                            arc_degrees=P.bow_worn_arc_degrees).translate(bow_xf)
    # Headband CLAMP cover (INNER head-side piece) — built in the slider frame, posed with
    # the slider so its bolts/slot align with the slider's clamp.
    cover = T_yoke(make_headband_clamp().translate((0, 0, slider_z)))

    asm = cq.Assembly(name="daily_driver")
    for nm, solid, col in (("cup", cup, CHARCOAL), ("baffle", baffle, ORANGE),
                           ("driver", driver, DRIVER_C), ("driver_clamp", driver_clamp, STEEL),
                           ("yoke", yoke, YOKE_C), ("slider", slider, SLIDER_C)):
        asm.add(solid, name=f"{nm}_R", color=col)
        asm.add(mirror_L(solid), name=f"{nm}_L", color=col)

    asm.add(rod, name="yoke_rod_R", color=STEEL)           # bought shoulder screw (post + head top-stop)
    asm.add(mirror_L(rod), name="yoke_rod_L", color=STEEL)
    asm.add(bow, name="bow_ref", color=STEEL)              # shared headband (REF)
    asm.add(pad, name="headband_pad", color=PAD_C)         # shared crown cushion
    asm.add(earpad, name="earpad_R", color=PAD_C)          # round pad mockup (bring your own)
    asm.add(mirror_L(earpad), name="earpad_L", color=PAD_C)
    asm.add(cover, name="headband_clamp_R", color=SLIDER_C)   # outer clamp plate
    asm.add(mirror_L(cover), name="headband_clamp_L", color=SLIDER_C)
    asm.add(shoe, name="slider_shoe_R", color=ORANGE)         # pressure pad (screw → shoe → post)
    asm.add(mirror_L(shoe), name="slider_shoe_L", color=ORANGE)

    # Pivot hardware on both ears (viz), riding with the cup group. Guarded.
    try:
        from parts.hardware import make_shoulder_screw, make_heatset_insert
        for sign in (+1, -1):
            tag = "p" if sign > 0 else "m"
            insert = T_cup(make_heatset_insert()
                           .rotate((0, 0, 0), (0, 1, 0), -90 * sign)
                           .translate((sign * P.pivot_boss_outer_radius, 0, pbz)))
            screw = T_cup(make_shoulder_screw()
                          .rotate((0, 0, 0), (0, 1, 0), 90 * sign)
                          .translate((sign * (P.pivot_boss_outer_radius - P.yoke_arm_thickness),
                                      0, pbz)))
            asm.add(insert, name=f"insert_{tag}_R", color=BRASS)
            asm.add(mirror_L(insert), name=f"insert_{tag}_L", color=BRASS)
            asm.add(screw, name=f"screw_{tag}_R", color=SCREW_C)
            asm.add(mirror_L(screw), name=f"screw_{tag}_L", color=SCREW_C)
    except Exception as e:  # noqa: BLE001 — viz only; never block the build
        print(f"  [warn] assembly: pivot hardware skipped ({e}).")

    # Thumbscrew (short 4-40) — the height lock, shown so the post+SHOE+thumbscrew mechanism
    # reads. Rides with the slider on the +Y OUTBOARD boss; its tip presses the SHOE (not the
    # post). T_yoke maps local +Y → global +X, so in the worn pose the knurled head faces
    # straight out the side of the head (the natural two-finger reach with the phones ON).
    try:
        from parts.hardware import make_thumbscrew
        from parts.slider_shoe import shoe_offset_y
        shoe_face_y = shoe_offset_y() + P.slider_shoe_thickness / 2     # +Y face of the shoe
        ts = (make_thumbscrew()
              .rotate((0, 0, 0), (1, 0, 0), -90)                       # shaft → +Y (outboard), tip at origin
              .translate((0, shoe_face_y, 0))                          # tip on the shoe's +Y face
              .translate((0, 0, slider_z + P.slider_thumbscrew_boss_z)))  # ride with the boss
        ts_R = T_yoke(ts)
        asm.add(ts_R, name="thumbscrew_R", color=SCREW_C)
        asm.add(mirror_L(ts_R), name="thumbscrew_L", color=SCREW_C)
    except Exception as e:  # noqa: BLE001 — viz only
        print(f"  [warn] assembly: thumbscrew skipped ({e}).")
    return asm


if __name__ == "__main__":
    make_assembly().export("output/assembly.step")
    print("wrote output/assembly.step")
