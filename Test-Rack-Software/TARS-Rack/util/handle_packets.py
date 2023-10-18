import util.datastreamer_server as Datastreamer
import util.packets as pkt
import util.handle_jobs as jobs

def add_transitions(statemachine: Datastreamer.ServerStateController):
    pass


### Always read incoming packets regardless of state
def handle_server_packets(Server: Datastreamer.DatastreamerServer):
    # Retrieve all the packets from the server input buffer
    packets = Server.packet_buffer.input_buffer
    for packet in packets:
        # For every packet, determine what to do based on its type
        match packet.packet_type:
            case pkt.DataPacketType.IDENT_PROBE:
                # For IDENT_PROBE, we send back the data we know
                Server.packet_buffer.add(pkt.CL_ID_CONFIRM(Server.board_type, Server.board_id))
            case pkt.DataPacketType.PING:
                # For PING, we send PONG.
                Server.packet_buffer.add(pkt.CL_PONG())
            case pkt.DataPacketType.ACKNOWLEDGE:
                # For an invalid ACK, we send back an invalid packet.
                if(Server.server_port != None):
                    Server.packet_buffer.add(pkt.CL_INVALID(packet))
            case pkt.DataPacketType.REASSIGN:
                # For REASSIGN, we check if the command is valid, reassign if yes, INVALID if no.
                if(Server.board_id != -1):
                    Server.board_id = packet.data['board_id']
                else:
                    Server.packet_buffer.add(pkt.CL_INVALID(packet))
            case pkt.DataPacketType.JOB:
                # For JOB, we try to trigger a job.
                jobs.handle_job_packet(packet)
                

            
    

def add_always_events(statemachine: Datastreamer.ServerStateController):
    statemachine.add_always_event(Datastreamer.ServerStateController.ServerState.ANY, handle_server_packets)