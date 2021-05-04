Code
=====

PM Sensor (Transceiver)
+++++++++++++++++++++++++


.. code-block:: c++

    #include <SPI.h>
    #include <RH_RF95.h>


    // for feather m0 */
    #define RFM95_CS 8
    #define RFM95_RST 4
    #define RFM95_INT 3

    // measure battery voltage
    #define VBATPIN A7

    // PM  
    #define pmsSerial Serial1

    // TX 
    // Change to 434.0 or other frequency, must match RX's freq!
    #define RF95_FREQ 915.0 // UBC-PM 01
    // #define RF95_FREQ 925.0 // UBC-PM 02

Datalogger (Receiver) 
+++++++++++++++++++++++++

.. code-block:: c++

    #include <SD.h>
    #include <SPI.h>
    #include "RTClib.h"
    #include <RH_RF95.h>

    // Define chipSelect
    const int chipSelect = 10;

    // Define Headers for file
    static char header[] = {"rtctime,millis,pm10_env,pm25_env,pm100_env,pm10_standard,pm25_standard,pm100_standard,particles_03um,particles_05um,particles_10um,particles_25um,particles_50um,particles_100um,TX_batvolt,RX_batvolt"};


