#ifdef MOISTURE_SENSOR_H
#define MOISTURE_SENSOR_H

#include <Arduino.h>

const int MEASUREMENT_CYCLES = 10;  // how many measurements are used for smoothening

class MoistureSensor {
public:
    /* MoistureSensor Constructor 
        Input: sensor pin
        Returns: none    */
    MoistureSensor(int data_pin);

    /* MoistureSensor Constructor
        Input: sensor pin, pre-measured dry and wet vals
        Returns: none */
    MoistureSensor(int data_pin, float dry_measure, float wet_measure);

    /* Take a reading 
        Input:  none
        Returns: calculated humidity percentage  */
    float take_reading();

    /* Calibrate lower bound for dry soil 
        Input: none
        Returns: none   
        Note: use bone dry soil for this    */
    void calibrate_dry();

    /* Calibrate higher bound for saturated soil
        Input: none
        Returns: none
        Note: Use fully saturated soil for this */
    void calibrate_wet();

private:
    int pin;
    float dry_val;
    float wet_val;

    /* Take a smoothened reading from the sensor
        Input: none
        Returns: an average analog reading from the sensor over cycles */
    void smoothened_reading();
};

#endif // MOISTURE_SENSOR_H