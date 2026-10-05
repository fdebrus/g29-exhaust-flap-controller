# JLCPCB assembly: SMT respin and ordering

Companion to `smt-respin-bom.csv`. Alternative to assembling the current THT board: a smaller SMT version.

## What was verified and what was not

The `LCSC # verified` column is honest about this. Five part numbers were confirmed on JLCPCB
part pages today (0805 10k, 0805 100k, SS14, 1N4148W, G5V-2-H1 DC12). The others are standard
parts that are in the library, but the exact LCSC number and the Basic/Extended status must be
picked in the JLCPCB parts search when you build the order, because stock and classification
change weekly. Do not copy numbers from memory or from forums.

## KiCad changes (schematic + PCB)

1. Resistors: footprint `Resistor_SMD:R_0805_2012Metric` (R10/R11: `R_1206_3216Metric`).
2. Ceramics: `Capacitor_SMD:C_0805_2012Metric`.
3. C1: `Capacitor_SMD:CP_Elec_6.3x7.7` or keep THT.
4. D1, D6: `Diode_SMD:D_SMA`. D2: `D_SMA` (SMAJ20A) or `D_SMB` (SMBJ20A). D3, D4, D5: `D_SOD-123`.
5. Q1, Q2: `Package_TO_SOT_SMD:SOT-23`. Re-check the pin mapping in the symbol: S8050 SOT-23 is
   pin 1 B, pin 2 E, pin 3 C. The BC337 TO-92 symbol was C-B-E.
6. U2: `Package_TO_SOT_SMD:TO-252-2` with a thermal pour on the tab, or keep TO-220.
7. F1: `Fuse:Fuse_1812_4532Metric` or keep radial.
8. Add the fields `LCSC` (part number) to every placed symbol. The Fabrication Toolkit plugin
   reads that field.
9. Set `DNP` on R9, R10, R11 so they are excluded from the CPL.
10. Keep all THT parts (terminals, headers, relay if hand-soldered) with the attribute
    "Exclude from position files" so they do not appear in the CPL.

Re-run the autorouter or re-route by hand; 0805 parts free up a lot of area, the board can
probably drop below 50 x 40 mm.

## Generating the JLCPCB files

- Install the KiCad plugin **Fabrication Toolkit** (Plugin and Content Manager).
- Run it: it produces Gerbers + drill (zip), `bom.csv` and `positions.csv` in JLCPCB format.
- Check `positions.csv`: every row has an LCSC number and a layer (`top`). Rotation offsets
  for diodes and SOT-23 are the usual gotcha: compare against the JLC render before confirming.

## Order

1. jlcpcb.com → Order now → upload the Gerber zip. 2 layers, 1.6 mm, 5 pcs.
2. Enable **PCB Assembly**. Pick **Standard** if you want the relay placed by JLC (THT), otherwise
   **Economic** (SMD only) is cheaper and you hand-solder the relay.
3. Assemble 2 of the 5 boards (minimum).
4. Upload `bom.csv` and `positions.csv`.
5. Parts matching: every line must resolve to a library part. Extended parts show a $3 feeder fee
   each; count them, swap for Basic equivalents where the footprint allows.
6. Component placement preview: verify the cathode band on D1, D2, D5, D6 and the polarity dot on
   C1. Rotate in the preview if needed.
7. Confirm. Expect 3 to 5 extra working days over bare PCBs.

## What you still solder yourself

Screw terminals (3), socket strips (3), XIAO, RXB6 and its 17 cm antenna, R9/R10/R11 after
measurement, and the relay if you chose Economic assembly. Ten minutes per board.
