# DELETE THIS!

import serial
import sys
import sv_pkt as packet

argc = len(sys.argv)

comport = "COM9"
port = serial.Serial(comport, write_timeout=1.0)

if(argc == 1):
    print("Needs a packet <ACK| ... >")
    exit(1)

pkt = sys.argv[1]

match pkt:
    case "ACK":
        port.write(packet.construct_acknowledge(0).encode())
    case "IDENT?":
        port.write(packet.construct_ident_probe().encode())

print("Sent")
while True:
    if port.in_waiting:
        data = port.read_all()
        packet_string = data.decode("utf8")
        print(packet_string)



