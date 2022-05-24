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
//#define RF95_FREQ 907.0 // UBC-PM 02
//#define RF95_FREQ 913.0 // UBC-PM 03
#define RF95_FREQ 918.0 // UBC-PM 04
//#define RF95_FREQ 923.0 // UBC-PM 05
//#define RF95_FREQ 925.0 // UBC-PM 06



// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

// timekeeper
unsigned long prMillis;

// #####################################  SET UP  ##########################################

void setup() 
{
// ##################################################
// Start serial baud rate (115200) and initiate LoRa Radio
// ##################################################
// Wait two second for sensor to boot up!
delay(2000);

pinMode(RFM95_RST, OUTPUT);
digitalWrite(RFM95_RST, HIGH);

Serial.begin(115200);


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
    prMillis = millis() / 1000;
    byte sec = prMillis % 60;
    prMillis = prMillis / 60;
    byte min = prMillis % 60;
    prMillis = prMillis / 60;
    byte hrs = prMillis % 24;
    String hhmmss = String(hrs) +":" + String(min) +":" + String(sec);

Serial.println("Transmitting..."); // Send a message to rf95_server
 //   time = millis();
    String pm = hhmmss;
    pm += ",";
    pm += String(data.pm10_env);
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
