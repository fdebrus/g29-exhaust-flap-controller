/*
  BMW Z4 G29 M40i - Exhaust flap override controller (ESP32)

  Modes:
    AUTO          relay released -> the car (DME) drives the actuator (factory behaviour)
    FORCED_OPEN   relay energized -> ESP32 sends the "open" PWM
    FORCED_CLOSED relay energized -> ESP32 sends the "closed" PWM (auto-reverts after a timeout)

  Fail-safe: at power-up, on reset, or if the ESP32 dies, the relay is released
  and the car is back in control. R6/R8 (100k) on the PCB keep both transistors off during boot.

  Libraries: rc-switch (sui77) - install from the Arduino Library Manager.
  Board: XIAO_ESP32C3 (Arduino core 2.x or 3.x). Enable "USB CDC On Boot" for Serial Monitor.

  !!! The PWM values below are PLACEHOLDERS. Measure the real DME signal first. !!!
*/

#include <WiFi.h>
#include <RCSwitch.h>

// ===================== Pins (Seeed XIAO ESP32-C3, strapping pins 2/8/9 avoided) =====================
constexpr int PIN_PWM      = 3;   // D1 -> PWM driver transistor
constexpr int PIN_RELAY    = 4;   // D2 -> relay driver transistor. HIGH = ESP32 controls the actuator
constexpr int PIN_RF_RX    = 5;   // D3 <- RXB6 data output
constexpr int PIN_DASH_ON  = 6;   // D4 <- dashboard ON wire, through 12V->3.3V divider
constexpr int PIN_DASH_OFF = 7;   // D5 <- dashboard OFF wire, through 12V->3.3V divider
constexpr int PIN_LED      = -1;  // XIAO ESP32-C3 has no user LED

// ===================== Signal parameters - SET FROM YOUR MEASUREMENTS =====================
constexpr uint32_t PWM_FREQ_HZ     = 100;    // PLACEHOLDER - copy the measured DME frequency
constexpr uint8_t  PWM_RES_BITS    = 10;
constexpr float    DUTY_OPEN_PCT   = 95.0f;  // F30 data, verify on the G29
constexpr float    DUTY_CLOSED_PCT = 5.0f;   // F30 data, verify on the G29
constexpr bool     PWM_INVERTED    = true;   // true with a low-side MOSFET + pull-up to 12V

// ===================== Behaviour =====================
constexpr bool     DASH_OFF_MEANS_AUTO      = true;  // dashboard OFF returns to factory mode
constexpr bool     ALLOW_FORCED_CLOSED      = true;  // remote OFF forces the flap closed
constexpr uint32_t FORCED_CLOSED_TIMEOUT_MS = 15UL * 60UL * 1000UL;  // back to AUTO after 15 min
constexpr uint32_t RELAY_SETTLE_MS          = 20;
constexpr uint32_t DEBOUNCE_MS              = 50;

// ===================== Remote codes =====================
// Leave at 0, open the Serial Monitor (115200), press each fob button, then paste the codes here.
constexpr unsigned long RF_CODE_ON   = 0;
constexpr unsigned long RF_CODE_AUTO = 0;
constexpr unsigned long RF_CODE_OFF  = 0;
constexpr uint32_t      RF_REPEAT_IGNORE_MS = 600;  // fobs repeat the code while held

// ===================== State =====================
enum class Mode { AUTO, FORCED_OPEN, FORCED_CLOSED };
Mode     mode      = Mode::AUTO;
uint32_t modeSince = 0;
RCSwitch rf;

struct DebouncedInput {
  int pin;
  bool stable;
  bool lastRaw;
  uint32_t changedAt;
};
DebouncedInput dashOn  {PIN_DASH_ON,  false, false, 0};
DebouncedInput dashOff {PIN_DASH_OFF, false, false, 0};

// ===================== PWM helpers (core 2.x and 3.x) =====================
void pwmInit() {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcAttach(PIN_PWM, PWM_FREQ_HZ, PWM_RES_BITS);
#else
  ledcSetup(0, PWM_FREQ_HZ, PWM_RES_BITS);
  ledcAttachPin(PIN_PWM, 0);
#endif
}

void pwmWriteRaw(uint32_t duty) {
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  ledcWrite(PIN_PWM, duty);
#else
  ledcWrite(0, duty);
#endif
}

uint32_t dutyFromWirePct(float wirePct) {
  float pct = PWM_INVERTED ? (100.0f - wirePct) : wirePct;
  const uint32_t maxDuty = (1UL << PWM_RES_BITS) - 1;
  return (uint32_t)(pct / 100.0f * maxDuty + 0.5f);
}

// ===================== Mode handling =====================
const char* modeName(Mode m) {
  switch (m) {
    case Mode::AUTO:          return "AUTO (car in control)";
    case Mode::FORCED_OPEN:   return "FORCED OPEN";
    case Mode::FORCED_CLOSED: return "FORCED CLOSED";
  }
  return "?";
}

