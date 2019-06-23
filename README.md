# ADB SERVICE
*** please notice that is still in the development phase

ADB Service allows you to interact with your decoder device. I tested it with ADB NCP4740SF - [WIFI PREMIUMBOX+](https://ncplus.pl/oferta/dekodery/wifi-premiumbox). If you have different type of ADB decoder, you can check if my solution works to you and let me know.

## INSTALLATION
To get started:

1. put all the files from `/custom_components/adb_service/` here: `<config directory>/custom_components/adb_service/`
2. setup configuration.yaml according to configuration section
3. restart your home assistant
4. check your states section - there should be sensor.adb

## CONFIGURATION

Just add it to your configuration.yaml

```yaml
adb_service:
  host: 192.168.0.174
```

### CONFIGURATION VARIABLES

key | description  
:--- | :---  
host(required) | IP address of your device

#### HOW TO GET IP ADDRESS
You should check your DHCP State of your router. I recommend to setup it as static IP.
Your device should be available on port :8080.
For example check the `http://<ip>:8080/system/version` - this page should returns similar response:

```json
{"internal_version":"1.8.11","external_version":"1.1.8","manufacturer":"Advanced Digital Broadcast","model":"NCP4740SF","friendly_name":"Główny Dekoder","release":"2015.09.01"}
```

## AVAILABLE SERVICES
### adb_service.press

It allows you to send any key to your device. You have to pass as a parameter which key want to press. As a default this is standby button.

#### PARAMS

key | description  
:--- | :---  
key | Name of key to send

#### AVAILABLE KEYS

The naming convetion to send key to device API is: `Key<button>`. You can pass it without Key prefix.

- StandBy
- ProgramDown
- ProgramUp
- Back
- VolumeUp
- VolumeDown
- Mute
- Guide
- Info
- Menu
- Exit
- Left
- Right
- Down
- Up
- Play
- Pause
- Rewind
- FForward
- Record
- Stop
- Ok
- Zero
- One
- Two
- Three
- Four
- Five
- Six
- Seven
- Eight
- Nine
- At 
- Red
- Green
- Yellow
- Blue
- OPTS
- Setup
- Lang
- Mode
- RecList
- TVRadio

To press channel 11 You have call the service twice with key One