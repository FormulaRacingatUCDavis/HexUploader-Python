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
usage: HexUploader.py [-h] [-p PORT] [-m MESSAGE] [-f FILE] {listports,upload,read,send}

Command line toolkit for the PICDuino

positional arguments:
  {listports,upload,read,send}
                        what you want to do with the PICDuino

optional arguments:
  -h, --help            show this help message and exit
  -p PORT               the port name connecting the PICDuino
  -m MESSAGE            message to send to PICDuino
  -f FILE               the name of the hex binary to upload
```
