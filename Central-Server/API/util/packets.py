# Contains all communication packets required for server-datastreamer communication.
# Contains constructor functions for each packet and also a decode function for server packets.

import json
from enum import Enum
import serial

class PacketDeserializeException(Exception):
    "Raised a packet fails to deserialize"
    def __init__(self, packet_string, reason="Generic deserialization error", message="Failed to deserialize packet"):
        self.packet_string = packet_string
        self.message = message
        self.reason = reason
        if len(self.packet_string) > 100:
            self.packet_string = self.packet_string[0:99] + ".. (rest hidden)"
        super().__init__(self.message + " " + packet_string + " ==> " + self.reason)

class DataPacketType(int, Enum):
    IDENT = 0
    ID_CONFIRM = 1
    READY = 2
    DONE = 3
    INVALID = 4
    BUSY = 5
    JOB_UPDATE = 6
    PONG = 7
    HEARTBEAT = 8
    # Server packets
    IDENT_PROBE = 100
    PING = 101
    ACKNOWLEDGE = 102
    REASSIGN = 103
    TERMINATE = 104
    CYCLE = 105
    JOB = 106
    # Misc packets
    RAW = 200

class DataPacket:
    """
    A class that stores the relevant data for any type of data packet
    """
    packet_type: str = "RAW"
    data: dict = None
    use_raw: bool = False
    raw_data: str = ""

    def __init__(self, p_type:DataPacketType, p_data:dict, data_raw=None) -> None:
        """
        Initializes the data packet. With raw data capabilities if raw_data is passed in.
        @p_type: The type of packet
        @p_data: Data stored within the packet
        @data_raw: The raw string to be decoded
        """
        self.packet_type = p_type
        self.data = p_data
        if data_raw != None:
            self.use_raw = True
            self.raw_data = data_raw

    def safe_deserialize(self, packet_string: str) -> None:
        """
        Deserializes a packet, running through possibilities of recoverable errors if an error is encountered.
        **CAREFUL!** This is an expensive operation, and should only be used if you are not sure if the stream is clear.
        """
        offset = 0

        while(offset < len(packet_string)):
            try:
                self.deserialize(packet_string[offset:])
                return
            except:
                offset += 1
            

    def deserialize(self, packet_string: str) -> None:
        """
        Deserialization constructor for DataPacket
        @packet_string: Raw packet string to deserialize
        """
        packet_header = None
        if "[[raw==>]]" in packet_string:
            # If the packet uses raw:
            self.use_raw = True
            p_split = packet_string.split("[[raw==>]]") # Element 0 will be proper packet json, element 1 will be raw data
            try:
                self.data = json.loads(p_split[0])['packet_data']
                packet_header = json.loads(p_split[0])
            except:
                raise PacketDeserializeException(packet_string, "Unable to deserialize packet header JSON")
            self.raw_data = p_split[1]

        else:
            # If the packet does not use raw:
            self.use_raw = False
            try:
                self.data = json.loads(packet_string)['packet_data']
                packet_header = json.loads(packet_string)
            except Exception as e:
                raise PacketDeserializeException(packet_string, "Unable to deserialize packet header JSON")

        # Set proper enum value
        if "packet_type" in packet_header:
            self.packet_type = DataPacketType(packet_header['packet_type'])
        else:
            raise PacketDeserializeException(packet_string, "Unable to access packet_type key in packet data")
    def serialize(self) -> str:
        """
        Serializes one packet to a raw data string
        """
        packet_dict = {'packet_type': self.packet_type, 'packet_data': self.data, 'use_raw': self.use_raw}
        string_construct = json.dumps(packet_dict)
        if(self.use_raw):
            string_construct +=  "[[raw==>]]" + self.raw_data
        return string_construct

    def __len__(self) -> int:
        return len(self.serialize())

    def __str__(self) -> str:
        if self.use_raw:
            if(len(self.raw_data) > 50):
                return "<packet:" + str(self.packet_type) + "> " + str(self.data) + " [raw: +" + str(len(self.raw_data)) + "c]"
            else:
                return "<packet:" + str(self.packet_type) + "> " + str(self.data) + " [raw: " + self.raw_data + "]"
        else:
            return "<packet:" + str(self.packet_type) + "> " + str(self.data)
        
