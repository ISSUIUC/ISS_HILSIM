# HILSIM Data-Streamer-RASPI [9/27/2023]
# HILSIM Server team:
# Michael Karpov (2027)
# ..your names here!..
#
#
#
# BRIEF: This server will run on the raspberryPi end of the hilsim testing rack, and its purpose
# will be to recieve job data and pass it on to whichever device is connected to this device, then send that data back.
# That's it! Work of when to run jobs/hardware cooldowns/getting jobs will
# be handled by the central server.

import config as test_board_config
import util.serial_wrapper as connection
import util.communication.packets as packet
import time
import util.avionics_meta as AVMeta
import util.handle_packets as handle_packets
import util.datastreamer_server as Datastreamer
import util.communication.ws_channel as ws_channel
import util.communication.communication_interface as comm
import threading

# Set up interface defined in config
avionics = test_board_config.use_interface
av_meta: AVMeta.PlatformMetaInterface = test_board_config.use_meta

############### HILSIM Data-Streamer-RASPI ###############


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


def should_heartbeat(Server: Datastreamer.DatastreamerServer):
    if (time.time() > Server.next_heartbeat_time):
        Server.next_heartbeat_time = time.time() + 3  # Heartbeat every 3 seconds
        return True
    return False

# Server connection


def send_wide_ident(Server: Datastreamer.DatastreamerServer):
    if (not Server.do_wide_ident):
        return True
    if (time.time() > Server.last_server_connection_check):
        if (Server.server_preferred_comm_method ==
                comm.CommunicationChannelType.WEBSOCKET):
            # Check websockets
            try:
                websocket = ws_channel.WebsocketChannel(
                    test_board_config.api_url, "/api/dscomm/ws/socket.io")
                # We've connected, we haven't sent an IDENT, but we know we're
                # in theory good to go.
                Server.do_wide_ident = False
                print(
                    "(send_wide_ident:websocket) Successfully connected to websocket at ",
                    websocket.websocket_location +
                    websocket.websocket_path)
                ws_channel.connected_websockets.append(websocket)
                packet.DataPacketBuffer.write_packet(
                    packet.CL_IDENT(av_meta.board_type), websocket)
            except Exception as e:
                print(e)

        # Check comports
        if (Server.server_preferred_comm_method ==
                comm.CommunicationChannelType.SERIAL):
            connection.t_init_com_ports()
            for port in connection.connected_comports:
                packet.DataPacketBuffer.write_packet(
                    packet.CL_IDENT(av_meta.board_type), port)

        Server.last_server_connection_check += 0.25
    return True


def check_server_connection(Server: Datastreamer.DatastreamerServer):
    all_channels: comm.CommunicationChannel = connection.connected_comports + \
        ws_channel.connected_websockets
    for channel in all_channels:
        in_packets = packet.DataPacketBuffer.channel_to_packet_list(
            channel, True)
        for pkt in in_packets:
            if pkt.packet_type == packet.DataPacketType.ACKNOWLEDGE:
                Server.board_id = pkt.data['board_id']
                Server.server_comm_channel = channel
                Server.had_server_comm_channel = True
                return True
    return False


def reset_connection_data(Server: Datastreamer.DatastreamerServer):
    Server.last_server_connection_check = time.time()
    Server.next_heartbeat_time = time.time() + 3
    connection.init_com_ports()
    for port in connection.connected_comports:
        connection.hard_reset(port)
    return True


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


def handle_heartbeat(Server: Datastreamer.DatastreamerServer):
    if(Server.server_comm_channel is None):
        return
    if (should_heartbeat(Server)):
        print("(heartbeat) Sent update at u+", time.time())
        Server.packet_buffer.add(
            packet.CL_HEARTBEAT(
                packet.HeartbeatServerStatus(
                    Server.state.server_state,
                    Server.server_start_time,
                    False,
                    False),
                packet.HeartbeatAvionicsStatus(
                    False,
                    "")))

def handle_power_cycle(Server: Datastreamer.DatastreamerServer):
    SState = Datastreamer.ServerStateController.ServerState
    # This is linked to ANY state, but we realistically only care about some:
    ignore_state = [SState.AV_DETECT, SState.CONNECTING, SState.INIT]
    if Server.state.server_state in ignore_state:
        return

    # We now know we're in a state with connected avionics
    if Server.signal_cycle:
        # Make sure we wait until all jobs are stopped to avoid weird side
        # effects
        if not Server.job_active:
            # Now we actually cycle the board
            try:
                if (avionics.av_instance.power_cycle()):
                    print("(power_cycle) Successfully power cycled avionics system")
                    # Manually send READY packet if not in ready state (May not
                    # be in READY state!)
                    Server.packet_buffer.add(packet.CL_READY())
                    print("(power_cycle) Sent READY packet")
                    Server.signal_abort = False
                    Server.signal_cycle = False
                else:
                    print("Unable to power cycle!")
                    Server.packet_buffer.add(
                        packet.MISC_ERR("Unable to power cycle"))
            except BaseException:
                print("ERROR during power cycle!")
                Server.packet_buffer.add(
                    packet.MISC_ERR("Error during power cycle"))

def main():
    Server = Datastreamer.instance
    # Server config setup
    # Sets up the priority communication channel
    Server.server_preferred_comm_method = test_board_config.preferred_communication_channel

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
    Server.state.add_transition_pipe(SState.INIT, SState.CONNECTING)
    # Always try to transition CONNECTING => AV_DETECT
    Server.state.add_transition_pipe(SState.CONNECTING, SState.AV_DETECT)
    # Always try to transition AV_DETECT => READY
    Server.state.add_transition_pipe(SState.AV_DETECT, SState.READY)
    # Always try to transition JOB_SETUP => JOB_RUNNING
    Server.state.add_transition_pipe(SState.JOB_SETUP, SState.JOB_RUNNING)
    # Always try to transition JOB_RUNNING => CLEANUP
    Server.state.add_transition_pipe(SState.JOB_RUNNING, SState.CLEANUP)
    # Always try to transition CLEANUP => READY
    Server.state.add_transition_pipe(SState.CLEANUP, SState.READY)
    # Always try to transition JOB_ERROR => CLEANUP (for graceful recovery)
    Server.state.add_transition_pipe(SState.JOB_ERROR, SState.CLEANUP)

    # Connection checks
    Server.state.add_transition_event(
        SState.ANY,
        SState.CONNECTING,
        reset_connection_data)
    Server.state.add_transition_event(
        SState.CONNECTING,
        SState.AV_DETECT,
        send_wide_ident)
    Server.state.add_transition_event(
        SState.CONNECTING,
        SState.AV_DETECT,
        check_server_connection)
    Server.state.add_transition_event(
        SState.AV_DETECT, SState.READY, detect_avionics)

    # Success events
    Server.state.add_success_event(SState.ANY, SState.READY, on_ready)

    # Always events
    Server.state.add_always_event(SState.ANY, handle_power_cycle)
    Server.state.add_always_event(SState.ANY, handle_heartbeat)

    handle_packets.add_transitions(Server.state)
    handle_packets.add_always_events(Server.state)
    
    while True:
        Server.tick()

        Server.packet_buffer.clear_input_buffer()



##########################################################

if __name__ == "__main__":
    main()
else:
    print("HILSIM Data streamer-raspi should not be run as an import! Try again by running this script directly.")
    exit(1)
