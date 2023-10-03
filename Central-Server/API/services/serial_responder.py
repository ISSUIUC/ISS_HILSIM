import serial
import time
import json
import sys
import os

stored_board_id = -1

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.packets as pkt
import util.client_packets as cl_pkt

ser = serial.Serial("COM9")
print("connected")

def tobinary(dict):
    return (json.dumps(dict) + "\n").encode()

if ser.in_waiting:
    data = ser.read_all()
    print("Cleared " + str(len(data)) + " bytes from memory")

while True:
    if ser.in_waiting:
        data = ser.read_all()
        string = data.decode("utf8")
        print("Got " + string)

        if string:
            if string == "!test_reset":
                stored_board_id = -1
                print("RESET TEST ENV \n\n")
                continue
            obj = json.loads(string)
            valid, type, data = cl_pkt.decode_packet(string)

            match type:
                case "PING":
                    print("Sending: ", cl_pkt.construct_pong())
                    ser.write(tobinary(cl_pkt.construct_pong()))
                case "IDENT?":
                    print("Sending: ", cl_pkt.construct_id_confirm("TARS", stored_board_id))
                    ser.write(tobinary(cl_pkt.construct_id_confirm("TARS", stored_board_id)))
                case "ACK":
                    print(stored_board_id)
                    if(stored_board_id == -1):
                        stored_board_id = int(data['board_id'])
                    else:
                        print("Sending: ", cl_pkt.construct_invalid(string))
                        ser.write(tobinary(cl_pkt.construct_invalid(string)))
                case "REASSIGN":
                    if(stored_board_id != -1):
                        stored_board_id = int(data['board_id'])
                    else:
                        print("Sending: ", cl_pkt.construct_invalid(string))
                        ser.write(tobinary(cl_pkt.construct_invalid(string)))