class DataPacketBuffer:
    """
    A utility class for encoding and decoding data streams with packets.
    """
    packet_buffer: list[DataPacket] = []
    input_buffer: list[DataPacket] = []

    def __init__(self, packet_list:list[DataPacket]=[]) -> None:
        self.packet_buffer = packet_list

    def add(self, packet: DataPacket) -> None:
        """Adds a packet to the packet buffer"""
        self.packet_buffer.append(packet)

    def write_buffer_to_serial(self, serial_port: serial.Serial) -> None:
        """
        Writes the entire packet buffer to serial
        """
        serialized_full: str = self.to_serialized_string()
        self.packet_buffer = []
        serial_port.write(serialized_full.encode())


    def write_packet(packet: DataPacket, serial_port: serial.Serial) -> None:
        """
        Writes a single packet to serial
        WARNING: using `write_packet` twice in a row will cause a deserialization error to be thrown due to a lack of a delimeter.
        """
        serial_port.write(packet.serialize().encode())

    def to_serialized_string(self) -> None:
        """
        Serializes the packet buffer
        """
        serialized_packets: list[str] = []
        for packet in self.packet_buffer:
            serialized_packets.append(packet.serialize())
        serialized_full: str = "[[pkt_end]]".join(serialized_packets)
        return serialized_full

    def stream_to_packet_list(stream: str, safe_deserialize:bool=False) -> list[DataPacket]:
        """
        Converts serialized packet buffer to a list of packets
        """
        serialized_packets = stream.split("[[pkt_end]]")
        ds_packets: list[DataPacket] = []
        for ser_pkt in serialized_packets:
            new_packet = DataPacket(DataPacketType.RAW, {})
            if(safe_deserialize):
                new_packet.safe_deserialize(ser_pkt)
            else:
                new_packet.deserialize(ser_pkt)

            ds_packets.append(new_packet)
        return ds_packets
    
    def read_to_input_buffer(self, port: serial.Serial) -> None:
        """
        Appends all current packets in the port's buffer into the DataPacketBuffer input buffer.
        """
        in_buffer = DataPacketBuffer.serial_to_packet_list(port)
        for in_packet in in_buffer:
            self.input_buffer.append(in_packet)
            
    def serial_to_packet_list(port: serial.Serial, safe_deserialize:bool=False) -> list[DataPacket]:
        """
        Converts all packets in a serial port's input buffer into a list of packets.
        """
        if(port.in_waiting):
            instr = ""
            while(port.in_waiting):
                data = port.read_all()
                string = data.decode("utf8")   
                if string:
                    instr += string
            return DataPacketBuffer.stream_to_packet_list(instr, safe_deserialize)
        return []

    def clear_input_buffer(self):
        """
        Clears this input buffer
        """
        self.input_buffer = []
        


class JobData:
    class GitPullType(int, Enum):
        BRANCH = 0 # Pull a branch
        COMMIT = 1 # Pull a specific commit
    
    class JobType(int, Enum):
        DEFAULT = 0 # Pull code, flash, run hilsim, return result
        DIRTY = 1 # Run hilsim with whatever is currently flashed, return result (tbd)
        TEST = 2 # Run some sort of test suite (tbd)

    class JobPriority(int, Enum):
        NORMAL = 0 # Normal priority, goes through queue like usual
        HIGH = 1 # High priority, get priority in the queue


    job_id:int
    pull_type: GitPullType = GitPullType.BRANCH # Whether to pull from a branch or a specific commit (or other target)
    pull_target: str = "master" # Which commit id / branch to pull from
    job_type: JobType = JobType.DEFAULT
    job_author_id: str = "" # We won't allow anonymous jobs, and we don't know what the id will look like yet, so this is a placeholder
    job_priority: JobPriority = JobPriority.NORMAL # Only 2 states for now, but we can add more later if we come up with something else
    job_timestep: int = 1 # How "precise" the job should be. 1 is the highest, higher numbers mean that some data points will be skipped but the job runs faster

    def __init__(self, job_id, pull_type: GitPullType=GitPullType.BRANCH, pull_target:str="master",
                 job_type:JobType=JobType.DEFAULT, job_author_id:str="", job_priority:JobPriority=JobPriority.NORMAL,
                 job_timestep:int=1) -> None:
        self.job_id = job_id
        self.pull_type = pull_type
        self.pull_target = pull_target
        self.job_type = job_type
        self.job_author_id = job_author_id
        self.job_priority = job_priority
        self.job_timestep = job_timestep

    def to_dict(self) -> dict:
        return {'job_id': self.job_id, 'pull_type': self.pull_type, 'pull_target': self.pull_target,
                'job_type': self.job_type, 'job_author_id': self.job_author_id, 'job_priority': self.job_priority,
                'job_timestep': self.job_timestep}



