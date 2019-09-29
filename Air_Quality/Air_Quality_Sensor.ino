/* Ling Tsiang and Oliver Fraser
 * Air Quality Sensor v2.1
 * w/ thanks to example Adafruit MQTT code
 * 
 * LED Status:
 * Blinks blue while attempting wifi connection
 * Red while trying to connect to mqtt server 
 * off while fan runs (but pin 13's LED will be on)
 * Both on for dust 1 reading
 * Blue only for dust 2 reading
 * Red on while ready and waiting for WAIT_TIME or button press
*/

// Timing
#define FAN_TIME 30     // fan runtime in seconds
#define SAMPLE_TIME 30  // time in seconds each sensor integrates for
#define WAIT_TIME 600   // time between samples

// WiFi parameters
#define WLAN_SSID       "University of Washington" // "University of Washington"
#define WLAN_PASS       ""

// Pin Definitions
#define BUTTONPIN 21    // momentary switch (button)
// LED pins
#define BLUEPIN 14      // Blue LED
#define REDPIN 32       // Red LED
#define DHTPIN 15       // Temp/Humidity
#define DUST1PIN 27     // Dust Sensor #1
#define DUST2PIN 33     // Dust Sensor #2
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
#include <Ewma.h>

void mqtt_connect();


class Grove_Dust_Sensor
{
  // Default sample time is 30 seconds
  public:
    unsigned long sampletime;
    
  Grove_Dust_Sensor(int Pin) {
    _pin = Pin;
    pinMode(Pin, INPUT);
  }

  float Sample(unsigned long sampletime_default = 30) {
    unsigned long duration;
    unsigned long lowpulseoccupancy;
    float ratio;
    float concentration;

    sampletime = sampletime_default;
    // first convert sample time from seconds to ms
    unsigned long sampletime_ms = 1000 * sampletime;
    lowpulseoccupancy = 0;
    unsigned long starttime = millis(); 
    // record the total time that the sensor is low during the sample
    while ((millis()-starttime) < sampletime_ms) 
    { 
      duration = pulseIn(_pin, LOW);
      lowpulseoccupancy = lowpulseoccupancy+duration;
    }
    // calculate percentage of time sensor is low
    ratio = lowpulseoccupancy / (sampletime_ms*10.0);
    // use fit to find concentration of 
    concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // using spec sheet curve
    return concentration;
  }
  
  private:
    int _pin;
};


// Object Creation
Bounce Button = Bounce();
Grove_Dust_Sensor dust1(DUST1PIN); 
Grove_Dust_Sensor dust2(DUST2PIN); 
Ewma FilterDust1(0.1);   // (0.1) = Less smoothing - faster to detect changes, but more prone to noise 
Ewma FilterDust2(0.1);  // (0.01) = More smoothing - less prone to noise, but slower to detect changes


//DHT dht(DHTPIN, DHT22);

// Create an WiFiClient class to connect to the MQTT server, then setup the MQTT
// client class by passing in the WiFi client and MQTT server and login details.

WiFiClient client;
Adafruit_MQTT_Client mqtt(&client, AIO_SERVER, AIO_SERVERPORT, AIO_USERNAME, AIO_KEY);

// Setup feeds
Adafruit_MQTT_Publish LEDcolor = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/LEDcolor");
Adafruit_MQTT_Publish dust1feed =  Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/Dust1");
Adafruit_MQTT_Publish dust2feed = Adafruit_MQTT_Publish(&mqtt, AIO_USERNAME "/feeds/Dust2");


void setup() {
  Serial.begin(9600);

  // Setup LEDs
  pinMode(BLUEPIN, OUTPUT);
  pinMode(REDPIN, OUTPUT);
  digitalWrite(BLUEPIN, HIGH);    // off
  digitalWrite(REDPIN, HIGH);  // off

  // Setup Button
  pinMode(BUTTONPIN, INPUT_PULLUP);
  Button.attach(BUTTONPIN);
  Button.interval(5);

  // Setup Fan 
  pinMode(FANPIN, OUTPUT);

  // Setup Temperature/Humidity sensor
  //dht.begin();
  
  // blink blue LED while connecting to WiFi access point
  Serial.println(); Serial.println();
  delay(10);
  Serial.print(F("Connecting to "));
  Serial.println(WLAN_SSID);
  WiFi.begin(WLAN_SSID, WLAN_PASS);
  bool LED = false;       // for blinking ...
  while (WiFi.status() != WL_CONNECTED) {
    LED = !LED;
    digitalWrite(BLUEPIN, LED);   
    Serial.print(F("."));
    delay(250);
  }
  // Success! Make sure blue is off
  digitalWrite(BLUEPIN, HIGH);     // off
  Serial.println();
  Serial.println(F("WiFi connected"));
  Serial.println(F("IP address: "));
  Serial.println(WiFi.localIP());

  // ready, red on
  digitalWrite(REDPIN, LOW);    // on
}

void loop() {
  // First make sure we are connected to adafruit IO
  if (! mqtt.ping(1)) {
    // ...connect to adafruit io
    if (! mqtt.connected())
      mqtt_connect();
  }
  digitalWrite(REDPIN, HIGH);    // off

  
  digitalWrite(FANPIN, HIGH);  // on
  delay(1000*FAN_TIME);
  digitalWrite(FANPIN, LOW);   // off 

  digitalWrite(REDPIN, LOW);    // on for Dust 1
  digitalWrite(BLUEPIN, LOW);    // on for Dust 1

  float concentration;
  // Dust 1
  Serial.print("Dust 1: ");
  concentration = dust1.Sample(SAMPLE_TIME);
  Serial.print(concentration);
  Serial.print(" (");
  Serial.print(dust1.sampletime);
  Serial.print(" second sample). Filtered: ");
  concentration = FilterDust1.filter(concentration);
  Serial.println(concentration);
  dust1feed.publish(concentration);

  // red off, blue remains on for dust 2
  digitalWrite(REDPIN, HIGH);  

  // Dust 2
  Serial.print("Dust 2: ");
  concentration = dust2.Sample(SAMPLE_TIME);
  Serial.print(concentration);
  Serial.print(" (");
  Serial.print(dust2.sampletime);
  Serial.print(" second sample). Filtered: ");
  concentration = FilterDust2.filter(concentration);
  Serial.println(concentration);
  dust2feed.publish(concentration);
  digitalWrite(BLUEPIN, HIGH);    // off

  // ready, red on
  digitalWrite(REDPIN, LOW);  // on

  // wait for WAIT_TIME, or till a button press
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
