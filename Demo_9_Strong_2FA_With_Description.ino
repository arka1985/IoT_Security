
/*
  Demo 9 – Strong 2FA IoT Security Demo
  --------------------------------------
  Board: NodeMCU (ESP8266)
  Sensor: DHT22

  FEATURES:
  1. Real sensor data displayed by default.
  2. Override requires:
       - Username & Password (Basic Authentication)
       - 6-digit OTP (2FA)
  3. OTP changes automatically every 15 seconds.
  4. After 3 wrong 2FA attempts → device permanently locks.
  5. Override persists until reboot.
  6. Clean HTML (no countdown display).

  HOW TO USE:
  Normal View:
      http://YOUR_IP

  Override Attempt:
      http://YOUR_IP/?t=80&h=10
      → Enter admin credentials
      → Enter 6-digit OTP from Serial Monitor
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define D5PIN D5
#define DHTTYPE DHT22

const char* ssid = "drarka.in";
const char* pass = "arkaprabha@1985";

const char* adminUser = "admin";
const char* adminPass = "1234";

DHT dht(D5PIN, DHTTYPE);
ESP8266WebServer server(80);

float overrideTemp = NAN;
float overrideHum  = NAN;

unsigned long lastCodeChange = 0;
const unsigned long codeInterval = 15000;  // 15 seconds
int twoFactorCode = 0;

int failedAttempts = 0;
bool permanentlyBlocked = false;

void generateNewCode() {
  twoFactorCode = random(0, 1000000);

  char buffer[7];
  sprintf(buffer, "%06d", twoFactorCode);

  Serial.print("New 6-digit 2FA Code: ");
  Serial.println(buffer);

  lastCodeChange = millis();
}

void setup() {

  Serial.begin(9600);
  randomSeed(micros());
  dht.begin();

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.print("Open this IP in browser: ");
  Serial.println(WiFi.localIP());

  generateNewCode();

  server.on("/", []() {

    if (permanentlyBlocked) {
      server.send(403, "text/plain",
                  "Device permanently locked due to multiple failed attempts.");
      return;
    }

    if (server.hasArg("t") || server.hasArg("h")) {

      if (!server.authenticate(adminUser, adminPass)) {
        return server.requestAuthentication();
      }

      if (!server.hasArg("code")) {

        String form = "<html><body bgcolor='black' text='white'><center>";
        form += "<h2>Enter 6-digit 2FA Code</h2>";
        form += "<form method='GET'>";
        form += "<input type='hidden' name='t' value='" + server.arg("t") + "'>";
        form += "<input type='hidden' name='h' value='" + server.arg("h") + "'>";
        form += "<input name='code' type='text'>";
        form += "<br><br><input type='submit' value='Submit'>";
        form += "</form>";
        form += "</center></body></html>";

        server.send(200, "text/html", form);
        return;
      }

      if (server.arg("code").toInt() != twoFactorCode) {

        failedAttempts++;
        Serial.print("Wrong attempt count: ");
        Serial.println(failedAttempts);

        if (failedAttempts >= 3) {
          permanentlyBlocked = true;
          Serial.println("DEVICE PERMANENTLY LOCKED!");
        }

        server.send(403, "text/plain", "Invalid 2FA Code!");
        return;
      }

      failedAttempts = 0;

      if (server.hasArg("t")) overrideTemp = server.arg("t").toFloat();
      if (server.hasArg("h")) overrideHum  = server.arg("h").toFloat();

      Serial.println("Override successful!");

      generateNewCode();

      server.sendHeader("Location", "/");
      server.send(303);
      return;
    }

    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (!isnan(overrideTemp)) t = overrideTemp;
    if (!isnan(overrideHum))  h = overrideHum;

    String page = "<html>";
    page += "<head><meta http-equiv='refresh' content='5'></head>";
    page += "<body bgcolor='black' text='white'><center>";

    page += "<h1>Temperature</h1>";
    page += "<h1><font color='cyan'>" + String(t) + " C</font></h1>";

    page += "<h1>Humidity</h1>";
    page += "<h1><font color='pink'>" + String(h) + " %</font></h1>";

    page += "</center></body></html>";

    server.send(200, "text/html", page);
  });

  server.begin();
}

void loop() {

  server.handleClient();

  if (!permanentlyBlocked && millis() - lastCodeChange >= codeInterval) {
    generateNewCode();
  }
}
