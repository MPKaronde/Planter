#include "moisture_sensor.h"

MoistureSensor::MoistureSensor(int pin) 
{
    this->pin = pin;

    // set dummy vals for wet and dry for now
    this->dry_val = 4095.0;
    this->wet_val = 0.0;
}

MoistureSensor::MoistureSensor(int pin, float dry_measure, float wet_measure) 
{
    this->pin = pin;
    this->dry_val = dry_measure;
    this->wet_val = wet_measure;
}

float MoistureSensor::smoothened_reading() 
{
    float total = 0.0;
    for (int i = 0; i < MEASUREMENT_CYCLES; i++) {
        total += analogRead(this->pin);
    }
    return total / MEASUREMENT_CYCLES;
}

void MoistureSensor::calibrate_dry() 
{
    this->dry_val = smoothened_reading();
} 

void MoistureSensor::calibrate_wet() 
{
    this->wet_val = smoothened_reading();
}

float MoistureSensor::take_reading() 
{
    float reading = smoothened_reading();
    // map the reading to a percentage based on the calibrated dry and wet values
    float percentage = (reading - this->dry_val) / (this->wet_val - this->dry_val) * 100.0;
    // clamp the percentage between 0 and 100
    if (percentage < 0.0) percentage = 0.0;
    if (percentage > 100.0) percentage = 100.0;
    return percentage;
}