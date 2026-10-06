import pcbnew, sys

# G29 exhaust flap controller - board v3 (XIAO ESP32-C3, SMT passives, relay kept,
# on-board 433 MHz receiver (JSMSEMI SYN480R), no dashboard-button inputs: the
# button reaches the board over 433 MHz like the fob).

FP = "/usr/share/kicad/footprints/"
board = pcbnew.BOARD()
board.GetDesignSettings().SetCopperLayerCount(2)

OX, OY = 100.0, 100.0          # board origin (mm)
W, H = 58.0, 40.0              # board size (mm)
mm = pcbnew.FromMM

nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]

def place(lib, name, ref, value, x, y, rot=0, pads=None, lcsc=""):
    fp = pcbnew.FootprintLoad(FP + lib + ".pretty", name)
    if fp is None:
        sys.exit(f"missing footprint {lib}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    fp.SetOrientationDegrees(rot)
    if lcsc:
        fp.SetProperty("LCSC", lcsc)
    board.Add(fp)
    if pads:
        for p in fp.Pads():
            n = pads.get(p.GetNumber())
            if n:
                p.SetNet(net(n))
    return fp

R0805 = ("Resistor_SMD", "R_0805_2012Metric")
R1206 = ("Resistor_SMD", "R_1206_3216Metric")
C0805 = ("Capacitor_SMD", "C_0805_2012Metric")
SMA   = ("Diode_SMD", "D_SMA")
SOD   = ("Diode_SMD", "D_SOD-123")
SOT23 = ("Package_TO_SOT_SMD", "SOT-23")
TB2   = ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")
S7    = ("Connector_PinSocket_2.54mm", "PinSocket_1x07_P2.54mm_Vertical")
S4    = ("Connector_PinSocket_2.54mm", "PinSocket_1x04_P2.54mm_Vertical")

# ---------------- modules ----------------
# Seeed XIAO ESP32-C3, USB toward top edge. Left: D0..D6, right: 5V GND 3V3 D10 D9 D8 D7
place(*S7, "U1A", "XIAO left", 4.0, 4.0, 0, {"2": "IO3", "3": "IO4", "4": "IO5"})
place(*S7, "U1B", "XIAO right", 19.24, 4.0, 0, {"1": "+5V_X", "2": "GND", "3": "+3V3"})
# ---------------- 433 MHz receiver: JSMSEMI SYN480R (C916347), datasheet typical application ----------------
# ANT -> node A; C2 1.8p and L1 27n shunt to GND; C1 6.8p series -> ANT pin; L2 47n shunt at ANT pin;
# C3 1u on VDD; SHUT -> GND (receive); SQ -> R1 0R -> GND (squelch off); RO -> Y1 13.52127 MHz -> GND.
C0603 = ("Capacitor_SMD", "C_0603_1608Metric"); L0603 = ("Inductor_SMD", "L_0603_1608Metric"); R0603 = ("Resistor_SMD", "R_0603_1608Metric")
place("TestPoint", "TestPoint_THTPad_D2.0mm_Drill1.0mm", "ANT1", "ANT 17cm", 26.0, 2.5, 0, {"1": "ANT_IN"})
place(*C0603, "C7", "1.8p C0G", 23.5, 5.5, 0, {"1": "ANT_IN", "2": "GND"})
place(*L0603, "L1", "27nH", 28.5, 5.5, 0, {"1": "ANT_IN", "2": "GND"})
place(*C0603, "C8", "6.8p C0G", 26.0, 8.0, 90, {"1": "ANT_IN", "2": "RF_IN"})
place(*L0603, "L2", "47nH", 30.0, 9.5, 0, {"1": "RF_IN", "2": "GND"})
# SOIC-8, pins 1-4 down the left side (1 GND, 2 ANT, 3 VDD, 4 NC), 5-8 up the right (5 DO, 6 SHUT, 7 SQ, 8 RO)
place("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm", "U3", "SYN480R", 25.0, 13.5, 0,
      {"1": "GND", "2": "RF_IN", "3": "+3V3", "5": "IO5", "6": "GND", "7": "SQ", "8": "XTAL"}, lcsc="C916347")
place(*C0603, "C9", "1u", 23.5, 17.8, 0, {"1": "+3V3", "2": "GND"})
place(*R0603, "R12", "0R", 27.3, 20.2, 0, {"1": "SQ", "2": "GND"})
place("Crystal", "Crystal_SMD_HC49-SD", "Y1", "13.52127MHz", 31.5, 18.0, 90, {"1": "XTAL", "2": "GND"}, lcsc="C279599")

# ---------------- relay ----------------
# G5V-2: 1/16 coil; 4,13 COM; 6,11 NC; 8,9 NO
# pole A: COM 4 = actuator, NC 6 = DME (fail-safe path), NO 8 = ESP32 PWM
# pole B: COM 13 = DME, NO 9 = dummy load while the ESP32 drives the flap
place("Relay_THT", "Relay_DPDT_Omron_G5V-2", "K1", "G5V-2-H1 DC12", 36.0, 4.0, 0,
      {"1": "COIL_N", "16": "+12V", "4": "ACT_SIG", "6": "DME_SIG", "8": "PWM_OUT",
       "13": "DME_SIG", "9": "DUMMY"}, lcsc="C128021")

# ---------------- power ----------------
place("Fuse", "Fuse_1812_4532Metric", "F1", "PTC 0.5A", 50.3, 3.8, 90, {"1": "+12V_IN", "2": "+12V_F"})
place(*SMA, "D1", "SS14", 53.0, 10.3, 90, {"1": "+12V", "2": "+12V_F"}, lcsc="C2480")     # pad 1 = cathode
place(*SMA, "D2", "SMAJ20A", 53.0, 17.4, 90, {"1": "+12V", "2": "GND"})                    # TVS, pad 1 = cathode
place("Capacitor_SMD", "CP_Elec_6.3x7.7", "C1", "100u 35V", 53.0, 26.0, 90, {"1": "+12V", "2": "GND"})
place("Package_TO_SOT_SMD", "TO-252-2", "U2", "78M05", 45.0, 36.0, 0, {"1": "+12V", "2": "GND", "3": "+5V"})
place(*C0805, "C2", "100n", 40.0, 30.0, 0, {"1": "+12V", "2": "GND"})
place(*C0805, "C3", "100n", 51.5, 31.9, 0, {"1": "+5V", "2": "GND"})
place(*C0805, "C4", "10u", 51.2, 37.0, 90, {"1": "+5V", "2": "GND"})
place(*SMA, "D6", "SS14", 12.0, 28.0, 0, {"1": "+5V_X", "2": "+5V"}, lcsc="C2480")        # pad 1 = cathode, toward the XIAO

# ---------------- relay driver ----------------
place(*R0805, "R5", "1k", 4.0, 24.0, 0, {"1": "IO4", "2": "Q1_B"})
place(*R0805, "R6", "100k", 8.5, 24.0, 0, {"1": "Q1_B", "2": "GND"})
place(*SOT23, "Q1", "S8050", 13.0, 24.0, 0, {"1": "Q1_B", "2": "GND", "3": "COIL_N"})      # SOT-23: 1 B, 2 E, 3 C
place(*SOD, "D5", "1N4148W", 30.5, 26.5, 0, {"1": "+12V", "2": "COIL_N"}, lcsc="C81598")  # pad 1 = cathode at +12V

# ---------------- PWM driver ----------------
place(*R0805, "R7", "1k", 17.5, 24.0, 0, {"1": "IO3", "2": "Q2_B"})
place(*R0805, "R8", "100k", 22.0, 24.0, 0, {"1": "Q2_B", "2": "GND"})
place(*SOT23, "Q2", "S8050", 25.5, 27.5, 0, {"1": "Q2_B", "2": "GND", "3": "PWM_OUT"})
place(*R0805, "R9", "1k opt", 40.0, 26.0, 0, {"1": "+12V", "2": "PWM_OUT"})               # DNP by default

# ---------------- dummy load (fit R10 or R11 after measurement) ----------------
place(*R1206, "R10", "DUM-GND", 35.5, 26.5, 0, {"1": "DUMMY", "2": "GND"})
place(*R1206, "R11", "DUM-12V", 35.5, 30.0, 0, {"1": "DUMMY", "2": "+12V"})

# ---------------- connectors ----------------
place(*TB2, "J1", "PWR", 4.0, 35.0, 0, {"1": "+12V_IN", "2": "GND"})
place(*TB2, "J3", "FLAP", 24.0, 35.0, 0, {"1": "DME_SIG", "2": "ACT_SIG"})

# ---------------- mounting holes (M2.5, for the enclosure bosses) ----------------
def hole(ref, x, y, d=2.7):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref); fp.SetValue("M2.5")
    fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
    fp.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    p = pcbnew.PAD(fp)
    p.SetAttribute(pcbnew.PAD_ATTRIB_NPTH); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
    p.SetSize(pcbnew.VECTOR2I(mm(d), mm(d))); p.SetDrillSize(pcbnew.VECTOR2I(mm(d), mm(d)))
    p.SetLayerSet(pcbnew.LSET.AllCuMask().AddLayer(pcbnew.F_Mask).AddLayer(pcbnew.B_Mask))
    p.SetPosition(fp.GetPosition())
    fp.Add(p); board.Add(fp)
