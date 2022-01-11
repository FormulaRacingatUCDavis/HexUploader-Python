import time
import serial
from serial.tools.list_ports import comports

### PIC 16 Signals

PIC16_ESC_BYTE = "05"
# Verifies if we are connected to a PICDuino board
PICDUINO_HANDSHAKE = PIC16_ESC_BYTE + "AA"
# Expected response
PICDUINO_HANDSHAKE_RESPONSE = "99"

RESET_PIC18 = PIC16_ESC_BYTE + "BB"
RESET_PIC18_RESPONSE = "01"

RESPONSE_TIMEOUT_SECS = 3

### Subcommand function helpers

def __validate_port_name(device_path):
    device_paths = map(lambda port: port.device, comports())
    if device_path not in device_paths:
        # The port can't be found
        print(f"Error: Invalid port with name: \"{device_path}\"")
        exit()

# TODO: use proper function annotations
'''
Sends a request to the microcontroller and awaits a response

@port_name is the name of the port where @request bytes is sent and @response bytes is expected
Both @request and @response are hex strings
@timeout is the time in seconds that the response must be received after @request was sent
Prints @begin_message when beginning to expect @response
Prints @success_message if @response is received
Prints @error_message if @response wasn't received and quits the program
'''
def send_and_await_response(port_name, request, response, begin_message,
                            success_message,
                            error_message,
                            timeout=RESPONSE_TIMEOUT_SECS):
    # Timeout is set to 0 so reading from the port does not stall the program
    with serial.Serial(port_name, timeout=0) as port:
        # Send request
        request_bytes = bytes.fromhex(request)
        port.write(request_bytes)

        print(begin_message)

        # Constantly check for response until timeout
        start = time.time()
        while(1):
            if time.time() - start >= timeout:
                # Response took too long to arrive
                print(error_message)
                exit()

            # Read one byte at a time
            byte = port.read()
            if byte.hex() == response:
                # Found the right response
                print(success_message)
                break
            # Continue checking for response

### Subcommand functions

def list_ports(args):
    ports = comports()
    # Print all the device paths
    print("Ports found:", len(ports))
    for port in ports:
        print(port.device)

def read_port(args):
    __validate_port_name(args.device_path)

    # Receive and print microcontroller output
    print("Press Ctrl+C to close the program. Receiver output:")
    # Open connection to port
    with serial.Serial(args.device_path) as port:
        while(True):
            # Print every line received
            # Line already ends with \n, so don't add another
            print(port.read_until().decode(encoding="ascii"), end="")

def perform_handshake(args):
    __validate_port_name(args.device_path)
    send_and_await_response(args.device_path,
                            request=PICDUINO_HANDSHAKE,
                            response=PICDUINO_HANDSHAKE_RESPONSE,
                            begin_message="Performing handshake...",
                            success_message="This microcontroller is a PICDuino!",
                            error_message="Could not verify this microcontroller is a PICDuino.")

def upload(args):
    __validate_port_name(args.device_path)

    # Open hex file
    try:
        hex_file = open(args.file)
    except:
        print(f"Error: cannot open file \"{args.file}\"")

    # Reset PIC18
    send_and_await_response(args.device_path,
                            request=RESET_PIC18,
                            response=RESET_PIC18_RESPONSE,
                            begin_message="Resetting PIC18...",
                            success_message="Successfully reset PIC18 to run the bootloader.",
                            error_message="Could not reset PIC18.")

    if args.read_after_upload:
        read_port(args.device_path)
