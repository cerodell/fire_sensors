// ############################################################################################################
// #####################################      Resiver Code       ##########################################
// ############################################################################################################
// Feather M0 (RH_RF95 915 MHz) and Featherwing Adalooger 
// Port: 143401
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


RTC_PCF8523 rtc;
const int chipSelect = 10;
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

/* for feather m0 RFM9x */
#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// Blinky on receipt
#define LED 13


// #####################################  SET UP  ##########################################

void setup()
{
  Serial.begin(57600);

#ifndef ESP8266
  while (!Serial); // wait for serial port to connect. Needed for native USB
#endif

  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (! rtc.initialized() || rtc.lostPower()) {
    Serial.println("RTC is NOT initialized, let's set the time!");
    // When time needs to be set on a new device, or after a power loss, the
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

    
  pinMode(LED, OUTPUT);
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);

  Serial.begin(115200);
  while (!Serial) {
    delay(1);
  }
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


  
  //SD Card: Open serial communications and wait for port to open:
  pinMode(8, OUTPUT);
  digitalWrite(8, HIGH);
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB port only
  }

  Serial.print("Initializing SD card...");

  // See if the card is present and can be initialized:
  if (!SD.begin(chipSelect)) {
    Serial.println("Card failed, or not present");
    // don't do anything more:
    while (1);
  }
  Serial.println("card initialized.");
}




// #####################################  LOOP  ##########################################

void loop()
{

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

  // Get time from RTC chip

    DateTime now = rtc.now();

    Serial.print(now.year(), DEC);
    Serial.print('/');
    Serial.print(now.month(), DEC);
    Serial.print('/');
    Serial.print(now.day(), DEC);
    Serial.print(" (");
    Serial.print(daysOfTheWeek[now.dayOfTheWeek()]);
    Serial.print(") ");
    Serial.print(now.hour(), DEC);
    Serial.print(':');
    Serial.print(now.minute(), DEC);
    Serial.print(':');
    Serial.print(now.second(), DEC);
    Serial.println();

  // Open file, write to SD card
  File dataFile = SD.open("blah2.txt", FILE_WRITE);

  if (dataFile) {
    dataFile.println((char*)buf);
    dataFile.close();
    // print to the serial port too:
    Serial.println((char*)buf);
  }
  // if the file isn't open, pop up an error:
  else {
    Serial.println("error opening blah2.txt");
  }
   
  }
  
}
