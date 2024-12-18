# This script provides a few wrapper functions for PySerial
import serial  # Pyserial! Not serial
import serial.tools.list_ports
import util.communication.packets as packet
import util.communication.serial_channel as serial_interface

connected_comports: list[serial_interface.SerialChannel] = []


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


def close_port(port: serial_interface.SerialChannel):
    """Close a specific port"""
    port.close()


def clear_port(port: serial_interface.SerialChannel):
    """Clears all of the data in the port buffer"""
    port.serial_port.reset_input_buffer()
    port.serial_port.reset_output_buffer()
    print("(clear_port) Successfully cleared port " + port.name)


def hard_reset(port: serial_interface.SerialChannel):
    """Clears all of the data in the port buffer by closing the port and opening it back up"""
    port.close()
    port.open()
    print("(clear_port) Successfully hard reset port " + port.serial_port.name)


alr_init = False


def t_init_com_ports():
    """
    TODO: Use to implement datastreamer tests
    https://github.com/orgs/ISSUIUC/projects/4/views/1?pane=issue&itemId=46714975
    Test script for init_com_ports()
    """
    global alr_init
    init_com_ports()
    if not alr_init:
        port = serial_interface.SerialChannel(
            serial.Serial("COM8", write_timeout=0))
        connected_comports.append(port)
        alr_init = True
        print("(init_comports) Initialized port COM8")


def init_com_ports():
    """
    Loop through each port and try to initialize it if it's not already initialized
    """
    print("(init_comports) Attempting to initialize all connected COM ports..")
    # Check if debug and then we can virtualize the serial channels
    for port_data in get_com_ports():
        try:
            port = serial_interface.SerialChannel(
                serial.Serial(port_data.device, write_timeout=0))
            connected_comports.append(port)
            print("(init_comports) Initialized port " + port_data.device)
        except serial.SerialException as err:
            if ("denied" in str(err)):
                for connected in connected_comports:
                    if (connected.serial_port.name == port_data.device):
                        print(
                            "(init_comports) " +
                            port_data.device +
                            " already initialized")

            else:
                print(err)
