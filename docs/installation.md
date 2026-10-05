# Assembly and installation

## Before ordering the PCB

1. Measurement done, signal confirmed **PWM** ([measurement.md](measurement.md)).
2. Print `hardware/v2-xiao-esp32c3/preview_front.png` at 1:1 (60 x 46 mm) and lay the XIAO on it:
   rows 15.24 mm apart; USB at top; left column D0..D6, right column 5V, GND, 3V3, D10, D9, D8, D7.
3. Upload `g29_flap_xiao_gerbers.zip` to any PCB maker (2 layers, 1.6 mm, default options).

## Assembly notes

- Solder low parts first (resistors, diodes, ceramic capacitors), then sockets, terminals, relay, regulator.
- C5 and C6 sit **under the XIAO**: use low ceramic capacitors and mount the XIAO on socket strips.
- Diode stripes: D1 toward +12 V, D2 (TVS) toward +12 V, D3/D4 toward the GPIO, D5 toward +12 V, D6 toward the XIAO.
- Check on the G5V-2 datasheet that your relay variant is not polarity-sensitive.
- **RF module (J4)**: J4 = GND, DATA, DATA, 3V3 (GND on the square pad). The RXB6 has 8 pins (4 per end):
  plug the DATA end into J4, oriented by the labels on the module so GND meets GND and VCC meets 3V3.
  Solder a **17 cm** straight wire to the ANT pin at the other end.
- Fit **R9** and **R10 or R11** only with the measured values.

## Firmware

1. Arduino IDE, ESP32 core 2.x or 3.x, board **XIAO_ESP32C3**, enable "USB CDC On Boot".
2. Library: **rc-switch** (Library Manager).
3. Set `PWM_FREQ_HZ`, `DUTY_OPEN_PCT`, `DUTY_CLOSED_PCT` from the measurements.
4. Flash with the RF codes at 0, open the Serial Monitor (115200), press ON / AUTO / OFF on the fob,
   copy the three codes into `RF_CODE_ON`, `RF_CODE_AUTO`, `RF_CODE_OFF`, flash again.

Pins: GPIO3 PWM, GPIO4 relay, GPIO5 RF data, GPIO6 dash ON, GPIO7 dash OFF.

## Bench test (before the car)

- 12 V supply on J1. Board starts in AUTO: relay off.
- Dashboard ON (12 V on J2 pin 2) -> relay clicks, PWM on J3 "FLAP" when relay is on.
- Fob AUTO -> relay off. Fob OFF -> forced closed, back to AUTO after 15 minutes.
- Check the signal on the FLAP terminal with the logic analyser (with divider): same frequency/duty as measured.
- Remove power while in ON -> relay must drop.

## Where to work on the car

Right-hand side of the trunk, behind the fuse-box cover and the EPP foam block. The actuator
wiring passes through the floor grommet below the rear power distribution box. Full survey and
wire identification procedure: [harness.md](harness.md).

Battery negative disconnected before opening the loom or cutting anything.

## Connections in the car

| Terminal | Pin      | Connect to                                                                                   |
| -------- | -------- | -------------------------------------------------------------------------------------------- |
| J1 POWER | 12V      | Switched +12 V (after ignition) via an add-a-fuse tap in the rear fuse box, own 2-3 A fuse. **Not** the actuator supply wire. |
| J1 POWER | GND      | Chassis bolt or battery negative post. **Not** the actuator ground wire.                     |
| J2 DASH  | 12V      | Supply for the dashboard button                                                              |
| J2 DASH  | ON / OFF | The button's two output wires                                                                |
| J3 FLAP  | DME      | Signal wire, **car side** (cut wire, end going to the DME)                                   |
| J3 FLAP  | FLAP     | Signal wire, **actuator side**                                                               |
| J3 FLAP  | GND      | Same chassis ground as J1                                                                    |

- Only the **signal wire** is cut, in the trunk loom above the grommet. Actuator +12 V and ground
  stay untouched; the ground wire does not even need to be located.
- Use solder sleeves or crimped, heat-shrunk butt connectors. No scotch-lock taps.
- Keep the original connector intact so the car can be returned to stock.
- Keep tap leads away from the twisted pairs in the loom. Finish with fabric harness tape.
- Mount the box in the trunk cavity away from the fuse box and the battery positive cable.

## After installation

- Drive in AUTO: the flap must behave exactly as before (Comfort / Sport).
- Read the fault memory (e.g. BimmerLink / BimmerCode with a compatible adapter) after a few drives,
  in AUTO and after using ON/OFF. Note any code (expected candidate: 138104).
