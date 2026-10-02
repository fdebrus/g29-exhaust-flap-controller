# PCB generator (v2)

Regenerates `hardware/v2-xiao-esp32c3` from Python, so placement changes are reproducible.

Requirements: KiCad 7 (with the `pcbnew` Python module and standard footprint libraries),
Java 21, [freerouting](https://github.com/freerouting/freerouting) 2.x.

```bash
FREEROUTING_JAR=/path/to/freerouting-2.1.0.jar ./run_all.sh
```

- `build_pcb.py` - footprints, positions, nets, board outline
- `run_all.sh` - design rules, Specctra export, autorouting, finishing
- `finish_pcb.py` - imports the routes, adds ground pours and silkscreen, runs DRC

Output: `g29_flap_xiao.kicad_pcb` and `drc.rpt` in this folder.
