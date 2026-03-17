#include "voltage_sensor.h"

// Constructor
VoltageSensor::VoltageSensor(int analogPin){
    pin = analogPin;
}

// Calculator method
float VoltageSensor::take_reading(){
    int adcVal = analogRead(pin);
    float vOut = (adcVal / ADC_CONVERSION) * VOLTAGE_REF;   // voltage into ADC
    float voltage = vOut * VOLTAGE_DIVIDER_RATIO;           // device divides voltage by 5
    return voltage;
}