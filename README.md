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
 ESP32 PWM driver ------| NO              |
                        +------------------+
```

- **AUTO** (default, relay released): the car drives the flap exactly as from the factory.
- **ON / OFF**: the ESP32 energizes the relay and sends its own PWM signal (flap open / closed).
- **Fail-safe**: if the board loses power, resets or crashes, the relay drops and the car is back in control.
- Only the **signal wire** is switched. The actuator's +12 V and ground stay on the original harness.
- The relay's second pole connects a **dummy load** to the DME while the ESP32 is in control,
  to try to avoid an open-circuit fault code.

Controls: the dashboard button (two 12 V wires, ON / OFF) and the original 433 MHz key fob (ON / AUTO / OFF).

## Project status

- [x] Teardown and analysis of the commercial kit ([docs/findings.md](docs/findings.md))
- [x] Firmware (AUTO / ON / OFF, dashboard + 433 MHz remote, fail-safe start)
- [x] PCB v1 (ESP32-DevKitC, 95 x 72 mm) and v2 (XIAO ESP32-C3, 60 x 46 mm)
- [ ] **Bench measurement of the kit's output signal** ([docs/measurement.md](docs/measurement.md))
- [ ] Measurement on the car (DME signal, actuator input impedance)
- [ ] Set PWM frequency / duty cycles in the firmware
- [ ] Verify XIAO footprint (1:1 print) and order PCB v2
- [ ] Assembly, bench test, installation ([docs/installation.md](docs/installation.md))
- [ ] Check fault memory after a few drives

## Repository layout

| Path | Content |
|---|---|
| `firmware/g29_exhaust_flap_xiao/` | Firmware for PCB v2 (Seeed XIAO ESP32-C3) - **recommended** |
| `firmware/g29_exhaust_flap_devkitc/` | Firmware for PCB v1 (ESP32-DevKitC V4) |
| `hardware/v2-xiao-esp32c3/` | KiCad board, Gerbers, BOM, previews - **recommended** |
| `hardware/v1-esp32-devkitc/` | First, larger version |
| `tools/pcb-generator/` | Scripts that regenerate the v2 board (KiCad 7 + freerouting) |
| `docs/` | Findings, measurement procedure, installation, shopping list |

## Important values still to confirm

The firmware PWM values are **placeholders** until measured:

| Parameter | Current value | Source |
|---|---|---|
| `PWM_FREQ_HZ` | 100 | guess - **must be measured** |
| `DUTY_OPEN_PCT` | 95 % | BMW F30 measurement, not verified on G29 |
| `DUTY_CLOSED_PCT` | 5 % | BMW F30 measurement, not verified on G29 |

## Disclaimer

Personal project, provided as-is. Modifying the exhaust behaviour may affect road legality
(noise approval), the vehicle inspection, warranty and insurance. The DME may log fault codes while
the controller is in ON/OFF mode. Measure before connecting anything to the car. Use at your own risk.

## License

MIT - see [LICENSE](LICENSE).
