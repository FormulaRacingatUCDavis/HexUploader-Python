import sys
import argparse
import serial
from serial.tools.list_ports import comports

if __name__ == "__main__":
    # Parse subcommands and their required args
    parser = argparse.ArgumentParser(description='Command line toolkit for the PICDuino microcontroller')
    # Create subparsers for each subcommand
    # Each subparser handles the required args for a subcommand
    subparsers = parser.add_subparsers(title='subcommand', dest='subcommand', required=True,
                                       description='valid subcommands to perform operation on microcontroller / serial ports')
    parser_listports = subparsers.add_parser('listports', help='lists all the serial port paths')
    parser_upload = subparsers.add_parser('upload', help='upload a hex binary file to the microcontroller')
    parser_read = subparsers.add_parser('read', help='read data from microcontroller')

    # Required subcommand args

    # Port required for all operations that connect to the microcontroller
    PORT_FLAG = '-p'
    PORT_DESTNAME = 'device_path'
    PORT_HELP_STR = 'device path for port connecting the microcontroller'
    parser_upload.add_argument(PORT_FLAG, dest=PORT_DESTNAME, help=PORT_HELP_STR, required=True)
    parser_read.add_argument(PORT_FLAG, dest=PORT_DESTNAME, help=PORT_HELP_STR, required=True)
    # File required to upload to microcontroller
    parser_upload.add_argument('-f', dest="file", help="Name of the hex binary to upload", required=True)

    # Validate and get subcommand + flags
    args = parser.parse_args()

    # Get available ports
    ports = comports()

    # Process operation
    if args.subcommand == "listports":
        # Print all the device paths
        print("Ports found:", len(ports))
        for port in ports:
            print(port.device)
    elif args.subcommand in ['upload', 'read']:
        # These commands require a port connection
        # Did the user enter a valid port?
        device_paths = map(lambda port: port.device, ports)
        if args.device_path not in device_paths:
            # The port can't be found
            print(f"Error: Invalid port with name: \"{args.device_path}\"")
            exit()

        # Open connection to port
        port = serial.Serial(args.device_path)

        if args.subcommand == 'read':
            # Receive and print microcontroller output
            print("Press Ctrl+C to close the program. Receiver output:")
            while(True):
                # Print string already ends with \n
                print(port.read_until().decode(encoding="ascii"), end="")
            # TODO: need to properly terminate when Ctrl+C is pressed
        elif args.subcommand == "upload":
            # TODO
            pass

        # Done using port
        port.close()
