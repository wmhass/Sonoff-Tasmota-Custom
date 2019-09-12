# Sonoff Tasmota Custom Firmware

[Sonoff-Tasmota-Custom](https://github.com/wmhass/Sonoff-Tasmota-Custom) is a modification for [Sonoff-Tasmota](https://github.com/arendst/Sonoff-Tasmota) to add a basic functionalities that are not included in the original repository and custom settings.

This repository is for developing new custom features for Sonoff-Tasmota.

## Table of Contents

* [Installation](#installation)
* [Send configurations to the Sonoff](#send-configurations-to-the-sonoff)
* [Useful and most common commands](#useful-and-most-common-commands)
* [Modifications to Sonoff-Tasmota](#modifications-to-sonoff-tasmota)
* [Initial setup flow](#initial-setup-flow)

## Installation ##

### Hardware requirements:
1. FTDI Adapter
2. Header Pins (You might need to solder them on the Sonoff in order to connect it to the FTDI Adapter)

### Steps
1. Install `Atom` and `PlatformIO`
2. Make sure you can run the `PIO Build` target to build the firmware.
  - This step will build the firmware and save it into `.pio/build/sonoff/framework.bin`
3. Connect the FTDI Adapter to your computer and check if the adapter is recognized. One way to double check it is to open the `Serial Monitor` if you are using the `Atom/PlatformIO` IDE  and see if something like `/dev/cu.usbserial-XXXXX` appears in the list of ports.
4. Connect the Sonoff to FTDI:
    1. Connect the FTDI VCC to the Sonoff VCC pin
    1. Connect the FTDI GND to the Sonoff GND pin
    1. Connect the FTDI RX to the Sonoff TX
    1. Connect the FTDI TX to the Sonoff RX
5. Put the Sonoff Device in "Flash mode":
    1. Disconnect the FTDI from your computer
    1. Press and hold the Sonoff button
    1. While holding the Sonoff button, connect the FTDI to your computer
    1. Wait for 5 seconds and release the Sonoff button.
    1. Done, now the Sonoff device is in Flash mode and prepared to receive a new firmware
6. Upload the firmware you built in the step #2: Although `PlatformIO` offers an `Upload` option, sometimes it does not work, so we use the `esptool` to do so. You can open the terminal inside the IDE (or whatever) and run `esptool.py --port /dev/cu.usbserial-AK0730II write_flash -fs 1MB -fm dout 0x0 .pio/build/sonoff/firmware.bin`
    1. Replace `cu.usbserial-AK0730II` by the name of your Port
7. Done, now disconnect the FTDI and connect it again to your computer and you should be good to go. In order to test if every thing worked, open the `Serial Monitor`, type `power` and press `Enter`. You should see an output with the status of the Sonoff: `stat/Sonoff_xxxxxx/RESULT = {"POWER":"ON"}`

Note: After you upload the firmware, it is nice to run a command to reset it to the initial configurations, just to make sure your device is not carry any configuration. In order to do that follow these steps:
  1. Connect the Sonoff to the FTDI adapter and connect the FTDI adapter to your computer
  2. Open the `Serial Monitor` by selecting your FTDI in the list of ports. In the serial monitor, type `reset 2`. You might see an output like this: `22:21:49 MQT: stat/Sonoff_xxxxxx/RESULT = {"Reset":"Erase, Reset and Restarting"}` then the Sonoff device will restart.

---

## Send configurations to the Sonoff ##

For a complete list of commands, check the [Sonoff Tasmota Commands original documentation](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands)

### Introduction

After you upload a new firmware and reset it to the initial configurations, when you turn on the Sonoff device, it will create a WiFi network with an `SSID` that might look like `Sonoff_xxxxxx-xxxx`. Now, the device is ready to receive new configurations.

### Important configurations

The next steps will be to connect the Sonoff to a wifi network, that means you need to set an ssid and a password (if network is protected) to it.

Also, you might want to connect your Sonoff to a MQTT server. You can set a mqtt host, a mqtt port, a mqtt user and a mqtt password.

### Sending configurations and commands to the Sonoff

There are three ways you can set configurations to the Sonoff:
1. From the Serial monitor
2. Making a HTTP Request call to the device IP address
3. MQTT

One command is executed per message. There is a way called "Backlog" that allows sending more than one command at once, but we will talk about it later in this topic. A command usually looks like this: "Command value". For example, if you want to set the ssid name to the device, you would use `ssid my_wifi_name`.

**If the Sonoff device is connected to a MQTT Server, every time a command is executed either by serial monitor or by HTTP requests, it will post a MQTT message to `stat/Sonoff_xxxxxx/RESULT`. In addition to that, some commands may post additional messages to other topics, such as the `power` commands, that retrieves the status of a relay**

#### Executing commands through Serial Monitor

If you want to send commands through the `Serial Monitor`, you would open the monitor and type: `ssid my_wifi_name`. Every time you send a command, the Sonoff Tasmota firmware will save the configuration and reset the device.

#### Executing commands through HTTP Requests

If you want to send commands through an HTTP request call, you first should now the IP address of the Sonoff in the network. If the Sonoff is in the setup mode and you are connected to its wifi network, the IP address will be `192.168.4.1`, otherwise you should know the Sonoff IP address in the current network (You can figure this out by checking typing `status 5` in the `Serial Monitor`).

Let's say you want to connect the Sonoff device to a wifi network called `my_wifi_name`, this is how you would send a command to the Sonoff through an HTTP Request call: `http://192.168.4.1/cm?cmnd=ssid%20my_wifi_name`. Note that there is a `%20` character between the `ssid` word and the wifi name. This is used because you need to escape the blank space there.

#### Executing commands through MQTT

To send commands and view responses you'll need an MQTT client.

Commands over MQTT are issued by using `cmnd/%topic%/<command> <parameter>`. If there is no `<parameter>` (an empty MQTT message/payload), a query is sent for current status of the `<command>`.

Most of times, the response of the MQTT commands will be published to the topic `stat/Sonoff_xxxxxx/RESULT`. There are some arbitrary exception such as the `status`, that will post its response to the topic `stat/Sonoff_xxxxxx/STATUS`. (I could not find a logic behind this topic changes, so you might have to use a MQTT client to test the commands you are going to use and see to what topic their response will be published to by subscribing to the `stat/Sonoff_xxxxxx/#`)

See [MQTT](https://github.com/arendst/Sonoff-Tasmota/wiki/MQTT) wiki to find out more.

#### Executing multiple commands at once (Backlog)

As mentioned before, every time a command is sent, the Sonoff will save the configurations and then will reset. But actually there is a way to send multiple commands, so it will only reset after setting all the passed configurations, and it is called `Backlog`. Basically, you just have to add the `Backlog` word at the beginning of the command. As an example, let's say we want to set the ssid name and the wifi password at once:
- From the terminal: `Backlog SSID my_wifi_name;Password 1234;Power On`
- From the HTTP Request call: `http://192.168.4.1/cm?cmnd=Backlog%20Ssid%20my_wifi_name%3BPassword%201234` (Note the `%3B` between the `my_wifi_name` and the `Password` word. This is the `;` character URL escaped. This character is used to separate commands.)
- An example of a more complex command that sets mqtt and wifi configuration: `http://192.168.4.1/cm?cmnd=Backlog%20MqttPort%201883%3BMqttHost%20192.168.0.108%3BSSId%20Lilo_escritorio%3BPassword%201357924680%3BGPIO14%203`

**When you execute multiple commands at once, the Sonoff device will post one message in the topic `stat/Sonoff_xxxxxx/RESULT` for each command it executed**

## Initial setup flow ##
When you are setting up the Sonoff for the first time, there are a few things you might want to configure:
- Set a `ssid` and `password` to connect the Sonoff to a wifi network
- Set `mqtthost` and `mqttport` to connect the SOnoff to a mqtt server
- Set a `timezone` according to where the device is located
- Disable the timer feature: Just to make sure that there are none timers active

## Useful and most common commands ##

For a complete list of commands, check the [Sonoff Tasmota Commands original documentation](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands)

### Restart Sonoff
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

- Serial Command: `restart 1`
- HTTP Request: http://192.168.0.137/cm?cmnd=restart%201
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/restart` / Payload: `1`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT`

Output:
```
{
  "Restart":"Restarting"
}
```

### Reset Sonoff
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/STATUS5`

- Serial Command: `status 5`
- HTTP Request: http://192.168.0.137/cm?cmnd=status%205
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/status`
  - MQTT response topic: `stat/Sonoff_xxxxxx/STATUS5`

There are other status information you can retrieve just by changing the code number (in the example above, the code `5` is used). Check more commands in the [Sonoff original documentation](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands)

Output:
```
{
   "StatusNET":{
      "Hostname":"Sonoff_xxxxxx-3616",
      "IPAddress":"192.168.0.131",
      "Gateway":"192.168.0.1",
      "Subnetmask":"255.255.255.0",
      "DNSServer":"192.168.0.1",
      "Mac":"DC:4F:22:43:2E:20",
      "Webserver":2,
      "WifiConfig":4
   }
}
```

### Check the time of the Sonoff
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

**Important note:**: Sonoff reset the date every time it reboots and fetches the new time using a NTP server. Check the [Sonoff original documentation](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands) to know how to change the address of the default NTP server.

- Serial Command: `time`
- HTTP Request: http://192.168.0.137/cm?cmnd=time
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/time`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT`

Output
```
{
  "Time":"2019-09-12T14:23:03"
}
```

### Set the timezone to the Sonoff
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

Set timezone offset from UTC in HOURS. The example here is assuming you want to set the Timezone to `-03:00`.

- Serial Command: `timezone -3`
- HTTP Request: http://192.168.0.137/cm?cmnd=timezone%20-3
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/timezone` / Payload: `-3`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT`

Output
```
{
  "Timezone":"-03:00"
}
```

### Check the Sonoff state
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

- Serial Command: `state`
- HTTP Request: http://192.168.0.137/cm?cmnd=state
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/state`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT`

Output:
```
{
   "Time":"2019-09-12T15:15:30",
   "Uptime":"0T00:11:29",
   "UptimeSec":689,
   "Heap":26,
   "SleepMode":"Dynamic",
   "Sleep":50,
   "LoadAvg":19,
   "MqttCount":1,
   "POWER":"ON",
   "Wifi":{
      "AP":1,
      "SSId":"Lilo_escritorio",
      "BSSId":"AC:84:C6:47:73:44",
      "Channel":10,
      "RSSI":100,
      "LinkCount":1,
      "Downtime":"0T00:00:04"
   }
}
```

### Check the Sonoff status:
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/STATUS`

- Serial Command: `Status`
- HTTP Request: http://192.168.0.137/cm?cmnd=status
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/status`
  - MQTT response topic: `stat/Sonoff_xxxxxx/STATUS` / Payload: Same as the output described below
Output:
```
{
 "Status":{
    "Module":4,
    "FriendlyName":[
       "Sonoff"
    ],
    "Topic":"Sonoff_xxxxxx",
    "ButtonTopic":"0",
    "Power":0,
    "PowerOnState":3,
    "LedState":1,
    "SaveData":1,
    "SaveState":1,
    "SwitchTopic":"0",
    "SwitchMode":[
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0
    ],
    "ButtonRetain":0,
    "SwitchRetain":0,
    "SensorRetain":0,
    "PowerRetain":0
 }
}
```

### Set WiFI+MQTT configuration
As mentioned before in the `Backlog` section, the Sonoff device will post one MQTT message for each command it executed to the tpoic `stat/Sonoff_xxxxxx/RESULT`.

- Serial Command: `Backglog ssid Lilo_escritorio;password 1357924680;mqtthost 192.168.0.108;mqttport 1883;`
- HTTP Request: http://192.168.0.137/cm?cmnd=Backlog%20MqttPort%201883%3BMqttHost%20192.168.0.108%3BSSId%20Lilo_escritorio%3BPassword%201357924680 (Note that the empty spaces and the `;` characters are escaped)

Output (The device will reset after sending the response):
```
{
  "WARNING":"Enable weblog 2 if response expected"
}
```

### Check relay state
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/POWER`

Depending on the Sonoff model, it may have more than only one Relay
- Serial Command: `power 1`
- HTTP Request: http://192.168.0.137/cm?cmnd=power1
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/power`
  - MQTT response topic: `stat/Sonoff_xxxxxx/POWER` / Payload: `ON` or `OFF`.
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below.
Output:
```
{
  POWER: "ON"
}
```

### Turn on/off relay
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/POWER`

Depending on the Sonoff model, it may have more than only one Relay
 - Serial Command: `power1 1` (or `0` to turn it off)
 - HTTP Request: http://192.168.0.137/cm?cmnd=power1%201 to turn on and http://192.168.0.137/cm?cmnd=power1%200 to turn off (Note that the empty space is escaped by using `%20`)
 - MQTT command message topic: `cmnd/Sonoff_xxxxxx/power` / Payload: `1` (or `0` to turn it off)
   - MQTT response topic: `stat/Sonoff_xxxxxx/POWER` / Payload: `ON` or `OFF`.
   - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below.
Output:
```
{
 POWER: "ON"
}
```

### Fetch list of timers
**Important note:**: The first field in the response JSON called `Timers` indicates if the timer feature is enabled (`on`) or disabled (`off`).

The Sonoff Tasmota firmware provides `16` programmable timers. The response JSON separates the timers in chunks of `4`. For more informations about timers, check the original documentation here: [https://github.com/arendst/Sonoff-Tasmota/wiki/Commands#timers](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands#timers)

MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

- Serial Command: `timers`
- HTTP Request: http://192.168.0.137/cm?cmnd=timers
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/timers`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below, but each `Timersx` chunk will be published in a separate message.

Output:
```
{
   "Timers":"OFF",
   "Timers1":{
      "Timer1":{
         "Arm":0,
         "Mode":0,
         "Time":"00:00",
         "Window":0,
         "Days":"0000000",
         "Repeat":0,
         "Output":1,
         "Action":0
      },
      "Timer2":{
         "Arm":0,
         "Mode":0,
         "Time":"00:00",
         "Window":0,
         "Days":"0000000",
         "Repeat":0,
         "Output":1,
         "Action":0
      },
      "Timer3":{
         ...
      },
      "Timer4":{
         ...
      }
   },
   "Timers2":{
      "Timer5":{
         "Arm":0,
         "Mode":0,
         "Time":"00:00",
         "Window":0,
         "Days":"0000000",
         "Repeat":0,
         "Output":1,
         "Action":0
      },
      "Timer6":{
         ...
      },
      "Timer7":{
         ...
      },
      "Timer8":{
         ...
      }
   },
   "Timers3":{
      "Timer9":{
         ...
      },
      "Timer10":{
         ...
      },
      "Timer11":{
         ...
      },
      "Timer12":{
         ...
      }
   },
   "Timers4":{
      "Timer13":{
         ...
      },
      "Timer14":{
         ...
      },
      "Timer15":{
         ...
      },
      "Timer16":{
         ...
      }
   }
}
```

### Enable/Disable Timer Feature
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

- Serial Command: `timers 1` to enable and `timers 0` to disable
- HTTP Request: http://192.168.0.137/cm?cmnd=timers%201 to enable and http://192.168.0.137/cm?cmnd=timers%200 to disable (Note that the empty space is escaped by using `%20`)
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/timers` / Payload: `1` to enable and `0` to disable
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below, but each key (`Timers` and `Timersx`) chunk will be published in a separate message.

Output (The output JSON format is the same as the fetch operation, so the representation here was simplified by using `...` for better readability):
```
{
   "Timers":"OFF",
   "Timers1":{
      ...
   },
   "Timers2":{
      ...
   },
   "Timers3":{
      ...
   },
   "Timers4":{
      ...
   }
}
```

### Setup timer
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

For more information about what each timer field means, check the original documentation here: [https://github.com/arendst/Sonoff-Tasmota/wiki/Commands#timers](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands#timers)

- Serial Command: `Timer1 {"Arm":1,"Time":"02:23","Window":0,"Days":"--TW--S","Repeat":1,"Output":1,"Action":1}`
- HTTP Request: http://192.168.0.137/cm?cmnd=Timer1%20{%22Arm%22:1,%22Time%22:%2202:23%22,%22Window%22:0,%22Days%22:%22--TW--S%22,%22Repeat%22:1,%22Output%22:1,%22Action%22:1}
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/timer` / Payload: `{"Arm":1,"Time":"02:23","Window":0,"Days":"--TW--S","Repeat":1,"Output":1,"Action":1}`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below
Output:
```
{
  "Timer1":{
     "Arm":1,
     "Mode":0,
     "Time":"02:23",
     "Window":0,
     "Days":"0011001",
     "Repeat":1,
     "Output":1,
     "Action":1
  }
}
```

### Setup Sonoff GPIOs module
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/RESULT`

This configurations will set the kind of sensor that will be connected to a specific `GPIO`. For this example, we will set the `GPIO14` to be used with a `SI7021`, which is a Sonoff Temperature&Humidity sensor. To check the complete list of supported sensors, go to the Sonoff device web panel configuration: [http://192.168.0.137/md](http://192.168.0.137/md)

- Serial Monitor command: `Backglog GPIO14 3`
- HTTP Request: http://192.168.0.137/cm?cmnd=GPIO14%203 (Note that the empty space is escaped `%20`)
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/gpio14` / Payload: `3`
  - MQTT response topic: `stat/Sonoff_xxxxxx/RESULT` / Payload: Same as the output described below

Output: (The device will reset after sending the response)
```
{
  "GPIO1":"0 (None)",
  "GPIO3":"0 (None)",
  "GPIO4":"0 (None)",
  "GPIO14":"3 (SI7021)"
}
```

### Check current sensor value
MQTT topic output after executing command from any interface (mqtt, web or serial): `stat/Sonoff_xxxxxx/STATUS8`

For more information about more status information, check the original documentation here: [https://github.com/arendst/Sonoff-Tasmota/wiki/Commands](https://github.com/arendst/Sonoff-Tasmota/wiki/Commands)

- Serial Monitor command: `status 8`
- HTTP Request: http://192.168.0.137/cm?cmnd=status%208 (Note that the empty space is escaped `%20`)
- MQTT command message topic: `cmnd/Sonoff_xxxxxx/status` / Payload: `8`
  - MQTT response topic: `stat/Sonoff_xxxxxx/STATUS8` / Payload: Same as the output described below

Output:
```
{
   "StatusSNS":{
      "Time":"2019-09-10T21:42:17",
      "SI7021":{
         "Temperature":25.1,
         "Humidity":63.7
      },
      "TempUnit":"C"
   }
}
```

## Modifications to Sonoff Tasmota ##
- Added a wifi scanner API to `xdrv_01_webserver.ino`
- Added a new `upload.py` script that only uploads an existent firmware without build it again
- Using `core_2_4_2` as the `core_active`