for ref, (x, y) in {"H1": (55.5, 3.0), "H2": (15.75, 37.0), "H3": (55.5, 37.0)}.items():
    hole(ref, x, y)

# ---------------- board outline ----------------
pts = [(0, 0), (W, 0), (W, H), (0, H)]
for a, b in zip(pts, pts[1:] + pts[:1]):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    s.SetStart(pcbnew.VECTOR2I(mm(OX + a[0]), mm(OY + a[1])))
    s.SetEnd(pcbnew.VECTOR2I(mm(OX + b[0]), mm(OY + b[1])))
    board.Add(s)

# ---------------- routing keep-out ring along the board edge (0.6 mm, both layers) ----------------
def keepout(x0, y0, x1, y1):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True); z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True)
    z.SetDoNotAllowCopperPour(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
    z.SetLayerSet(pcbnew.LSET.AllCuMask(2))
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i, (px, py) in enumerate(pts):
        v = pcbnew.VECTOR2I(mm(OX + px), mm(OY + py))
        if i == 0: z.AppendCorner(v, -1)
        else: z.AppendCorner(v, -1)
    board.Add(z)
E = 0.6
keepout(0, 0, W, E); keepout(0, H - E, W, H); keepout(0, 0, E, H); keepout(W - E, 0, W, H)

out = sys.argv[1] if len(sys.argv) > 1 else "placed.kicad_pcb"
board.Save(out)
print("saved", out, "footprints:", len(board.GetFootprints()))
