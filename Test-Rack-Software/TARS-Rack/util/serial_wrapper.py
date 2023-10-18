import serial # Pyserial! Not serial
import serial.tools.list_ports
import util.config
import util.packets as packet
import json

connected_comports: list[serial.Serial] = []
packet_buffer: dict = {}

"""
Function to retrieve a list of comports connected to this device
@returns ListPortInfo[] A list of port data.
"""
def get_com_ports():
    return serial.tools.list_ports.comports()


"""Close all connected COMports"""
def close_com_ports():
    print("(cloase_com_ports) Closing all initialized comports..")
    for port in connected_comports:
        port.close()

def close_port(port: serial.Serial):
    print("(cloase_com_ports) Closing " + port.name)
    for comport in connected_comports:
        if(comport.name == port.name):
            comport.close()

"""Clears all of the data in the port buffer"""
def clear_port(port: serial.Serial):
    port.reset_input_buffer()
    port.reset_output_buffer()
    print("(clear_port) Successfully cleared port " + port.name)

"""Clears all of the data in the port buffer"""
def hard_reset(port: serial.Serial):
    port.close()
    port.open()
    print("(clear_port) Successfully hard reset port " + port.name)

"""
TODO: Delete this!
Test script for init_com_ports()
"""
alr_init = False
def t_init_com_ports():
    global alr_init
    init_com_ports()
    if alr_init == False:
        port = serial.Serial("COM8", write_timeout=0)
        connected_comports.append(port)
        alr_init = True
        print("(init_comports) Initialized port COM8")
    

"""
Loop through each port and try to initialize it if it's not already initialized
"""
def init_com_ports():
    print("(init_comports) Attempting to initialize all connected COM ports..")
    for port_data in get_com_ports():
        try:
            port = serial.Serial(port_data.device, write_timeout=0)
            connected_comports.append(port)
            print("(init_comports) Initialized port " + port_data.device)
        except serial.SerialException as err:
            if("denied" in str(err)):
                for connected in connected_comports:
                    if(connected.name == port_data.device):
                        print("(init_comports) " + port_data.device + " already initialized")
                
            else:
                print(err)
            
