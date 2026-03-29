
/*
  NodeMCU (ESP8266) + DHT22 WiFi Monitor
  --------------------------------------
  What this program does:
  1. Connects NodeMCU to your WiFi network
  2. Reads Temperature and Humidity from DHT22 sensor (connected to D5)
  3. Creates a simple webpage
  4. Shows values in large Cyan (Temperature) and Pink (Humidity) text
  5. Automatically refreshes every 5 seconds
*/

#include <ESP8266WiFi.h>        // Library for WiFi connection
#include <ESP8266WebServer.h>   // Library to create web server
#include <DHT.h>                // Library to use DHT sensor

#define D5PIN D5               // Define D5 pin for DHT22 data

// Replace with your WiFi name and password
const char* ssid = "YOUR_WIFI";
const char* pass = "YOUR_PASSWORD";

DHT dht(D5PIN, DHT22);          // Create DHT object (Pin, Sensor type)
ESP8266WebServer server(80);    // Create web server on port 80

void setup() {
  Serial.begin(9600);           // Start serial communication (for IP display)
  dht.begin();                  // Start DHT sensor

  WiFi.begin(ssid, pass);       // Start connecting to WiFi
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);                 // Wait until WiFi connects
  }

  Serial.println("Connected to WiFi");
  Serial.print("Open this IP in browser: ");
  Serial.println(WiFi.localIP());   // Print IP address

  // When someone opens the IP address
  server.on("/", []() {

    float t = dht.readTemperature();   // Read temperature
    float h = dht.readHumidity();      // Read humidity

    // Create simple HTML page
    String page = "<html>";
    page += "<head>";
    page += "<meta http-equiv='refresh' content='5'>";  // Auto refresh every 5 sec
    page += "</head>";
    page += "<body bgcolor='black' text='white'>";
    page += "<center>";

    page += "<h1>Temperature</h1>";
    page += "<h1><font color='cyan'>" + String(t) + " C</font></h1>";

    page += "<h1>Humidity</h1>";
    page += "<h1><font color='pink'>" + String(h) + " %</font></h1>";

    page += "</center>";
    page += "</body>";
    page += "</html>";

    server.send(200, "text/html", page);  // Send webpage to browser
  });

  server.begin();   // Start the web server
}

void loop() {
  server.handleClient();   // Continuously handle browser requests
}