void applyMode(Mode m) {
  if (m == Mode::FORCED_CLOSED && !ALLOW_FORCED_CLOSED) m = Mode::AUTO;
  if (m == mode) return;

  if (m == Mode::AUTO) {
    digitalWrite(PIN_RELAY, LOW);   // hand control back to the car first
    delay(RELAY_SETTLE_MS);
    pwmWriteRaw(0);                 // driver MOSFET off
  } else {
    float pct = (m == Mode::FORCED_OPEN) ? DUTY_OPEN_PCT : DUTY_CLOSED_PCT;
    pwmWriteRaw(dutyFromWirePct(pct));  // signal ready before switching
    if (mode == Mode::AUTO) {
      delay(RELAY_SETTLE_MS);
      digitalWrite(PIN_RELAY, HIGH);
    }
  }

  mode = m;
  modeSince = millis();
  if (PIN_LED >= 0) digitalWrite(PIN_LED, mode == Mode::AUTO ? LOW : HIGH);
  Serial.printf("[mode] %s\n", modeName(mode));
}

// ===================== Inputs =====================
bool risingEdge(DebouncedInput& in) {
  bool raw = digitalRead(in.pin) == HIGH;
  uint32_t now = millis();
  if (raw != in.lastRaw) {
    in.lastRaw = raw;
    in.changedAt = now;
  }
  if (raw != in.stable && now - in.changedAt >= DEBOUNCE_MS) {
    in.stable = raw;
    return raw;  // true only on a debounced LOW -> HIGH transition
  }
  return false;
}

void handleDashboard() {
  if (risingEdge(dashOn)) {
    Serial.println("[dash] ON");
    applyMode(Mode::FORCED_OPEN);
  }
  if (risingEdge(dashOff)) {
    Serial.println("[dash] OFF");
    applyMode(DASH_OFF_MEANS_AUTO ? Mode::AUTO : Mode::FORCED_CLOSED);
  }
}

void handleRemote() {
  static unsigned long lastCode = 0;
  static uint32_t lastCodeAt = 0;

  if (!rf.available()) return;
  unsigned long code = rf.getReceivedValue();
  unsigned int bits = rf.getReceivedBitlength();
  unsigned int proto = rf.getReceivedProtocol();
  rf.resetAvailable();

  if (code == 0) return;
  uint32_t now = millis();
  if (code == lastCode && now - lastCodeAt < RF_REPEAT_IGNORE_MS) {
    lastCodeAt = now;
    return;
  }
  lastCode = code;
  lastCodeAt = now;

  Serial.printf("[rf] code=%lu bits=%u protocol=%u\n", code, bits, proto);

  if (RF_CODE_ON   != 0 && code == RF_CODE_ON)   applyMode(Mode::FORCED_OPEN);
  else if (RF_CODE_AUTO != 0 && code == RF_CODE_AUTO) applyMode(Mode::AUTO);
  else if (RF_CODE_OFF  != 0 && code == RF_CODE_OFF)  applyMode(Mode::FORCED_CLOSED);
}

void handleTimeouts() {
  if (mode == Mode::FORCED_CLOSED && millis() - modeSince >= FORCED_CLOSED_TIMEOUT_MS) {
    Serial.println("[safety] forced-closed timeout, back to AUTO");
    applyMode(Mode::AUTO);
  }
}

// ===================== Setup / loop =====================
void setup() {
  pinMode(PIN_RELAY, OUTPUT);
  digitalWrite(PIN_RELAY, LOW);  // car in control, before anything else
  if (PIN_LED >= 0) { pinMode(PIN_LED, OUTPUT); digitalWrite(PIN_LED, LOW); }

  pwmInit();
  pwmWriteRaw(0);

  pinMode(PIN_DASH_ON, INPUT);   // external divider acts as pull-down
  pinMode(PIN_DASH_OFF, INPUT);

  WiFi.mode(WIFI_OFF);           // not used for now
  Serial.begin(115200);

  rf.enableReceive(digitalPinToInterrupt(PIN_RF_RX));

  Serial.println();
  Serial.println("G29 exhaust flap controller - started in AUTO (car in control)");
  if (RF_CODE_ON == 0 || RF_CODE_AUTO == 0 || RF_CODE_OFF == 0) {
    Serial.println("Remote codes not set: press each fob button and copy the codes shown.");
  }
  Serial.printf("PWM %lu Hz, open %.0f%%, closed %.0f%% (verify these on the car!)\n",
                (unsigned long)PWM_FREQ_HZ, DUTY_OPEN_PCT, DUTY_CLOSED_PCT);
}

void loop() {
  handleDashboard();
  handleRemote();
  handleTimeouts();
}
