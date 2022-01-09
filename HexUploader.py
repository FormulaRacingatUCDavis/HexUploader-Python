import argparse

import SerialIO

def create_parser():
    parser = argparse.ArgumentParser(description='Command line toolkit for the PICDuino microcontroller')
    # Create subparsers for each subcommand
    # Each subparser handles the required args for a subcommand
    subparsers = parser.add_subparsers(title='subcommand', dest='subcommand', required=True,
                                       description='valid subcommands to perform operation on microcontroller / serial ports')
    parser_listports = subparsers.add_parser('listports', help='lists all the serial port paths')
    parser_upload = subparsers.add_parser('upload', help='upload a hex binary file to the microcontroller')
    parser_read = subparsers.add_parser('read', help='read data from microcontroller')
    parser_verify = subparsers.add_parser('verify', help='checks if microcontroller is a PICDuino')

    # Required subcommand args
    # Port required for all operations that connect to the microcontroller
    PORT_FLAG = '-p'
    PORT_DESTNAME = 'device_path'
    PORT_HELP_STR = 'device path for port connecting the microcontroller'
    parser_upload.add_argument(PORT_FLAG, dest=PORT_DESTNAME, help=PORT_HELP_STR, required=True)
    parser_read.add_argument(PORT_FLAG, dest=PORT_DESTNAME, help=PORT_HELP_STR, required=True)
    parser_verify.add_argument(PORT_FLAG, dest=PORT_DESTNAME, help=PORT_HELP_STR, required=True)
    # File required to upload to microcontroller
    parser_upload.add_argument('-f', dest="file", help="Name of the hex binary to upload", required=True)
    # Add option to read immediately after uploading
    parser_upload.add_argument('--read', dest="read_after_upload", action="store_true", help="read immediately after uploading")

    # Subcommand functions
    parser_listports.set_defaults(func=SerialIO.list_ports)
    parser_read.set_defaults(func=SerialIO.read_port)
    parser_upload.set_defaults(func=SerialIO.upload)
    parser_verify.set_defaults(func=SerialIO.perform_handshake)

    return parser

if __name__ == "__main__":
    # Parse subcommands and arguments
    parser = create_parser()
    # Validate and get subcommand + flags
    args = parser.parse_args()
    # Call subcommand function
    args.func(args)
