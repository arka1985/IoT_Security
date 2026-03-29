import network, socket, time, machine, dht, ubinascii, secrets, hashlib, rp2, sys

# --- [1. STABLE WIFI & HARDWARE SETUP] ---
rp2.country('US')
sensor = dht.DHT22(machine.Pin(15))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# CRITICAL: Disables WiFi sleep to prevent browser timeouts
wlan.config(pm = 0xa11140) 
wlan.connect(secrets.SSID, secrets.PASSWORD)

print("Connecting to WiFi", end="")
while wlan.status() < 3:
    print(".", end="")
    time.sleep(1)

my_ip = wlan.ifconfig()[0]
print(f"\n" + "="*40)
print(f"[LIVE DASHBOARD] http://{my_ip}")
print("="*40)

# --- [2. SECURITY CONFIGURATION] ---
auth = ubinascii.b2a_base64(f"{secrets.WEB_USER}:{secrets.WEB_PASS_STRONG}".encode()).strip().decode()
expected_basic = f"Basic {auth}"

TOTP_INTERVAL = 15
authorized_ips = {}  # Tracks who has passed 2FA
fail_counts = {}     # Tracks hacker attempts
MAX_FAILS = 3
last_totp, last_sec = "", -1

def get_totp():
    """Generates the 6-digit PIN every 15 seconds"""
    step = int(time.time() // TOTP_INTERVAL)
    h = hashlib.sha256(str(step).encode() + b"SALT_PICO").digest()
    return str(int(ubinascii.hexlify(h[:4]), 16))[-6:]

# --- [3. SOCKET ENGINE] ---
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(1) # Listen to 1 request at a time to prevent crashes
s.settimeout(0.1)

t, h, spoof = "0.0", "0.0", False

# --- [4. MAIN LOOP] ---
try:
    while True:
        # --- A. SHELL DISPLAY (Smooth & Fast) ---
        curr_t = int(time.time())
        code = get_totp()
        if curr_t != last_sec:
            last_sec = curr_t
            if code != last_totp: 
                last_totp = code
                print(f"\n[NEW TOTP] {last_totp}")
            # Print the countdown on the same line
            print(f"\r[2FA CODE: {last_totp}] Rotates in: {TOTP_INTERVAL-(curr_t%TOTP_INTERVAL):02d}s ", end="")

        # --- B. SENSOR READING ---
        if not spoof:
            try: 
                sensor.measure()
                t, h = "{:.1f}".format(sensor.temperature()), "{:.1f}".format(sensor.humidity())
            except: pass

        # --- C. HANDLE CONNECTIONS ---
        conn = None
        try:
            conn, addr = s.accept()
            ip = addr[0]
            conn.settimeout(0.5)
            
            req = conn.recv(1024).decode()
            if not req:
                conn.close()
                continue

            # 1. Check IP Ban List
            if ip in fail_counts and fail_counts[ip] >= MAX_FAILS:
                conn.sendall(b'HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n<h1>IP BLOCKED</h1>')
                conn.close()
                continue

            # 2. Check Username & Password
            if expected_basic in req:
                
                # Check if user just submitted a 2FA code
                if 'code=' in req:
                    if f"code={last_totp}" in req:
                        # Authorize IP for 10 minutes
                        authorized_ips[ip] = time.time() + 600
                        print(f"\n[AUTH] {ip} successfully passed 2FA.")
                    else:
                        # Add a strike for a wrong guess
                        fail_counts[ip] = fail_counts.get(ip, 0) + 1
                        print(f"\n[WARN] {ip} guessed wrong TOTP ({fail_counts[ip]}/{MAX_FAILS})")
                        conn.sendall(b'HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n<h2>Invalid 2FA Code</h2>')
                        conn.close()
                        continue

                # 3. Serve UI based on Authorization
                if ip in authorized_ips and time.time() < authorized_ips[ip]:
                    # --- AUTHORIZED: SHOW MASSIVE NEON DATA ---
                    html = f"""<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2">
                    <style>
                        body {{ background:#000; color:white; font-family:sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; }}
                        .l {{ color:#333; font-size:1.5rem; letter-spacing:5px; margin-top:20px; font-weight:bold; }}
                        .t {{ color:cyan; font-size:10rem; font-weight:bold; margin:0; text-shadow:0 0 30px cyan; }}
                        .h {{ color:pink; font-size:10rem; font-weight:bold; margin:0; text-shadow:0 0 30px pink; }}
                    </style></head><body>
                        <div class="l">TEMPERATURE</div><div class="t">{t}&deg;</div>
                        <div class="l">HUMIDITY</div><div class="h">{h}%</div>
                    </body></html>"""
                else:
                    # --- NOT AUTHORIZED: SHOW 2FA POPUP ---
                    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {{ background:#0a0a0a; color:cyan; font-family:sans-serif; text-align:center; padding-top:20vh; margin:0; }}
                        input {{ background:black; border:2px solid cyan; color:cyan; padding:15px; font-size:1.5rem; border-radius:10px; width:150px; text-align:center; outline:none; }}
                        button {{ background:cyan; border:none; padding:15px 30px; font-size:1rem; font-weight:bold; border-radius:10px; margin-top:20px; color:black; cursor:pointer; }}
                    </style></head><body>
                        <h2>2FA REQUIRED</h2>
                        <form action="/" method="get">
                            <input type="text" name="code" placeholder="000000" inputmode="numeric" autofocus autocomplete="off"><br>
                            <button type="submit">AUTHORIZE</button>
                        </form></body></html>"""
                
                # Encode and send standard HTTP/1.1 response
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{html}'
                conn.sendall(response.encode('utf-8'))
                
            else:
                # Triggers browser Username/Password box
                conn.sendall(b'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Pico"\r\nConnection: close\r\n\r\n')
            
            conn.close()
        except OSError:
            pass # Keep looping quietly if no one is connecting
        
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\n[SHUTDOWN] Stopping Server...")
finally:
    s.close()