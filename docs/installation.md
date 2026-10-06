# Assembly and installation

## Before ordering the PCB

1. Measurement done, signal confirmed **PWM** ([measurement.md](measurement.md)).
2. Print `hardware/v3-xiao-esp32c3/preview_front.png` at 1:1 (58 x 40 mm) and lay the XIAO on it:
   rows 15.24 mm apart; USB at top; left column D0..D6, right column 5V, GND, 3V3, D10, D9, D8, D7.
3. Order from JLCPCB with assembly: `hardware/v3-xiao-esp32c3/jlcpcb/HOW_TO_UPLOAD.md`.

## Assembly notes

- JLCPCB places everything except the XIAO and the DNP parts (R9, R10, R11).
- If hand-soldering the SMD parts: 0805 passives and SMA/SOD-123/SOT-23 first, then the DPAK
  regulator, then the through-hole relay, terminals and socket strips.
- Diode cathode = pad 1 = the end with the silkscreen bar: D1 and D6 (SS14) bar toward +12 V /
  toward the XIAO; D2 (TVS) bar toward +12 V; D5 (1N4148W) bar toward +12 V.
- Q1/Q2 S8050 SOT-23: pin 1 base, pin 2 emitter, pin 3 collector (the lone pad).
- **Antenna**: solder a **17 cm** straight wire (quarter wave at 433.92 MHz) into the ANT pad at the
  top edge, route it out through the enclosure hole and along the harness, away from the relay coil.
- **Receiver**: U3 must be the JSMSEMI SYN480R (C916347). The Synoxo SYN480R has a different pinout
  and needs a 6.7458 MHz crystal; it does not work on this board. R12 (0R) disables the squelch;
  leave it out if the data line is too noisy in AUTO mode (costs 3 dB sensitivity).
- Fit **R9** (1k pull-up, 0805) and **R10 or R11** (1206 dummy load) only with the measured values.

## Firmware

1. Arduino IDE, ESP32 core 2.x or 3.x, board **XIAO_ESP32C3**, enable "USB CDC On Boot".
2. Library: **rc-switch** (Library Manager).
3. Set `PWM_FREQ_HZ`, `DUTY_OPEN_PCT`, `DUTY_CLOSED_PCT` from the measurements.
4. Flash with the RF codes at 0, open the Serial Monitor (115200), press ON / AUTO / OFF on the fob
   and then the dashboard button (its cabin box also transmits on 433 MHz). Copy the codes into
   `RF_CODE_ON`, `RF_CODE_AUTO`, `RF_CODE_OFF` and, if they differ from the fob, `RF_CODE_BTN_ON`,
   `RF_CODE_BTN_OFF`. Flash again.

Pins: GPIO3 PWM, GPIO4 relay, GPIO5 receiver data (U3 DO). No wired inputs.

## Bench test (before the car)

- 12 V supply on J1. Board starts in AUTO: relay off.
- Fob ON -> relay clicks, PWM on J3 "FLAP" when relay is on.
- Fob AUTO -> relay off. Fob OFF -> forced closed, back to AUTO after 15 minutes.
- Check the signal on the FLAP terminal with the logic analyser (with divider): same frequency/duty as measured.
- Remove power while in ON -> relay must drop.

## Where to work on the car

Right-hand side of the trunk, behind the fuse-box cover and the EPP foam block. The actuator
wiring passes through the floor grommet below the rear power distribution box. Full survey and
wire identification procedure: [harness.md](harness.md).

Battery negative disconnected before opening the loom or cutting anything.

## Connections in the car

| Terminal | Pin  | Connect to                                                                                   |
| -------- | ---- | -------------------------------------------------------------------------------------------- |
| J1 PWR   | 12V  | Switched +12 V (after ignition) via an add-a-fuse tap in the rear fuse box, own 2-3 A fuse. **Not** the actuator supply wire. |
| J1 PWR   | GND  | Chassis bolt or battery negative post. **Not** the actuator ground wire.                     |
| J3 FLAP  | DME  | Signal wire, **car side** (cut wire, end going to the DME)                                   |
| J3 FLAP  | FLAP | Signal wire, **actuator side**                                                               |

There is no connector for the dashboard button: the kit's cabin box sends the button presses over
433 MHz and the on-board receiver picks them up like the fob.

- Only the **signal wire** is cut, in the trunk loom above the grommet. Actuator +12 V and ground
  stay untouched; the ground wire does not even need to be located.
- Use solder sleeves or crimped, heat-shrunk butt connectors. No scotch-lock taps.
- Keep the original connector intact so the car can be returned to stock.
- Keep tap leads away from the twisted pairs in the loom. Finish with fabric harness tape.
- Mount the box in the trunk cavity away from the fuse box and the battery positive cable.
  A 3D-printed enclosure is in `hardware/v3-xiao-esp32c3/enclosure/` (M2.5 screws into bosses,
  USB-C and terminal openings, fixing tabs for cable ties).

## After installation

- Drive in AUTO: the flap must behave exactly as before (Comfort / Sport).
- Read the fault memory (e.g. BimmerLink / BimmerCode with a compatible adapter) after a few drives,
  in AUTO and after using ON/OFF. Note any code (expected candidate: 138104).
