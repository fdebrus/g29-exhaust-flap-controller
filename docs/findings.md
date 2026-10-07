# Findings

Everything we know so far, with how confident we are. "Verified" means seen or measured directly;
"inferred" means deduced, still to be confirmed.

## The car

| Item | Status | Notes |
|---|---|---|
| Z4 G29 M40i has an electrically controlled exhaust flap | Verified | |
| Actuator part number 18308686640, 3-pin connector, driven by the DME | From parts listings | Shared with G20 M340i, G42, G05 X5, F90 M5 and others |
| Signal type is PWM | **Inferred** | See evidence below |
| PWM 5 % = closed, 95 % = open | **Inferred** | Measured on an F30 330i (different actuator), posted on the Pico Technology forum |
| Disconnecting the actuator logs DME fault 138104 (exhaust flap activation, open circuit) | From fault-code listings | Not tested on our car |
| Some commercial modules claim no fault codes | Vendor claim (dAHLer) | Suggests the DME can be kept happy with a load |

## The commercial kit (Chinese, "宝马原厂电机控制器")

The kit has three parts: a replacement light-switch panel with an exhaust button, a cabin box,
a trunk box, and a 3-button key fob (ON / AUTO / OFF). Seller confirmed in writing that it
**replaces** the factory cable: its AUTO button does **not** give control back to the car.

### Key fob
- Resonator marked **R433** -> transmits on **433.92 MHz** (EU-permitted band).

### Cabin box (connected to the dashboard button)
- Blue carrier board with **two plug-in RF modules**, each with its own antenna and an unmarked 8-pin chip.
- Crystals **9.81563 MHz** and **13.52127 MHz**. These match the SYN5xx receiver family values for
  **315 MHz** and **433.92 MHz** respectively.
- Central microcontroller, markings removed.
- Seller's answer "433-315" confirms the two bands.
- Note: 315 MHz is not a permitted short-range band in the EU.

### Trunk box ("HJS-3线电机驱动板-A-V1.1-211118" = "HJS 3-wire motor driver board, A, V1.1, 2021-11-18")
- **U3 marked "531R"** -> likely **SYN531R** ASK receiver; crystal **13.52127 MHz** -> receives on **433.92 MHz**.
- **U1**: 28-pin microcontroller, markings removed. Unpopulated headers P1/P2/P3 (programming/debug).
- **U2**: 78L05 regulator. **D1/D4/D5**: SS14 Schottky. **R1 ("α 075")**: probably a 0.75 A resettable fuse.
- **Output stage**: two identical channels, small NPN transistors (marked "1AM", typically MMBT3904)
  with 510 Ω resistors (R6, R7) and 2 k / 4.7 k resistors. **No LIN transceiver** on the board.
- Two channels probably serve cars with two flap actuators.
- Seller: signal voltage 12 V, signal wire in their harness is **red-black**.

### Bench measurement of the trunk box (7 Oct 2026)
Stabilised 12.0 V supply, multimeter (DC) on the three output wires: black = ground, red = 12 V
permanent, yellow = signal.

| Kit mode | Yellow (V) | As % of supply |
| -------- | ---------- | -------------- |
| Open     | 10.48      | 87 %           |
| Auto     | 5.95       | 50 %           |
| Off      | 1.41       | 12 %           |

These are multimeter averages: three fixed levels, consistent with a PWM at 12 V level driven
actively (push-pull), or with three DC levels; a multimeter cannot tell. Frequency and duty cycle
are to be measured with `tools/pwm_probe` (see [measurement.md](measurement.md)).

**The kit never connects to the DME.** Its harness drives the actuator only; the car's signal wire
is left unconnected. "Auto" is simply a fixed 50 % output, not a copy of the car's signal. This is
the real reason the kit cannot hand control back: there is no path for it.

### Conclusion on signal type
Three fixed output levels at 12 V, a transistor output stage, a 3-wire actuator and the F30 data
all point to **PWM at 12 V level, driven actively**. Consequence for our board: fit **R9** (1 k
pull-up) so the open-collector driver produces a 12 V level too. Frequency still to be measured.

### Open questions (car only)
- The DME's own frequency, levels and Comfort/Sport duty cycles (pwm_probe at the actuator connector).
- Whether the DME logs a fault with its signal wire open (the kit was never installed in the car,
  so there is no field evidence either way); decides whether R10/R11 are populated.
- Whether the actuator is proportional (what does the flap do at the kit's 50 %?).

## Commercial alternatives (if you don't want to build)

Two plug-and-play modules list the G29 and advertise keeping the factory mode:
- **MODE Auto Concepts** valve control module (auto mode reverts to OEM control, open in any drive mode).
- **Grail Automotive** exhaust valve controller (two settings: fully open, or OEM operation).

Neither states whether the DME stays fault-free. Both are vendor claims, not independently tested.
