import network
import socket
import time
import machine
import dht
import ubinascii
import secrets

# -------------------------
# Sensor Setup
# -------------------------
sensor = dht.DHT22(machine.Pin(15))

# -------------------------
# WiFi Connection
# -------------------------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print("Connected! IP:", ip)

# -------------------------
# Authentication Setup
# -------------------------
auth = ubinascii.b2a_base64(
    f"{secrets.WEB_USER}:{secrets.WEB_PASS}".encode()
).strip().decode()

expected = f"Basic {auth}"

# -------------------------
# Socket Setup
# -------------------------
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
s.settimeout(1.0)   # Prevents freezing

# -------------------------
# Variables
# -------------------------
t, h = "0.0", "0.0"
spoof_active = False

print("Server running...")

# -------------------------
# Main Loop
# -------------------------
try:
    while True:

        # Update real sensor data
        if not spoof_active:
            try:
                sensor.measure()
                t = "{:.1f}".format(sensor.temperature())
                h = "{:.1f}".format(sensor.humidity())
            except:
                pass

        conn = None

        try:
            conn, addr = s.accept()
            conn.settimeout(1.0)

            raw_req = conn.recv(1024)
            if not raw_req:
                conn.close()
                continue

            req = raw_req.decode()

            # -------------------------
            # AUTH CHECK
            # -------------------------
            if expected in req:

                # Spoof Sensor
                if '/set_env?' in req:
                    try:
                        query = req.split('?')[1].split(' ')[0]
                        parts = query.split('&')
                        for p in parts:
                            if p.startswith('t='):
                                t = p.split('=')[1]
                            if p.startswith('h='):
                                h = p.split('=')[1]
                        spoof_active = True
                    except:
                        pass

                # Reset
                if '/reset' in req:
                    spoof_active = False

                # -------------------------
                # HTML UI
                # -------------------------
                html = f"""<!DOCTYPE html>
<html>
<head>
<title>Pico Secure Monitor</title>
<meta http-equiv="refresh" content="2">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body {{
    background-color: #121212;
    font-family: sans-serif;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
}}
.card {{
    background-color: #1e1e1e;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    text-align: center;
    width: 320px;
}}
.temp {{
    color: cyan;
    font-size: 2.5rem;
    font-weight: bold;
}}
.hum {{
    color: pink;
    font-size: 2.5rem;
    font-weight: bold;
}}
.label {{
    color: #888;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
.status {{
    margin-top: 1rem;
    color: orange;
    font-size: 0.9rem;
}}
button {{
    margin-top: 1rem;
    padding: 8px 15px;
    border: none;
    border-radius: 6px;
    background: #333;
    color: white;
}}
</style>
</head>
<body>
<div class="card">
    <div class="label">Temperature</div>
    <div class="temp">{t} &deg;C</div>
    <div class="label">Humidity</div>
    <div class="hum">{h} %</div>

    <div class="status">
        {"SPOOF MODE ACTIVE" if spoof_active else "LIVE SENSOR DATA"}
    </div>

    <a href="/reset"><button>Reset</button></a>
</div>
</body>
</html>"""

                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                conn.sendall(html)

            else:
                conn.send('HTTP/1.0 401 Unauthorized\r\n')
                conn.send('WWW-Authenticate: Basic realm="Restricted"\r\n\r\n')
                conn.send('<h1>401 Unauthorized</h1>')

            conn.close()

        except OSError:
            time.sleep(0.1)

        except Exception:
            if conn:
                conn.close()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Server Stopped")
    s.close()