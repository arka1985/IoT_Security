# Raspberry Pi Pico WH - Cybersecurity Masterclass

Welcome to the **Ultimate IoT Security Demo**. This project takes you on a journey from a completely vulnerable device to a military-grade secure system, demonstrating every step of the attack and defense lifecycle.

## 📦 Required Hardware
1.  **Raspberry Pi Pico WH** (with Headers)
2.  **SSD1306 OLED Display** (I2C)
3.  **DHT22 Sensor** (Temperature & Humidity)
4.  **Micro USB Cable** (Data capable)

## 🔌 Wiring Guide (No Breadboard Needed!)

| Component | Pin Name | Pico Pin | Physical Pin |
| :--- | :--- | :--- | :--- |
| **OLED** | SDA | GP0 | Pin 1 |
| **OLED** | SCL | GP1 | Pin 2 |
| **OLED** | VCC | 3V3(OUT) | Pin 36 |
| **OLED** | GND | GND | Pin 38 |
| **DHT22** | DATA | GP15 | Pin 20 |
| **DHT22** | **VCC** | **GP14** | **Pin 19** (Power Source) |
| **DHT22** | GND | GND | Pin 18 |

> **Note**: We power the DHT22 using **GP14** (Pin 19) as a "Software Power Pin" so you can plug the sensor directly into Pins 18, 19, and 20.

---

## 🚀 Setup Instructions

1.  **Install Firmware**: Hold `BOOTSEL` button -> Plug in USB -> Copy MicroPython `.uf2` file to `RPI-RP2` drive.
2.  **WiFi Setup**: Open `secrets.py` and enter your WiFi Credentials:
    ```python
    SSID = "Your_WiFi_Name"
    PASSWORD = "Your_WiFi_Password"
    WEB_USER = "admin"
    WEB_PASS = "12"  # Keep this weak for the demo!
    ```
3.  **Upload Files**: Use Thonny IDE to upload **ALL** `.py` files to the Pico **EXCEPT** the ones labeled "(PC)".

---

## 🎓 The Cybersecurity Journey (10 Steps)

### Phase 1: The Vulnerable IoT Device

#### 1. Offline Mode (The Baseline)
*   **File**: `01_offline_mode.py`
*   **Concept**: A dumb device. It only shows data on its own screen.
*   **Action**: Run verify OLED shows Temp/Humidity. Safe but useless remotely.

#### 2. The Read-Only Wall (Secure but Useless)
*   **File**: `02_read_only.py`
*   **Concept**: We add WiFi but no control. You can see data on a webpage, but can't change anything.
*   **Action**: Visit the IP Address. Try to click things. Nothing happens. Secure, but boring.

#### 3. The Unsecured Door (Vulnerable!)
*   **File**: `03_unsecured_web.py`
*   **Concept**: We add a feature to "Set Message" remotely, but forget to add a password.
*   **Vulnerability**: Anyone on the WiFi can control the device.
*   **Action (Two Ways to Hack)**:

*   **Action (Two Ways to Hack)**:

    **Method A: Using Web Browser (The "Manual" Hack)**
    1.  **Change Message**:
        `http://10.187.47.36/set_msg?msg=HACKED`
    2.  **Spoof Temperature (999C)**:
        `http://10.187.47.36/set_env?t=999&h=0`
    3.  **Reset System**:
        `http://10.187.47.36/reset`

    **Method B: Using Python Script (The "Hacker Tool")**
    1.  Open **Command Prompt (cmd)** on your PC.
    2.  Navigate to your project folder:
        `cd C:\Users\arka\RASPBERRY_WH_SECURITY`
    3.  Run the exploit tool:
        `python 03a_exploit_tool.py 10.187.47.36 "HACKED"`
    4.  **Result**: The OLED immediately changes. You have hacked the device.

---

### Phase 2: Authentication & Attacks

#### 4. Secure Basic Auth (The Benchmark)
*   **File**: `04_secure_basic_auth.py`
*   **Concept**: We add "Basic Authentication" (Username/Password).
*   **Action**: Run it. Try to visit the webpage. You MUST enter `admin` / `12` to see data. Attack scripts fail.

#### 5. The Insider Threat (Weak Password)
*   **File**: `05_weak_login.py` (Run on Pico)
*   **Concept**: We have a login, but the password is weak ("12") and the internal code is buggy.
*   **The Hack (Brute Force)**:
    1.  Run `05_weak_login.py` on Pico.
    2.  Open **Command Prompt (cmd)** on PC.
        *   Navigate: `cd C:\Users\arka\RASPBERRY_WH_SECURITY`
    3.  Run the Brute Force Tool:
        `python 05a_bruteforce_tool.py 10.187.47.36 admin`
    4.  **Watch**: The script guesses `00`, `01`... `12`. **CRACKED!**
    5.  **Control Menu (Type 1, 2, or 3)**:
        *   `1`: Spoof Temp/Humidity.
        *   `2`: Reset System.
        *   `3`: Send text message (e.g. "HACKED").

---

### Phase 3: Advanced Defenses

#### 6. Defense: Lockout (3 Strikes)
*   **File**: `06_defense_lockout.py`
*   **Concept**: Block the IP after 3 failed attempts.
*   **Demo**:
    1.  Run `06` on Pico.
    2.  Run the Brute Force Tool (`05a`).
    3.  **Result**: `00` (Fail), `01` (Fail), `02` (Fail). **BLOCKED!** (HTTP 403).

#### 7. Defense: Slow Hashing (Time Cost)
*   **File**: `07_defense_slow_hash.py`
*   **Concept**: Force the Pico to run 5000 rounds of hashing for every login.
*   **Demo**:
    1.  Run `07` on Pico.
    2.  Run the Brute Force Tool (`05a`).
    3.  **Result**: It becomes **incredibly slow** (1 guess per second). Brute force becomes impossible.

#### 8. Defense: Visual Verification (Secure Storage)
*   **File**: `08_visual_hashing.py`
*   **Concept**: Prove that we store Hashes, not Passwords.
*   **The "Visual Hack" Demo**:
    1.  Run `08` on Pico.
    2.  Run the Brute Force Tool (`05a`).
    3.  **Watch OLED**: You see the input password vs the HASH.
    4.  **Result**: You see `Match` only when the Hashes match. You never see the stored password.

---

### Phase 4: Modern Security (2FA)

#### 9. 2FA: Physical Token (OLED)
*   **File**: `09_2fa_oled.py`
*   **Concept**: Password + a Random PIN shown on the device screen.
*   **Security**: Hacker needs your Password **AND** physical access to the room.

#### 10. 2FA: App Authenticator (TOTP)
*   **File**: `10_2fa_app.py`
*   **Concept**: Google/Microsoft Authenticator.
*   **Security**: Banking-grade security. The code changes every 30 seconds.

---

## 🛠️ Troubleshooting
*   **Web Page Won't Load**: Stop script, wait 5s, Run again. (Sockets take time to close).
*   **Brute Force Fails**: Increase `timeout` in `05a_bruteforce_tool.py` if network is slow.
*   **OLED Blank**: Check wiring. Ensure `ssd1306.py` is on the Pico.
