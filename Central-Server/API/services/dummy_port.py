import serial
import json

port = serial.Serial("COM9", timeout=5, write_timeout=0)

print(json.loads('{"packet_type": 4, "packet_data": {}, "use_raw": true}'))

while True:
    pass