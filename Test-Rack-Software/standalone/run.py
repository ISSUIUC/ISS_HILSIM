# Datastreamer standalone entry point
# Spec @ https://github.com/orgs/ISSUIUC/projects/4/views/1?pane=issue&itemId=52868143

# Implement standalone datastreamer functionality
# Implement new state machine
# Add ability to write to this directory (or `./output`) after runs finish.
# Reuse as much of the already written code as possible.
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import config
import job_config
from util import serial_wrapper as connection
from util.communication import packets as packet
import time
from util import avionics_meta as AVMeta
from util import datastreamer_server as Datastreamer
from util.communication import ws_channel as ws_channel
from util.communication import communication_interface as comm
import threading
from util import handle_jobs as jobs
import util.communication.packets as pkt


avionics = config.use_interface
av_meta: AVMeta.PlatformMetaInterface = config.use_meta

def handle_error_state(Server: Datastreamer.DatastreamerServer):
    # Recoverable error
    pass

def handle_first_setup(Server: Datastreamer.DatastreamerServer):
    try:
        Server.board_type = av_meta.board_type
        avionics.av_instance.first_setup()
        return True
    except Exception as e:
        print(e)
        return False

def detect_avionics(Server: Datastreamer.DatastreamerServer):
    try:
        return avionics.av_instance.detect()
    except Exception as e:
        print("(detect_avionics) Detect_avionics encountered an error during the detection process:")
        print(e)
        print()

def on_ready(Server: Datastreamer.DatastreamerServer):
    Server.signal_abort = False

    print("(transition_to_ready) Reset fail flags and sent READY packet.")

def halt(Server: Datastreamer.DatastreamerServer):
    exit(0)
    return True

def main():
    Server = Datastreamer.instance

     # END Server config setup
    SState = Datastreamer.ServerStateController.ServerState  # SState alias

    # Make sure setup is done before any transition:
    # Require repo first_setup to transition from INIT
    Server.state.add_transition_event(
        SState.INIT, SState.ANY, handle_first_setup)

    # FSM error handling:
    # Generic error
    Server.state.add_transition_event(
        SState.ANY, SState.ERROR, handle_error_state)

    # Set up FSM flow:
    # Always try to transition INIT => CONNECTING
    Server.state.add_transition_pipe(SState.INIT, SState.AV_DETECT)
    # Always try to transition AV_DETECT => READY
    Server.state.add_transition_pipe(SState.AV_DETECT, SState.READY)
    # Always try to transition JOB_SETUP => JOB_RUNNING
    Server.state.add_transition_pipe(SState.JOB_SETUP, SState.JOB_RUNNING)
    # Always try to transition JOB_RUNNING => CLEANUP
    Server.state.add_transition_pipe(SState.JOB_RUNNING, SState.CLEANUP)
    # Always try to transition CLEANUP => READY
    Server.state.add_transition_pipe(SState.CLEANUP, SState.HALT)

    
    Server.state.add_transition_event(
        SState.AV_DETECT, SState.READY, detect_avionics)
    
    Server.state.add_success_event(SState.ANY, SState.READY, on_ready)

    Server.state.add_always_event(SState.HALT, halt)
    
    jobs.handle_standalone_job_transitions(Server.state)

    print()

    while True:
        Server.tick()

        if Server.state.server_state == SState.READY:
            raw_csv = ""

            Server.current_job_data = pkt.JobData(-1, job_config.PULL_TYPE, 
                                                job_config.PULL_TARGET, pkt.JobData.JobType.DEFAULT, 
                                                pkt.JobData.JobPriority.HIGH, 0.1)

            Server.current_job = avionics.HilsimRun(Server, avionics.av_instance, raw_csv, Server.current_job_data)
            
            Server.state.try_transition(SState.JOB_SETUP)

        Server.packet_buffer.clear_input_buffer()

if __name__ == "__main__":
    main()
else:
    print("Datastreamer standalone must be run as the entry point. It cannot be imported.")
    exit(1)