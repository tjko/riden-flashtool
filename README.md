# riden-flashtool
Riden RD6006(P)/RD6012/RD6018 Firmware Flash Tool

This script allows updating firmware on Riden RD60xx power supply units.

NOTE! This script is based on observing the USB traffic between the "official" (Windows)
firmware update program and the power supply module. There is no guarantees that this
works 100% of the time. However it's been successfully used with several Riden RD6006
modules to update firmware from a Linux computer.

## Requirements

Script has been developed/tested under Linux (Raspberry Pi), but should work
on other platforms as long as there is Python 3 and "serial" module installed.

* Python 3
  * serial (pySerial) module

## Supported models

Currently script has been validated with following models:

Make|Model|Info
----|-----|----
RIDEN|RD6006|Tested with Bootloader V1.09
RIDEN|RD6006P|Tested with Bootloader V1.12
RIDEN|RD6012|Tested with Bootloader V1.09
RIDEN|RD6012P|Tested with Bootloader V1.14
RIDEN|RD6018|Tested with Bootloader V1.10
RIDEN|RD6018W|Tested with Bootloader V1.12
RIDEN|RD6024|Tested with Bootloader v1.38

## Updating Firmware

First, obtain firmware file (Note, this tool does not validate data being flashed
to device, so make sure correct firmware image is being used!)

Next, connect power supply module to computer (and note the serial port it gets assigned).

__NOTE, it is recommended to connect the power supply directly to a computer, as using
a USB hub can lead to flashing process to fail.__

Update firmware by running: _flash-rd.py \<serialport\> \<filename\>_




For example:

```
# ./flash-rd.py /dev/ttyUSB0 RD60062_V1.32.bin
Serial port: /dev/ttyUSB3 (115200bps)
Firmware size: 109888 bytes
Check if device is in bootloader mode...No
Found device (using Modbus): RD6006 (60062) v1.26
Rebooting to bootloader mode...
Device information (from bootloader):
    Model: RD6006 (60062)
 Firmware: v1.26
      S/N: 000xxxxx
Updating firmware........................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................b'OK'
Firmware update complete.
```

If you have trouble starting the update and you see following:

```
Check if device is in bootloader mode...No
No response from device.
```

Check device settings and make sure "Interface" is set to "USB".
Alternatively, set device manually to bootloader mode first.


## Command Line Arguments

```
usage: flash-rd.py [-h] [--speed SPEED] port [firmware]

Riden RD60xx Firmware Flash Tool

positional arguments:
  port           Serial port
  firmware       Firmware file. If not specified, only reboot to bootloader
                 mode and print version of Riden device

optional arguments:
  -h, --help     show this help message and exit
  --speed SPEED  Serial port speed
```


## Recovering from a failed firmware update

Failed firmware upgrade can lead unit not booting up (or flash memory getting
corrupted by some other way).

In case unit doesn't boot normally, it is usually still possible to recover unit
by re-flashing the firmware.

Recovering firmware:
1. Boot unit to bootloader mode manually: Press and hold "ENTER" button when powering on the unit.
2. Run the firmware update again.



