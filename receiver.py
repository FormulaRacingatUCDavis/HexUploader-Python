# Script that receives serial input from the PICDuino
# Args: <fulldevicename> e.g /dev/ttyUSB0 aka the port connecting the PICDuino

import sys
import serial.tools.list_ports

if __name__ == "__main__":
    # Input validation

    if len(sys.argv) < 2:
        print("Usage: python3 HexUploader.py <fulldevicename>")
        exit()

    ports = serial.tools.list_ports.comports()
    if sys.argv[1] not in ports:
        print(f"Error: Invalid port name: \"{sys.argv[1]}\"")
        exit()

    # Open and read from port
    print("Press Ctrl+C to close the program. Receiver output:")
    port = serial.Serial(sys.argv[1])
    while(True):
        # Decode byte array to string
        # https://docs.python.org/3/library/stdtypes.html#bytes.decode
        # Don't print newline since string already ends with \n
        # read_until() continues to read until it encounters \n
        print(port.read_until().decode(), end="")

    # TODO: this code will never run
    port.close()

