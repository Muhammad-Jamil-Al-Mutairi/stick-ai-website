include <Arduino_RouterBridge.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include "MAX30105.h"
#include "heartRate.h" // The built-in peak detection algorithm

Adafruit_MPU6050 mpu;
MAX30105 particleSensor;

unsigned long lastUpdateMillis = 0;
const long UPDATE_INTERVAL = 20; 
int movementSampleCount = 0;

// Heart Rate Math Variables
const byte RATE_SIZE = 4; // Average across 4 beats
byte rates[RATE_SIZE]; 
byte rateSpot = 0;
long lastBeat = 0; 
float beatsPerMinute;
int beatAvg = 0;

void bridgeLog(String message) {
    Bridge.notify("log_data_properly", message);
}

void setup() {
    pinMode(LED_BUILTIN, OUTPUT); 
    Bridge.begin();
    delay(2000); 
    
    bridgeLog("Initializing AI Stick Hardware...");
    Wire.begin(); 

    if (!mpu.begin(0x68, &Wire)) bridgeLog("Error: MPU-6050 not found!");
    else {
        mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
        bridgeLog("MPU-6050 initialized.");
    }

    if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) bridgeLog("Error: MAX30102 not found!");
    else {
        particleSensor.setup();
        particleSensor.setPulseAmplitudeRed(0x1F);
        particleSensor.setPulseAmplitudeIR(0x1F);
        bridgeLog("MAX30102 initialized.");
    }
}

void loop() {
    digitalWrite(LED_BUILTIN, (millis() / 500) % 2); 
    unsigned long currentMillis = millis();

    // =========================================================
    // 1. FAST POLLING (Runs constantly to keep Heart Rate accurate)
    // =========================================================
    long irValue = particleSensor.getIR();
    
    // Clear the ghost average if you lift your finger!
    if (irValue < 20000) {
        beatAvg = 0; 
    } 
    
    if (checkForBeat(irValue) == true) {
        long delta = millis() - lastBeat;
        lastBeat = millis();
        beatsPerMinute = 60 / (delta / 1000.0); 
        
        if (beatsPerMinute < 255 && beatsPerMinute > 20) {
            rates[rateSpot++] = (byte)beatsPerMinute;
            rateSpot %= RATE_SIZE;
            beatAvg = 0;
            for (byte x = 0 ; x < RATE_SIZE ; x++) beatAvg += rates[x];
            beatAvg /= RATE_SIZE;
        }
    }
    
    // =========================================================
    // 2. TIMED POLLING (Runs every 20ms for AI IMU Data)
    // =========================================================
    if (currentMillis - lastUpdateMillis >= UPDATE_INTERVAL) {
        lastUpdateMillis = currentMillis;

        sensors_event_t a, g, temp;
        mpu.getEvent(&a, &g, &temp);

        movementSampleCount++;

        // THE FIX: Changed from 10 to 2. 
        // This forces the board to send data every 40ms (25Hz)
        if (movementSampleCount >= 2) { 
            // Send accelerometer data to the Python AI script
            Bridge.notify("record_sensor_movement", a.acceleration.x, a.acceleration.y, a.acceleration.z);
            
            // Send heart rate data to the Python AI script
            bridgeLog("HR_DEBUG:" + String(beatAvg) + "," + String(irValue)); 
            
            movementSampleCount = 0;
        }
    }
}
