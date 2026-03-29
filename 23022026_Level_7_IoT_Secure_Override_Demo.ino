
/*
  IoT Security Demo – Password Protected Override
  ------------------------------------------------
  Board: NodeMCU (ESP8266)
  Sensor: DHT22

  PURPOSE:
  1. Show real temperature & humidity by default.
  2. Allow override using URL parameters (?t= & ?h=).
  3. Require username & password before allowing override.
  4. Fake values remain until reboot.

  HOW TO TEST:

  Normal:
    http://YOUR_IP

  Override (Browser):
    http://YOUR_IP/?t=100&h=5
    → Browser will ask Username & Password

  Override (CMD):
    curl -u admin:1234 "http://YOUR_IP/?t=80&h=10"

  NOTE:
  This uses Basic Authentication over HTTP.
  Password is NOT encrypted (educational demo only).
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define D5PIN D5
#define DHTTYPE DHT22

// ---------------- WIFI CONFIG ----------------
const char* ssid = "drarka.in";            // Your WiFi Name
const char* pass = "arkaprabha@1985";      // Your WiFi Password

// ---------------- ADMIN LOGIN ----------------
const char* adminUser = "admin";           // Username for override
const char* adminPass = "1234";            // Password for override

// ---------------- OBJECTS ----------------
DHT dht(D5PIN, DHTTYPE);
ESP8266WebServer server(80);

// ---------------- OVERRIDE STORAGE ----------------
float overrideTemp = NAN;
float overrideHum  = NAN;

void setup() {

  Serial.begin(9600);       // Start Serial Monitor
  dht.begin();              // Start DHT sensor

  WiFi.begin(ssid, pass);   // Connect to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.println("Connected!");
  Serial.print("Open this IP in browser: ");
  Serial.println(WiFi.localIP());

  // ---------------- WEB SERVER ----------------
  server.on("/", []() {

    // If user tries to override values
    if (server.hasArg("t") || server.hasArg("h")) {

      // Ask for authentication
      if (!server.authenticate(adminUser, adminPass)) {
        return server.requestAuthentication();
      }

      // If login successful → store override
      if (server.hasArg("t")) overrideTemp = server.arg("t").toFloat();
      if (server.hasArg("h")) overrideHum  = server.arg("h").toFloat();

      Serial.println("Override authorized!");
    }

    // Read real sensor values
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    // Replace with override if exists
    if (!isnan(overrideTemp)) t = overrideTemp;
    if (!isnan(overrideHum))  h = overrideHum;

    // -------- HTML PAGE --------
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

  server.begin();  // Start server
}

void loop() {
  server.handleClient();  // Keep server running
}
