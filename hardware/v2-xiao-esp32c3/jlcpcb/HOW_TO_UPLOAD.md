# JLCPCB upload set (current THT board, Standard assembly)

Three files, upload in this order:

1. `../g29_flap_xiao_gerbers.zip` — PCB fabrication (unchanged).
   Settings: 2 layers, 1.6 mm, 5 pcs, default options. Tick **PCB Assembly** → **Standard**
   (through-hole), assemble **2** boards, top side.
2. `bom.csv` — 19 lines, 30 parts: all passives, diodes, transistors, regulator, relay,
   screw terminals and socket strips. C2 is 100 nF (was 330 nF; C1 100 µF sits next to it).
3. `positions.csv` — placement of those 30 parts. Mid X/Y is the centre of each footprint's
   pads, same origin and Y convention as the Gerbers (X as KiCad, Y negated).

## Parts matching step

LCSC numbers in `bom.csv` fall in three groups (see the Notes column):
- **Verified on JLCPCB/LCSC part pages**: resistors (UNI-ROYAL MFR0W4F series), 100 nF leaded
  MLCC (C94703), 1N5819-AP (C19983441), relay G5V-2-H1 DC12 (C128021).
- **Page seen but stock unknown, often Pre-order**: screw terminals (Phoenix 2P C6366685,
  Dinkle 3P C6943200), 1x7 socket (PreciDip C6669651). If the matching page shows Pre-order,
  click Search and pick an in-stock equivalent ("3.5mm 3P screw terminal",
  "Female Header 7 Position 2.54mm").
- **Left blank**: parts that auto-matched on the first upload (C1, C4, D2, D3/D4, D5, Q1/Q2, U2)
  and the 1x4 socket (J4). Keep your earlier picks; search for J4.

K1 note: the H1 variant is the high-sensitivity coil (960 Ω, 12.5 mA). Same pinout and
footprint as the G5V-2-12VDC in the schematic; the 1 k base resistor is fine for it.

## Not in these files (you solder them)

F1 PTC (not in JLC library); XIAO ESP32-C3; RXB6 and antenna; R9, R10, R11 (DNP until measured).

## Before confirming

- Diodes D1, D2, D5, D6, D3, D4: KiCad pad 1 (square, left) is the **cathode**. JLC marks the
  anode "A"/"+": it must be on the **right** pad. Rotate 180° in the preview if not.
- C1, C4: square pad = +, left.
- Q1, Q2: KiCad pad 1 (left) is the collector of the BC337. Check which pin JLC's part calls
  pin 1; rotate if their pin 1 is the emitter. Flat face toward the silkscreen D-shape.
- Screw terminals: wire openings toward the bottom board edge.
- Relay K1: pin 1 at the top-left square pad.
- Expect ~$8 setup + per-joint fee (THT ~$0.017/joint) + $3 per extended part. Untick stencil.
- Re-check everything in the DFM report 4–6 h after ordering; production starts after that.
