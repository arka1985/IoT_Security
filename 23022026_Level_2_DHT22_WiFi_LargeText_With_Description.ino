
/*
  NodeMCU (ESP8266) + DHT22 Web Server
  ------------------------------------
  - Connects to WiFi
  - Reads Temperature & Humidity from DHT22 (connected to D5)
  - Displays large values in browser (PC & Mobile on same WiFi)
*/

#include <ESP8266WiFi.h>        // Library to connect ESP8266 to WiFi
#include <ESP8266WebServer.h>   // Library to create web server
#include <DHT.h>                // Library for DHT sensor

#define D5PIN D5                // Define D5 pin for DHT22 data

// Replace with your WiFi details
const char* ssid = "YOUR_WIFI_NAME";
const char* pass = "YOUR_WIFI_PASSWORD";

DHT dht(D5PIN, DHT22);          // Create DHT object (pin, sensor type)
ESP8266WebServer server(80);    // Create web server on port 80

void setup() {
  Serial.begin(9600);           // Start serial communication
  dht.begin();                  // Start DHT sensor
  delay(2000);                  // Wait 2 seconds for sensor stability

  WiFi.begin(ssid, pass);       // Start WiFi connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);                 // Wait until connected
  }

  Serial.println("Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());   // Print IP address (open in browser)

  // When someone opens the IP address
  server.on("/", []() {
    server.send(200, "text/html",
      "<html><body style='font-size:50px; text-align:center;'>"
      + String(dht.readTemperature()) + " C<br>"
      + String(dht.readHumidity()) + " %"
      + "</body></html>");
  });

  server.begin();               // Start the web server
}

void loop() {
  server.handleClient();        // Handle incoming browser requests
}
