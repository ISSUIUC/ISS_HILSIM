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
import util.serial_wrapper as server
import util.packets as packet
import util.config as config
import os
import time
import serial

############### HILSIM Data-Streamer-RASPI ###############

server_port: serial.Serial = None
tester_boards: list[serial.Serial] = None
board_id = -1
current_job: avionics.HilsimRun = None
current_job_data: dict = None
signal_abort = False
job_active = False

def ready():
    return avionics.ready and server_port != None

def setup_job(job_packet_data):
    global current_job
    current_job = avionics.HilsimRun(job_packet_data['csv_data'], job_packet_data['job_data'])
    current_job_data = job_packet_data['job_data']

def handle_server_packet(packet_type, packet_data, packet_string, comport: serial.Serial):
    global server_port, job_active
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

    if (not ready()):
        print("(datastreamer) Recieved packet but not ready! Send ACK first.")
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
            except Exception as e:
                log_string += "Job rejected: " + str(e)
                comport.write(packet.construct_invalid(packet_string).encode())
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

def main():
    global server_port, tester_boards, board_id, job_active
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
    while True: # Run setup
        # Are we in init state? (Don't have a server connected)
        if server_port == None and time.time() > next_conn_debounce:
            print("(datastreamer) Missing server connection! Running server probe")
            server.t_init_com_ports()
            for port in server.connected_comports:
                server.send_ident(port)

            next_conn_debounce = time.time() + 0.5
            

        if not avionics.ready and time.time() > next_av_debounce:
            avionics.detect_avionics([server_port], server_port != None)

            # Uncomment line below if testing with actual avionics
            # avionics.ready = True

            if(avionics.ready):
                print("(datastreamer) Avionics ready!")
            next_av_debounce = time.time() + 0.1

        listener_list = server.connected_comports
        if(server_port != None):
            listener_list = [server_port]

        # Reads all comport data and acts on it
        read_data(listener_list)

        def send_running_job_status(job_status_packet):
            server_port.write(packet.construct_job_update(job_status_packet, current_job.get_current_log()).encode())
            print(f"(current_job_status) Is_OK: {str(job_status_packet['job_ok'])}, Current action: {job_status_packet['current_action']}, Status: {job_status_packet['status']}")

        # Runs currently active job (If any)
        if(job_active):
            if(last_job_loop_time != time.time()):
                dt = time.time() - last_job_loop_time
                run_finished, run_errored, cur_log = current_job.step(dt, send_running_job_status)
                
                
                # CURRENT ISSUE:
                # Doesn't stream enough data.


                
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