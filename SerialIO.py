import time
try:
    import serial
    from serial.tools.list_ports import comports
except:
    print("Could not import pyserial. Please make sure it is installed.")
    exit()

### PIC 16 signals (hex)

PIC16_ESC_BYTE = "05"
# Verifies if we are connected to a PICDuino board
PICDUINO_HANDSHAKE = PIC16_ESC_BYTE + "AA"
PICDUINO_HANDSHAKE_RESPONSE = "99"

# Resets PIC18 to start up the bootloader again
RESET_PIC18 = PIC16_ESC_BYTE + "BB"
RESET_PIC18_RESPONSE = "01"

# Requests bootloader operation. Stops bootloader from handing off to main program. 
REQUEST_BOOTLOADER = "55"
REQUEST_BOOTLOADER_RESPONSE = "69" #heh heh

### Bootloader commands (hex)

# Expected response for all commands
CMD_SUCCESS_RESPONSE = "01"
CMD_UNSUPPORTED_RESPONSE = "FF"
CMD_ADDRESS_ERROR_RESPONSE = "FE"

## Erase flash
WRITE_FLASH_CMD = "02"
ERASE_FLASH_CMD = "03"
WRITE_CONFIG_CMD = "07"
CALCULATE_CHECKSUM_CMD = "08"

# Range of addresses to erase
APP_START_ADDRESS = 0x900
FLASH_END_ADDRESS = 0x10000

# The erase flash command takes in a number of rows to erase
ROW_ADDRESS_COUNT = 128
APP_NUM_ROWS = (FLASH_END_ADDRESS - APP_START_ADDRESS) // ROW_ADDRESS_COUNT

# Must convert app start address to little endian
# ERASE_START_ADDR = "00" + "09" + "0000"
UNLOCK_SEQUENCE = "55AA"

# Start address: 0x900 -> 00 09 00 00
NEW_RESET_VECTOR = "00090000"

# Number of rows: (0x10000 - 0x900) / 128 = 494
# 494 = 0x1EE -> EE 01
ERASE_FLASH = ERASE_FLASH_CMD + "EE01" + UNLOCK_SEQUENCE + NEW_RESET_VECTOR

# Number of bytes for checksum = total length of program memory.
# 0x10000 - 0x0900 = 0xF700
# 0xF700 -> "00F7" (little endian)
CALCULATE_CHECKSUM = CALCULATE_CHECKSUM_CMD + "00F7" + "0000" + NEW_RESET_VECTOR

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
def send_and_await_response(port_name, request, rx_length, begin_message=None,
                            error_message="Timeout!",
                            timeout=RESPONSE_TIMEOUT_SECS):
    # Timeout is set to 0 so reading from the port does not stall the program
    with serial.Serial(port_name, timeout=0) as port:
        # Send request
        request_bytes = bytes.fromhex(request)
        port.write(request_bytes)

        if begin_message: 
            print(begin_message)

        # Constantly check for response until timeout
        start = time.time()

        rx = []
        while len(rx) < rx_length:
            if time.time() - start >= timeout:
                # Response took too long to arrive
                if error_message:
                    print(error_message)
                raise Exception("Request timed out!")

            # Read one byte at a time
            byte = port.read()
            if byte != b'':
               rx.append(byte)
        return rx

def compare_result(expected, actual, success_message=None, error_message=None):
    if actual == expected:
        if success_message:
            print(success_message)

    elif actual == bytes.fromhex(CMD_UNSUPPORTED_RESPONSE):
        print("Error: command unsupported")
        exit()
    elif actual == bytes.fromhex(CMD_ADDRESS_ERROR_RESPONSE):
        print("Error: address error")
        exit()
    else:
        if error_message:
            print(error_message)
        exit()



### Subcommand functions

def list_ports(args, output=True):
    ports = comports()

    # Print all the device paths
    if output:
        print("Ports found:", len(ports))

    austuino_ports = []
    for port in ports:
        is_austuino = ''
        try:
            rx = send_and_await_response(port.device,
                                request=PICDUINO_HANDSHAKE,
                                error_message=None,
                                rx_length=1,
                                timeout=0.1)
        except Exception:
            rx = False

        if rx:
            if rx[0] == bytes.fromhex(PICDUINO_HANDSHAKE_RESPONSE):
                is_austuino = ' Austuino'
                austuino_ports.append(port.device)

        if output:
            print(port.device + is_austuino)

    return austuino_ports

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
            
def unhex(hex):
    return int(hex, 16)    
            
# record types: 
DATA_RECORD = "00"
EOF_RECORD = "01"
EXT_ADDR_RECORD = "04"
            
