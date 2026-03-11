# linux telemetry

python script that reads cpu and memory info from /proc and sends it to an arduino over serial

the arduino can then display it on leds or whatever. i have mine showing cpu load on 5 leds

## requirements

```
pip install pyserial
```

## how to run

```
python3 monitor.py
```

if you have an arduino connected:
```
python3 monitor.py --port /dev/ttyUSB0
```

## notes
- only tested on ubuntu, might not work on other distros
- the cpu % calculation is probably slightly off, will fix
- network monitoring doesnt work great, sometimes shows negative values (bug)
- arduino code is in the firmware folder
