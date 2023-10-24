# This script provides a few wrapper functions for PySerial
import serial # Pyserial! Not serial
import serial.tools.list_ports
import util.packets as packet

connected_comports: list[serial.Serial] = []


def get_com_ports():
    """
    Function to retrieve a list of comports connected to this device
    @returns ListPortInfo[] A list of port data.
    """
    return serial.tools.list_ports.comports()


def close_com_ports():
    """Close all connected COMports"""
    print("(cloase_com_ports) Closing all initialized comports..")
    for port in connected_comports:
        port.close()

def close_port(port: serial.Serial):
    """Close a specific port"""
    port.close()

def clear_port(port: serial.Serial):
    """Clears all of the data in the port buffer"""
    port.reset_input_buffer()
    port.reset_output_buffer()
    print("(clear_port) Successfully cleared port " + port.name)


def hard_reset(port: serial.Serial):
    """Clears all of the data in the port buffer by closing the port and opening it back up"""
    port.close()
    port.open()
    print("(clear_port) Successfully hard reset port " + port.name)


alr_init = False
def t_init_com_ports():
    """
    TODO: Delete this!
    Test script for init_com_ports()
    """
    global alr_init
    init_com_ports()
    if alr_init == False:
        port = serial.Serial("COM8", write_timeout=0)
        connected_comports.append(port)
        alr_init = True
        print("(init_comports) Initialized port COM8")
    


def init_com_ports():
    """
    Loop through each port and try to initialize it if it's not already initialized
    """
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
            
