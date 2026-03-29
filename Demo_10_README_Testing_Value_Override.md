# Secure IoT Demo -- Testing Value Override

This guide explains how to attempt changing temperature and humidity
values using a **browser** and **Command Prompt (CMD)**.

System Security: - Admin username: `admin` - Admin password: `1234` -
Google Authenticator TOTP required - 3 wrong attempts → "Unauthorized
access"

------------------------------------------------------------------------

## 1️⃣ Step 1 -- Login First

1.  Open browser

2.  Go to:

    http://YOUR_DEVICE_IP/

3.  Enter:

    -   Username: `admin`
    -   Password: `1234`

4.  Scan QR or manually add secret to Google Authenticator

5.  Enter the 6-digit OTP

6.  After success → Live sensor page opens

------------------------------------------------------------------------

## 2️⃣ Attempt to Change Value WITHOUT Credentials (Should Fail)

### Browser Test

Try:

http://YOUR_DEVICE_IP/set?t=90&h=50

Expected Result: - Password and OTP required - OR Unauthorized access

------------------------------------------------------------------------

### CMD Test

Open Command Prompt and run:

curl "http://YOUR_DEVICE_IP/set?t=90&h=50"

Expected Result: - Password and OTP required - OR Unauthorized access

------------------------------------------------------------------------

## 3️⃣ Correct Way to Update Values

You MUST provide:

-   Password
-   Fresh 6-digit OTP
-   New temperature (t)
-   New humidity (h)

### Browser Method

http://YOUR_DEVICE_IP/set?pass=1234&otp=123456&t=90&h=50

Replace `123456` with current Google Authenticator code.

------------------------------------------------------------------------

### CMD Method

curl "http://YOUR_DEVICE_IP/set?pass=1234&otp=123456&t=90&h=50"

------------------------------------------------------------------------

## 4️⃣ What Happens After 3 Wrong Attempts?

If wrong password or OTP is entered 3 times:

System response:

    Unauthorized access

Further updates will be blocked until device restart.

------------------------------------------------------------------------

## 5️⃣ Important Notes

-   OTP changes every 30 seconds
-   If OTP expired → request fails
-   Live page auto-refreshes every 5 seconds
-   Without correct credentials, override will NOT work

------------------------------------------------------------------------

## Demo Tip

For demonstration: 1. First show failed attempt 2. Then show correct
authenticated update 3. Explain OTP time window 4. Explain brute-force
protection (3 attempt limit)

------------------------------------------------------------------------

End of Guide
