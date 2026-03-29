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

while not wlan.isconnected():
    time.sleep(1)

print("Connected! IP:", wlan.ifconfig()[0])

# -------------------------
# Security Setup
# -------------------------
auth = ubinascii.b2a_base64(
    f"{secrets.WEB_USER}:{secrets.WEB_PASS_STRONG}".encode()
).strip().decode()
expected = f"Basic {auth}"

attempt_counter = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 60 

# -------------------------
# Socket Setup
# -------------------------
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
s.settimeout(1.0)

t, h = "0.0", "0.0"
spoof_active = False

print("Server Secure & Running...")

try:
    while True:
        if not spoof_active:
            try:
                sensor.measure()
                t = "{:.1f}".format(sensor.temperature())
                h = "{:.1f}".format(sensor.humidity())
            except: pass

        conn = None
        try:
            conn, addr = s.accept()
            client_ip = addr[0]
            curr_t = time.time()

            # --- LOCKOUT CHECK ---
            if client_ip in attempt_counter:
                fails, l_time = attempt_counter[client_ip]
                if fails >= MAX_ATTEMPTS:
                    if curr_t - l_time < LOCKOUT_TIME:
                        conn.send('HTTP/1.0 403 Forbidden\r\n\r\n')
                        conn.send('<h1>403 Forbidden: Locked out.</h1>')
                        conn.close()
                        continue
                    else:
                        attempt_counter[client_ip] = [0, 0]

            conn.settimeout(1.0)
            raw_req = conn.recv(1024)
            if not raw_req:
                conn.close()
                continue

            req = raw_req.decode()

            if expected in req:
                attempt_counter[client_ip] = [0, 0] 
                
                if '/set_env?' in req:
                    query = req.split('?')[1].split(' ')[0]
                    for p in query.split('&'):
                        if p.startswith('t='): t = p.split('=')[1]
                        if p.startswith('h='): h = p.split('=')[1]
                    spoof_active = True
                if '/reset' in req: spoof_active = False

                # --- UPDATED STYLISH HTML UI ---
                html = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            background-color: #121212; 
            color: white; 
            font-family: sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
        }}
        .card {{
            background: #1e1e1e;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            text-align: center;
        }}
        .label {{ color: #888; font-size: 1.2rem; text-transform: uppercase; }}
        .temp {{ color: cyan; font-size: 5rem; font-weight: bold; margin: 10px 0; }}
        .hum {{ color: pink; font-size: 5rem; font-weight: bold; margin: 10px 0; }}
        .status {{ color: orange; font-size: 1rem; margin-top: 20px; }}
        button {{
            background: #333; color: white; border: none; padding: 10px 20px;
            border-radius: 10px; cursor: pointer; margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="label">Temperature</div>
        <div class="temp">{t}&deg;C</div>
        <div class="label">Humidity</div>
        <div class="hum">{h}%</div>
        <div class="status">MODE: {"SPOOFED" if spoof_active else "LIVE SENSOR"}</div>
        <a href="/reset"><button>Reset Sensor</button></a>
    </div>
</body>
</html>"""
                
                conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                conn.sendall(html)
            else:
                if client_ip not in attempt_counter:
                    attempt_counter[client_ip] = [1, curr_t]
                else:
                    attempt_counter[client_ip][0] += 1
                    attempt_counter[client_ip][1] = curr_t
                
                conn.send('HTTP/1.0 401 Unauthorized\r\n')
                conn.send('WWW-Authenticate: Basic realm="Restricted"\r\n\r\n')
                conn.send('<h1>401 Unauthorized</h1>')

            conn.close()
        except Exception:
            if conn: conn.close()
except KeyboardInterrupt:
    s.close()