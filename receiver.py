# Script that receives serial input from the PICDuino
import serial.tools.list_ports

if __name__ == "__main__":
    selection = -1
    valid_selection = False
    while valid_selection == False:
        # Print available serial ports
        ports = serial.tools.list_ports.comports()

        if len(ports) == 0:
            print("There are no ports available. Please reconnect your PICDuino and try again")
            exit()

        print("<selection number>: <serial port>")
        for i in range(0, len(ports)):
            port = ports[i]
            print(f"{i}: {port[0]}")

        # Prompt user to open port
        selection = int(input("Enter selection number for port to read from:"))

        # Input validation
        if selection < 0 or selection >= len(ports):
            print("Error: please enter a valid selection!")
        else:
            valid_selection = True

    # Open and read from port
    print("Press Ctrl+C to close the program. Receiver output:")
    port = serial.Serial(port[0])
    while(True):
        # Decode byte array to string
        # https://docs.python.org/3/library/stdtypes.html#bytes.decode
        # Don't print newline since string already ends with \n
        # read_until() continues to read until it encounters a newline
        print(port.read_until().decode(), end="")

    # TODO: this code can never run
    port.close()

