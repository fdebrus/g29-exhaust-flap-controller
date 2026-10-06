# PCB generator (v3)

Regenerates `hardware/v3-xiao-esp32c3` from Python, so placement changes are reproducible.

Requirements: KiCad 7 (with the `pcbnew` Python module and standard footprint libraries),
Java 21, [freerouting](https://github.com/freerouting/freerouting) 2.x.

```bash
FREEROUTING_JAR=/path/to/freerouting-2.1.0.jar ./run_all.sh
```

- `build_pcb.py` - footprints, positions, nets, board outline, edge keep-out ring (the netlist lives here)
- `run_all.sh` - design rules (0.3 mm signal / 0.6 mm power, 0.2 mm clearance), Specctra export, autorouting, finishing
- `finish_pcb.py` - imports the routes, adds ground pours and silkscreen, runs DRC

Output: `g29_flap_xiao.kicad_pcb` and `drc.rpt` in this folder. Then:

```bash
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Paste,B.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts -o gerbers/ --no-protel-ext g29_flap_xiao.kicad_pcb
kicad-cli pcb export drill -o gerbers/ --format excellon --excellon-separate-th g29_flap_xiao.kicad_pcb
```

DRC on the current board: 0 errors, 0 warnings (apart from KiCad's "library not configured"
notes, which come from loading footprints by path), 0 unconnected pads.
