import sys
import argparse
import serial.tools.list_ports

# Pass in command to print error message
def validate_and_open_port(portname, ports):
    getportname = lambda port: port.name
    if portname not in map(getportname, ports):
        # The port can't be found
        print(f"Error: Invalid port name: \"{portname}\"")
        exit()

    # Open port
    return serial.Serial(portname)

if __name__ == "__main__":
    # Specify required/optional args
    parser = argparse.ArgumentParser(description='Command line toolkit for the PICDuino microcontroller')

    # List of operations
    parser.add_argument('operation', choices=[
        'listports',
        'upload',
        'read',
        'send'
    ], help="operation to perform with the serial ports / microcontroller")

    # Did the user enter a valid operation?
    parser.parse_args()

    # Only require these arguments for specific commands
    ops_requiring_port = ['upload', 'read', 'send']
    parser.add_argument('-p', dest="portname", help="the port name connecting the PICDuino", required=sys.argv[1] in ops_requiring_port)
    parser.add_argument('-m', dest="message", help="message to send to PICDuino", required=sys.argv[1] == 'send')
    parser.add_argument('-f', dest="file", help="the name of the hex binary to upload", required=sys.argv[1] == 'upload')

    # Get op + flags
    args = parser.parse_args()

    # Get available ports
    ports = serial.tools.list_ports.comports()

    # Process operation
    if args.operation == "listports":
        # Print all the port names
        print("Ports found:", len(ports))
        for port in ports:
            print(port.name)
    elif args.operation in ops_requiring_port:
        port = validate_and_open_port(args.portname, ports)
        if args.operation == 'read':
            # Print output
            print("Press Ctrl+C to close the program. Receiver output:")
            while(True):
                # Don't print newline since string already ends with \n
                print(port.read_until().decode(), end="")
            # TODO: need to properly terminate
        elif args.operation == "send":
            # Send message
            port.write(bytes(message))
        elif args.operation == "upload":
            # TODO
            pass

        # Done using port
        port.close()
