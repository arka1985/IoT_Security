import network, socket, time, machine, dht, secrets

sensor = dht.DHT22(machine.Pin(15))

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

while not wlan.isconnected():
    time.sleep(1)

print("IP:", wlan.ifconfig()[0])

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(1)

while True:
    sensor.measure()
    t = "{:.1f}".format(sensor.temperature())
    h = "{:.1f}".format(sensor.humidity())

    conn, addr = s.accept()
    req = conn.recv(1024)

    html = f"""
    <html>
    <body style="margin:0;height:100vh;display:flex;justify-content:center;align-items:center;font-family:sans-serif;">
        <div style="text-align:center;">
            <h1 style="color:cyan;">Temperature: {t} C</h1>
            <h1 style="color:pink;">Humidity: {h} %</h1>
        </div>
    </body>
    </html>
    """

    conn.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
    conn.send(html)
    conn.close()