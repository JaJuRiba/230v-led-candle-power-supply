# P1 standalone DC enclosure — populated-board integration

**60 × 78 × 16 mm**, excluding leads. Both keyed headers and both jacket exits face **+Y**. This is a digital first-article design for the isolated low-voltage controller, not a recessed installation. No physical fit, pull, thermal or electrical qualification.

[Dimensioned top view and height datums](interfaces.svg) · [open](open.svg) · [closed](closed.svg) · [exploded](exploded.svg) · [review assembly](assembly.step) · [executed checks](verification.txt)

### Registration and service space

[Unmodified KiCad STEP](../../hardware/p1/mechanical/p1.step) → case coordinates in mm: **(19−x, −17−y, 5+z)**. This is a rigid 180° rotation about Z plus translation, not a mirror. The 38 × 34 substrate is centred on XY zero, bottom Z5. The STEP core ends at Z6.5162; the mounted parts start around Z6.601. Do not centre the populated Z bounding box or stretch the core to nominal board thickness. The report pins the STEP checksum and checks both header bounds and substrate faces. All 30 fitted references are represented; JP1/JP2 are copper-only. The component shapes, including generic package representations, are as exported, not measured maxima.

The four 6 × 6 pads centred at (±18, ±16) support the corners. Edge cheeks allow 0.55 per side; four 2 × 2 roof stops end at Z7.15. Check contact areas for solder, copper features, flash and board warp. Rotation, warp and printed seam mismatch are not bounded by the translational sweep.

| Interface | J1 input | J2 five-pair output |
|---|---:|---:|
| Axis X; +Y exit at Y55, Z8.2 | +13 | −6 |
| Added external mate allowance, W × L × H | 6 × 8 × 4 | 14 × 8 × 4 |
| Free straight fan-out to saddle | 21.8 | 21.8 |
| Assumed round jacket OD | 4 | 6 |
| Split bore: 6-long grip / 3-long free mouth | 3.70 / 5.20 | 5.70 / 7.20 |

Tan blocks in the review assembly are **reservations**, not supplied mating parts. The mate block starts just beyond the header front, at Y16.2/Z6.6; the final 21.8 mm is reserved for the transition into a straight jacket. Align leads with their own axis; no folded-back cable, crossed lanes, internal splice or 90° jacket bend is required by the layout. Use an external labelled breakout for the five pairs. Verify actual SH mating housings, crimp contacts, approved conductor sizes, transition lengths and minimum bend radii against the selected harness. A supplier requiring more room means revising the bay, not forcing a bend. No latch mechanism, individual conductor curves or cable deformation is simulated.

### Make and assemble — unpowered; not run

1. Print [base STL](base.stl) floor-down and [lid STL](lid.stl) exterior-down, mm at 100%. [Base STEP](base.step) and [lid STEP](lid.step) instead use assembled coordinates. Inspect slicer preview for half-bore finish, counterbore bridges, floor flatness and single-body parts. Remove burrs; gauge pilots, seam, stops and both bores.
2. Provide four thermoplastic thread-forming screws Ø2.5 × 10 under head, head ≤5.0 diameter × 2.2 high. Axes X±24, Y−18/+50. Lid Ø2.9 through, Ø5.3 × 2.2 recess; base Ø2.0 × 5.8 blind pilot. Nominal engagement 4.4. Use a straight driver nose ≤Ø4.8. Confirm pilot/torque on a material coupon; no validated tightening torque.
3. Check actual jacket OD around and along each grip, and confirm intact jacket covers all 6 mm. OD ±0.10 and printed diameter ±0.20 gives **0 to 0.60 mm diametral squeeze**: CAD alone cannot establish retention. Reject loose or crushed jackets; adjust `IN_OD`/`OUT_OD`, squeeze or cable selection and regenerate. Never clamp loose conductors instead of the jacket.
4. Dry-fit a dummy board, then the unpowered PCBA. Mate keyed plugs without pulling wires. Lower board vertically onto seats, lay jackets into their aligned saddles and check for unloaded crimps. Lower lid straight; hand-start screws diagonally until the shoulders meet. Stop for board flex, trapped wires or a bowed seam. Label `DC IN` and output pairs against the board pin table; verify continuity/polarity with power disconnected.
5. Service in reverse: remove lid and **lift both jackets free of the grips** before moving a plug. The open-case calculation reserves 10 mm straight +Y withdrawal per lane with a narrow tool up to mate width +3 mm. Grip the housing; do not extract it by the pigtail. If actual tool/latch cannot enter, lift the unclamped assembly and disconnect outside. Keep strain off solder anchors.
6. Record actual board, harness and screw part numbers, print profile, seat/stop and seam measurements. Test closed-case jacket slip/flex unpowered against an agreed service load; record force, time, movement, damage and continuity. Reject connector motion or jacket damage. Populated fit, retention, thermal performance and suitability for use remain untested.

### Reproduce

In this directory with Python 3.13, CadQuery 2.7, trimesh, scipy and system GL libraries: `python model.py && python verify.py > verification.txt`. [CAD](model.py) · [verification source](verify.py). The checker reimports individual STEP/STLs, checks volumes and orientation, tests nominal intersections and conservative vertical swept boxes, probes the split bores, and checks listed adverse dimensional stacks. The assembly reimport checks solid count. Driver and jaw checks are geometric tool reservations, not proof of tool engagement; stack values are design allowances, not measured print capability.
