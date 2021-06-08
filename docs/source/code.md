# Code

## PM Sensor (Transceiver)

The sketch transmits PM sensor data to another Feather M0 transceiver. Data is sent every two seconds

The sketch makes use of the following tutorial by Adafruit. 
- [Feather M0 Lora](https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/overview)
- [PM2.5 air quality sensor](https://learn.adafruit.com/pm25-air-quality-sensor)

Portions of the example sketches in these tutorials are piecemealed to form this sketch.

Thank you Adafruit :) 


```c++
// #####    Transmitter Code       #####
// 
// Feather M0 (RH_RF95 915 MHz) and PM2.5 Air Quality Sensor
//
// The sketch transmits PM sensor data to another Feather M0 transceiver. Data is sent every one second 
// -*- mode: C++ -*-


#include <SPI.h>
#include <RH_RF95.h>
//#include <SoftReset.h>


// for feather m0 */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

// measure battery voltage
#define VBATPIN A7

// PM  
#define pmsSerial Serial1

// TX 
// Leagl operating frequency in North America 902-928, NOTE set freqmust match RX's freq!
//#define RF95_FREQ 902.0 // UBC-PM 01
#define RF95_FREQ 907.0 // UBC-PM 02
//#define RF95_FREQ 913.0 // UBC-PM 03
//#define RF95_FREQ 918.0 // UBC-PM 04
//#define RF95_FREQ 923.0 // UBC-PM 05



// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);



// #####################################  SET UP  ##########################################

void setup() 
{
// ##################################################
// Start serial baud rate (115200) and initiate LoRa Radio
// ##################################################
pinMode(RFM95_RST, OUTPUT);
digitalWrite(RFM95_RST, HIGH);

Serial.begin(115200);

/*
while (!Serial) {
    delay(1);
}
*/
delay(100);

Serial.println("Feather LoRa TX Test!");

// manual reset
digitalWrite(RFM95_RST, LOW);
delay(10);
digitalWrite(RFM95_RST, HIGH);
delay(10);

while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
}
Serial.println("LoRa radio init OK!");

// Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
}
Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

// Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

// The default transmitter power is 13dBm, using PA_BOOST.
// If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
// you can set transmitter powers from 5 to 23 dBm:
rf95.setTxPower(23, false);


// ##################################################
// Start serial (pmsSerial) baud rate (9600) afor PM sensor
// ##################################################  
pmsSerial.begin(9600);

}

// ############################ PM sensor Data structure ##################################

// TX 
int16_t packetnum = 0;  // packet counter, we increment per xmission

// PM sensor Data structure
struct pms5003data {
uint16_t framelen;
uint16_t pm10_standard, pm25_standard, pm100_standard;
uint16_t pm10_env, pm25_env, pm100_env;
uint16_t particles_03um, particles_05um, particles_10um, particles_25um, particles_50um, particles_100um;
uint16_t unused;
uint16_t checksum;
};

struct pms5003data data;



// #####################################  LOOP  ##########################################

void loop()
{
// ##################################################
//  Get data for PM sensor from readPMSdata function
// ################################################## 
if (readPMSdata(&pmsSerial)) {
    // reading data was successful!

    Serial.println();
    Serial.println("---------------------------------------");
    Serial.println("Concentration Units (standard)");
    Serial.print("PM 1.0: "); Serial.print(data.pm10_standard);
    Serial.print("\t\tPM 2.5: "); Serial.print(data.pm25_standard);
    Serial.print("\t\tPM 10: "); Serial.println(data.pm100_standard);

    Serial.println("---------------------------------------");
    Serial.println("Concentration Units (environmental)");
    Serial.print("PM 1.0: "); Serial.print(data.pm10_env);
    Serial.print("\t\tPM 2.5: "); Serial.print(data.pm25_env);
    Serial.print("\t\tPM 10: "); Serial.println(data.pm100_env);


    Serial.println("---------------------------------------");
    Serial.print("Particles > 0.3um / 0.1L air:"); Serial.println(data.particles_03um);
    Serial.print("Part icles > 0.5um / 0.1L air:"); Serial.println(data.particles_05um);
    Serial.print("Particles > 1.0um / 0.1L air:"); Serial.println(data.particles_10um);
    Serial.print("Particles > 2.5um / 0.1L air:"); Serial.println(data.particles_25um);
    Serial.print("Particles > 5.0um / 0.1L air:"); Serial.println(data.particles_50um);
    Serial.print("Particles > 10.0 um / 0.1L air:"); Serial.println(data.particles_100um);
    Serial.println("---------------------------------------");

}

// ##################################################
// Call on PIN A7 to measure battery voltage
// ##################################################
float measuredvbat = analogRead(VBATPIN);
measuredvbat *= 2;    // we divided by 2, so multiply back
measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
measuredvbat /= 1024; // convert to voltage



// ##################################################
// Pack PM data and transmit to reciver
// #################################################

Serial.println("Transmitting..."); // Send a message to rf95_server
    String pm  = String(data.pm10_env);
    pm += ",";
    pm += String(data.pm25_env);
    pm += ",";
    pm += String(data.pm100_env);
    pm += ",";
    pm += String(data.pm10_standard);
    pm += ",";
    pm += String(data.pm25_standard);
    pm += ",";
    pm += String(data.pm100_standard);
    pm += ",";
    pm += String(data.particles_03um);
    pm += ",";
    pm += String(data.particles_05um);
    pm += ",";
    pm += String(data.particles_10um);
    pm += ",";
    pm += String(data.particles_25um);
    pm += ",";
    pm += String(data.particles_50um);
    pm += ",";
    pm += String(data.particles_100um);
    pm += ",";   
    pm += String(measuredvbat);
    pm += ",";

if (data.pm25_env > 16000)
    {
//      Watchdog.reset();
    Serial.println("###############SOFT RESET##########################");
    }

// convert pm data to bit16            
uint16_t pm_len = pm.length() + 1;
Serial.println("PM of:  " + pm);Serial.println(pm_len);

// convert pm data to byte
char radiopacket[pm_len];
pm.toCharArray(radiopacket, pm_len);
Serial.print("Sending "); Serial.println(radiopacket);

// Send PM data
Serial.println("Sending...");
delay(10);
rf95.send((uint8_t *)radiopacket, pm_len);

// Wait for PM data to be recived
Serial.println("Waiting for packet to complete..."); 
delay(10);
rf95.waitPacketSent();
// Now wait for a reply
uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t len = sizeof(buf);

// Get confirmation of PM data recived 
Serial.println("Waiting for reply...");
if (rf95.waitAvailableTimeout(1000))
{ 
    // Should be a reply message for us now   
    if (rf95.recv(buf, &len))
{
    Serial.print("RX reply: ");
    Serial.println((char*)buf);
    Serial.print("RSSI: ");
    Serial.println(rf95.lastRssi(), DEC);    
    }
    else
    {
    Serial.println("Receive failed");
    }
}
else
{
    Serial.println("No reply, is there a listener around?");
}

// delay(2300);
// delay(10000);



}



// ############################ PM sensor Data Function ##################################

boolean readPMSdata(Stream *s) {
if (! s->available()) {
    return false;
}

// Read a byte at a time until we get to the special '0x42' start-byte
if (s->peek() != 0x42) {
    s->read();
    return false;
}

// Now read all 32 bytes
if (s->available() < 32) {
    return false;
}
    
uint8_t buffer[32];    
uint16_t sum = 0;
s->readBytes(buffer, 32);

// get checksum ready
for (uint8_t i=0; i<30; i++) {
    sum += buffer[i];
}

/* debugging
for (uint8_t i=2; i<32; i++) {
    Serial.print("0x"); Serial.print(buffer[i], HEX); Serial.print(", ");
}
Serial.println();
*/

// The data comes in endian'd, this solves it so it works on all platforms
uint16_t buffer_u16[15];
for (uint8_t i=0; i<15; i++) {
    buffer_u16[i] = buffer[2 + i*2 + 1];
    buffer_u16[i] += (buffer[2 + i*2] << 8);
}

// put it into a nice struct :)
memcpy((void *)&data, (void *)buffer_u16, 30);

if (sum != data.checksum) {
    Serial.println("Checksum failure");
    return false;
}
// success!
return true;
}
```

