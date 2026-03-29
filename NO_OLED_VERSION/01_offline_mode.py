import machine
import time
import dht

# Pin where DHT22 DATA is connected
sensor = dht.DHT22(machine.Pin(15))

print("DHT22 Simple Serial Demo Started")

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()

        print("Temperature:", temp, "°C")
        print("Humidity:", hum, "%")
        print("---------------------")

    except:
        print("Sensor Error")

    time.sleep(2)