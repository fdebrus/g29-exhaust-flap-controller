# Shopping list

Full component list: `hardware/v3-xiao-esp32c3/jlcpcb/bom.csv`.

## Modules (not assembled by the PCB maker)
- **Seeed Studio XIAO ESP32-C3** (exactly this model; not S3/C6/RP2040, not the "ESP32-C3 Super Mini").
  Check the external antenna is included. Solder two 1x7 male headers if not pre-soldered.
- 17 cm of stiff insulated wire for the antenna (the 433 MHz receiver is on the board)

## Measurement
- USB logic analyser 24 MHz 8-channel (fx2lafw / PulseView compatible)
- 10 kΩ + 3.3 kΩ resistors for the input divider
- Back-probe pins, multimeter
- Tone generator + probe (Klein VDV500-705 or similar) for finding the signal wire in the trunk loom

## Installation
- Add-a-fuse tap for the rear fuse box (mini low-profile type, check yours) + 2-3 A fuse
- Automotive wire 0.5-0.75 mm², several colours
- Solder sleeves or heat-shrink butt connectors
- Enclosure: print `hardware/v3-xiao-esp32c3/enclosure/` (PETG/ASA) + 3 M2.5 x 6 self-tapping screws, cable ties
- Fabric harness tape (tesa 51608, 15 mm)

## PCB
- Gerbers in `hardware/v3-xiao-esp32c3/`, ordered with assembly from JLCPCB (see `jlcpcb/HOW_TO_UPLOAD.md`)
- If assembling yourself: 0805 passives, SMA/SOD-123 diodes, SOT-23 transistors and a DPAK
  regulator are hand-solderable with a fine tip; the relay, terminals and sockets are through-hole.
