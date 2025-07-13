#!/usr/bin/env python3
#
# flash-rd.py - Riden RD60xx Firmware Flash Tool
#
# Copyright (C) 2020-2025 Timo Kokkonen <tjko@iki.fi>
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

"""Riden PSU Firmware Updater"""

import sys
import argparse
from time import sleep
import serial



class RidenFirmwareUpdater:
    """Riden RD60xx Power Supply Firmware Updater"""

    supported_models = [ 60062, 60065, 60066,
                         60121, 60125, 60181,
                         60241,
                         60301 ]


    def __init__(self, port, verbose=False):
        self.port = port
        self.verbose_mode = verbose


    def read_data(self, count):
        """Read block of data from device."""

        if self.verbose_mode:
            print('Waiting data...')
        res = self.port.read(count)
        if self.verbose_mode:
            print(f'Read: {len(res)}: {res}')
        return res


    def write_data(self, data):
        """Write block of data to device."""

        if self.verbose_mode:
            print(f'Write: {len(data)}: {data}')
        res = self.port.write(data)
        return res


    def update_firmware(self, firmware):
        """Send firmware image to device."""

        self.port.timeout = 5
        self.write_data(b'upfirm\r\n')
        res = self.read_data(6)
        if res != b'upredy':
            print(f'Failed to initiate flashing: {res}')
            return 1

        print('Updating firmware...', end='', flush=True)
        pos = 0
        while pos < len(firmware):
            buf = firmware[pos:pos+64]
            self.write_data(buf)
            res = self.read_data(2)
            if res != b'OK':
                print(f'Flash failed: {res}')
                return 2
            print('.', end='', flush=True)
            pos += 64
        print(res)
        return 0


    def bootloader_mode(self):
        """Set device into bootloader mode."""

        # Check if unit is in bootloader.
        print('Check if device is in bootloader mode...', end='', flush=True)
        self.write_data(b'queryd\r\n')
        res = self.read_data(4)
        if res == b'boot':
            print('Yes')
            return 0
        print('No')

        # Try Modbus if unit not in bootloader mode...

        # Send modbus command (read registers 0-3)
        self.port.timeout = 5
        self.write_data(b'\x01\x03\x00\x00\x00\x04\x44\x09')
        res = self.read_data(13)
        if len(res) == 0:
            print('No response from device.')
            return 1
        if len(res) != 13 or res[0] != 0x01 or res[1] != 0x03 or res[2] != 0x08:
            print(f'Invalid response received: {res}')
            return 2
        model = res[3] << 8 | res[4]
        fwver = res[10] / 100
        print(f'Found a device (using Modbus): RD{int(model/10)} ({model}) v{fwver:.2f}')

        # Send modbus command (write 0x1601 into register 0x100) to reboot
        print('Rebooting into bootloader mode...')
        self.write_data(b'\x01\x06\x01\x00\x16\x01\x47\x96')
        res = self.read_data(1)
        if res != b'\xfc':
            print('Failed to reboot device.')
            return 3

        # Wait for unit to reboot...
        sleep(3)
        return 0


    def device_info(self):
        """Return device model information."""

        self.write_data(b'getinf\r\n')
        res = self.read_data(13)
        if len(res) == 0:
            print('No response from bootloader')
            return(-1, 0, 0)
        if len(res) != 13 or res[0:3] != b'inf':
            print(f'Invalid response from bootloader: {res}')
            return(-2, 0, 0)
        snum = res[6] << 24 | res[5] << 16 | res[4] << 8 | res[3]
        model = res[8] << 8 | res[7]
        fwver = res[11] / 100
        return(model, fwver, snum)


    def supported_model(self, model):
        """Check if device model is supported for firmware update."""
        if model in self.supported_models:
            return True
        return False



####################################################################################

def main():
    """Main program when invoked as a script."""

    # Parse command-line arguments

    parser = argparse.ArgumentParser(description='Riden RD60xx Firmware Flash Tool')
    parser.add_argument('port', help='Serial port')
    parser.add_argument('firmware', nargs='?',
                        help='Firmware file. If not specified, only reboot to bootloader'
                             ' mode and print version of the device.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-s', '--speed', type=int, default=115200,
                        help='Serial port speed (default: 115200)')
    args = parser.parse_args()


    # Open serial connection

    print(f'Serial port: {args.port} ({args.speed}bps)')
    try:
        port = serial.Serial(port=args.port, baudrate=args.speed, timeout=2)
    except serial.SerialException as err:
        sys.exit(err)


    # Read firmware file into memory

    if args.firmware:
        try:
            with open(args.firmware, 'rb') as file:
                firmware = file.read()
        except OSError as err:
            sys.exit(err)
        print(f'Firmware image size: {len(firmware)} bytes')
    else:
        firmware = ''


    # Put device into bootloader mode, if it's not already in it...

    psu = RidenFirmwareUpdater(port, verbose=args.verbose)
    res = psu.bootloader_mode()
    if res:
        sys.exit('Failed to set device into bootloader mode.')


    # Query device information from bootloader

    model, fwver, snum = psu.device_info()

    if model >= 0:
        print('Device information (from bootloader):')
        print(f'    Model: RD{int(model / 10)} ({model})')
        print(f' Firmware: v{fwver:.2f}')
        print(f'      S/N: {snum:0>8d}')

    if not psu.supported_model(model):
        sys.exit(f'Unsupported device: {model}')

    # Update firmware

    if len(firmware) > 0:
        res = psu.update_firmware(firmware)
        if res == 0:
            print('Firmware update complete.')
        else:
            sys.exit('Firmware update FAILED!')



if __name__ == '__main__':
    main()

# eof :-)
