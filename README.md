# HexUploader-Python
Python version of HexUploader that uses the Pyserial library

## Compatibility
Only verified to work on:

**OS**
- Ubuntu 20.04.3 LTS
- Windows 10 Build 19043

**Misc**
- Python version: 3.8.10 (Linux) and 3.10.1 (Windows)
- pyserial version: v3.5 (both Linux and Windows)

## Linux Setup
1. To open a serial port through Python, you must add yourself as a user to the group `dialout` in order to have read permissions. To do this, run `sudo adduser $USER dialout`
2. Restart your computer to apply the changes from step 2.

## How to use
1. Physically connect Arduino to computer
2. Run the script according to the syntax listed below.

### Help sections
`python3 HexUploader.py -h`:
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
`python3 HexUploader.py read -h`:
```
usage: HexUploader.py read [-h] -p DEVICE_PATH

optional arguments:
  -h, --help      show this help message and exit
  -p DEVICE_PATH  device path for port connecting the microcontroller
```
`python3 HexUploader.py send -h`:
```
usage: HexUploader.py send [-h] -p DEVICE_PATH -m MESSAGE

optional arguments:
  -h, --help      show this help message and exit
  -p DEVICE_PATH  device path for port connecting the microcontroller
  -m MESSAGE      Message to send to microcontroller
```
`python3 HexUploader.py upload -h`:
```
usage: HexUploader.py upload [-h] -p DEVICE_PATH -f FILE

optional arguments:
  -h, --help      show this help message and exit
  -p DEVICE_PATH  device path for port connecting the microcontroller
  -f FILE         Name of the hex binary to upload
```
