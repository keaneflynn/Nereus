import json
import os
import socket
import time


class retrieveData:
    def __init__(self, client_info):
        with open(client_info) as file:
            self.clients = json.load(file)

    def pitTags(self, port=10001):
        # Generate blank list to put output from each 
        raw_list = []
        # Loop through PIT antenna clients and grab data
        for key, value in self.clients.items():
        # Create a socket object with a timeout to prevent indefinite blocking
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # Set a 3-second timeout
                s.settimeout(3)  
                try:
                    # Connect to the device
                    s.connect((key, port))
                    # Send the request command for 'Memory Tag Download' (MTD)
                    request_command = b'MTD\r\n'
                    s.send(request_command)
                    # Introduce a brief 3-sec delay to allow device to process command
                    time.sleep(3)
                    # Create empty byte array to append incoming packets to 
                    data = bytearray()
                    # Read data in chunks, formatting and appending what is returned
                    while True:
                        # Receive data in 1024-byte chunks
                        # IS1001 Remote Comms Boards set MTU to 
                        byte_data = s.recv(1024)
                        if not byte_data:
                            continue  # Pass loop iteration if no more data is 
                                      # received should always be received  
                                      # regardless of tags collected or not
                                      # It will be terminated once 'Complete' arrives
                        # Concatenate incoming bytearray data packets
                        data.extend(byte_data)
                        # Biomark ends report with 'Complete', this will end it
                        if b'Complete' in byte_data: 
                            break
                    # Decode concatenated bytestring from reader to readable, 
                    # workable format with UTF-8 decoding
                    concat = data.decode('utf-8')
                    # Convert data from bytestring to str and return
                    raw_list.append([concat, key, value['latitude'], 
                                     value['longitude'], value['site']])
                # Error handling 
                # Throw exception if socket request hangs
                except socket.timeout: 
                    print("""Timeout occurred while waiting for data from client {}.
                          Network likely down: {}""".
                          format(key, time.strftime("%Y-%m-%d %H:%M:%S")))
                    continue
                # Log errors to service file error log
                except Exception as e: 
                    print("Unknown error with client {}: {}".format(key, e))
                    continue

        return raw_list
            
    def formatTagData(self, raw_data):
        # Blank list to append looped data to
        formatted_data = []
        # Loop through output string serial data and format
        # for clean append to postgres
        for client in raw_data:
            for info in client[0].splitlines():
                # Extract data exclusively beginning with "TAG"
                # This is how biomark denotes PIT detection serial data.
                # Only parses lines of length 49 as these are the ones without 
                # errors present from something like packet drop
                if 'TAG' in info and len(info) == 49:
                    reader_data = info.split(' ')[1:5] 
                    datetime = reader_data[1] + ' ' + reader_data[2]
                    # Order same as readout from IS1001
                    data = [reader_data[1], reader_data[2], reader_data[0], 
                            reader_data[3], client[2], client[3], client[1],
                            datetime, client[4]]
                    formatted_data.append(data)
        # Convert to tuple for .executemany method for psycopg
        return tuple(formatted_data)
