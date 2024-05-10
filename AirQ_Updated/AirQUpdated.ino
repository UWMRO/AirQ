
/*
 * Air Quality Sensor v3.1
 * 
 * Name of driver/board port for coding arduino is "Adafruit ESP32 Feather"
 */
// Timing
#define FAN_TIME 30     // fan runtime in seconds
#define SAMPLE_TIME 30  // time in seconds each sensor integrates for MIGHT NOT NEED
#define WAIT_TIME 600   // time between samples

// WiFi parameters CHANGE FOR INSTALLATION
#define WLAN_SSID       "moto g power (2022)_6470" // "phone hotspot"
#define WLAN_PASS       ""

// Pin Definitions
#define BUTTONPIN 21    // momentary switch (button)

// LED pins
#define FANPIN 13       // Fan (use pin 13 due to integrated LED)

// Adafruit IO
#define AIO_SERVER      "io.adafruit.com"
#define AIO_SERVERPORT  1883
#define AIO_USERNAME    "ltsiang"
#define AIO_KEY         "a0949d9c814146789aa8245b0e6f4204"  // Obtained from account info on io.adafruit.com

#include <Bounce2.h>  // debounce library 
//#include "DHT.h"
#include <WiFi.h>
#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include <Arduino.h>
#include <Ewma.h> //MIGHT NEED TO REMOVE

//Libraries for sensirion sensor
#include <SensirionI2CSen5x.h>
#include <Wire.h>

void mqtt_connect();

// Button Object Creation
Bounce Button = Bounce();

// The used commands use up to 48 bytes. On some Arduino's the default buffer
// space is not large enough
#define MAXBUF_REQUIREMENT 48

#if (defined(I2C_BUFFER_LENGTH) &&                 \
     (I2C_BUFFER_LENGTH >= MAXBUF_REQUIREMENT)) || \
    (defined(BUFFER_LENGTH) && BUFFER_LENGTH >= MAXBUF_REQUIREMENT)
#define USE_PRODUCT_INFO
#endif

SensirionI2CSen5x sen5x;

// Create an WiFiClient class to connect to the MQTT server, then setup the MQTT
// client class by passing in the WiFi client and MQTT server and login details.

WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);

// Setup feeds NEED TO CHANGE PUBLISH COMMANDS
Adafruit_MQTT_Publish LEDcolor = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/LEDcolor");
Adafruit_MQTT_Publish dust1feed =  Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/Dust1");
Adafruit_MQTT_Publish dust2feed = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/Dust2");


void setup() {

    Serial.begin(115200);
    while (!Serial) {
        delay(100);
    }

    // Setup Button
    pinMode(BUTTONPIN, INPUT_PULLUP);
    Button.attach(BUTTONPIN);
    Button.interval(5);

    // Setup Fan 
    pinMode(FANPIN, OUTPUT);

    // Setup i2c
    Wire.begin();
    sen5x.begin(Wire);

    uint16_t error;
    char errorMessage[256];
    error = sen5x.deviceReset();
    if (error) {
        Serial.print("Error trying to execute deviceReset(): ");
        errorToString(error, errorMessage, 256);
        Serial.println(errorMessage);
    }

    // Loop while connecting to WiFi access point
    Serial.println(); Serial.println();
    delay(10);
    Serial.print(F("Connecting to "));
    Serial.println(WLAN_SSID);
    WiFi.begin(WLAN_SSID, WLAN_PASS);
    while (WiFi.status() != WL_CONNECTED) {  
      Serial.print(F("."));
      delay(250);
    }

    Serial.println();
    Serial.println(F("WiFi connected"));
    Serial.println(F("IP address: "));
    Serial.println(WiFi.localIP());

    float tempOffset = 0.0;
    error = sen5x.setTemperatureOffsetSimple(tempOffset);
    if (error) {
        Serial.print("Error trying to execute setTemperatureOffsetSimple(): ");
        errorToString(error, errorMessage, 256);
        Serial.println(errorMessage);
    } else {
        Serial.print("Temperature Offset set to ");
        Serial.print(tempOffset);
        Serial.println(" deg. Celsius (SEN54/SEN55 only");
    }

    // Start Measurement
    error = sen5x.startMeasurement();
    if (error) {
        Serial.print("Error trying to execute startMeasurement(): ");
        errorToString(error, errorMessage, 256);
        Serial.println(errorMessage);
    }
}

