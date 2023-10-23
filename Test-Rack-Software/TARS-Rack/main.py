# HILSIM Data-Streamer-RASPI [9/27/2023]
# HILSIM Server team:
# Michael Karpov (2027)
# ..your names here!..
#
#
#
# BRIEF: This server will run on the raspberryPi end of the hilsim testing rack, and its purpose
# will be to recieve job data and pass it on to whichever device is connected to this device, then send that data back.
# That's it! Work of when to run jobs/hardware cooldowns/getting jobs will be handled by the central server.

import av_platform.interface as avionics
import av_platform.stream_data as platform
import util.serial_wrapper as connection
import util.packets as packet
import util.config as config
import os
import time
import serial
from enum import Enum
import util.handle_packets as handle_packets
import util.datastreamer_server as Datastreamer

############### HILSIM Data-Streamer-RASPI ###############

def handle_error_state(Server: Datastreamer.DatastreamerServer):
    pass

def handle_job_setup_error(Server: Datastreamer.DatastreamerServer):
    pass

def handle_job_runtime_error(Server: Datastreamer.DatastreamerServer):
    pass

def handle_first_setup(Server: Datastreamer.DatastreamerServer):
    try:
        Server.board_type = config.board_type
        avionics.av_instance.first_setup()
        return True
    except Exception as e:
        return False
    
def should_heartbeat(Server: Datastreamer.DatastreamerServer):
    if(time.time() > Server.next_heartbeat_time):
        Server.next_heartbeat_time = time.time() + 3 # Heartbeat every 3 seconds
        return True
    return False

# Server connection
def send_wide_ident(Server: Datastreamer.DatastreamerServer):
    if(time.time() > Server.last_server_connection_check):
        connection.t_init_com_ports()
        for port in connection.connected_comports:
            packet.DataPacketBuffer.write_packet(packet.CL_IDENT(config.board_type), port)
        Server.last_server_connection_check += 0.25
    return True    
    

def check_server_connection(Server: Datastreamer.DatastreamerServer):
    global board_id, server_port
    for port in connection.connected_comports:
        in_packets = packet.DataPacketBuffer.serial_to_packet_list(port, True)
        for pkt in in_packets:
            if pkt.packet_type == packet.DataPacketType.ACKNOWLEDGE:
                Server.board_id = pkt.data['board_id']
                Server.server_port = port

                #temporary, close all non-server ports:
                for port in connection.connected_comports:
                    if(port.name != Server.server_port.name):
                        print("TEMP: closed " + port.name)
                        port.close()

                return True
    return False

def reset_connection_data(Server: Datastreamer.DatastreamerServer):
    Server.last_server_connection_check = time.time()
    Server.next_heartbeat_time = time.time() + 3
    connection.t_init_com_ports()
    for port in connection.connected_comports:
        connection.hard_reset(port)
    return True

def detect_avionics(Server: Datastreamer.DatastreamerServer):
    # Let's assume we can detect avionics already
    return True

def main():
    Server = Datastreamer.instance
    SState = Datastreamer.ServerStateController.ServerState # SState alias

    # Make sure setup is done before any transition:
    Server.state.add_transition_event(SState.INIT, SState.ANY, handle_first_setup) # Require repo first_setup to transition from INIT
    
    # FSM error handling:
    # Generic error
    Server.state.add_transition_event(SState.ANY, SState.ERROR, handle_error_state) 
    Server.state.add_transition_event(SState.JOB_SETUP, SState.JOB_ERROR, handle_job_setup_error)
    Server.state.add_transition_event(SState.JOB_RUNNING, SState.JOB_ERROR, handle_job_runtime_error)

    # Set up FSM flow:
    Server.state.add_transition_pipe(SState.INIT, SState.CONNECTING) # Always try to transition INIT => CONNECTING
    Server.state.add_transition_pipe(SState.CONNECTING, SState.AV_DETECT) # Always try to transition CONNECTING => AV_DETECT
    Server.state.add_transition_pipe(SState.AV_DETECT, SState.READY) # Always try to transition AV_DETECT => READY
    Server.state.add_transition_pipe(SState.JOB_SETUP, SState.JOB_RUNNING) # Always try to transition JOB_SETUP => JOB_RUNNING
    Server.state.add_transition_pipe(SState.JOB_RUNNING, SState.CLEANUP) # Always try to transition JOB_RUNNING => CLEANUP
    Server.state.add_transition_pipe(SState.CLEANUP, SState.READY) # Always try to transition CLEANUP => READY
    Server.state.add_transition_pipe(SState.JOB_ERROR, SState.CLEANUP) # Always try to transition JOB_ERROR => CLEANUP (for graceful recovery)
    
    # Connection checks
    Server.state.add_transition_event(SState.ANY, SState.CONNECTING, reset_connection_data)
    Server.state.add_transition_event(SState.CONNECTING, SState.AV_DETECT, send_wide_ident)
    Server.state.add_transition_event(SState.CONNECTING, SState.AV_DETECT, check_server_connection)
    Server.state.add_transition_event(SState.AV_DETECT, SState.READY, detect_avionics)

    handle_packets.add_transitions(Server.state)
    handle_packets.add_always_events(Server.state)


    while True:
        Server.tick()

        # Actions that always happen:
        if(Server.server_port != None and should_heartbeat(Server)):
            print("(heartbeat) Sent update at u+", time.time())
            Server.packet_buffer.add(packet.CL_HEARTBEAT(packet.HeartbeatServerStatus(Server.state.server_state, Server.server_start_time, False, False),
                                                  packet.HeartbeatAvionicsStatus(False, "")))
        # End "Always" actions.
        Server.packet_buffer.clear_input_buffer()
            

##########################################################

if __name__ == "__main__":
    main()
else:
    print("HILSIM Data streamer-raspi should not be run as an import! Try again by running this script directly.")
    exit(1)