## Datalogger (Receiver) 

The sketch receives PM data from another Feather M0 transceiver and writes the data to the SD card every two second 

The sketch makes use of the following tutorials by Adafruit. 
- [Feather M0 Lora](https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/overview)
- [Featherwing Adalogger](https://learn.adafruit.com/adafruit-adalogger-featherwing/overview)
- [Adafruit 128x64 OLED FeatherWing](https://learn.adafruit.com/adafruit-128x64-oled-featherwing)

Portions of the example sketches in these tutorials are piecemealed to form this sketch.

Thank you Adafruit :) 

```c++
// ############################################################################################################
// #####################################      Resiver Code       ##########################################
// ############################################################################################################
// Feather M0 (RH_RF95 915 MHz) and Featherwing Adalooger 
// -*- mode: C++ -*-
// 



#include <SD.h>
#include <SPI.h>
#include <Wire.h>
#include "RTClib.h"
#include <RH_RF95.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
 
Adafruit_SH110X display = Adafruit_SH110X(64, 128, &Wire);

// Define chipSelect
const int chipSelect = 10;

// Define Headers for file
static char header[] = {"rtctime,millis,pm10_env,pm25_env,pm100_env,pm10_standard,pm25_standard,pm100_standard,particles_03um,particles_05um,particles_10um,particles_25um,particles_50um,particles_100um,TX_batvolt,RX_batvolt"};

// Used for RTC time keeper
RTC_PCF8523 rtc;

// for feather m0 RFM9x
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

// measure battery voltage
#define VBATPIN A7

// Legal operating frequency in North America 902-928, NOTE set frequency match RX's freq!
//#define RF95_FREQ 902.0 // UBC-PM 01
//#define RF95_FREQ 907.0 // UBC-PM 02
//#define RF95_FREQ 913.0 // UBC-PM 03
//#define RF95_FREQ 918.0 // UBC-PM 04
#define RF95_FREQ 923.0 // UBC-PM 05



// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// Blinky on receipt
#define LED 13

// timekeeper
unsigned long time;




// #####################################  SET UP  ##########################################

void setup()
{ 
// ##################################################
// Start serial baud rate (57600) and RTC chip for time keeping
// ##################################################
  Serial.begin(57600);
  delay(2000);
/*
#ifndef ESP8266
  while (!Serial); // wait for serial port to connect. Needed for native USB
#endif
*/
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (! rtc.initialized() || rtc.lostPower()) {
    Serial.println("RTC is NOT initialized, let's set the time!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));


// ##################################################
// Start serial baud rate (115200) and initiate LoRa Radio
// ##################################################
  Serial.begin(115200);
/*
  while (!Serial) {     //Needed for native USB
    delay(1);
  }
*/
  display.begin(0x3C, true); // Address 0x3C default

  display.display();
  delay(1000);
  
   // Clear the buffer.
  display.clearDisplay();
  display.display();

  Serial.println("Feather LoRa RX Datalogger!");
    // text display tests
  display.setRotation(1);
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0,0);
  display.println("UBC-PM Datalogger :)");

  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);

  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
    while (1);
  }
  Serial.println("LoRa radio init OK!");
  display.println("Radio OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    display.println("setFrequency failed :(");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);


  // ##################################################  
  //SD Card: Open serial communications and wait for port to open:
  // ##################################################
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);

  /*
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB port only
  }
*/
  Serial.print("Initializing SD card...");

  // See if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    display.println("Card failed, or not present");
    // don't do anything more:
    while (1);
  }
  Serial.println("card initialized.");
  display.println("Card initialized.");


  // ##################################################
  // Call on RTC chip to create file name
  // This is also done in the loop
  // ##################################################
  DateTime now = rtc.now();
  String Filename = String(now.year());
  Filename += String(now.month());
  Filename += String(now.day());
  // Filename += "_";
  // Filename += String(now.hour());
  // Filename += String(now.minute());
  Filename += ".txt";


  // ##################################################
  // Open file, write to SD card
  // ##################################################
  File dataFile = SD.open(Filename, FILE_WRITE);
  if (dataFile) {
    dataFile.println((char*)header);
    dataFile.close();
    // print to the serial port too:
    Serial.println((char*)header);
    display.println("New file created: ");
    display.print(Filename);
    
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening .txt");
    display.println("error in creating txt file");
  }

  display.display(); // actually display all of the above

}




// #####################################  LOOP  ##########################################

void loop()
{
  display.display();
  display.setRotation(1);
  display.setTextSize(1);
  display.setTextColor(SH110X_WHITE);
  display.setCursor(0,0);
// ##################################################
// Recive and uppack data and send confirmation back
// ##################################################
  if (rf95.available())
  {
    // Should be a message for us now
    uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);
    
    if (rf95.recv(buf, &len))
    {
      digitalWrite(LED, HIGH);
      RH_RF95::printBuffer("Received: ", buf, len);
      Serial.print("Got: ");
      Serial.println((char*)buf);
      Serial.print("RSSI: ");
      Serial.println(rf95.lastRssi(), DEC);

      // Send a reply
      uint8_t data[] = "Recived PM Data :)";
      rf95.send(data, sizeof(data));
      rf95.waitPacketSent();
      Serial.println("Sent a reply");
      digitalWrite(LED, LOW);
    }
    else
    {
      Serial.println("Receive failed");
    }

  // ##################################################
  // Call on PIN A7 to measure battery voltage
  // ##################################################
  float measuredvbat = analogRead(VBATPIN);
  measuredvbat *= 2;    // we divided by 2, so multiply back
  measuredvbat *= 3.3;  // Multiply by 3.3V, our reference voltage
  measuredvbat /= 1024; // convert to voltage
  String batvolt_string = String(measuredvbat);

  // convert batvolt to bit16 
  uint16_t batvolt_len = batvolt_string.length() + 1;
  Serial.print("VBat: " ); Serial.println(batvolt_string);

  // convert time to byte
  char RX_batvolt[batvolt_len];
  batvolt_string.toCharArray(RX_batvolt, batvolt_len);
  //Serial.println((char*)batvolt_len);
  
  // ##################################################
  // Call on RTC chip to create time count (RTCtime) name
  // convert RTCtime to string 
  // ##################################################
  DateTime now = rtc.now();
  String RTCtime_string = String(now.year());
  RTCtime_string += "-";
  RTCtime_string += String(now.month());
  RTCtime_string += "-";
  RTCtime_string += String(now.day());
  RTCtime_string += "T";
  RTCtime_string += String(now.hour());
  RTCtime_string += ":";
  RTCtime_string += String(now.minute());
  RTCtime_string += ":";
  RTCtime_string += String(now.second());
  RTCtime_string += ",";

  // convert time to bit16 
  uint16_t RTCtime_len = RTCtime_string.length() + 1;
  Serial.println("Time of:  " + RTCtime_string);
  //Serial.print("RTCtime string lenght: ");Serial.println(RTCtime_len);

  // convert time to byte
  char RTCtime[RTCtime_len];
  RTCtime_string.toCharArray(RTCtime, RTCtime_len);
  //Serial.println((char*)RTCtime_len);

  // ##################################################
  // Start Milliseconds (mill_sec) from start
  // convert mill_sec to string
  // ##################################################
  time = millis();
  String mill_sec = String(time);
  mill_sec += ",";
  //Serial.println(mill_sec);
  
  // convert mill_sec to bit16 
  uint16_t mill_sec_len = mill_sec.length() + 1;
  //Serial.println("Milliseconds from start:  " + mill_sec);
  //Serial.print("Milliseconds string lenght: ");
  //Serial.println(mill_sec_len);

  // convert mill_sec to byte
  char mill[mill_sec_len];
  mill_sec.toCharArray(mill, mill_sec_len);
  //Serial.println((char*)mill);

  // ##################################################
  // Call on RTC chip to create file name
  // This is also done in the setup
  // ##################################################
  String Filename = String(now.year());
  Filename += String(now.month());
  Filename += String(now.day());
  // Filename += "_";
  // Filename += String(now.hour());
  // Filename += String(now.minute());
  Filename += ".txt";

 // ################################################## 
 // Open file, write to SD card
 // ##################################################
  File dataFile = SD.open(Filename, FILE_WRITE);
  if (dataFile) {
    display.clearDisplay();
    dataFile.print((char*)RTCtime);dataFile.print((char*)mill);dataFile.print((char*)buf);dataFile.println((char*)RX_batvolt);
    dataFile.close();
    // print to the serial port too:
    Serial.print("Wrote to SD: ");Serial.print((char*)RTCtime);Serial.print((char*)mill);Serial.print((char*)buf);Serial.println((char*)RX_batvolt);
    String str_time = (char*)RTCtime;
    int index0 = str_time.indexOf(',');
    String time_display = str_time.substring(0,index0);
    display.println(time_display);
    
    String str_data = String((char*)buf);
    int firstCommaIndex = str_data.indexOf(',');
    int secondCommaIndex = str_data.indexOf(',', firstCommaIndex+1);
    int thirdCommaIndex = str_data.indexOf(',', secondCommaIndex+1);
    int lastindex = str_data.lastIndexOf(',');

    String pm_1 = str_data.substring(0, firstCommaIndex);
    String pm_25 = str_data.substring(firstCommaIndex+1, secondCommaIndex);
    String pm_10 = str_data.substring(secondCommaIndex+1, thirdCommaIndex);
    String bat_power = str_data.substring(lastindex-4,lastindex);

    display.print("PM 1.0:  ");display.println(pm_1);
    display.print("PM 2.5:  ");display.println(pm_25);
    display.print("PM 10.0: ");display.println(pm_10);
    display.print("TXPower: ");display.println(bat_power);

    display.display();

  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening please.txt");
  }
   
  }
    display.display();

}
```

