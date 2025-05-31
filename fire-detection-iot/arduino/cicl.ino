const int mq2Pin = A0;
const int mq7Pin = A1;
const int flamePin = A2;

bool fireDetected = false;

void setup() {
  Serial.begin(9600);      // Send to Python
  Serial1.begin(9600);     // Send to ESP32 via TX1 (Pin 18)
}

void loop() {
  if (fireDetected) return;  // ⛔ Stop after fire

  int mq2Value = analogRead(mq2Pin);
  int mq7Value = analogRead(mq7Pin);
  int flameValue = analogRead(flamePin);

  // 🔁 Send to Python
  Serial.print(mq2Value);
  Serial.print(", ");
  Serial.print(mq7Value);
  Serial.print(", ");
  Serial.println(flameValue);

  // ⏳ Wait for Python verdict
  String verdict = "";
  unsigned long start = millis();
  while (millis() - start < 1500) {
    if (Serial.available()) {
      verdict = Serial.readStringUntil('\n');
      verdict.trim();
      break;
    }
  }

  // 📤 Forward verdict + values to ESP32
  Serial1.print(verdict);
  Serial1.print(",");
  Serial1.print(mq2Value);
  Serial1.print(",");
  Serial1.print(mq7Value);
  Serial1.print(",");
  Serial1.println(flameValue);

  // 🔒 Stop loop if fire
  if (verdict == "FIRE") {
    fireDetected = true;
  }

  delay(500);
}