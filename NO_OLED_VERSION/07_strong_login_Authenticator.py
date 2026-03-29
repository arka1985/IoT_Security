import network, socket, time, machine, dht, ubinascii, secrets, hashlib, rp2, ntptime

# --- [1. WIFI & TIME SYNC] ---
rp2.country('US')
sensor = dht.DHT22(machine.Pin(15))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm = 0xa11140) # Disable WiFi sleep (Fixes browser timeouts)
wlan.connect(secrets.SSID, secrets.PASSWORD)

print("Connecting to WiFi", end="")
while wlan.status() < 3:
    print(".", end="")
    time.sleep(1)

my_ip = wlan.ifconfig()[0]

print("\nSyncing exact time with Internet (NTP)", end="")
ntp_success = False
for i in range(10): # Try up to 10 times to ensure we get the real time
    try:
        ntptime.settime()
        ntp_success = True
        break
    except:
        time.sleep(1)
        print(".", end="")

if ntp_success:
    print(" [SUCCESS] Clock synced!")
else:
    print("\n[!!!] CLOCK SYNC FAILED [!!!] Codes will not match.")

# --- [2. CRITICAL FIX: EPOCH DETECTION] ---
if time.localtime(0)[0] == 2000:
    UNIX_OFFSET = 946684800
    print("[SYSTEM] Y2K Epoch detected. Applying 30-year correction.")
else:
    UNIX_OFFSET = 0
    print("[SYSTEM] 1970 Unix Epoch detected. No correction needed.")

# --- [3. BULLETPROOF GOOGLE AUTHENTICATOR SETUP] ---
print("\n" + "="*50)
print(" 📱 ADD THIS NEW KEY TO GOOGLE AUTHENTICATOR")
print("="*50)
print("Option 1: Scan this QR Code from your browser:")
print("https://api.qrserver.com/v1/create-qr-code/?data=otpauth://totp/Pico:Pico%20Monitor?secret=GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ&issuer=Pico&size=300x300")
print("Option 2: Enter Key Manually:")
print("Account: Pico Monitor")
print("Key:     GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ")
print("-" * 50)
print(f"[LIVE DASHBOARD] http://{my_ip}")
print("="*50 + "\n")

auth = ubinascii.b2a_base64(f"{secrets.WEB_USER}:{secrets.WEB_PASS_STRONG}".encode()).strip().decode()
expected_basic = f"Basic {auth}"

TOTP_INTERVAL = 30 

# CRITICAL FIX: We bypass Base32 decoding entirely. 
# These are the exact raw bytes that equal "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
SECRET_BYTES = b"12345678901234567890"

authorized_ips = {}
fail_counts = {}
MAX_FAILS = 3
last_totp, last_sec = "", -1

def hmac_sha1(key, msg):
    """Official HMAC-SHA1 algorithm"""
    if len(key) > 64: key = hashlib.sha1(key).digest()
    key = key + b'\x00' * (64 - len(key))
    ipad = bytes(x ^ 0x36 for x in key)
    opad = bytes(x ^ 0x5C for x in key)
    inner = hashlib.sha1(ipad + msg).digest()
    return hashlib.sha1(opad + inner).digest()

