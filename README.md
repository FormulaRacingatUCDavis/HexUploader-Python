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
2. Run the script `python3 HexUploader.py`
