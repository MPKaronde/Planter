#include <Arduino.h>
#include "voltage_sensor.h"
#include "pinout.h"

VoltageSensor sensor(SENSOR_PIN);

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("\nADC READING: ");
  Serial.println(analogRead(SENSOR_PIN));

  Serial.println("\nVOLTAGE READING: ");
  Serial.println(sensor.take_reading());
  delay(1000);
}
