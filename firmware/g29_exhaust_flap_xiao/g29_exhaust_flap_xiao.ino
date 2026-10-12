/*
  BMW Z4 G29 M40i - Exhaust flap override controller (ESP32)

  Modes:
    AUTO          relay released -> the car (DME) drives the actuator (factory behaviour)
    FORCED_OPEN   relay energized -> ESP32 sends the "open" PWM
    FORCED_CLOSED relay energized -> ESP32 sends the "closed" PWM (auto-reverts after a timeout)

  Fail-safe: at power-up, on reset, or if the ESP32 dies, the relay is released
  and the car is back in control. R6/R8 (100k) on the PCB keep both transistors off during boot.

  Controls: the original 433 MHz key fob, and the dashboard button of the commercial kit.
  The button is not wired to this board: its cabin box transmits on 433 MHz like the fob,
  so both arrive through the on-board SYN480R receiver (U3, DO -> GPIO5). Capture the codes
  of both with the Serial Monitor.

  Libraries: rc-switch (sui77) - install from the Arduino Library Manager.
  Board: XIAO_ESP32C3 (Arduino core 2.x or 3.x). Enable "USB CDC On Boot" for Serial Monitor.

  !!! The PWM values below are PLACEHOLDERS. Measure the real DME signal first. !!!
*/

#include <WiFi.h>
#include <RCSwitch.h>

// ===================== Pins (Seeed XIAO ESP32-C3, strapping pins 2/8/9 avoided) =====================
constexpr int PIN_PWM      = 3;   // D1 -> PWM driver transistor
constexpr int PIN_RELAY    = 4;   // D2 -> relay driver transistor. HIGH = ESP32 controls the actuator
constexpr int PIN_RF_RX    = 5;   // D3 <- SYN480R DO (on-board 433 MHz receiver)
constexpr int PIN_LED      = -1;  // XIAO ESP32-C3 has no user LED

// ===================== Signal parameters - SET FROM YOUR MEASUREMENTS =====================
constexpr uint32_t PWM_FREQ_HZ     = 100;    // PLACEHOLDER - copy the measured DME frequency
constexpr uint8_t  PWM_RES_BITS    = 10;
constexpr float    DUTY_OPEN_PCT   = 95.0f;  // F30 data, verify on the G29
constexpr float    DUTY_CLOSED_PCT = 5.0f;   // F30 data, verify on the G29
constexpr bool     PWM_INVERTED    = true;   // true with a low-side MOSFET + pull-up to 12V

// ===================== Behaviour =====================
constexpr bool     BTN_OFF_MEANS_AUTO       = true;  // dashboard-button OFF returns to factory mode
constexpr bool     ON_TOGGLES_TO_AUTO       = false; // ON while already forced open -> AUTO (for a single-code button)
constexpr uint32_t ON_TOGGLE_GUARD_MS       = 2000;  // a held/repeated ON within this window does not toggle back
constexpr bool     ALLOW_FORCED_CLOSED      = true;  // remote OFF forces the flap closed
constexpr uint32_t FORCED_CLOSED_TIMEOUT_MS = 15UL * 60UL * 1000UL;  // back to AUTO after 15 min
constexpr uint32_t RELAY_SETTLE_MS          = 20;

// ===================== Remote codes =====================
// The fob is an EV1527-style 24-bit transmitter: 20-bit address + 4-bit button (rc-switch protocol 1).
// Measured 12 Oct 2026: ON = 954817 (0xE91C1), OFF = 954818 (0xE91C2), AUTO = 954820 (0xE91C4).
// Any code whose upper 20 bits match RF_ADDRESS is accepted; the low nibble selects the button.
// To pair another fob: set RF_ADDRESS = 0, open the Serial Monitor, press a button, copy the address.
constexpr unsigned long RF_ADDRESS  = 0xE91C;   // upper 20 bits of the fob's codes (0 = accept any, log only)
constexpr uint8_t       RF_BTN_ON   = 0x1;
constexpr uint8_t       RF_BTN_OFF  = 0x2;
constexpr uint8_t       RF_BTN_AUTO = 0x4;
// Dashboard button (via the kit's cabin box). If it uses another address, put it here (0 = unused).
constexpr unsigned long RF_ADDRESS_BTN = 0;
constexpr uint8_t       RF_BTN_BTN_ON  = 0x1;
constexpr uint8_t       RF_BTN_BTN_OFF = 0x2;
constexpr uint32_t      RF_REPEAT_IGNORE_MS = 600;  // fobs repeat the code while held

// ===================== State =====================
enum class Mode { AUTO, FORCED_OPEN, FORCED_CLOSED };
Mode     mode      = Mode::AUTO;
uint32_t modeSince = 0;
RCSwitch rf;

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

  unsigned long addr = code >> 4;
  uint8_t btn = code & 0xF;
  Serial.printf("[rf] code=%lu bits=%u protocol=%u addr=0x%lX btn=0x%X\n", code, bits, proto, addr, btn);

  if (bits != 24) return;
  if (RF_ADDRESS != 0 && addr == RF_ADDRESS) {
    if (btn == RF_BTN_ON) {
      if (ON_TOGGLES_TO_AUTO && mode == Mode::FORCED_OPEN && now - modeSince > ON_TOGGLE_GUARD_MS)
        applyMode(Mode::AUTO);
      else
        applyMode(Mode::FORCED_OPEN);
    }
    else if (btn == RF_BTN_AUTO) applyMode(Mode::AUTO);
    else if (btn == RF_BTN_OFF)  applyMode(Mode::FORCED_CLOSED);
  } else if (RF_ADDRESS_BTN != 0 && addr == RF_ADDRESS_BTN) {
    if      (btn == RF_BTN_BTN_ON)  applyMode(Mode::FORCED_OPEN);
    else if (btn == RF_BTN_BTN_OFF) applyMode(BTN_OFF_MEANS_AUTO ? Mode::AUTO : Mode::FORCED_CLOSED);
  }
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

  WiFi.mode(WIFI_OFF);           // not used for now
  Serial.begin(115200);

  rf.enableReceive(digitalPinToInterrupt(PIN_RF_RX));

  Serial.println();
  Serial.println("G29 exhaust flap controller - started in AUTO (car in control)");
  if (RF_ADDRESS == 0) {
    Serial.println("RF_ADDRESS not set: press a fob button and copy the addr shown into RF_ADDRESS.");
  }
  Serial.printf("PWM %lu Hz, open %.0f%%, closed %.0f%% (verify these on the car!)\n",
                (unsigned long)PWM_FREQ_HZ, DUTY_OPEN_PCT, DUTY_CLOSED_PCT);
}

void loop() {
  handleRemote();
  handleTimeouts();
}
