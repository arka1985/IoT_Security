
/*
  IoT Insecurity Demo
  -------------------
  Board: NodeMCU (ESP8266)
  Sensor: DHT22
  
  PURPOSE:
  1. Show real temperature and humidity by default.
  2. Allow anyone on same WiFi to override values using URL.
  3. Fake values remain until device is rebooted.
  
  HOW TO HACK:
  Browser:
    http://YOUR_IP/?t=100&h=5
  
  CMD (Windows):
    curl "http://YOUR_IP/?t=80&h=10"
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define D5PIN D5
#define DHTTYPE DHT22

// ---------------- WIFI DETAILS ----------------
const char* ssid = "drarka.in";            // Your WiFi Name
const char* pass = "arkaprabha@1985";      // Your WiFi Password

// ---------------- OBJECTS ----------------
DHT dht(D5PIN, DHTTYPE);
ESP8266WebServer server(80);

// ---------------- OVERRIDE STORAGE ----------------
// If these stay NAN → real sensor data is shown
// If changed → fake values will be shown
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

  // ------------- WEB SERVER HANDLER -------------
  server.on("/", []() {

    // If URL contains ?t= or ?h= → store override permanently
    if (server.hasArg("t")) overrideTemp = server.arg("t").toFloat();
    if (server.hasArg("h")) overrideHum  = server.arg("h").toFloat();

    // Read real sensor values
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    // If override exists → replace real data
    if (!isnan(overrideTemp)) t = overrideTemp;
    if (!isnan(overrideHum))  h = overrideHum;

    // -------- HTML PAGE (Same Structure As Your Original) --------
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
