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

### Conclusion on signal type
A simple transistor output with no LIN transceiver, a 3-wire actuator and the F30 data all point
to **PWM at 12 V level**, probably open-collector with a pull-up of roughly 510 Ω to 1 kΩ.
**Still inferred** - confirm with the bench test in [measurement.md](measurement.md).

## Commercial alternatives (if you don't want to build)

Two plug-and-play modules list the G29 and advertise keeping the factory mode:
- **MODE Auto Concepts** valve control module (auto mode reverts to OEM control, open in any drive mode).
- **Grail Automotive** exhaust valve controller (two settings: fully open, or OEM operation).

Neither states whether the DME stays fault-free. Both are vendor claims, not independently tested.
