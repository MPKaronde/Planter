#include "transmitter.h"

Transmitter::Transmitter(const char* device_name) {
    this->device_name = device_name;
    this->ssid = WIFI_SSID;
    this->password = WIFI_PASSWORD;
    this->server_url = SERVER_URL;
}

void Transmitter::init() {
    WiFi.begin(ssid, password);
    Serial.print("Connecting to WiFi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");
}

void Transmitter::verify_connection() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi connection lost. Reconnecting...");
        init();
    }
}

void Transmitter::send_data(float battery_voltage, float solar_voltage, float moisture_percentage) {
    verify_connection();

    // Create JSON payload
    String payload = "{";
    payload += "\"device_name\":\"" + String(device_name) + "\",";
    payload += "\"battery_voltage\":" + String(battery_voltage) + ",";
    payload += "\"solar_voltage\":" + String(solar_voltage) + ",";
    payload += "\"moisture_percentage\":" + String(moisture_percentage);
    payload += "}";

    // Send HTTP POST request
    WiFiClient client;
    HTTPClient http;
    
    http.begin(client, server_url);
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode > 0) {
        Serial.println("Data sent successfully");
        Serial.println("Response: " + http.getString());
    } else {
        Serial.println("Error sending data: " + String(httpResponseCode));
    }
    
    http.end();
}