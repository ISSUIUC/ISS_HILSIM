import util.communication.communication_interface as communication_interface
import serial

class SerialChannel(communication_interface.CommunicationChannel):
    serial_port: serial.Serial = None
    def __init__(self, serial_port: serial.Serial) -> None:
        self.serial_port = serial_port
        self.is_open = serial_port.is_open

    def open(self) -> None:
        self.serial_port.open()

    def close(self) -> None:
        self.serial_port.close()

    def waiting_in(self) -> bool:
        return self.serial_port.in_waiting > 0
    
    def waiting_out(self) -> bool:
        return self.serial_port.out_waiting > 0
    
    def read(self) -> str:
        if(self.serial_port.in_waiting):
            instr = ""
            while(self.serial_port.in_waiting):
                data = self.serial_port.read_all()
                string = data.decode("utf8")   
                if string:
                    instr += string
            return instr
        return ""
    
    def write(self, data: str) -> None:
        self.serial_port.write(data.encode())