void loop() {

    // First make sure we are connected to adafruit IO
    if (! mqtt.ping(1)) {
      // ...connect to adafruit io
      if (! mqtt.connected())
        mqtt_connect();
    }

    // Need to store sample and publish to adafruit
    //dust2feed.publish(concentration);

    digitalWrite(FANPIN, HIGH);  // fan on
    delay(1000*FAN_TIME);
    SampleSen55();               // sample
    digitalWrite(FANPIN, LOW);   // fan off 

    // timer to to wait for next sample, exits if button is pressed
    unsigned long start_ms = millis();
    unsigned long wait_ms = 1000 * WAIT_TIME;
    while ((millis()-start_ms) < wait_ms)
    {
      Button.update();
      if ( Button.fell() ) {
        break;
      }
    }
}

void SampleSen55() {
  uint16_t error;
    char errorMessage[256];

    delay(1000);

    // Read Measurement
    float massConcentrationPm1p0;
    float massConcentrationPm2p5;
    float massConcentrationPm4p0;
    float massConcentrationPm10p0;
    float ambientHumidity;
    float ambientTemperature;
    float vocIndex;
    float noxIndex;
    error = sen5x.readMeasuredValues(
        massConcentrationPm1p0, massConcentrationPm2p5, massConcentrationPm4p0,
        massConcentrationPm10p0, ambientHumidity, ambientTemperature, vocIndex,
        noxIndex);
    if (error) {
      Serial.print("Error trying to execute readMeasuredValues(): ");
      errorToString(error, errorMessage, 256);
      Serial.println(errorMessage);
    } else {
      Serial.print("MassConcentrationPm1p0:");
      Serial.print(massConcentrationPm1p0);
      Serial.print("\t");
      Serial.print("MassConcentrationPm2p5:");
      Serial.print(massConcentrationPm2p5);
      Serial.print("\t");
      Serial.print("MassConcentrationPm4p0:");
      Serial.print(massConcentrationPm4p0);
      Serial.print("\t");
      Serial.print("MassConcentrationPm10p0:");
      Serial.print(massConcentrationPm10p0);
      Serial.print("\t");
      Serial.print("AmbientHumidity:");
      if (isnan(ambientHumidity)) {
          Serial.print("n/a");
      } else {
          Serial.print(ambientHumidity);
      }
      Serial.print("\t");
      Serial.print("AmbientTemperature:");
      if (isnan(ambientTemperature)) {
          Serial.print("n/a");
      } else {
          Serial.print(ambientTemperature);
      }
      Serial.print("\t");
      Serial.print("VocIndex:");
      if (isnan(vocIndex)) {
          Serial.print("n/a");
      } else {
          Serial.print(vocIndex);
      }
      Serial.print("\t");
      Serial.print("NoxIndex:");
      if (isnan(noxIndex)) {
          Serial.println("n/a");
      } else {
          Serial.println(noxIndex);
      }
    }
}


void mqtt_connect() {
  Serial.print(F("Connecting to the MQTT service... "));

  int8_t ret;

  while ((ret = mqtt.connect()) != 0) {
    Serial.println(ret);
    switch (ret) {
      case 1: Serial.println(F("Wrong protocol")); break;
      case 2: Serial.println(F("ID rejected")); break;
      case 3: Serial.println(F("Server unavail")); break;
      case 4: Serial.println(F("Bad user/pass")); break;
      case 5: Serial.println(F("Not authed")); break;
      case 6: Serial.println(F("Failed to subscribe")); break;
      default: Serial.println(F("Connection failed")); break;
    }
    if (ret >= 0)
      mqtt.disconnect();
    Serial.println(F("Retrying connection..."));
    delay(5000);
  }
  Serial.println(F("Connected!"));
}
