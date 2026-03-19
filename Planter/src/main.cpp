#include <Arduino.h>
#include "voltage_sensor.h"
#include "moisture_sensor.h"
#include "constants.h"
#include "pinout.h"
#include "transmitter.h"

const char* DEVICE_NAME = "Barry";  // name of this device, used for identification on server

VoltageSensor   battery_sensor(BATTERY_SENSOR_PIN);
VoltageSensor   solar_sensor(SOLAR_SENSOR_PIN);
MoistureSensor  moisture_sensor(MOISTURE_SENSOR_PIN, SENSOR_A_DRY_VAL, SENSOR_A_WET_VAL);
Transmitter     transmitter(DEVICE_NAME);

void setup() {
  Serial.begin(9600);
  transmitter.init();
}

void loop() {
  transmitter.send_data(5, 6, 50);
  delay(1000);
}
