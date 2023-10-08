# Contains all communication packets required for the SERVER side of the server-datastreamer communication.
# Contains constructor functions for each packet and also a decode function for client packets.
import json

#### SERVER PACKETS ####
def construct_ident_probe():
    # Constructs IDENT? packet
    packet_dict = {'type': "IDENT?", 'data': {}}
    return json.dumps(packet_dict)

def construct_ping():
    # Constructs PING packet
    packet_dict = {'type': "PING", 'data': {}}
    return json.dumps(packet_dict)

def construct_acknowledge(board_id: int):
    # Constructs ACK packet
    packet_dict = {'type': "ACK", 'data': {'board_id': board_id}}
    return json.dumps(packet_dict)

def construct_reassign(board_id: int):
    # Constructs ACK packet
    packet_dict = {'type': "REASSIGN", 'data': {'board_id': board_id}}
    return json.dumps(packet_dict)

def construct_terminate():
    # Constructs TERMINATE packet
    packet_dict = {'type': "TERMINATE", 'data': {}}
    return json.dumps(packet_dict)

def construct_cycle():
    # Constructs TERMINATE packet
    packet_dict = {'type': "CYCLE", 'data': {}}
    return json.dumps(packet_dict)

def construct_job(job_data, flight_csv):
    # Constructs TERMINATE packet
    packet_dict = {'type': "JOB", 'data': {'job_data': job_data}}
    return json.dumps(packet_dict) + "[raw==>]" + flight_csv # [raw==>] used as delimiter

#### CLIENT PACKETS ####
def decode_packet(packet: str):
    packet_dict = json.loads(packet)
    if(type(packet_dict) == str):
        packet_dict = json.loads(packet_dict)
    return validate_client_packet(packet_dict['type'], packet_dict['data']), packet_dict['type'], packet_dict['data']

def validate_client_packet(packet_type: str, packet_data):
    match packet_type:
        case "IDENT":
            return "board_type" in packet_data
        case "ID-CONF":
            return "board_id" in packet_data and "board_type" in packet_data
        case "READY":
            return True
        case "DONE":
            return "hilsim_result" in packet_data and "job_data" in packet_data
        case "JOB-UPD":
            return "hilsim_result" in packet_data and "job_status" in packet_data
        case "INVALID":
            return "raw_packet" in packet_data
        case "BUSY":
            return "job_data" in packet_data
        case "PONG":
            return True


    