def get_google_auth_code():
    """Generates the 6-digit Google Auth code using real UTC Time"""
    unix_time = time.time() + UNIX_OFFSET
    time_step = int(unix_time // TOTP_INTERVAL)
    
    msg = bytearray(8)
    for i in range(7, -1, -1):
        msg[i] = time_step & 0xff
        time_step >>= 8
        
    hash_result = hmac_sha1(SECRET_BYTES, msg)
    offset = hash_result[19] & 0x0F
    code_int = ((hash_result[offset] & 0x7F) << 24 |
                (hash_result[offset+1] & 0xFF) << 16 |
                (hash_result[offset+2] & 0xFF) << 8 |
                (hash_result[offset+3] & 0xFF))
    
    code = str(code_int % 1000000)
    return "0" * (6 - len(code)) + code

# --- [4. SOCKET ENGINE] ---
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(1)
s.settimeout(0.1)

t, h, spoof = "0.0", "0.0", False

# --- [5. MAIN LOOP] ---
try:
    while True:
        curr_t = int(time.time())
        code = get_google_auth_code()
        
        # Smooth shell display
        if curr_t != last_sec:
            last_sec = curr_t
            if code != last_totp: last_totp = code
            print(f"\r[Pico Code: {last_totp}] | Matches phone? Rotates in: {TOTP_INTERVAL-(curr_t%TOTP_INTERVAL):02d}s ", end="")

        if not spoof:
            try: 
                sensor.measure()
                t, h = "{:.1f}".format(sensor.temperature()), "{:.1f}".format(sensor.humidity())
            except: pass

        conn = None
        try:
            conn, addr = s.accept()
            ip = addr[0]
            conn.settimeout(0.5)
            
            req = conn.recv(1024).decode()
            if not req:
                conn.close()
                continue

            # 1. Firewall Check (Ban List)
            if ip in fail_counts and fail_counts[ip] >= MAX_FAILS:
                conn.sendall(b'HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n<h1>IP BLOCKED: Too Many Failed 2FA Attempts</h1>')
                conn.close()
                continue

            # 2. Basic Auth Check
            if expected_basic in req:
                
                # Check for 2FA Submission
                if 'code=' in req:
                    if f"code={last_totp}" in req:
                        authorized_ips[ip] = time.time() + 600 # 10 minute session
                        print(f"\n[AUTH SUCCESS] {ip} unlocked dashboard.")
                        # --- HTTP 302 REDIRECT (Cleans the URL) ---
                        conn.sendall(b'HTTP/1.1 302 Found\r\nLocation: /\r\nConnection: close\r\n\r\n')
                        conn.close()
                        continue
                    else:
                        fail_counts[ip] = fail_counts.get(ip, 0) + 1
                        print(f"\n[AUTH FAILED] {ip} Wrong Code. ({fail_counts[ip]}/{MAX_FAILS})")
                        conn.sendall(b'HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n<h2>Invalid Google Auth Code</h2>')
                        conn.close()
                        continue

                # 3. Render View
                if ip in authorized_ips and time.time() < authorized_ips[ip]:
                    # --- DASHBOARD VIEW ---
                    html = f"""<!DOCTYPE html><html><head><meta http-equiv="refresh" content="2;url=/">
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
                    # --- 2FA LOGIN VIEW ---
                    html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
                    <style>
                        body {{ background:#0a0a0a; color:cyan; font-family:sans-serif; text-align:center; padding-top:20vh; margin:0; }}
                        input {{ background:black; border:2px solid cyan; color:cyan; padding:15px; font-size:1.5rem; border-radius:10px; width:200px; text-align:center; outline:none; letter-spacing:3px; }}
                        button {{ background:cyan; border:none; padding:15px 30px; font-size:1rem; font-weight:bold; border-radius:10px; margin-top:20px; color:black; cursor:pointer; }}
                    </style></head><body>
                        <h2>GOOGLE AUTHENTICATOR</h2>
                        <form action="/" method="get">
                            <input type="text" name="code" placeholder="000 000" inputmode="numeric" autofocus autocomplete="off"><br>
                            <button type="submit">UNLOCK DASHBOARD</button>
                        </form></body></html>"""
                
                response = f'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n{html}'
                conn.sendall(response.encode('utf-8'))
            else:
                conn.sendall(b'HTTP/1.1 401 Unauthorized\r\nWWW-Authenticate: Basic realm="Pico"\r\nConnection: close\r\n\r\n')
            
            conn.close()
        except OSError:
            pass
        
        time.sleep(0.02)
except KeyboardInterrupt:
    print("\n[SHUTDOWN] Stopping Server...")
finally:
    s.close()