class JobStatus:
    """Static class for making job statuses"""
    class JobState(int, Enum):
        IDLE = 0
        ERROR = 1
        SETUP = 2
        RUNNING = 3
        
    job_state: JobState = JobState.IDLE
    current_action: str = ""
    status_text: str = ""
    def __init__(self, job_state: JobState, current_action:str, status_text:str) -> None:
        self.job_state = job_state
        self.current_action = current_action
        self.status_text = status_text

    def to_dict(self) -> dict:
        return {'job_state': self.job_state, 'current_action': self.current_action, 'status_text': self.status_text}

class HeartbeatServerStatus:
    server_state: Enum # ServerState, from main.
    server_startup_time: float # (Time.time())
    is_busy: bool # Current job running, being set up, or in cleanup.
    is_ready: bool # Ready for another job

    def __init__(self, server_state: Enum, server_startup_time: float,
                 is_busy: bool, is_ready: bool) -> None:
        self.server_state = server_state
        self.server_startup_time = server_startup_time
        self.is_busy = is_busy
        self.is_ready = is_ready

    def to_dict(self) -> dict:
        return {'server_state': self.server_state, 'server_startup_time': self.server_startup_time,
         'is_busy': self.is_busy, 'is_ready': self.is_ready}


class HeartbeatAvionicsStatus:
    connected:bool # Connected to server
    avionics_type:str # May turn this into an enum
    # More debug info to come

    def __init__(self, connected:bool, avionics_type:str) -> None:
        self.connected = connected
        self.avionics_type = avionics_type

    def to_dict(self):
        return {'connected': self.connected, 'avionics_type':self.avionics_type}
        

#### CLIENT PACKETS ####
# Client packets are prefixed with CL
def CL_IDENT(board_type: str) -> DataPacket:
    """Constructs IDENT packet
    @board_type: The type of avionics stack for this packet"""
    packet_data = {'board_type': board_type}
    return DataPacket(DataPacketType.IDENT, packet_data)

def CL_ID_CONFIRM(board_type: str, board_id: int) -> DataPacket:
    """Constructs ID_CONFIRM packet
    @board_type: The type of avionics stack connected to this server
    @board_id: The ID assigned to this board before server restart."""
    packet_data = {'board_type': board_type, 'board_id': board_id}
    return DataPacket(DataPacketType.ID_CONFIRM, packet_data)

def CL_READY() -> DataPacket:
    """Constructs READY packet"""
    packet_data = {}
    return DataPacket(DataPacketType.READY, packet_data)

def CL_DONE(job_data: JobData, hilsim_result:str) -> DataPacket:
    """Constructs DONE packet (RAW)
    @job_data: The job data sent along with this packet (For ID purposes)
    @hilsim_result: Raw string of the HILSIM output"""
    packet_data = {'job_data': job_data.to_dict()}
    return DataPacket(DataPacketType.READY, packet_data, hilsim_result)

def CL_INVALID(invalid_packet:DataPacket) -> DataPacket:
    """Constructs INVALID packet (RAW)
    @raw_packet: The packet that triggered the INVALID response"""
    packet_data = {}
    return DataPacket(DataPacketType.INVALID, packet_data, str(invalid_packet))

def CL_BUSY(job_data: JobData) -> DataPacket:
    """Constructs BUSY packet
    @job_data: Job data for current job"""
    packet_data = {'job_data': job_data.to_dict()}
    return DataPacket(DataPacketType.BUSY, packet_data)