def parse_hex(args):
    # Open hex file
    try:
        hex_file = open(args.file)
    except:
        print(f"Error: cannot open file \"{args.file}\"")
        
    lines = hex_file.readlines()
    hex_file.close()
    
    ext_addr = "0000"
    write_commands = []

    memory_checksum = 0

    for (num, line) in enumerate(lines): 
        line = line.strip()
        
        # all hex records start with ':'
        if not line[0] == ':': 
            print(f"No colon on line {num + 1}.")
            return False
          
        # break record up into bytes
        bytes = []   
        for i in range(1, len(line), 2):
            bytes.append(line[i] + line[i+1])
            
        # data length is first byte
        expected_data_length = unhex(bytes[0])
        
        # 1(data length) + 2(address) + 1(record type) + 1(checksum) = 5
        actual_data_length = len(bytes) - 5
        
        if not expected_data_length == actual_data_length:
            print(f"Wrong datalength on line {num + 1}.")
            exit()
            
        # verify checksum 
        checksum = 0
        for (i, byte) in enumerate(bytes):
            if i < (len(bytes) - 1):  # not last byte
                checksum += unhex(byte)
            else:  # last byte
                checksum = ((~(checksum & 0xFF)) + 1) & 0xFF; #8 bit 2s complement
                if not checksum == unhex(byte):  #last byte is checksum
                    print(f"Bad checksum on line {num + 1}.")
                    exit()
                    
        record_type = bytes[3]
        
        if record_type == EXT_ADDR_RECORD: 
            ext_addr = bytes[5] + bytes[4]   #upper 16 bits of address, little endian
            
        elif record_type == DATA_RECORD:
            if ext_addr == "0000" and bytes[1] == "00" and bytes[2] in ["00", "08", "18"]:     #reset vector and interrupt vectors
                bytes[1] = "09"
            
            if ext_addr == "0000":  # outside of program memory
                cmd = WRITE_FLASH_CMD
                in_program_memory = True
            else: 
                cmd = WRITE_CONFIG_CMD
                in_program_memory = False
                
            write_command = cmd + bytes[0] + "00" + UNLOCK_SEQUENCE + bytes[2] + bytes[1] + ext_addr
            
            for i in range(actual_data_length):
                write_command += bytes[i+4]
                if bytes[i+4] == PIC16_ESC_BYTE:   #escape byte must be written twice to go through
                    write_command += PIC16_ESC_BYTE

                if in_program_memory:
                    memory_checksum += ((~unhex(bytes[i+4])) & 0xFF)
            
            write_commands.append(write_command)
            
        elif record_type == EOF_RECORD:
            memory_checksum &= 0xFFFF  #16 bits
            return write_commands, memory_checksum
                    
    print("No EOF record found!")
    exit()


def perform_handshake(args):
    pass
    #bad code
#    __validate_port_name(args.device_path)
#    rx = send_and_await_response(args.device_path,
#                            request=PICDUINO_HANDSHAKE,
#                            response=PICDUINO_HANDSHAKE_RESPONSE,
#                            begin_message="Performing handshake...",
#                            success_message="This microcontroller is a PICDuino!",
#                            error_message="Could not verify this microcontroller is a PICDuino.")


def reset(args):
    # Reset PIC18
    rx = send_and_await_response(args.device_path,
                            request=RESET_PIC18,
                            rx_length=1,
                            begin_message="Resetting PIC18..."
                            )

    compare_result(bytes.fromhex(RESET_PIC18_RESPONSE),
                   rx[0],
                   success_message="Successfully reset PIC18.",
                   error_message="Could not reset PIC18.")

                            
def request_bootloader(args):
    rx = send_and_await_response(args.device_path,
                            request=REQUEST_BOOTLOADER, 
                            rx_length=1,
                            begin_message="Requesting bootloader...",
                            )

    compare_result(bytes.fromhex(REQUEST_BOOTLOADER_RESPONSE),
                   rx[0],
                   success_message="Bootloader running.",
                   error_message="Could not start bootloader.")
                            
def erase_flash(args):
    # Send erase flash command
    rx = send_and_await_response(args.device_path,
                            request=ERASE_FLASH,
                            rx_length=10,
                            begin_message="Erasing flash...",
                            )

    compare_result(bytes.fromhex(CMD_SUCCESS_RESPONSE),
                   rx[9],
                   success_message = "Successfully erased flash.",
                   error_message = "Could not erase flash.")

def validate(args, memory_checksum):
    rx = send_and_await_response(args.device_path,
                                 request=CALCULATE_CHECKSUM,
                                 rx_length=11,
                                 begin_message="Validating...",
                                 )

    received_checksum = int.from_bytes(rx[10] + rx[9], "big")

    compare_result(memory_checksum,
                   received_checksum,
                   success_message="Validation successful!",
                   error_message="Validation failed.")

def upload(args):
    if args.device_path:
        __validate_port_name(args.device_path)
    else:
        austuino_ports = list_ports(args, output=False)
        if len(austuino_ports) == 1:
            args.device_path = austuino_ports[0]
            print(f'Austuino found on {args.device_path}')
        else:
            if len(austuino_ports) == 0:
                print('No Austuinos found!')
            else:
                print('More than one Austuino found!')

            print('Please specify port with "-p".')
            list_ports(args, output=True)    #print ports for convenience
            exit()



    print("Loading hex...")
    write_commands, memory_checksum = parse_hex(args)
    if not write_commands: 
        print("Invalid hex.")
        exit()

    print("Hex loaded.")
    # TODO: perform handshake to verify this is a PIC18?

    reset(args)
    request_bootloader(args)
    erase_flash(args)

    #write flash
    print('Programming...')
    for write_command in write_commands:
        rx = send_and_await_response(args.device_path,
                                request=write_command,
                                rx_length=10)

        compare_result(bytes.fromhex(CMD_SUCCESS_RESPONSE),
                       rx[9],
                       error_message='Failed to write record.')

    print('Programming complete.')

    #validate checksum
    validate(args, memory_checksum)

    # reset to exit bootloader
    reset(args)

    if args.read_after_upload:
        read_port(args.device_path)
