# DELETE THIS!

import serial
import sys
import sv_pkt as packet
import time

argc = len(sys.argv)

comport = "COM9"
port = serial.Serial(comport, write_timeout=1.0)

print("Init")
start = time.time()
delay_until_ack = 0.5; ack_run = False
delay_until_ident = 1; ident_run = False

while True:
    if port.in_waiting:
        data = port.read_all()
        packet_string = data.decode("utf8")
        valid, p_type, data = packet.decode_packet(packet_string)
        
        print( type(data) )
        print(valid, p_type, data)



