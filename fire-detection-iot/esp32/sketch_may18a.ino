#include <WiFi.h>
#include <HTTPClient.h>

#define RXD2 16  // Serial2 RX from Mega
#define TXD2 17  // Not used

const char* ssid = "Myhotspot";
const char* password = "12345678";

const String FIREBASE_HOST = "https://use-this-one-70e96-default-rtdb.asia-southeast1.firebasedatabase.app";
const String FIREBASE_AUTH = "YOUR_FIREBASE_AUTH"
bool stopUploads = false;

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n✅ WiFi connected");
}

void loop() {
  if (stopUploads) return;

  if (Serial2.available()) {
    String msg = Serial2.readStringUntil('\n');
    msg.trim();
    Serial.println("📩 From Mega: " + msg);

    int sep1 = msg.indexOf(',');
    int sep2 = msg.indexOf(',', sep1 + 1);
    int sep3 = msg.indexOf(',', sep2 + 1);

    if (sep1 == -1 || sep2 == -1 || sep3 == -1) {
      Serial.println("❌ Invalid data format");
      return;
    }

    String verdict = msg.substring(0, sep1);
    String mq2 = msg.substring(sep1 + 1, sep2);
    String mq7 = msg.substring(sep2 + 1, sep3);
    String flame = msg.substring(sep3 + 1);

    String json = "{";
    json += "\"verdict\":\"" + verdict + "\",";
    json += "\"mq2\":" + mq2 + ",";
    json += "\"mq7\":" + mq7 + ",";
    json += "\"flame\":" + flame + ",";
    json += "\"timestamp\":" + String(millis());
    json += "}";

    String url = FIREBASE_HOST + "/sensor_data.json?auth=" + FIREBASE_AUTH;

    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(json);

    if (code == 200) {
      Serial.println("✅ Uploaded to Firebase:");
      Serial.println(json);
    } else {
      Serial.print("❌ Upload failed: ");
      Serial.println(http.errorToString(code));
    }

    http.end();
    delay(1000);

    if (verdict == "FIRE") {
      stopUploads = true;
      Serial.println("🛑 Uploads stopped due to FIRE verdict");
    }
  }
}
