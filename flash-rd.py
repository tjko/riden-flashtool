#!/usr/bin/env python3
#
# flash-rd.py - Riden RD60xx Firmware Flash Tool
#
# Copyright (C) 2020 Timo Kokkonen <tjko@iki.fi>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import argparse
import serial
from time import sleep

supported_models = [ 60062 ]
verbose_mode = 0


def read_reply(serial, count):
    if (verbose_mode):
        print("Waiting data...")
    r = serial.read(count)
    if (verbose_mode):
        print("Read: %d: %s" % (len(r),r))
    return r

def write_string(serial, s):
    if (verbose_mode):
        print("Write: %d: %s" % (len(s),s))
    r = serial.write(s)
    return r

def update_firmware(serial, firmware):
    write_string(serial, b'upfirm\r\n')
    r = read_reply(serial, 6)
    if (r != b'upredy'):
        print("Failed to initiate flashing: %s" %(r))
        return 1
    print("Updating firmware...", end="", flush=True)
    pos = 0
    while (pos < len(firmware)):
        buf = firmware[pos:pos+64]
        write_string(serial, buf)
        r = read_reply(serial, 2)
        if (r != b'OK'):
            print("Flash failed: %s" % (r))
            return 2
        print(".", end="", flush=True)
        pos += 64
    print(r)
    return 0


####################################################################################

# parse command-line arguments

parser = argparse.ArgumentParser(description='Riden RD60xx Firmware Flash Tool')
parser.add_argument('port', help='Serial port')
parser.add_argument('firmware', help='Firmware file')
parser.add_argument('--speed', type=int, default=115200, help='Serial port speed')
parser.add_argument('--bootloader', action='store_true', help='Set unit to booaloader mode only.')
args = parser.parse_args()


# open serial connection

print("Serial port: %s (%dbps)" % (args.port, args.speed))
serial = serial.Serial(port=args.port, baudrate=args.speed, timeout=2)


# read firmware file
try:
    f = open(args.firmware, 'rb')
except:
    exit("Cannot open file: %s" % (args.firmware))
firmware = f.read()
f.close()
print("Firmware size: %d bytes" % (len(firmware)))



print("Check if device is in bootloader mode...", end="", flush=True)
write_string(serial, b'queryd\r\n')
res=read_reply(serial, 4)
serial.timeout=5;
if (res == b'boot'):
    print("Yes")
else:
    print("No")

    # try modbus query (read registers 0-3)...
    write_string(serial, b'\x01\x03\x00\x00\x00\x04\x44\x09')
    res=read_reply(serial, 13)
    if (len(res) == 0):
        exit("No response from device.")
    if (len(res) != 13 or res[0] != 0x01 or res[1] != 0x03 or res[2] != 0x08):
        exit("Invalid response received: %s" % (res))

    model = (res[3] << 8 | res[4]);
    print("Found device (using Modbus): RD%d (%d) v%0.2f" % (model/10,model,res[10]/100))

    print("Rebooting to bootloader mode...")
    # try modbus write to register 0x100 (value 0x1601)...
    write_string(serial, b'\x01\x06\x01\x00\x16\x01\x47\x96')
    res=read_reply(serial, 1)
    if (res != b'\xfc'):
        exit("Failed to reboot device.")
    sleep(3)



# query device information from bootloader

write_string(serial, b'getinf\r\n')
res=read_reply(serial,13)
if (len(res) == 0):
    exit("No response fro bootloader")
if (len(res) != 13 or res[0:3] != b'inf'):
    exit("Invalid response from bootloader: %s" % (res))

sn = (res[6] << 24 | res[5] << 16 | res[4] << 8 | res[3])
model = (res[8] <<8 | res[7])
fwver = res[11]/100

print("Device information (from bootloader):")
print("    Model: RD%d (%d)" % (model/10,model))
print(" Firmware: v%0.2f" % (fwver))
print("      S/N: %08d" % (sn))

if (model not in supported_models):
    exit("Unsupported device!")

if (args.bootloader):
    print("Unit is now in bootloader mode.")
    exit()


# update firmware

res = update_firmware(serial, firmware)
if (res == 0):
    print("Firmware update complete.")
else:
    print("Firmware update FAILED!")


# eof :-)
