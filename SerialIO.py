import time
import serial
from serial.tools.list_ports import comports

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

# Range of addresses to erase
APP_START_ADDRESS = 0x900
FLASH_END_ADDRESS = 0x10000

# The erase flash command takes in a number of rows to erase
ROW_ADDRESS_COUNT = 128
APP_NUM_ROWS = (FLASH_END_ADDRESS - APP_START_ADDRESS) // ROW_ADDRESS_COUNT

# Must convert app start address to little endian
# ERASE_START_ADDR = "00" + "09" + "0000"
UNLOCK_SEQUENCE = "55AA"

# Number of rows: (0x10000 - 0x900) / 128 = 494
# 494 = 0x1EE -> EE 01
# Start address: 0x900 -> 00 09 00 00
ERASE_FLASH = ERASE_FLASH_CMD + "EE01" + UNLOCK_SEQUENCE + "00090000"

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
def send_and_await_response(port_name, request, response, begin_message=None,
                            success_message=None,
                            error_message="Error!",
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
        while(1):
            if time.time() - start >= timeout:
                # Response took too long to arrive 
                print(error_message)
                exit()

            # Read one byte at a time
            byte = port.read()
            #if byte != b'':
              #print(byte.hex())

            if byte == bytes.fromhex(response):
                # Found the right response
                if success_message: 
                    print(success_message)
                break
            elif byte == bytes.fromhex(CMD_UNSUPPORTED_RESPONSE):
                print("Error: command unsupported")
                exit()
            elif byte == bytes.fromhex(CMD_ADDRESS_ERROR_RESPONSE):
                print("Error: address error")
                exit()
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
            return False
            
        # verify checksum 
        checksum = 0
        for (i, byte) in enumerate(bytes):
            if i < (len(bytes) - 1):  # not last byte
                checksum += unhex(byte)
            else:  # last byte
                checksum = ((~(checksum & 0xFF)) + 1) & 0xFF; #8 bit 2s complement
                if not checksum == unhex(byte):  #last byte is checksum
                    print(f"Bad checksum on line {num + 1}.")
                    return False
                    
        record_type = bytes[3]
        
        if record_type == EXT_ADDR_RECORD: 
            ext_addr = bytes[5] + bytes[4]   #upper 16 bits of address, little endian
            
        elif record_type == DATA_RECORD:
            if bytes[2] == "00" and bytes[1] == "00" and ext_addr == "0000": #move reset vector to 0x0900
                bytes[1] = "09"
            
            if ext_addr == "0000":  # outside of program memory
                cmd = WRITE_FLASH_CMD
                program_memory = True
            else: 
                cmd = WRITE_CONFIG_CMD
                program_memory = False
                
            write_command = cmd + bytes[0] + "00" + UNLOCK_SEQUENCE + bytes[2] + bytes[1] + ext_addr
            
            for i in range(actual_data_length):
                write_command += bytes[i+4]
                #TODO: calculate checksum
            
            write_commands.append(write_command)
            
        elif record_type == EOF_RECORD: 
            return write_commands
                    
    print("No EOF record found!")
    return False
        
        
        
        
    

def perform_handshake(args):
    __validate_port_name(args.device_path)
    send_and_await_response(args.device_path,
                            request=PICDUINO_HANDSHAKE,
                            response=PICDUINO_HANDSHAKE_RESPONSE,
                            begin_message="Performing handshake...",
                            success_message="This microcontroller is a PICDuino!",
                            error_message="Could not verify this microcontroller is a PICDuino.")
                            
def reset(args):
    # Reset PIC18
    send_and_await_response(args.device_path,
                            request=RESET_PIC18,
                            response=RESET_PIC18_RESPONSE,
                            begin_message="Resetting PIC18...",
                            success_message="Successfully reset PIC18.",
                            error_message="Could not reset PIC18.")
                            
def request_bootloader(args):
    send_and_await_response(args.device_path, 
                            request=REQUEST_BOOTLOADER, 
                            response=REQUEST_BOOTLOADER_RESPONSE, 
                            begin_message="Requesting bootloader...",
                            success_message="Bootloader running.",
                            error_message="Could not start bootloader.")
                            
def erase_flash(args):
    # Send erase flash command
    send_and_await_response(args.device_path,
                            request=ERASE_FLASH,
                            response=CMD_SUCCESS_RESPONSE,
                            begin_message="Erasing flash...",
                            success_message="Successfully erased flash.",
                            error_message="Could not erase flash.",
                            timeout=900)




def upload(args):
    __validate_port_name(args.device_path)
    
    print("Loading hex...")
    write_commands = parse_hex(args)
    if not write_commands: 
        print("Invalid hex.")
        exit()

    print("Hex loaded.")
    # TODO: perform handshake to verify this is a PIC18?

    #reset PIC18
    reset(args)
    
    request_bootloader(args)
    

    # send_and_await_response(args.device_path,
    #                         request="000000000000000000",
    #                         response="99",
    #                         begin_message="Getting bootloader info",
    #                         success_message="done",
    #                         error_message="did not work")

    erase_flash(args)
    
    #write flash
    for write_command in write_commands: 
        send_and_await_response(args.device_path,
                                request=write_command,
                                response=CMD_SUCCESS_RESPONSE,
                                error_message='Failed to write record.')
    #reset to exit bootloader                           
    reset(args)

    if args.read_after_upload:
        read_port(args.device_path)
