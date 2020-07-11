# riden-flashtool
Riden RD6006 Firmware Flash Tool

This script allows updating firmware on Riden RD60xx power supply units.

NOTE! This script is based on observing the USB traffic between the "official" (Windows)
firmware update program and the power supply module. There is no guarantees that this
works 100% of the time. However it's been successfully used with several Riden RD6006
modules to update firmware from a Linux computer.

## Requirement

Script has been developed/tested under Linux (Raspberry Pi), but should work
on other platforms as long as there is Python 3 and "serial" module installed.

* Python 3
* serial (pySerial) module

## Supported models

Currently script has been validated with following models:

Make|Model|Info
----|-----|----
RIDEN|RD6006|Tested with Bootloader V1.09


## Updating Firmware

First, obtain firmware file (Note, this tool does not validate data being flashed
to device, so make sure correct firmware image is being used!)

Next, connect power supply module to computer (and note the serial port it gets assigned).

Update firmware by running flash-rd.py <serialport> <filename>.

For example:

```
# ./flash-rd.py /dev/ttyUSB0 RD60062_V1.32.bin
Serial port: /dev/ttyUSB0
Firmware size: 113472 bytes
Check if device is in bootloader mode...
Not in bootloader mode.
Found device:
 Model: RD6006 (60062)
 Firmware: v1.25
Rebooting to boot mode...
Updating firmware................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................................b'OK'
Firmware update complete.
```

## Command Line Arguments

```
usage: flash-rd.py [-h] [--speed SPEED] [--address ADDRESS] port firmware

Riden RD60xx Firmware Flash Tool

positional arguments:
  port               Serial port
  firmware           Firmware file

optional arguments:
  -h, --help         show this help message and exit
  --speed SPEED      Serial port speed
```


## Recovering from a failed firmware update

In case unit doesnt boot normally, if firmware update has failed earlier or
flash memory is corrupt for some reason. It is usually still possible to recover
assuming bootloader is still intact by forcing unit to boot into bootloader.

To enter bootloader mode manually:  press and hold "ENTER" button when powering on the unit.

(unit should display something like "Bootloader V1.09" when its booted up into bootloader mode)

