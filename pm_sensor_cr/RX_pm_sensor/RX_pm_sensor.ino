// ############################################################################################################
// #####################################      Resiver Code       ##########################################
// ############################################################################################################
// Feather M0 (RH_RF95 915 MHz) and Featherwing Adalooger 
//
// The sketch receives PM data from another Feather M0 transceiver and writes the data to the SD card every one second 
// -*- mode: C++ -*-
// 
// The sketch makes use of the following tutorials by Adafruit. 
// Feather M0 Lora: https://learn.adafruit.com/adafruit-feather-m0-radio-with-lora-radio-module/overview
// Featherwing Adalooger: https://learn.adafruit.com/adafruit-adalogger-featherwing/overview
// Portions of the example sketches in these tutorials are piecemealed to form this sketch.

// Thank you Adafruit :) 


#include <SD.h>
#include <SPI.h>
#include "RTClib.h"
#include <RH_RF95.h>

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

// Change to 434.0 or other frequency, must match RX's freq!
// #define RF95_FREQ 915.0 // UBC-PM 01
#define RF95_FREQ 925.0 // UBC-PM 02


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

// rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));


// ##################################################
// Start serial baud rate (115200) and initiate LoRa Radio
// ##################################################
  Serial.begin(115200);
/*
  while (!Serial) {     //Needed for native USB
    delay(1);
  }
*/

  delay(100);

  Serial.println("Feather LoRa RX Test!");

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
    // don't do anything more:
    while (1);
  }
  Serial.println("card initialized.");


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
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening .txt");
  }
}




// #####################################  LOOP  ##########################################

void loop()
{
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
    dataFile.print((char*)RTCtime);dataFile.print((char*)mill);dataFile.print((char*)buf);dataFile.println((char*)RX_batvolt);
    dataFile.close();
    // print to the serial port too:
    Serial.print("Wrote to SD: ");Serial.print((char*)RTCtime);Serial.print((char*)mill);Serial.print((char*)buf);Serial.println((char*)RX_batvolt);
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening please.txt");
  }
   
  }
  
}