def CL_JOB_UPDATE(job_status: JobStatus, current_log: str) -> DataPacket:
    """Constructs JOB_UPDATE packet (RAW)
    @job_status: State of current job
    @current_log: Current outputs of HILSIM
    """
    packet_data = {'job_status': job_status.to_dict()}
    return DataPacket(DataPacketType.JOB_UPDATE, packet_data, current_log)

def CL_PONG() -> DataPacket:
    """Constructs PONG packet"""
    packet_data = {}
    return DataPacket(DataPacketType.PONG, packet_data)

def CL_HEARTBEAT(server_status: HeartbeatServerStatus, av_status: HeartbeatAvionicsStatus) -> DataPacket:
    """Constructs HEARTBEAT packet
    @server_status: State of the serve
    @av_status: Connection and working status of avionics.
    """
    packet_data = {'server_status': server_status.to_dict(), "avionics_status": av_status.to_dict()}
    return DataPacket(DataPacketType.HEARTBEAT, packet_data)

#### SERVER PACKETS ####
# Server packets are prefixed with SV
def SV_IDENT_PROBE() -> DataPacket:
    """Constructs IDENT_PROBE packet"""
    packet_data = {}
    return DataPacket(DataPacketType.IDENT_PROBE, packet_data)

def SV_PING() -> DataPacket:
    """Constructs PING packet"""
    packet_data = {}
    return DataPacket(DataPacketType.PING, packet_data)

def SV_ACKNOWLEDGE(board_id: int) -> DataPacket:
    """Constructs IDENT_PROBE packet"""
    packet_data = {'board_id': board_id}
    return DataPacket(DataPacketType.ACKNOWLEDGE, packet_data)

def SV_REASSIGN(board_id: int) -> DataPacket:
    """Constructs REASSIGN packet"""
    packet_data = {'board_id': board_id}
    return DataPacket(DataPacketType.REASSIGN, packet_data)

def SV_TERMINATE() -> DataPacket:
    """Constructs TERMINATE packet"""
    packet_data = {}
    return DataPacket(DataPacketType.TERMINATE, packet_data)

def SV_CYCLE() -> DataPacket:
    """Constructs CYCLE packet"""
    packet_data = {}
    return DataPacket(DataPacketType.CYCLE, packet_data)

def SV_JOB(job_data: JobData, flight_csv: str) -> DataPacket:
    """Constructs JOB packet"""
    packet_data = {'job_data': job_data.to_dict()}
    return DataPacket(DataPacketType.JOB, packet_data, flight_csv)

class PacketValidator:
    def is_server_packet(packet: DataPacket):
        return packet.packet_type.value > 99 and packet.packet_type.value < 199
    
    def is_client_packet(packet: DataPacket):
        return packet.packet_type.value > -1 and packet.packet_type.value < 99

    def validate_server_packet(server_packet: DataPacket):
        match server_packet.packet_type:
            case DataPacketType.IDENT_PROBE:
                return True
            case DataPacketType.ACKNOWLEDGE:
                return "board_id" in server_packet.data
            case DataPacketType.REASSIGN:
                return "board_id" in server_packet.data
            case DataPacketType.TERMINATE:
                return True
            case DataPacketType.CYCLE:
                return True
            case DataPacketType.JOB:
                return "job_data" in server_packet.data and server_packet.use_raw
            case DataPacketType.PING:
                return True

    def validate_client_packet(client_packet: DataPacket):
        match client_packet.packet_type:
            case DataPacketType.IDENT:
                return "board_type" in client_packet.data
            case DataPacketType.ID_CONFIRM:
                return "board_id" in client_packet.data and "board_type" in client_packet.data
            case DataPacketType.READY:
                return True
            case DataPacketType.DONE:
                return client_packet.use_raw and "job_data" in client_packet.data
            case DataPacketType.JOB_UPDATE:
                return client_packet.use_raw and "job_status" in client_packet.data
            case DataPacketType.INVALID:
                return client_packet.use_raw
            case DataPacketType.BUSY:
                return "job_data" in client_packet.data
            case DataPacketType.PONG:
                return True