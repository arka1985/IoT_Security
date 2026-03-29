
/*
  Demo 8 – IoT 2-Factor Authentication (2FA) with Redirect Fix
  --------------------------------------------------------------
  Board: NodeMCU (ESP8266)
  Sensor: DHT22

  FEATURES:
  1. Real sensor data shown by default.
  2. Override requires:
     - Username & Password (Basic Auth)
     - 2FA Code (2-digit random number)
  3. After successful override, page redirects to prevent refresh errors.
  4. Fake values persist until reboot.
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

int twoFactorCode = 0;

void generateNewCode() {
  twoFactorCode = random(10, 100);
  Serial.print("New 2FA Code: ");
  Serial.println(twoFactorCode);
}

void setup() {

  Serial.begin(9600);
  randomSeed(micros());
  dht.begin();

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  Serial.print("Open this IP: ");
  Serial.println(WiFi.localIP());

  generateNewCode();

  server.on("/", []() {

    if (server.hasArg("t") || server.hasArg("h")) {

      if (!server.authenticate(adminUser, adminPass)) {
        return server.requestAuthentication();
      }

      if (!server.hasArg("code")) {

        String form = "<html><body bgcolor='black' text='white'><center>";
        form += "<h2>Enter 2FA Code</h2>";
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
        server.send(403, "text/plain", "Invalid 2FA Code!");
        return;
      }

      if (server.hasArg("t")) overrideTemp = server.arg("t").toFloat();
      if (server.hasArg("h")) overrideHum  = server.arg("h").toFloat();

      Serial.println("Override successful with 2FA!");

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
}
