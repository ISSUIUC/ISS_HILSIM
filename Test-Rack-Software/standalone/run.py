# Datastreamer standalone entry point
# Spec @ https://github.com/orgs/ISSUIUC/projects/4/views/1?pane=issue&itemId=52868143

# Implement standalone datastreamer functionality
# Implement new state machine
# Add ability to write to this directory (or `./output`) after runs finish.
# Reuse as much of the already written code as possible.
import config as standalone_config
import util.serial_wrapper as connection
import util.communication.packets as packet
import time
import util.avionics_meta as AVMeta
import util.handle_packets as handle_packets
import util.datastreamer_server as Datastreamer
import util.communication.ws_channel as ws_channel
import util.communication.communication_interface as comm
import threading


avionics = standalone_config.use_interface
av_meta: AVMeta.PlatformMetaInterface = standalone_config.use_meta

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

    # we only want to send ready packet if we are not in the process of
    # CYCLE'ing!
    if (not Server.signal_cycle):
        Server.packet_buffer.add(packet.CL_READY())
        print("(transition_to_ready) Reset fail flags and sent READY packet.")
    else:
        print("(transition_to_ready) In CYCLE process! Cleared fail flag")

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
    
    handle_packets.add_transitions_standalone(Server.state)
    handle_packets.add_always_events(Server.state)
    


if __name__ == "__main__":
    main()
else:
    print("Datastreamer standalone must be run as the entry point. It cannot be imported.")
    exit(1)