import serial # Pyserial! Not serial
import serial.tools.list_ports
import util.config
import util.packets as packet

connected_comports = []

"""
Function to retrieve a list of comports connected to this device
@returns ListPortInfo[] A list of port data.
"""
def get_com_ports():
    return serial.tools.list_ports.comports()


"""
Close all initialized ports, then loop through each port and initialize it.
"""
def init_com_ports():
    print("(init_comports) Closing all initialized comports..")
    for port in connected_comports:
        port.close()
    print("(init_comports) Attempting to initialize all connected COM ports..")
    for port_data in get_com_ports():
        try:
            port = serial.Serial(port_data.device)
            connected_comports.append(port)
        except serial.SerialException as err:
            if("denied" in str(err)):
                for connected in connected_comports:
                    if(connected.name == port_data.device):
                        print("(init_comports) " + port_data.device + " already initialized")
                    else:
                        print("(init_comports) " + port_data.device + " cannot be initialized.")
                
            else:
                print(err)
            

"""
Function which sends an IDENT packet to a given port. This function will be called for every single port connected to the raspi until it gets
an ACK packet from the central server.
@param port: serial.Serial -- Port to send the IDENT packet to
"""
def send_ident(port: serial.Serial):
    port.write(packet.construct_ident(config.boa))

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