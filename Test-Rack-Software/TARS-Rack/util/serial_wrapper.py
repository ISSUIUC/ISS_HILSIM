import serial # Pyserial! Not serial
import serial.tools.list_ports
import util.config
import util.packets as packet

connected_comports: list[serial.Serial] = []

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
    if port.in_waiting:
        data = port.read_all()

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
            

"""
Function which sends an IDENT packet to a given port. This function will be called for every single port connected to the raspi until it gets
an ACK packet from the central server.
@param port: serial.Serial -- Port to send the IDENT packet to
"""
def send_ident(port: serial.Serial):
    port.write(packet.construct_ident(util.config.board_type).encode())

"""
The main function that handles all packets sent by the server, also returns the packet data to the caller.
"""
def handle_server_packet(port: serial.Serial, raw_packet: str):
    valid_packet, packet_type, packet_data = packet.decode_packet(raw_packet)
    if not valid_packet:
        port.write(packet.construct_invalid(raw_packet))
    else:
        # TODO: Handle server comm packets here.
        pass
    return valid_packet, packet_type, packet_data
    

"""
Ping all connected devices with an IDENT packet
"""
def ping_ident():
    for comport_info in get_com_ports():
        comport = serial.Serial(comport_info.device, 9600, timeout=10)
        send_ident(comport)