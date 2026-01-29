// Arduino LED Control for Radiology System

const int PIN_GREEN = 8;
const int PIN_YELLOW = 9;
const int PIN_RED = 10;

String command = "";

void setup() {
  Serial.begin(9600);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_YELLOW, OUTPUT);
  pinMode(PIN_RED, OUTPUT);

  // Initial state: All OFF
  digitalWrite(PIN_GREEN, LOW);
  digitalWrite(PIN_YELLOW, LOW);
  digitalWrite(PIN_RED, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim(); // Remove any whitespace/newlines

    if (command == "START_SCAN" || command == "INITIALIZE_SYSTEM") {
      setLedState(true, false, false); // Green
    } else if (command == "SCAN_COMPLETED") {
      setLedState(false, true, false); // Yellow
    } else if (command == "STOP_SCAN") {
      setLedState(false, true, false); // Yellow (Treat Stop as Complete/Pause)
    } else if (command == "EMERGENCY_STOP" || command == "EMERGENCY") {
      setLedState(false, false, true); // Red
    } else if (command == "RESET") {
      setLedState(false, false, false); // All OFF
    }
  }
}

void setLedState(bool green, bool yellow, bool red) {
  digitalWrite(PIN_GREEN, green ? HIGH : LOW);
  digitalWrite(PIN_YELLOW, yellow ? HIGH : LOW);
  digitalWrite(PIN_RED, red ? HIGH : LOW);
}
