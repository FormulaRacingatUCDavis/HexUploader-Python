# HexUploader-Python
Python version of HexUploader that uses the Pyserial library

## Compatibility
Only verified to work on:
- OS: Ubuntu 20.04.3 LTS
- Python version: 3.8.10
- pyserial version: v3.5

## Prerequisites on Linux
1. Install the latest version of pyserial by running `python3 -m pip install pyserial`
2. To open a serial port through Python, you must add yourself as a user to the group `dialout` in order to have read permissions. To do this, run `sudo adduser $USER dialout`
3. Restart your computer to apply the changes from step 2.

## How to use
1. Physically connect Arduino to computer
2. Run the script. This is the output of `python3 HexUploader.py -h`:
```
usage: HexUploader.py [-h] {listports,upload,read,send} ...

Command line toolkit for the PICDuino microcontroller

optional arguments:
  -h, --help            show this help message and exit

subcommand:
  valid subcommands to perform operation on microcontroller / serial ports

  {listports,upload,read,send}
    listports           lists all the serial ports
    upload              upload a hex binary file to the microcontroller
    read                read data from microcontroller
    send                send data to microcontroller
```
