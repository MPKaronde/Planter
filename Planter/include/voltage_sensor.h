#ifndef VOLTAGE_SENSOR_H
#define VOLTAGE_SENSOR_H

#include <Arduino.h>

const int ADC_CONVERSION = 4095;        // 12-bit ADC resolution
const float VOLTAGE_REF = 3.3;          // Reference voltage
const int VOLTAGE_DIVIDER_RATIO = 5;    // Voltage divider ratio in chip

class VoltageSensor {
public:
    /* Voltage Sensor Constructor
        Input: analogPin (ESP32 pin to which sensor data connected)
        Returns: none  */
    VoltageSensor(int analogPin);

    /* Calculates voltage reading
        Input: None
        Output: Voltage reading for this sensor */
    float take_reading();

private:
    int pin;        // The analog pin connected to the voltage sensor
};

#endif // VOLTAGE_SENSOR_H