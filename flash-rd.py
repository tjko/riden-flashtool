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
    serial.write(s)
    return

def update_firmware(serial, fw):
    write_string(serial, b'upfirm\r\n')
    r = read_reply(serial, 6)
    if (r != b'upredy'):
        print("Failed to initiate flashing: %s" %(r))
        return 1
    print("Updating firmware...")
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
parser.add_argument('--address', type=int, default=1, help='Modbus address')
args = parser.parse_args()


# open serial connection

print("Serial port: %s" % (args.port))
serial = serial.Serial(port=args.port, baudrate=args.speed, timeout=2)


# read firmware file
try:
    f = open(args.firmware, 'rb')
except:
    exit("Cannot open file: %s" % (args.firmware))
firmware = f.read()
f.close()
print("Firmware size: %d bytes" % (len(firmware)))



print("Check if device is in bootloader mode...")
write_string(serial, b'queryd\r\n')
res=read_reply(serial, 4)
serial.timeout=5;
if (res == b'boot'):
    print("In bootloader mode.")
else:
    print("Not in bootloader mode.")

    # try modbus query (read registers 0-3)...
    write_string(serial, b'\x01\x03\x00\x00\x00\x04\x44\x09')
    res=read_reply(serial, 13)
    if (len(res) == 0):
        exit("No response from device.")
    if (len(res) != 13 or res[0] != 0x01 or res[1] != 0x03 or res[2] != 0x08):
        exit("Invalid response received: %s" % (res))

    print("Found device:")    
    model = (res[3] << 8 | res[4]);
    print(" Model: RD%d (%d)" % (model/10,model))
    print(" Firmware: v%0.2f" % (res[10]/100))
    if (model not in supported_models):
        exit("Unsupported device!")

    print("Rebooting to boot mode...")
    # try modbus write to register 0x100 (value 0x1601)...
    write_string(serial, b'\x01\x06\x01\x00\x16\x01\x47\x96')
    res=read_reply(serial, 1)
    if (res != b'\xfc'):
        exit("Failed to reboot device.")
    sleep(3)


# update firmware

res = update_firmware(serial, firmware)
if (res == 0):
    print("Firmware update complete.")
else:
    print("Firmware update FAILED!")


# eof :-)
