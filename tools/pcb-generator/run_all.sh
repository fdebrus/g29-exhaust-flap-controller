#!/usr/bin/env bash
# Regenerates the v2 board: place -> autoroute (freerouting 2.x) -> ground pour -> DRC.
# Needs KiCad 7 (pcbnew Python module) and Java 21. Set FREEROUTING_JAR to the freerouting jar path.
set -e
cd "$(dirname "$0")"
python3 build_pcb.py > /dev/null
python3 - <<'P'
import pcbnew
b=pcbnew.LoadBoard('placed.kicad_pcb')
nc=b.GetDesignSettings().m_NetSettings.m_DefaultNetClass
nc.SetTrackWidth(pcbnew.FromMM(0.4)); nc.SetClearance(pcbnew.FromMM(0.25))
nc.SetViaDiameter(pcbnew.FromMM(0.8)); nc.SetViaDrill(pcbnew.FromMM(0.4))
b.Save('placed.kicad_pcb')
pcbnew.ExportSpecctraDSN(b,'board.dsn')
P
python3 - <<'P'
p='board.dsn'; t=open(p).read()
s=t.index('(class kicad_default'); seg=t[s:]; d=0
for i,ch in enumerate(seg):
    d+= ch=='('; d-= ch==')'
    if ch==')' and d==0: break
cls=seg[:i+1]; power=['+12V','+12V_F','+12V_IN','+5V','GND']
sig=[n for n in cls.split('"')[2].split('(circuit')[0].split() if n not in power]
via='(circuit (use_via Via[0-1]_800:400_um))'
new=f'(class kicad_default "" {" ".join(sig)} {via} (rule (width 400) (clearance 250.1)))\n    (class power {" ".join(power)} {via} (rule (width 800) (clearance 250.1)))'
open(p,'w').write(t[:s]+new+seg[i+1:])
P
rm -f board.ses
timeout 900 java -jar "${FREEROUTING_JAR:-freerouting.jar}" --gui.enabled=false -de board.dsn -do board.ses -mp 60 > fr.log 2>&1
grep -o '"incomplete_count": [0-9]*' fr.log | tail -1
python3 finish_pcb.py
