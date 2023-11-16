import util.datastreamer_server as Datastreamer
import util.communication.packets as pkt
import config as test_board_config
import util.avionics_interface as AVInterface
import time
import traceback
import inspect

avionics = test_board_config.use_interface

def run_setup_job(Server: Datastreamer.DatastreamerServer):
    """Invokes the avionics system's job setup method.
    
    Avionics setup methods are generally blocking. Make sure that they properly call Server.defer() when possible."""
    try:
        Server.job_active = True
        job = Server.current_job_data
        accepted_status = pkt.JobStatus(pkt.JobStatus.JobState.SETUP, "ACCEPTED", "Setting up job " + str(job.job_id))
        Server.packet_buffer.add(pkt.CL_JOB_UPDATE(accepted_status, ""))
        Server.defer()
        
        current_job: AVInterface.HilsimRunInterface = Server.current_job # For type hints
        setup_successful, setup_fail_reason = current_job.job_setup()
        if(setup_successful):
            current_job.post_setup()
            return True
        else:
            raise Exception("Setup failed: " + setup_fail_reason)
    except Exception as e:
        print("(job_setup) Error while setting up job")
        print(e)
        print(traceback.format_exc())
        Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
        return False
    
def run_job(Server: Datastreamer.DatastreamerServer):
    
    """Invokes the step() method in the current HilsimRun (plaform-blind)"""
    dt = time.time() - Server.last_job_step_time
    current_job: AVInterface.HilsimRunInterface = Server.current_job # For type hints

    if(Server.signal_abort):
        job_status = pkt.JobStatus(pkt.JobStatus.JobState.ERROR, "ABORTED_MANUAL", f"Abort signal was sent")
        Server.packet_buffer.add(pkt.CL_JOB_UPDATE(job_status, current_job.get_current_log()))
        Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
        return False

    run_finished, run_errored, return_log = current_job.step(dt)
    if(run_finished):
        if(run_errored):
            Server.state.force_transition(Datastreamer.ServerStateController.ServerState.JOB_ERROR)
            return False
        else:
            print("(job_done) Finished job with job id " + str(Server.current_job_data.job_id))
            Server.packet_buffer.add(pkt.CL_DONE(Server.current_job_data, "\n".join(return_log)))
            print("(job_done) sent DONE packet to server with job result")
            return True

    Server.last_job_step_time = time.time()
    return False

def job_cleanup(Server: Datastreamer.DatastreamerServer):
    Server.job_active = False
    Server.current_job = None
    Server.current_job_data = None
    return True

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
    statemachine.add_transition_event(SState.CLEANUP, SState.READY, job_cleanup)

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