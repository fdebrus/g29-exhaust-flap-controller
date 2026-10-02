import pcbnew, re

mm = pcbnew.FromMM
b = pcbnew.LoadBoard('placed.kicad_pcb')

# ---- minimal s-expression parser ----
def parse(text):
    toks = re.findall(r'\(|\)|"[^"]*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t.strip('"'))
    return stack[0][0]

ses = parse(open('board.ses').read())
def find(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            yield c

routes = next(find(ses, 'routes'))
res = next(find(routes, 'resolution'))
scale = 1.0 / float(res[2]) / 1000.0           # units -> mm  (um / res)
def pt(x, y):
    return pcbnew.VECTOR2I(mm(float(x) * scale), mm(-float(y) * scale))

layers = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}
nt, nv = 0, 0
for netnode in find(next(find(routes, 'network_out')), 'net'):
    n = b.FindNet(netnode[1])
    for w in find(netnode, 'wire'):
        p = next(find(w, 'path'))
        layer, width, coords = p[1], float(p[2]) * scale, p[3:]
        xy = list(zip(coords[0::2], coords[1::2]))
        for a, c in zip(xy, xy[1:]):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pt(*a)); t.SetEnd(pt(*c))
            t.SetWidth(mm(width)); t.SetLayer(layers[layer]); t.SetNet(n)
            b.Add(t); nt += 1
    for v in find(netnode, 'via'):
        via = pcbnew.PCB_VIA(b)
        via.SetPosition(pt(v[2], v[3]))
        via.SetWidth(mm(0.8)); via.SetDrill(mm(0.4))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); via.SetNet(n)
        b.Add(via); nv += 1
print('tracks', nt, 'vias', nv)

# ---- ground pours on both layers ----
OX, OY, W, H = 100, 100, 60, 46
gnd = b.FindNet('GND')
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(gnd)
    z.SetLocalClearance(mm(0.4)); z.SetMinThickness(mm(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetThermalReliefGap(mm(0.5)); z.SetThermalReliefSpokeWidth(mm(0.5))
    ol = z.Outline(); ol.NewOutline()
    for x, y in [(0.5, 0.5), (W - 0.5, 0.5), (W - 0.5, H - 0.5), (0.5, H - 0.5)]:
        ol.Append(mm(OX + x), mm(OY + y))
    b.Add(z)

# ---- silkscreen labels ----
def silk(txt, x, y, size=1.0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetLayer(layer)
    if layer == pcbnew.B_SilkS: t.SetMirrored(True)
    t.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size))); t.SetTextThickness(mm(size * 0.15))
    b.Add(t)

for f in b.GetFootprints():
    if f.GetReference() in ("U1A", "U1B", "J1", "J2", "J3"): f.Reference().SetVisible(False)
silk("J2: 12V ON OFF", 7.5, 36.9, 0.8)
silk("J1: 12V GND", 26.0, 36.9, 0.8)
silk("J3: DME FLAP GND", 47.5, 36.9, 0.8)
silk("XIAO ESP32-C3  USB ^", 11.6, 1.5, 0.8)
silk("G29 flap ctrl v2 (XIAO)", 30.0, 23.0, 1.2, pcbnew.B_SilkS)
silk("R10 OR R11", 47.0, 35.0, 0.8)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
out = 'g29_flap_xiao.kicad_pcb'
b.Save(out)
print('drc written', pcbnew.WriteDRCReport(b, 'drc.rpt', pcbnew.EDA_UNITS_MILLIMETRES, True))
