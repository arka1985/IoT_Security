
/*
  NodeMCU (ESP8266) + DHT22
  Encryption-Only WiFi Monitor
  --------------------------------
  What this program does:
  1. Connects NodeMCU to WiFi
  2. Reads Temperature & Humidity from DHT22 (D5)
  3. Encrypts values using XOR with a secret key
  4. Sends encrypted values to browser
  5. Browser decrypts and displays real values
  6. Auto refresh every 5 seconds

  NOTE:
  This is educational encryption only (not HTTPS).
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

#define D5PIN D5

// Replace with your WiFi credentials
const char* ssid = "YOUR_WIFI";
const char* pass = "YOUR_PASSWORD";

DHT dht(D5PIN, DHT22);
ESP8266WebServer server(80);

int secretKey = 123;   // Encryption key (change if needed)

void setup() {
  Serial.begin(9600);
  dht.begin();

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  Serial.print("Open this IP in browser: ");
  Serial.println(WiFi.localIP());

  server.on("/", []() {

    float t = dht.readTemperature();   // Read temperature
    float h = dht.readHumidity();      // Read humidity

    // Encrypt values (multiply by 10 to preserve decimal)
    int encT = ((int)(t * 10)) ^ secretKey;
    int encH = ((int)(h * 10)) ^ secretKey;

    String page = "<html><head>";
    page += "<meta http-equiv='refresh' content='5'>";
    page += "</head><body bgcolor='black' text='white'><center>";

    page += "<h1>Encrypted Sensor Monitor</h1>";

    // JavaScript decrypts values in browser
    page += "<script>";
    page += "var key=" + String(secretKey) + ";";
    page += "var t=(" + String(encT) + "^key)/10;";
    page += "var h=(" + String(encH) + "^key)/10;";
    page += "document.write('<h1 style=\\"color:cyan\\">'+t+' C</h1>');";
    page += "document.write('<h1 style=\\"color:pink\\">'+h+' %</h1>');";
    page += "</script>";

    page += "</center></body></html>";

    server.send(200, "text/html", page);
  });

  server.begin();
}

void loop() {
  server.handleClient();
}
