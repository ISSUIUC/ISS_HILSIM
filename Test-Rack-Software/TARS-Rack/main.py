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
        avionics.first_setup()
        return True
    except:
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
            

def send_ready():
    global server_port
    connection.write_to_buffer(server_port, packet.construct_ready())
    connection.write_all(server_port)

def setup_job(job_packet_data):
    global current_job
    while(server_port.in_waiting):
        data = server_port.read_all()
        string = data.decode("utf8")   
        if string:
            job_packet_data['csv_data'] += string
    
    current_job = avionics.HilsimRun(job_packet_data['csv_data'], job_packet_data['job_data'])
    current_job_data = job_packet_data['job_data']

def handle_server_packet(packet_type, packet_data, packet_string, comport: serial.Serial):
    global server_port, job_active, signal_abort
    if(packet_type != "JOB"):
        print("Handling packet << " + packet_string)
    else:
        print("Handling packet << " + packet_type + f" ({packet_data['job_data']}) + [hidden csv data]")
    global server_port, board_id
    if packet_type == "ACK":
        if server_port == None:
            server_port = comport
            board_id = packet_data['board_id']
            print("(datastreamer) Connected to server as board " + str(board_id) + "!")
            return
        else:
            print("Recieved ACK packets from more than one source! Discarding second ACK.")
            comport.write(packet.construct_invalid(packet_string).encode())
            return

    log_string = ""
    match packet_type:
        case "IDENT?":
            comport.write(packet.construct_id_confirm(config.board_type, board_id).encode())
            log_string += "Sending packet >> " + packet.construct_id_confirm(config.board_type, board_id)
        case "PING":
            comport.write(packet.construct_pong().encode())
            log_string += "Sending packet >> " + packet.construct_pong()
        case "REASSIGN":
            if(board_id != -1):
                new_id = packet_data['board_id']
                log_string += "Reassigned board ID (" + str(board_id) + " ==> " + str(new_id) + ")" 
                board_id = new_id
            else:
                comport.write(packet.construct_invalid(packet_string).encode())
                log_string += "Recieved REASSIGN packet but this board has not been initialized"
        case "JOB":
            try:
                setup_job(packet_data)
                job_status = packet.construct_job_status(True, "Setup", "Accepted")
                log_string += "Job set up"
                print("(handle_packet) Job accepted")
                comport.write(packet.construct_job_update(job_status, []).encode())

                # Returns true if the job should be canceled.
                def cancel_job():
                    read_data([server_port])
                    return signal_abort
                
                completed, status = current_job.job_setup(cancel_job)
                job_status = packet.construct_job_status(completed, "Setup", status)
                comport.write(packet.construct_job_update(job_status, []).encode())

                if(completed):
                    job_active = True
                    job_clock_reset = False
                elif (signal_abort):
                    send_ready()
            except Exception as e:
                log_string += "Job rejected: " + str(e)
                comport.write(packet.construct_invalid(packet_string).encode())
        case "TERMINATE":
            # Terminate currently running job
            signal_abort = True

    if(log_string == ""):
        log_string = "(handle_packet) No special log string for pkt\n" + packet_string
    else:
        log_string = "(handle_packet) " + log_string
    print(log_string)

def read_data(listener_list: list[serial.Serial]):
    # Process all incoming packets (Caution! Will process EVERYTHING before server is connected!)
    for comport in listener_list:
        if comport.in_waiting:
            data = comport.read_all()
            packet_string = data.decode("utf8")
            valid, type, data = packet.decode_packet(packet_string)
            if not valid:
                # If it's not valid, it's either not a valid packet, or type="RAW" (just a string)
                if type == "RAW":
                    avionics.handle_raw(packet_string)
                else:
                    # invalid packet
                    comport.write(packet.construct_invalid(packet_string).encode())
            else:
                # Is server packet
                handle_server_packet(type, data, packet_string, comport)

def main_old():
    global server_port, board_id, job_active, job_clock_reset
    # TODO: Implement application-specific setup
    # TODO: Implement stack-specific setup
    # TODO: Implement Server-application communication (Serial communication)
    # TODO: Testing?

    # Initialize repository
    # avionics.first_setup()

    next_conn_debounce = time.time() + 0.5
    next_av_debounce = time.time() + 0.1
    last_job_loop_time = time.time()

    print("(datastreamer) first setup done")
    while True: 
        # Are we in init state? (Don't have a server connected)
        if server_port == None and time.time() > next_conn_debounce:
            print("(datastreamer) Missing server connection! Running server probe")
            connection.t_init_com_ports()
            for port in connection.connected_comports:
                connection.send_ident(port)
            next_conn_debounce = time.time() + 0.5
            

        if not avionics.ready and time.time() > next_av_debounce:
            avionics.detect_avionics([server_port], server_port != None)

            # Uncomment line below if testing with actual avionics
            # avionics.ready = True

            if(avionics.ready):
                print("(datastreamer) Avionics ready!")
            next_av_debounce = time.time() + 0.1

        listener_list = connection.connected_comports
        if(server_port != None):
            listener_list = [server_port]

        # Reads all comport data and acts on it
        read_data(listener_list)

        def send_running_job_status(job_status_packet):
            server_port.write(packet.construct_job_update(job_status_packet, current_job.get_current_log()).encode())
            print(f"(current_job_status) Is_OK: {str(job_status_packet['job_ok'])}, Current action: {job_status_packet['current_action']}, Status: {job_status_packet['status']}")

        # Runs currently active job (If any)
        if(job_active):
            if(signal_abort):
                # Stop job immediately and notify server of status
                job_active = False
                job_status = packet.construct_job_status(False, "Stopped", "The job has been forcefully stopped")
                print("(run_job) Job terminated")
                
                connection.write_to_buffer(server_port, packet.construct_job_update(job_status, current_job.get_current_log()))
                send_ready()
                continue

            if(job_clock_reset == False):
                current_job.reset_clock()
                job_clock_reset = True
                last_job_loop_time = time.time()
            
            
            if(last_job_loop_time != time.time()):
                dt = time.time() - last_job_loop_time
                run_finished, run_errored, cur_log = current_job.step(dt, send_running_job_status)
                
                if(run_finished):
                    job_active = False
                    pass

                if(run_errored):
                    job_active = False
                    pass

                last_job_loop_time = time.time()
        
        


            
            
        

    

    
    print("(main) Waiting 5s for port to open back up")
    time.sleep(5) # Wait for port to start back up
    
    s.init_com_ports()
    port = getfirstport()
    if(not port):
       return

    # Run hilsim (jank for now)
    file = open(os.path.join(os.path.dirname(__file__), "./av_platform/flight_computer.csv"), 'r')
    text = file.read()
    
    print()
    def noout(t):
        print(t['status'], end='\r')
    hilsim_result = platform.run_hilsim(text, port, noout)
    print()

    logfile = os.path.join(os.path.dirname(__file__), "./post_return.txt")

    f = open(logfile, "w", encoding="utf-8")
    f.write(hilsim_result.replace("\r\n", "\n"))
    print("(main) Finished remote hilsim run!")
    git.remote_reset()

    pass


##########################################################

if __name__ == "__main__":
    main()
else:
    print("HILSIM Data streamer-raspi should not be run as an import! Try again by running this script directly.")
    exit(1)