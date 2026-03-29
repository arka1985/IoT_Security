# IoT Insecurity Demo (ESP8266 + DHT22)

## Objective

Demonstrate how an insecure IoT device can have its sensor values
overridden by anyone on the same WiFi network using a browser or command
line.

------------------------------------------------------------------------

## Hardware Required

-   NodeMCU (ESP8266)
-   DHT22 Sensor
-   Jumper wires
-   WiFi Network

------------------------------------------------------------------------

## Connections

DHT22: - VCC → 3.3V - GND → GND - DATA → D5

------------------------------------------------------------------------

## How It Works

1.  By default, the device reads real temperature and humidity from
    DHT22.
2.  The values are shown on a webpage.
3.  If someone sends values using URL parameters (`?t=` and `?h=`), the
    device stores them and overrides real sensor data.
4.  The overridden values remain until the device is rebooted.

------------------------------------------------------------------------

## Step-by-Step Demo Procedure

### 1. Upload the Code

-   Open Arduino IDE
-   Select correct board (NodeMCU 1.0 ESP8266)
-   Upload the provided sketch
-   Open Serial Monitor
-   Note the IP address shown

Example: http://10.39.28.3

------------------------------------------------------------------------

### 2. Show Real Data

Open browser and type:

http://YOUR_IP

Participants will see real temperature and humidity values.

------------------------------------------------------------------------

### 3. Demonstrate Override (Browser)

In browser address bar type:

http://YOUR_IP/?t=100&h=5

Now refresh normal page:

http://YOUR_IP

Values will remain overridden.

------------------------------------------------------------------------

### 4. Demonstrate Override (CMD -- Windows)

Open Command Prompt and type:

curl "http://YOUR_IP/?t=80&h=10"

Refresh browser page --- values will now show 80 and 10.

------------------------------------------------------------------------

## What This Demonstrates

-   No authentication
-   No encryption
-   Anyone on same WiFi can change sensor values
-   Persistent manipulation until reboot

------------------------------------------------------------------------

## Resetting to Real Data

Reboot the NodeMCU.

------------------------------------------------------------------------

## Security Lesson

This demo shows why: - Input validation is important - Authentication is
necessary - IoT devices must not trust URL parameters blindly

------------------------------------------------------------------------

Author: IoT Security Teaching Demo
