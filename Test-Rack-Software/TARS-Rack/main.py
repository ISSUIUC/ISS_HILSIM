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

import av_platform.run_setup as run
import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as s
import av_platform.stream_data as platform
import os
import time

############### HILSIM Data-Streamer-RASPI ###############

def getfirstport():
    if(len(s.connected_comports) > 0):
        return s.connected_comports[0]
    else:
        print("didn't find any ports.")
        return False

def main():
    # TODO: Implement application-specific setup
    # TODO: Implement stack-specific setup
    # TODO: Implement Server-application communication (Serial communication)
    # TODO: Testing?

    git.remote_clone()
    git.remote_reset()
    pio.pio_clean()
    git.remote_pull_branch("AV-999/protobuf-integration")

    port = getfirstport()
    if(not port):
       return

    try:
        pio.pio_upload("mcu_hilsim")
    except:
        pio.pio_upload("mcu_hilsim")
    
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