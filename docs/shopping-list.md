# Shopping list

Full component list per board: see `hardware/v2-xiao-esp32c3/bom.csv`.

## Modules
- **Seeed Studio XIAO ESP32-C3** (exactly this model; not S3/C6/RP2040, not the "ESP32-C3 Super Mini").
  Check the external antenna is included. Solder two 1x7 male headers if not pre-soldered.
- **RXB6 433 MHz** superheterodyne receiver (buy 2). Not the 315 MHz version.

## Measurement
- USB logic analyser 24 MHz 8-channel (fx2lafw / PulseView compatible)
- 10 kΩ + 3.3 kΩ resistors for the input divider
- Back-probe pins, multimeter

## Installation
- Add-a-fuse tap (check fuse type in the G29 fuse box)
- Automotive wire 0.5-0.75 mm², several colours
- Solder sleeves or heat-shrink butt connectors
- Small enclosure (about 70 x 55 x 30 mm), foam tape or cable ties
- Fabric harness tape

## PCB
- v2 Gerbers, ordered from any PCB maker (usually 5 pieces minimum)
