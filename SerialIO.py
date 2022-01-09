import time
import serial
from serial.tools.list_ports import comports

# PIC 16 Signals

PIC16_ESC_BYTE = "05"
# Verifies if we are connected to a PICDuino board
PICDUINO_HANDSHAKE = PIC16_ESC_BYTE + "AA"
# Expected response
PICDUINO_HANDSHAKE_RESPONSE = "99"

def list_ports(args):
    ports = comports()
    # Print all the device paths
    print("Ports found:", len(ports))
    for port in ports:
        print(port.device)

# Checks if a port name is valid
def __validate_port_name(device_path):
    device_paths = map(lambda port: port.device, comports())
    if device_path not in device_paths:
        # The port can't be found
        print(f"Error: Invalid port with name: \"{device_path}\"")
        exit()

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
        # Perform handshake
        handshake_request = bytes.fromhex(PICDUINO_HANDSHAKE)
        port.write(handshake_request)

        print("Performing handshake with microcontroller...")

        start = time.time()
        while 1:
            if time.time() - start >= 3: # 3 seconds timeout
                print("Cannot verify if board is a PICDuino")
                exit()
            byte = port.read()
            # Issue: the 0x99 can come from anywhere, not just the PIC16
            if byte.hex() == PICDUINO_HANDSHAKE_RESPONSE:
                # Verified that microcontroller is PICDuino
                break
            # Otherwise keep listening for response

        print("This board is a PICDuino")

def upload(args):
    __validate_port_name(args.device_path)

    # Open hex file
    try:
        hex_file = open(args.file)
    except:
        print(f"Error: cannot open file \"{args.file}\"")

    # TODO: upload

    if args.read_after_upload:
        read_port(args.device_path)
