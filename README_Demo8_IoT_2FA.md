# Demo 8 -- IoT 2-Factor Authentication (2FA)

## Objective

Demonstrate 2-Factor Authentication (2FA) in an IoT device.

Override requires: 1. Username & Password 2. 2-digit dynamic 2FA code

------------------------------------------------------------------------

## Step 1 -- Upload Code

1.  Open Arduino IDE
2.  Select NodeMCU 1.0 (ESP8266)
3.  Upload Demo8_IoT_2FA_Final.ino
4.  Open Serial Monitor
5.  Note IP address

------------------------------------------------------------------------

## Step 2 -- View Real Data

Open browser:

http://YOUR_IP

Real sensor data is displayed.

------------------------------------------------------------------------

## Step 3 -- Override Attempt

Open:

http://YOUR_IP/?t=80&h=10

You will see: 1. Username/Password popup Username: admin Password: 1234
2. 2FA input page

------------------------------------------------------------------------

## Step 4 -- Enter 2FA Code

Check Serial Monitor for:

New 2FA Code: XX

Enter that code in browser.

If correct: - Override succeeds - Page redirects automatically - New 2FA
code generated

------------------------------------------------------------------------

## CMD Test

curl -u admin:1234 "http://YOUR_IP/?t=80&h=10&code=XX"

Replace XX with current 2FA code.

------------------------------------------------------------------------

## Teaching Points

-   Two-factor authentication
-   Post-Redirect-Get pattern
-   Persistent override
-   Improved security over basic authentication

------------------------------------------------------------------------

Note: This still uses HTTP (not HTTPS). Credentials can be captured on
network.
