
#include <DHT.h>

#define DHTPIN D5
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  Serial.print("Temp: ");
  Serial.print(dht.readTemperature());
  Serial.print(" C  Hum: ");
  Serial.print(dht.readHumidity());
  Serial.println(" %");
  delay(2000);
}
