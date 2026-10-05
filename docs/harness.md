# Harness survey on the car (G29 M40i)

Where the actuator wiring runs, where to tap it, and how the wires were identified.
Observed on one car (2022 build). Items marked **to verify** are not yet confirmed.

## Actuator and connector

- One electric actuator on the **right-hand rear silencer**, BMW part 18308686640, 3-pin connector.
- The connector is reachable by hand from under the car, right side, without removing anything.
- The actuator pigtail runs forward under a heat-shield sleeve toward the body. No intermediate
  connector was found before the body entry, so the pigtail's wire colours cannot be followed
  visually past the sleeve.

## Where the wiring enters the body

- Right-hand side of the trunk, behind the side trim, next to the **rear power distribution box**
  (fuse box, BMW 6114 8734162).
- Remove the fuse-box cover, then lift out the black EPP foam block (press-fit, no fasteners).
- At the bottom of the cavity, below the fuse box, a large rubber **floor grommet** passes the
  rear harness to the underbody. This is the only harness exit in that area and the actuator
  wires are in it.
- The fuse box does **not** need to be removed. Do not try: it is a coded module, permanently
  fed from the battery via the thick red cable on the left of the cavity.

## Wire identification (no wiring diagram needed)

Battery negative disconnected, actuator connector unplugged.

1. Open the harness fabric tape over 15-20 cm above the grommet and fan the wires out.
2. Tone generator (Klein VDV500-705 used) on one harness-side pin of the actuator connector,
   black clip on bare chassis. Probe the fanned wires in the trunk, lowest sensitivity first.
3. Repeat for the other pins.

Result: **two** of the three pins tone normally. The **third goes silent**: it is the actuator
ground, bonded to the chassis, so the toner is shorted. This is expected and useful: the two
toning wires are supply and signal, which is all that matters.

4. Confirm each located wire with a multimeter in continuity mode between the pin and the wire
   (long test lead, fine needle through the insulation). Seal the pin-pricks with heat-shrink.
5. Battery reconnected, ignition on: back-probe the two located wires. Steady ~12 V = supply.
   Intermediate / changing between Comfort and Sport = **signal**. That is the wire to cut.

Only the signal wire is cut. The ground wire is left alone and not identified in the loom.

## Cautions in the opened loom

- The main loom above the grommet carries twisted pairs (bus lines). Do not pierce them and keep
  tap leads away from them.
- Re-wrap with harness fabric tape (tesa 51608 or 51036, 15 mm is the right width here;
  9/15/19/25/32 mm exist).

## Commercial kit Y-harness colours

The vendor's 3-pin Y-harness uses red, black and yellow. Yellow = signal is a plausible
convention, **not verified**: check the cavity number of the yellow wire against the OEM
connector, then the voltage test above.

## Related, to verify

- Owners report fuse **203** (7.5 A, the only 7.5 A in the rear box) as the flap actuator supply
  on the G29. Documented for the X3 G01, two forum reports for the G29, not confirmed here.
- Unplugging the actuator is reported to log DME fault **138104** (open circuit) on the M340i;
  not tested on the G29.
