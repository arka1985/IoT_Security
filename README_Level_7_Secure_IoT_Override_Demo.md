# IoT Secure Override Demo (Password Protected)

## Objective

Demonstrate how an IoT device: 1. Shows real DHT22 sensor data by
default. 2. Allows override only after authentication. 3. Protects
override using Basic Authentication.

------------------------------------------------------------------------

## Hardware Required

-   NodeMCU (ESP8266)
-   DHT22 Sensor
-   WiFi Network

Connections: - DHT22 VCC → 3.3V - DHT22 GND → GND - DHT22 DATA → D5

------------------------------------------------------------------------

## Step 1: Upload the Code

1.  Open Arduino IDE.
2.  Select Board: NodeMCU 1.0 (ESP8266).
3.  Upload the provided secure demo code.
4.  Open Serial Monitor.
5.  Note the IP address shown.

Example: http://10.39.28.3

------------------------------------------------------------------------

## Step 2: View Real Data (Normal Mode)

Open browser and type:

http://YOUR_IP

You will see: - Real Temperature (Cyan) - Real Humidity (Pink)

No password required for viewing.

------------------------------------------------------------------------

## Step 3: Override Using Browser (Protected)

In browser address bar type:

http://YOUR_IP/?t=100&h=5

A login popup will appear.

Username: admin Password: 12345

If correct: - Values change to 100 C and 5 % - Fake values remain until
reboot

If wrong: - Access denied

------------------------------------------------------------------------

## Step 4: Override Using CMD (Windows)

Open Command Prompt and type:

curl -u admin:12345 "http://YOUR_IP/?t=80&h=10"

Then open browser:

http://YOUR_IP

You will see overridden values (80 C, 10 %).

------------------------------------------------------------------------

## What This Demonstrates

-   Authentication protection
-   Persistent override
-   Basic Auth over HTTP
-   Importance of securing IoT endpoints

------------------------------------------------------------------------

## Important Security Note

This uses Basic Authentication over HTTP. The password is Base64
encoded, NOT encrypted. It can still be captured using Wireshark.

For real security, HTTPS (TLS) is required.

------------------------------------------------------------------------

Demo Type: Secure IoT Teaching Demonstration
