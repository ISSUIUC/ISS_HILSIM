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

def ready():
    return avionics.ready and server_port != None

def main():
    global server_port, tester_boards, board_id
    # TODO: Implement application-specific setup
    # TODO: Implement stack-specific setup
    # TODO: Implement Server-application communication (Serial communication)
    # TODO: Testing?

    # Initialize repository
    # avionics.first_setup()

    next_conn_debounce = time.time() + 0.5
    next_av_debounce = time.time() + 0.1

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
            print("(datastreamer) Attempting to detect avionics")
            avionics.detect_avionics([server_port])
            # let's just assume avionics is ready
            avionics.ready = True
            if(avionics.ready):
                print("(datastreamer) Avionics ready!")
            next_av_debounce = time.time() + 0.1

        listener_list = server.connected_comports
        if(server_port != None):
            listener_list = [server_port]

        # Process all incoming packets
        for comport in listener_list:
            if comport.in_waiting:
                data = port.read_all()
                packet_string = data.decode("utf8")
                valid, type, data = packet.decode_packet(packet_string)
                if not valid:
                    comport.write(packet.construct_invalid(packet_string).encode())
                else:
                    if type == "ACK":
                        if server_port == None:
                            server_port = comport
                            board_id = data['board_id']
                            print("(datastreamer) Connected to server!")
                            continue
                        else:
                            print("Recieved ACK packets from more than one source! Discarding second ACK.")
                            comport.write(packet.construct_invalid(packet_string).encode())
                            continue


                    if (not ready()):
                        print("(datastreamer) Recieved packet but not ready! Send ACK first.")
                        comport.write(packet.construct_invalid(packet_string).encode())
                        continue

                    match type:
                        case "IDENT?":
                            comport.write(packet.construct_id_confirm(config.board_type, board_id).encode())


            
            
        

    

    
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