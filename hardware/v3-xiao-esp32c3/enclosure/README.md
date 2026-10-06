# Enclosure (3D printed)

Parametric OpenSCAD model for board v3 (58 x 40 mm). Outer size **62.8 x 44.8 x 26 mm**
(base 24 mm + lid), inner height 17 mm above the PCB.

## Features
- Board held by **three M2.5 self-tapping screws** (board holes H1-H3) into bosses, plus a
  support ledge along the left edge. Board sits 4 mm above the floor.
- **USB-C opening** in the top wall for the XIAO (flash without opening the box).
- **Two wire openings** in the bottom wall for the J1 and J3 screw terminals.
- **Antenna exit** (3.2 mm) in the top wall right above the ANT pad: the 17 cm wire goes straight
  up from the pad and out. Run it along the harness, away from the relay coil.
- Snap-fit lid with lip and vent slots. Two **fixing tabs** with 4.2 mm holes for cable ties or
  screws in the trunk cavity.

## Printing
PETG or ASA (the trunk gets warm in summer; PLA softens). 0.2 mm layers, 3 perimeters,
20 % infill, no supports: both parts print flat, open side up. Boss hole 2.0 mm for PETG
(`boss_id`), 2.2 mm for harder filaments.

## Files
- `enclosure.scad` - the model; `part = "base" | "lid" | "both"`
- `enclosure_base.stl`, `enclosure_lid.stl`
- `assembly.scad` - board with approximate component bodies inside the base, for the renders
- `render_open.png`, `render_top.png`, `render_exploded.png`

## Regenerating
```bash
openscad -o enclosure_base.stl -D 'part="base"' enclosure.scad
openscad -o enclosure_lid.stl  -D 'part="lid"'  enclosure.scad
xvfb-run openscad -o render_open.png --camera=31,22,14,50,0,200,235 -D show_lid=false assembly.scad
```
All dimensions (wall, clearance, cutout positions, boss size) are parameters at the top of
`enclosure.scad`. Cutout positions are in board coordinates (origin top-left of the PCB).

Not yet test-printed: check the lid snap fit on the first print and adjust `clr` (0.4 mm) if
the board is tight in the cavity.
