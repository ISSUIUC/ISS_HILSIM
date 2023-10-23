import util.datastreamer_server as Datastreamer
import util.packets as pkt
import av_platform.interface as avionics
import util.avionics_interface as AVInterface
import time

def run_setup_job(Server: Datastreamer.DatastreamerServer):
    """Invokes the avionics system's job setup method.
    
    Avionics setup methods are generally blocking. Make sure that they properly call Server.defer() when possible."""
    try:
        job = Server.current_job_data
        accepted_status = pkt.JobStatus(pkt.JobStatus.JobState.SETUP, "Setting up job " + str(job.job_id), "Accepted")
        Server.packet_buffer.add(pkt.CL_JOB_UPDATE(accepted_status, ""))
        Server.defer()
        
        current_job: AVInterface.HilsimRunInterface = Server.current_job # For type hints
        setup_successful, setup_fail_reason = current_job.job_setup()
        if(setup_successful):
            return True
        else:
            raise Exception("Setup failed: " + setup_fail_reason)
    except Exception as e:
        print(e)
        Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
        return False
    
def run_job(Server: Datastreamer.DatastreamerServer):
    """Invokes the step() method in the current HilsimRun (plaform-blind)"""
    dt = time.time() - Server.last_job_step_time
    run_finished, run_errored, return_log = Server.current_job.step(dt)
    if(run_finished):
        if(run_errored):
            Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
            return False
        else:
            # The job has successfully completed! Inform the server of this fact
            # TODO: report job finish status to server
            return True

    Server.last_job_step_time = time.time()

def handle_job_setup_error(Server: Datastreamer.DatastreamerServer):
    pass

def handle_job_runtime_error(Server: Datastreamer.DatastreamerServer):
    pass

def handle_job_transitions(statemachine: Datastreamer.ServerStateController):
    """Add transition events for jobs"""
    SState = Datastreamer.ServerStateController.ServerState
    statemachine.add_transition_event(SState.JOB_SETUP, SState.JOB_RUNNING, run_setup_job) 
    statemachine.add_transition_event(SState.JOB_RUNNING, SState.CLEANUP, run_job)
    statemachine.add_transition_event(SState.JOB_SETUP, SState.JOB_ERROR, handle_job_setup_error)
    statemachine.add_transition_event(SState.JOB_RUNNING, SState.JOB_ERROR, handle_job_runtime_error)

def handle_job_packet(packet: pkt.DataPacket):
    """Handles all job packets sent by the Kamaji server"""
    SState = Datastreamer.ServerStateController.ServerState
    # If already running job or in setup:
    if(Datastreamer.instance.state.server_state == SState.JOB_SETUP or Datastreamer.instance.state.server_state == SState.JOB_RUNNING or Datastreamer.instance.state.server_state == SState.JOB_ERROR):
        Datastreamer.instance.packet_buffer.add(pkt.CL_INVALID(packet))
        return

    # Set up a job
    job = packet.data['job_data']
    raw_csv = packet.raw_data
    Datastreamer.instance.current_job_data = pkt.JobData(job['job_id'], pkt.JobData.GitPullType(job['pull_type']),
                                                    job['pull_target'], pkt.JobData.JobType(job['job_type']),
                                                    job['job_author_id'], pkt.JobData.JobPriority(job['job_priority']),
                                                    job['job_timestep'])
    Datastreamer.instance.current_job = avionics.HilsimRun(Datastreamer.instance, avionics.av_instance, raw_csv, Datastreamer.instance.current_job_data)
    
    Datastreamer.instance.state.try_transition(Datastreamer.ServerStateController.ServerState.JOB_SETUP)