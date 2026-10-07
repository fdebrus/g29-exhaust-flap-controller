/*
  PWM probe for the G29 flap project - Seeed XIAO ESP32-C3

  Measures frequency, duty cycle and high/low times of a 12 V logic signal.
  Wiring: signal -> 10k -> GPIO5 (D3), 3.3k from GPIO5 to GND, grounds common.
  (12 V * 3.3 / 13.3 = 3.0 V at the pin; never feed 12 V directly.)

  Serial Monitor 115200. Prints once per second. "DC high"/"DC low" when no edges
  are seen, which is how you tell a true DC level from a PWM.
*/
constexpr int PIN_IN = 5;

volatile uint32_t tRise = 0, tFall = 0;
volatile uint32_t highSum = 0, lowSum = 0, periodSum = 0;
volatile uint32_t edges = 0, periods = 0;
volatile uint32_t minHigh = UINT32_MAX, maxHigh = 0;

void IRAM_ATTR onEdge() {
  uint32_t now = micros();
  if (digitalRead(PIN_IN)) {                 // rising edge
    if (tRise) { periodSum += now - tRise; periods++; }
    if (tFall) lowSum += now - tFall;
    tRise = now;
  } else {                                   // falling edge
    if (tRise) {
      uint32_t h = now - tRise; highSum += h;
      if (h < minHigh) minHigh = h;
      if (h > maxHigh) maxHigh = h;
    }
    tFall = now;
  }
  edges++;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_IN, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_IN), onEdge, CHANGE);
  delay(1500);
  Serial.println("\nPWM probe on GPIO5: freq / duty / high / low, 1 s windows");
}

void loop() {
  delay(1000);
  noInterrupts();
  uint32_t e = edges, p = periods, hs = highSum, ls = lowSum, ps = periodSum;
  uint32_t mnH = minHigh, mxH = maxHigh;
  edges = periods = highSum = lowSum = periodSum = 0; minHigh = UINT32_MAX; maxHigh = 0;
  interrupts();

  if (p < 2) {
    Serial.printf("no PWM: DC %s (%u edges)\n", digitalRead(PIN_IN) ? "HIGH" : "LOW", e);
    return;
  }
  float period = (float)ps / p;                 // us
  float high = (float)hs / p, low = (float)ls / p;
  Serial.printf("f = %7.1f Hz   duty(high) = %5.1f %%   high = %7.1f us   low = %7.1f us   jitter(high) %u..%u us\n",
                1e6f / period, 100.0f * high / (high + low), high, low, mnH, mxH);
}
