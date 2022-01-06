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

        print("List of serial ports:")
        for i in range(0, len(ports)):
            port = ports[i]
            print(f"{i}: {port[0]}")

        # Prompt user to open port
        selection = int(input("Enter selection number for port:"))

        # Input validation
        if selection < 0 or selection >= len(ports):
            print("Error: please select a valid number!")
        else:
            valid_selection = True

    # Open and read from port
    print("Press Ctrl+C to close the program. Receiver output:")
    port = serial.Serial(port[0])
    while(True):
        print(port.read_until())

    port.close()
    # '''

