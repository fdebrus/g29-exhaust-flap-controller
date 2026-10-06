# G29 Exhaust Flap Controller

Open-source controller for the exhaust flap of the **BMW Z4 G29 M40i**: open the flap on demand
(even in Comfort mode) while keeping **full factory behaviour** the rest of the time.

Commercial kits exist, but the cheap ones replace the factory control entirely (their "AUTO" mode
does not hand control back to the car). This project fixes that with a fail-safe relay design.

## How it works

```
                       +------------------+
Engine computer (DME) -| NC              |
                       |   DPDT relay    COM|--- Exhaust flap actuator (signal wire)
ESP32-C3 PWM driver ---| NO              |
                       +------------------+
```

- **AUTO** (default, relay released): the car drives the flap exactly as from the factory.
- **ON / OFF**: the ESP32-C3 energizes the relay and sends its own PWM signal (flap open / closed).
- **Fail-safe**: if the board loses power, resets or crashes, the relay drops and the car is back in control.
- Only the **signal wire** is cut. The actuator's +12 V and ground stay on the original harness.
  The board takes its own power from a fused source in the trunk, not from the actuator wires.
- The relay's second pole connects a **dummy load** to the DME while the ESP32-C3 is in control,
  to try to avoid an open-circuit fault code.

Controls: the original 433 MHz key fob (ON / AUTO / OFF) and the kit's dashboard button, whose
cabin box also transmits on 433 MHz. Nothing is wired from the dashboard to the board.

## Hardware

Board **v3**: Seeed XIAO ESP32-C3 on socket strips, **on-board 433 MHz receiver** (JSMSEMI
SYN480R + 13.52127 MHz crystal, wire antenna pad), SMT passives (0603/0805, SMA, SOD-123,
SOT-23, DPAK), Omron G5V-2 DPDT relay, two 2-pin screw terminals. **58 x 40 mm**, 2 layers,
29 placed parts, designed for JLCPCB assembly (`hardware/v3-xiao-esp32c3/jlcpcb/`). No RXB6
module any more.

Earlier boards are in the git history only: v2 (same circuit with through-hole parts, an RXB6
module and a wired dashboard input, 60 x 46 mm) before the `v2-removed` tag, v1 (ESP32-DevKitC)
before the `v1-removed` tag.

## Project status

- [x] Teardown and analysis of the commercial kit ([docs/findings.md](docs/findings.md))
- [x] Firmware (AUTO / ON / OFF over 433 MHz: fob + dashboard button, fail-safe start)
- [x] PCB v3 (XIAO ESP32-C3, on-board SYN480R receiver, SMT, 58 x 40 mm, 3 mounting holes, DRC clean)
- [x] 3D-printed enclosure (OpenSCAD, 62.8 x 44.8 x 26 mm, not yet test-printed)
- [ ] Receiver sensitivity check against an RXB6 (first board)
- [x] Harness survey on the car: tap point and wire identification ([docs/harness.md](docs/harness.md))
- [ ] **Bench measurement of the kit's output signal** ([docs/measurement.md](docs/measurement.md))
- [ ] Measurement on the car (DME signal, actuator input impedance)
- [ ] Set PWM frequency / duty cycles in the firmware
- [ ] Verify XIAO footprint (1:1 print) and order the assembled PCB
- [ ] Assembly, bench test, installation ([docs/installation.md](docs/installation.md))
- [ ] Check fault memory after a few drives

## Repository layout

| Path                              | Content                                                      |
| --------------------------------- | ------------------------------------------------------------ |
| `firmware/g29_exhaust_flap_xiao/` | Firmware (Seeed XIAO ESP32-C3)                               |
| `hardware/v3-xiao-esp32c3/`       | KiCad board, Gerbers, previews, DRC report, JLCPCB BOM + CPL, 3D-printed enclosure |
| `tools/pcb-generator/`            | Scripts that regenerate the board (KiCad 7 + freerouting)    |
| `docs/`                           | Findings, harness survey, measurement, installation, shopping list |

## Important values still to confirm

The firmware PWM values are **placeholders** until measured:

| Parameter         | Current value | Source                                   |
| ----------------- | ------------- | ---------------------------------------- |
| `PWM_FREQ_HZ`     | 100           | guess - **must be measured**             |
| `DUTY_OPEN_PCT`   | 95 %          | BMW F30 measurement, not verified on G29 |
| `DUTY_CLOSED_PCT` | 5 %           | BMW F30 measurement, not verified on G29 |

## Disclaimer

Personal project, provided as-is. Modifying the exhaust behaviour may affect road legality
(noise approval), the vehicle inspection, warranty and insurance. The DME may log fault codes while
the controller is in ON/OFF mode. Measure before connecting anything to the car. Use at your own risk.

## License

MIT - see [LICENSE](LICENSE).
