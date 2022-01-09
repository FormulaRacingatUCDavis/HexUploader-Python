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

# Checks if a port name is valid
def __validate_port_name(device_path):
    device_paths = map(lambda port: port.device, comports())
    if device_path not in device_paths:
        # The port can't be found
        print(f"Error: Invalid port with name: \"{device_path}\"")
        exit()

# TODO: use proper function annotations
'''
Sends a message to the microcontroller and awaits a response

@port is where @request bytes is sent and @response bytes is expected
Both @message and @response must be in hex strings
@timeout is the time in seconds that the response must be received after the message was sent
Prints @success_message if @response is received
Prints @error_message if @response wasn't received and quits the program
'''
def send_and_await_response(port, request, response, begin_message,
                            success_message,
                            error_message,
                            timeout=RESPONSE_TIMEOUT_SECS):
    request_bytes = bytes.fromhex(request)
    port.write(request_bytes)
    # Continuously search for response until timeout
    print(begin_message)
    start = time.time()
    while(1):
        if time.time() - start >= timeout:
            print(error_message)
            exit()

        byte = port.read()
        if byte.hex() == response:
            print(success_message)
            break;

def reset_pic16(port):
    send_and_await_response(port,
                            request=RESET_PIC18,
                            response=RESET_PIC18_RESPONSE,
                            begin_message="Resetting PIC18...",
                            success_message="Successfully reset PIC18 to run the bootloader.",
                            error_message="Could not reset PIC18.")

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
    # Open connection to port and handle any keyboard interrupts automatically
    with serial.Serial(args.device_path) as port:
        while(True):
            # Print string already ends with \n
            print(port.read_until().decode(encoding="ascii"), end="")

def perform_handshake(args):
    __validate_port_name(args.device_path)
    with serial.Serial(args.device_path) as port:
        send_and_await_response(port,
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

    with serial.Serial(args.device_path) as port:
        reset_pic16(port)

    if args.read_after_upload:
        read_port(args.device_path)
