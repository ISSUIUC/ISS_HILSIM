# Contains all communication packets required for server-datastreamer communication.
# Contains constructor functions for each packet and also a decode function for server packets.

import json

#### CLIENT PACKETS ####
def construct_ident(board_type: str):
    # Constructs IDENT packet
    packet_dict = {'type': "IDENT", 'data': {'board_type': board_type}}
    return json.dumps(packet_dict)

def construct_id_confirm(board_type: str, board_id: int):
    # Constructs ID-CONF packet
    packet_dict = {'type': "ID-CONF", 'data': {'board_type': board_type, 'board_id': board_id}}
    return json.dumps(packet_dict)

def construct_ready():
    # Constructs READY packet
    packet_dict = {'type': "READY", 'data': {}}
    return json.dumps(packet_dict)

def construct_done(job_data, hilsim_result: str):
    # Constructs DONE packet
    packet_dict = {'type': "DONE", 'data': {'job_data': job_data, 'hilsim_result': hilsim_result}}
    return json.dumps(packet_dict)

def construct_invalid(raw_packet):
    # Constructs INVALID packet
    packet_dict = {'type': "INVALID", 'data': {'raw_packet': raw_packet}}
    return json.dumps(packet_dict)

def construct_busy(job_data):
    # Constructs BUSY packet
    packet_dict = {'type': "BUSY", 'data': {'job_data': job_data}}
    return json.dumps(packet_dict)

def construct_job_update(job_status, current_log: list[str]):
    # Constructs JOB-UPD packet
    packet_dict = {'type': "JOB-UPD", 'data': {'job_status': job_status, 'hilsim_result': current_log}}
    return json.dumps(packet_dict)

def construct_pong():
    # Constructs PONG packet
    packet_dict = {'type': "PONG", 'data': {}}
    return json.dumps(packet_dict)

#### Intermediate data ####
def construct_job_status(job_ok: bool, current_action: str, status_text: str):
    return {"job_ok": job_ok, 'current_action': current_action, "status": status_text}

#### SERVER PACKETS ####
def decode_packet(packet: str):
    try:
        if "[raw==>]" in packet:
            # This is a job packet, we treat it differently.
            packet_split = packet.split("[raw==>]")
            job_packet = packet_split[0]
            raw_data = packet_split[1]
            packet_dict = json.loads(job_packet)
            packet_dict['data']['csv_data'] = raw_data
            return validate_server_packet(packet_dict['type'], packet_dict['data']), packet_dict['type'], packet_dict['data']
        packet_dict = json.loads(packet)
    except Exception as e:
        return False, "RAW", packet
    return validate_server_packet(packet_dict['type'], packet_dict['data']), packet_dict['type'], packet_dict['data']

def validate_server_packet(packet_type: str, packet_data):
    match packet_type:
        case "IDENT?":
            return True
        case "ACK":
            return "board_id" in packet_data
        case "REASSIGN":
            return "board_id" in packet_data
        case "TERMINATE":
            return True
        case "CYCLE":
            return True
        case "JOB":
            return "job_data" in packet_data and "csv_data" in packet_data
        case "PING":
            return True

    