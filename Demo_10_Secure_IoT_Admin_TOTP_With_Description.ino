
/*
  ===============================================================
  Secure IoT System – Admin + Password + TOTP (QR + Manual)
  ===============================================================

  FEATURES:
  ✓ Admin login (username: admin, password: 1234)
  ✓ Google Authenticator TOTP (6-digit, 30-second)
  ✓ QR code generation using api.qrserver.com
  ✓ Manual secret setup option
  ✓ Auto-refresh live sensor display (every 5 sec)
  ✓ Secure /set route (requires password + fresh OTP)
  ✓ 3 wrong update attempts → "Unauthorized access"
  ✓ Cyan temperature, Pink humidity display

  REQUIRED LIBRARIES:
  - Base32-Decode
  - NTPClient
  (BearSSL is included in ESP8266 core)

  HARDWARE:
  - NodeMCU (ESP8266)
  - DHT22 connected to D5
*/

#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <Base32-Decode.h>
#include <BearSSLHelpers.h>

const char* ssid = "drarka.in";
const char* password = "arkaprabha@1985";

const String ADMIN_USER = "admin";
const String ADMIN_PASS = "1234";

const String SECRET_KEY = "JBSWY3DPEHPK3PXPJBSWY3DPEHPK3PXP";

#define DHTPIN D5
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

ESP8266WebServer server(80);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

uint8_t decodedKey[32];
int decodedKeyLen = 0;

bool loggedIn = false;
int failedAttempts = 0;
bool blocked = false;

float overrideTemp = NAN;
float overrideHum  = NAN;

String getTOTP(unsigned long epochSeconds) {

  uint64_t counter = epochSeconds / 30;

  uint8_t msg[8];
  for (int i = 7; i >= 0; i--) {
    msg[i] = counter & 0xFF;
    counter >>= 8;
  }

  uint8_t hash[20];
  br_hmac_key_context kc;
  br_hmac_context ctx;

  br_hmac_key_init(&kc, &br_sha1_vtable, decodedKey, decodedKeyLen);
  br_hmac_init(&ctx, &kc, 0);
  br_hmac_update(&ctx, msg, sizeof(msg));
  br_hmac_out(&ctx, hash);

  int offset = hash[19] & 0x0F;

  uint32_t binary =
    ((hash[offset] & 0x7F) << 24) |
    ((hash[offset+1] & 0xFF) << 16) |
    ((hash[offset+2] & 0xFF) << 8) |
    (hash[offset+3] & 0xFF);

  uint32_t otp = binary % 1000000;

  char buf[7];
  snprintf(buf, sizeof(buf), "%06u", otp);

  return String(buf);
}

void handleRoot() {

  if (!loggedIn) {

    if (!server.hasArg("user")) {
      server.send(200, "text/html",
        "<h3>Admin Login</h3>"
        "<form method='GET'>"
        "Username:<br><input name='user'><br>"
        "Password:<br><input name='pass' type='password'><br><br>"
        "<input type='submit' value='Login'>"
        "</form>");
      return;
    }

    if (server.arg("user") != ADMIN_USER ||
        server.arg("pass") != ADMIN_PASS) {
      server.send(401, "text/plain", "Invalid credentials");
      return;
    }

    if (!server.hasArg("otp")) {

      String otpURL =
        "otpauth://totp/IoT-Secure?secret=" +
        SECRET_KEY +
        "&issuer=IoT-Secure";

      String qrURL =
        "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" +
        otpURL;

      String html =
        "<h3>Google Authenticator Setup</h3>"
        "<img src='" + qrURL + "' width='250'><br><br>"
        "<p><b>Manual Setup Key:</b> " + SECRET_KEY + "</p>"
        "<hr>"
        "<form method='GET'>"
        "<input type='hidden' name='user' value='admin'>"
        "<input type='hidden' name='pass' value='1234'>"
        "Enter 6-digit OTP:<br><input name='otp'><br><br>"
        "<input type='submit' value='Verify'>"
        "</form>";

      server.send(200, "text/html", html);
      return;
    }

    timeClient.update();

    if (server.arg("otp") == getTOTP(timeClient.getEpochTime())) {
      loggedIn = true;
    } else {
      server.send(401, "text/plain", "Invalid OTP");
      return;
    }
  }

  float t = isnan(overrideTemp) ? dht.readTemperature() : overrideTemp;
  float h = isnan(overrideHum)  ? dht.readHumidity()    : overrideHum;

  String html =
    "<meta http-equiv='refresh' content='5'>"
    "<body style='background:black;color:white;text-align:center;'>"
    "<h2>Secure Live Sensor Data</h2>"
    "<h3>Temperature</h3>"
    "<h1 style='color:cyan;'>" + String(t,1) + " C</h1>"
    "<h3>Humidity</h3>"
    "<h1 style='color:pink;'>" + String(h,1) + " %</h1>"
    "</body>";

  server.send(200, "text/html", html);
}

void handleSet() {

  if (blocked) {
    server.send(403, "text/plain", "Unauthorized access");
    return;
  }

  if (!server.hasArg("pass") || !server.hasArg("otp")) {
    server.send(400, "text/plain", "Password and OTP required");
    return;
  }

  timeClient.update();

  if (server.arg("pass") != ADMIN_PASS ||
      server.arg("otp") != getTOTP(timeClient.getEpochTime())) {

    failedAttempts++;

    if (failedAttempts >= 3) {
      blocked = true;
      server.send(403, "text/plain", "Unauthorized access");
      return;
    }

    server.send(401, "text/plain", "Invalid credentials");
    return;
  }

  failedAttempts = 0;

  if (server.hasArg("t")) overrideTemp = server.arg("t").toFloat();
  if (server.hasArg("h")) overrideHum  = server.arg("h").toFloat();

  server.send(200, "text/plain", "Values updated successfully");
}

void setup() {

  Serial.begin(115200);
  dht.begin();

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(300);

  Serial.println("Connected!");
  Serial.println(WiFi.localIP());

  timeClient.begin();
  while (!timeClient.update()) timeClient.forceUpdate();

  decodedKeyLen = base32decode(
    SECRET_KEY.c_str(),
    decodedKey,
    sizeof(decodedKey)
  );

  server.on("/", handleRoot);
  server.on("/set", handleSet);
  server.begin();
}

void loop() {
  server.handleClient();
  timeClient.update();
}
