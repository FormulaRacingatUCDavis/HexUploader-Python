# Script that receives serial input from the PICDuino
# Args: <fulldevicename> e.g /dev/ttyUSB0 aka the port connecting the PICDuino

import sys
import serial.tools.list_ports

# Pass in command to print error message
def validate_and_open_port():
    if len(sys.argv) < 3:
        # A port wasn't provided
        print(f"Usage: python3 receiver.py {sys.argv[1]} <portname>")
        exit()

    if sys.argv[1] not in ports:
        # The port can't be found
        print(f"Error: Invalid port name: \"{sys.argv[1]}\"")
        exit()

    # Open port
    return serial.Serial(sys.argv[1])

if __name__ == "__main__":
    # Input validation
    if len(sys.argv) < 2:
        # A command wasn't provided
        print("Usage: python3 receiver.py <command>")
        print("Available commands:")
        print("listports")
        print("upload")
        print("read")
        print("send")
        exit()

    # Get available ports
    ports = serial.tools.list_ports.comports()
   
    # Process command
    if sys.argv[1] == "listports":
        # Print all the port names
        for port in ports:
            print(port.name)
    elif sys.argv[1] == "upload":
        # TODO
    elif sys.argv[1] == "read":
        port = validate_and_open_port()
        
        # Print output
        print("Press Ctrl+C to close the program. Receiver output:")
        while(True):
            # read_until() continues to read until it encounters \n
            # Don't print newline since string already ends with \n
            # Convert byte array to string
            print(port.read_until().decode(), end="")
        # TODO: need to properly terminate
    elif sys.argv[1] == "send":
        port = validate_and_open_port()

        if len(sys.argv) < 4:
            # No message found
            print("Usage: python3 receiver.py send <portname> <message>")
            exit()

        # Send message
        port.write(bytes(sys.argv))

    port.close()

