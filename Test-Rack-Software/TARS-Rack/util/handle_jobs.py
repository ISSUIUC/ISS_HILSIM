import util.datastreamer_server as Datastreamer
import util.packets as pkt
import util.pio_commands as pio
import util.git_commands as git

def run_setup_job(Server: Datastreamer.DatastreamerServer):
    # This is a blocking action. Thus we will manually invoke Server.defer() between logical steps.
    try:
        if (Server.current_job == None):
            raise Exception("Setup error: Server.current_job is not defined.")
        job_data: pkt.JobData = Server.current_job


        git.remote_reset()
        git.remote_pull_branch(job_data.pull_target)

        Server.defer() # Check for abort signals
        if(Server.signal_abort):
            Server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
            return False
        
        pio.pio_clean()

        Server.defer() # Check for abort signals
        if(Server.signal_abort):
            Server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
            return False
        
        try:
            pio.pio_upload("mcu_hilsim")
        except:
            Server.defer() # Check for abort signals
            if(Server.signal_abort):
                Server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
                return False
            pio.pio_upload("mcu_hilsim")

        return True
    except:
        Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
        return False
    
def run_job(Server: Datastreamer.DatastreamerServer):
    pass


def handle_job_transitions(statemachine: Datastreamer.ServerStateController):
    SState = Datastreamer.ServerStateController.ServerState
    statemachine.add_transition_event(SState.JOB_SETUP, SState.JOB_RUNNING, run_setup_job) 

def handle_job_packet(packet: pkt.DataPacket):
    SState = Datastreamer.ServerStateController.ServerState
    # If already running job or in setup:
    if(Datastreamer.instance.state.server_state == SState.JOB_SETUP or Datastreamer.instance.state.server_state == SState.JOB_RUNNING or Datastreamer.instance.state.server_state == SState.JOB_ERROR):
        Datastreamer.instance.packet_buffer.add(pkt.CL_INVALID(packet))
        return

    # Set up a job
    job = packet.data['job_data']
    Datastreamer.instance.current_job = pkt.JobData(job['job_id'], pkt.JobData.GitPullType(job['pull_type']),
                                                    job['pull_target'], pkt.JobData.JobType(job['job_type']),
                                                    job['job_author_id'], pkt.JobData.JobPriority(job['job_priority']),
                                                    job['job_timestep'])
    
    Datastreamer.instance.state.try_transition(Datastreamer.ServerStateController.ServerState.JOB_SETUP)

    

    pass