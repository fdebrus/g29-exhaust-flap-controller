# Measurement procedure

Goal: confirm PWM, and get the **frequency** and **duty cycles** for the firmware, plus the
dummy-load and pull-up values for the PCB.

## What PWM means

The signal wire switches between 0 V and 12 V at a fixed rhythm (the **frequency**, in Hz).
The share of each cycle spent at 12 V is the **duty cycle** (%). The actuator reads the duty
cycle as a position: e.g. 5 % closed, 95 % open, values in between = intermediate positions.

## Equipment

- USB logic analyser, 24 MHz 8-channel (fx2lafw-compatible clone, ~10 EUR)
- [PulseView](https://sigrok.org/wiki/PulseView) (free). On Windows, install the driver with Zadig as described on the sigrok wiki.
- 10 kΩ and 3.3 kΩ resistors (voltage divider)
- Multimeter, back-probe pins
- Laptop running on battery

## Protect the analyser - always

The analyser inputs accept **5 V maximum**. Car signals are 12-14 V.

```
 signal wire ---[ 10 kΩ ]---+--- CH1
                            |
                         [ 3.3 kΩ ]
                            |
 ground ------------------- +--- GND (analyser)
```

14 V in -> about 3.5 V on CH1. Always connect the analyser GND to the circuit ground.

## Step 1 - Bench test on the commercial kit (no car needed)

1. Power the kit's **trunk box** with 12 V (bench supply or 12 V battery).
2. Divider input on the **red-black** output wire (seller's information), analyser GND on the box ground.
3. PulseView: driver `fx2lafw`, sample rate >= 1 MHz, a few seconds of capture.
4. Press **ON** on the fob, capture. Press **OFF**, capture.

Read:
- Regular square wave, duty cycle changes ON vs OFF -> **PWM**. Note frequency and both duty cycles.
- Irregular bursts that don't change shape -> possibly **LIN** (PulseView has a LIN decoder). Stop and redesign.

Note: this shows what the kit sends. The car may use other values - step 2 checks that.

## Step 2 - On the car (DME signal)

1. Back-probe the actuator connector signal wire, connector **plugged in**, ignition on.
2. Capture in **Comfort**, then **Sport**, engine running.
3. Note frequency and duty cycle in each mode.

Use the DME values for the firmware if they differ from the kit.

## Step 3 - Actuator input (for R9 / R10 / R11)

Connector **unplugged**, multimeter on the **actuator side**:
- Resistance signal pin -> ground, and signal pin -> +12 V pin.
- This sizes the dummy load (fit R10 to GND **or** R11 to +12 V, same value as measured).
- If the line floats with the actuator alone, the DME output is probably open-collector and **R9** (pull-up) is needed.

## Results (fill in)

| | Kit ON | Kit OFF | Car Comfort | Car Sport |
|---|---|---|---|---|
| Frequency (Hz) | | | | |
| Duty cycle (%) | | | | |

| Actuator measurement | Value |
|---|---|
| Signal -> GND | |
| Signal -> +12 V | |
