#include "moisture_sensor.h"

MoistureSensor::MoistureSensor(int pin) 
{
    this->pin = pin;
    this->dry_val = 1023.0;  // default dry value (bone dry soil)
    this->wet_val = 0.0;     // default wet value (fully saturated soil)
}