# JLCPCB upload set (board v3, on-board SYN480R receiver)

Files: `../g29_flap_v3_gerbers.zip`, `bom.csv`, `positions.csv`.

Order: 2 layers, 1.6 mm, 5 pcs, default options. PCB Assembly → **Standard** (the relay,
terminals and socket strips are through-hole), assemble 2 boards, top side only.

## Parts matching

Every BOM line carries the LCSC number that was matched and verified in stock in October 2026.
If one has gone out of stock, pick an equivalent in the same package; the two that must not be
substituted blindly are **U3** (JSMSEMI SYN480R C916347 only; the Synoxo SYN480R has another
pinout and crystal) and **Y1** (13.52127 MHz, 20 pF load).

Not in the files (DNP or hand-soldered): R9, R10, R11, the XIAO ESP32-C3, the antenna wire (ANT1 pad).

## Placement preview

Validated on the first upload of this board; nothing needed rotating. For reference:
K1 pin-1 mark at the top square pad (CPL gives body centre, rotation 270). Diodes: pad 1 = cathode =
silkscreen bar; JLC's "A"/"+" mark on the other pad (D1, D2: top; D5, D6: right). C1 "+" at the
bottom. Q1/Q2, U2, U3: pin-1 dot on the top-left pad. Terminals: wire openings toward the bottom edge.

Check the DFM report a few hours after ordering before production starts.
