import pcbnew, sys

FP = "/usr/share/kicad/footprints/"
board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.SetCopperLayerCount(2)

OX, OY = 100.0, 100.0          # board origin (mm)
W, H = 60.0, 46.0              # board size (mm)
mm = pcbnew.FromMM

nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]

def place(lib, name, ref, value, x, y, rot=0, pads=None, silk_value=False):
    fp = pcbnew.FootprintLoad(FP + lib + ".pretty", name)
    if fp is None:
        sys.exit(f"missing footprint {lib}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
    fp.SetOrientationDegrees(rot)
    board.Add(fp)
    if pads:
        for p in fp.Pads():
            n = pads.get(p.GetNumber())
            if n:
                p.SetNet(net(n))
    if silk_value:
        fp.Value().SetLayer(pcbnew.F_SilkS)
    return fp


R  = ("Resistor_THT", "R_Axial_DIN0207_L6.3mm_D2.5mm_P2.54mm_Vertical")
DZ = ("Diode_THT", "D_DO-35_SOD27_P2.54mm_Vertical_AnodeUp")
CD = ("Capacitor_THT", "C_Disc_D3.0mm_W2.0mm_P2.50mm")
TO92 = ("Package_TO_SOT_THT", "TO-92_Inline_Wide")
TB2 = ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal")
TB3 = ("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal")
S7 = ("Connector_PinSocket_2.54mm", "PinSocket_1x07_P2.54mm_Vertical")

# Seeed XIAO ESP32-C3, USB toward top edge. Left: D0..D6, right: 5V GND 3V3 D10 D9 D8 D7
place(*S7, "U1A", "XIAO left", 4.0, 4.0, 0, {"2": "IO3", "3": "IO4", "4": "IO5", "5": "IO6", "6": "IO7"})
place(*S7, "U1B", "XIAO right", 19.24, 4.0, 0, {"1": "+5V_X", "2": "GND", "3": "+3V3"})
place("Connector_PinSocket_2.54mm", "PinSocket_1x04_P2.54mm_Vertical", "J4", "RF", 24.0, 4.0, 0,
      {"1": "GND", "2": "IO5", "3": "IO5", "4": "+3V3"})

# relay
place("Relay_THT", "Relay_DPDT_Omron_G5V-2", "K1", "G5V-2-12VDC", 28.0, 4.0, 0,
      {"1": "COIL_N", "16": "+12V", "4": "ACT_SIG", "6": "DME_SIG", "8": "PWM_OUT",
       "13": "DME_SIG", "9": "DUMMY"})

# power
place("Capacitor_THT", "C_Disc_D7.5mm_W5.0mm_P5.00mm", "F1", "PTC", 44.0, 4.6, 0, {"1": "+12V_IN", "2": "+12V_F"})
place("Diode_THT", "D_DO-41_SOD81_P3.81mm_Vertical_AnodeUp", "D1", "1N5819", 53.0, 4.0, 0, {"1": "+12V", "2": "+12V_F"})
place("Diode_THT", "D_DO-15_P5.08mm_Vertical_AnodeUp", "D2", "P6KE20A", 44.0, 9.5, 0, {"1": "+12V", "2": "GND"})
place("Capacitor_THT", "CP_Radial_D6.3mm_P2.50mm", "C1", "100u35V", 54.0, 10.3, 0, {"1": "+12V", "2": "GND"})
place("Package_TO_SOT_THT", "TO-220-3_Vertical", "U2", "L7805", 45.0, 16.5, 0, {"1": "+12V", "2": "GND", "3": "+5V"})
place(*CD, "C2", "330n", 43.5, 21.0, 0, {"1": "+12V", "2": "GND"})
place(*CD, "C3", "100n", 48.5, 21.0, 0, {"1": "+5V", "2": "GND"})
place("Capacitor_THT", "CP_Radial_D5.0mm_P2.00mm", "C4", "10u", 54.5, 21.0, 0, {"1": "+5V", "2": "GND"})
place("Diode_THT", "D_DO-41_SOD81_P3.81mm_Vertical_AnodeUp", "D6", "1N5819", 44.0, 26.5, 0, {"1": "+5V_X", "2": "+5V"})
place(*DZ, "D5", "1N4148", 56.0, 32.5, 0, {"1": "+12V", "2": "COIL_N"})
place(*R, "R9", "1k opt", 51.0, 26.5, 0, {"1": "+12V", "2": "PWM_OUT"})
place(*R, "R10", "DUM-GND", 44.0, 32.5, 0, {"1": "DUMMY", "2": "GND"})
place(*R, "R11", "DUM-12V", 50.0, 32.5, 0, {"1": "DUMMY", "2": "+12V"})

# inputs (row A)
place(*R, "R1", "10k", 2.5, 26.5, 0, {"1": "DASH_ON", "2": "IO6"})
place(*R, "R2", "3k3", 8.0, 26.5, 0, {"1": "IO6", "2": "GND"})
place(*DZ, "D3", "3V3", 13.5, 26.5, 0, {"1": "IO6", "2": "GND"})
place(*CD, "C5", "100n", 6.0, 22.6, 0, {"1": "IO6", "2": "GND"})
place(*R, "R3", "10k", 19.0, 26.5, 0, {"1": "DASH_OFF", "2": "IO7"})
place(*R, "R4", "3k3", 24.5, 26.5, 0, {"1": "IO7", "2": "GND"})
place(*DZ, "D4", "3V3", 30.0, 26.5, 0, {"1": "IO7", "2": "GND"})
place(*CD, "C6", "100n", 12.0, 22.6, 0, {"1": "IO7", "2": "GND"})

# drivers (row B)
place(*R, "R5", "1k", 2.5, 32.5, 0, {"1": "IO4", "2": "Q1_B"})
place(*R, "R6", "100k", 8.0, 32.5, 0, {"1": "Q1_B", "2": "GND"})
place(*TO92, "Q1", "BC337", 13.5, 32.5, 0, {"1": "COIL_N", "2": "Q1_B", "3": "GND"})
place(*R, "R7", "1k", 21.5, 32.5, 0, {"1": "IO3", "2": "Q2_B"})
place(*R, "R8", "100k", 27.0, 32.5, 0, {"1": "Q2_B", "2": "GND"})
place(*TO92, "Q2", "BC337", 32.5, 32.5, 0, {"1": "PWM_OUT", "2": "Q2_B", "3": "GND"})

# connectors
place(*TB3, "J2", "DASH", 4.0, 41.0, 0, {"1": "+12V", "2": "DASH_ON", "3": "DASH_OFF"})
place(*TB2, "J1", "PWR", 24.0, 41.0, 0, {"1": "+12V_IN", "2": "GND"})
place(*TB3, "J3", "FLAP", 44.0, 41.0, 0, {"1": "DME_SIG", "2": "ACT_SIG", "3": "GND"})
# ---------------- Board outline ----------------
pts = [(0, 0), (W, 0), (W, H), (0, H)]
for a, b in zip(pts, pts[1:] + pts[:1]):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(mm(0.1))
    s.SetStart(pcbnew.VECTOR2I(mm(OX + a[0]), mm(OY + a[1])))
    s.SetEnd(pcbnew.VECTOR2I(mm(OX + b[0]), mm(OY + b[1])))
    board.Add(s)

out = sys.argv[1] if len(sys.argv) > 1 else "placed.kicad_pcb"
board.Save(out)
print("saved", out, "footprints:", len(board.GetFootprints()))
