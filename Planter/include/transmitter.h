#ifndef TRANSMITTER_H
#define TRANSMITTER_H

#include <Arduino.h>
#include <WiFi.h>
#include "constants.h"
#include <HTTPClient.h>

class Transmitter{
public:
    /* Constructor
        Input: Device name
        Returns: none   */
    Transmitter(const char* device_name);

    /* Initialize Connection, run in begin loop
        Input: none
        Returns: none*/
    void init();

    /* Send data to server
        Input: battery voltage, solar voltage, moisture percentage
        Returns: none */
    void send_data(float battery_voltage, float solar_voltage, float moisture_percentage); 
private:
    const char* ssid = WIFI_SSID;                           // WiFi SSID
    const char* password = WIFI_PASSWORD;                   // WiFi password        
    const char* server_url = "http://example.com/data";     // Raspberru Pi Url
    const char* device_name;                                // Name of this device, used for identification on server       

    /* Verify WiFi connection before sending data, fix if necessary
        Input: none
        Returns: none */
    void verify_connection();
};

#endif // TRANSMITTER_H