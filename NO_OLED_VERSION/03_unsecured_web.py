import network
import socket
import time
import machine
import dht
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

print("Connected!")
print("IP Address:", wlan.ifconfig()[0])

# -------------------------
# Socket Server Setup
# -------------------------
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
s.settimeout(1)   # ⭐ IMPORTANT → Prevents freezing

# -------------------------
# Variables
# -------------------------
spoof_active = False
t, h = "0.0", "0.0"

# -------------------------
# Main Loop
# -------------------------
try:
    while True:

        # Read real sensor if not spoofing
        if not spoof_active:
            try:
                sensor.measure()
                t = "{:.1f}".format(sensor.temperature())
                h = "{:.1f}".format(sensor.humidity())
            except:
                pass

        # Wait for connection (non-blocking)
        try:
            conn, addr = s.accept()
        except OSError:
            time.sleep(0.1)
            continue

        try:
            raw_req = conn.recv(1024)
            if not raw_req:
                conn.close()
                continue

            request = raw_req.decode()

            # -------------------------
            # Spoof Request
            # -------------------------
            if '/set_env?' in request:
                try:
                    query = request.split('?')[1].split(' ')[0]
                    for p in query.split('&'):
                        if p.startswith('t='):
                            t = p.split('=')[1]
                        if p.startswith('h='):
                            h = p.split('=')[1]
                    spoof_active = True
                except:
                    pass

            # -------------------------
            # Reset Request
            # -------------------------
            if '/reset' in request:
                spoof_active = False

            # -------------------------
            # HTML Page
            # -------------------------
            html = f"""<!DOCTYPE html>
<html>
<head>
<title>Remote Monitor</title>
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
    width: 300px;
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
    <a href="/reset"><button>Reset to Live</button></a>
</div>
</body>
</html>"""

            # Send response
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.sendall(html)
            conn.close()

        except Exception as e:
            conn.close()

        time.sleep(0.1)

# -------------------------
# Clean Exit
# -------------------------
except KeyboardInterrupt:
    print("Server Stopped by User")
    s.close()