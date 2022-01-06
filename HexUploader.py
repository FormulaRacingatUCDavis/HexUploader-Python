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
    parser = argparse.ArgumentParser(description='Command line toolkit for the PICDuino')
    # List of commands
    parser.add_argument('command', choices=[
        'listports',
        'upload',
        'read',
        'send'
    ], help="what you want to do with the PICDuino")
    
    # Only require these arguments for specific commands
    parser.add_argument('-p', dest="portname", help="the port name connecting the PICDuino", required=
            ('upload' in sys.argv or 'read' in sys.argv or 'send' in sys.argv)
            )
    parser.add_argument('-m', dest="message", help="message to send to PICDuino", required='send' in sys.argv)
    parser.add_argument('-f', dest="file", help="the name of the hex binary to upload", required='upload' in sys.argv)

    # Get user inputted commands
    args = parser.parse_args()

    # Get available ports
    ports = serial.tools.list_ports.comports()
   
    # Process command
    if args.command == "listports":
        # Print all the port names
        print("Ports found:", len(ports))
        for port in ports:
            print(port.name)
    elif args.command in ['read', 'send', 'upload']:
        port = validate_and_open_port(args.portname, ports)
        if args.command == 'read':
            # Print output
            print("Press Ctrl+C to close the program. Receiver output:")
            while(True):
                # Don't print newline since string already ends with \n
                print(port.read_until().decode(), end="")
            # TODO: need to properly terminate
        elif command == "send":
            # Send message
            port.write(bytes(message))
        elif command == "upload":
            # TODO
            pass

        # Done with port
        port.close()
