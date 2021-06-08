

# The particulate matter sensor

The UBC AQ instrument uses the [plantower pms5003](http://www.plantower.com/en/content/?108.html) air quality sensor. The sensor is considered an optical particle counter.

![Principle of optical particle counter OPC](_static/img/opc_drawing.png)

credit: Weber et al., 2010

  
OPC senors work by......

This OPC sensor has become popular and is used by [PurpleAir](https://www2.purpleair.com/?gclid=Cj0KCQjwh_eFBhDZARIsALHjIKflOmByuJ0A_mMy2lciYPGGEEeVXIl6s4t98ah8vJy6T58homDww-0aAvuMEALw_wcB) and others


## Build
To treat the PM sensor as radiosondes/dropsonde requires the date to be broadcast remotely. 
This is made possible by using a Long Range (LoRa) packet radio transceiver. The transceiver
used for this project is the Adafruit Feather M0 Radio with LoRa Radio Module (link). 
For legal (link)use in North America, the Feather M0 broadcast frequency is set between (902 - 928 MHz).


### PM Sensor (Transceiver)

#### Top View
![UBC PM Sensor](_static/img/ubc_pm1.jpeg)

#### Side View
![UBC PM Sensor](_static/img/ubc_pm2.jpeg)

### Datalogger (Receiver) 

![UBC PM Sensor](_static/img/ubc_rx1.jpeg)

