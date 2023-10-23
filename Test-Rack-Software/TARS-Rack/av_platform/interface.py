# AV Interface (TARS)
# This is the specific interface.py file for the TARS avionics stack.
# Implements all methods in avionics_interface
# All implementations of avionics_interface must expose an `av_instance` variable which is an instance of
# a class which derives from AvionicsInterface (from avionics_interface.py).
# HilsimRun does not need to be exposed, but must derive from avionics_interface.HilsimRun
# Michael Karpov (2027)

import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as server
import av_platform.csv_datastream as csv_datastream
import pandas
import io 
import time
import serial
import util.packets as pkt
import traceback
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer

class TARSAvionics(AVInterface.AvionicsInterface):
    TARS_port: serial.Serial = None

    # Doesn't do anything for TARS, but other boards may have initialization packets
    def handle_init(self) -> None:
        return super().handle_init()
    
    def detect(self) -> bool:
        # For TARS, we need to make sure that we're already connected to the server
        if(not self.server):
            self.ready = False
            return
        print("(detect_avionics) Attempting to detect avionics")

        ignore_ports = [self.server.server_port]

        for comport in server.connected_comports:
            if not (comport in ignore_ports):
                print("(detect_avionics) Detected viable target @ " + comport.name)
                self.TARS_port = comport
                self.ready = True

    def first_setup(self) -> None:
        git.remote_clone()
        git.remote_reset()

    def code_reset(self) -> None:
        git.remote_reset()
        # Clean build dir
        pio.pio_clean()
    
    def code_pull(self, git_target) -> None:
        git.remote_pull_branch(git_target)
    
    def code_flash(self) -> None:
        """Flashes code to the stack. For TARS, uses environment `mcu_hilsim`"""
        # For TARS, we need to attempt the code flash twice, since it always fails the first time.
        try:
            pio.pio_upload("mcu_hilsim")
        except:
            pio.pio_upload("mcu_hilsim")

class HilsimRun(AVInterface.HilsimRunInterface):
    av_interface: TARSAvionics # Specify av_interface is TARS-specific!
    return_log = []
    flight_data_raw = ""
    flight_data_dataframe = None
    flight_data_rows = None
    current_line = 0
    last_packet_time = 0
    start_time = 0
    current_time = 0
    port = None
    job_data = None

    def get_current_log(self) -> str:
        return self.return_log

    def job_setup(self):
        if (self.job == None):
            raise Exception("Setup error: Server.current_job is not defined.")
        
        # Temporarily close port so code can flash
        # self.av_interface.TARS_port.close()

        if(self.job.pull_type == pkt.JobData.GitPullType.BRANCH):
            try:
                
                self.av_interface.code_reset()

                # Check for defer (This may be DRY, but there aren't many better ways to do this --MK)
                self.server.defer()
                if(self.server.signal_abort):
                    self.server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
                    return False, "Abort signal recieved"

                self.av_interface.code_pull(self.job.pull_target)
                job = self.server.current_job_data
                accepted_status = pkt.JobStatus(pkt.JobStatus.JobState.SETUP, "COMPILE_READY", f"Finished pre-compile setup on job {str(job.job_id)}")
                self.server.packet_buffer.add(pkt.CL_JOB_UPDATE(accepted_status, ""))

                # Check for defer (This may be DRY, but there aren't many better ways to do this --MK)
                self.server.defer()
                if(self.server.signal_abort):
                    self.server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
                    return False, "Abort signal recieved"
                
                self.av_interface.code_flash()

                job = self.server.current_job_data
                accepted_status = pkt.JobStatus(pkt.JobStatus.JobState.SETUP, "COMPILED", f"Finished code flash on job {str(job.job_id)}")
                self.server.packet_buffer.add(pkt.CL_JOB_UPDATE(accepted_status, ""))

                # Check for defer (This may be DRY, but there aren't many better ways to do this --MK)
                self.server.defer()
                if(self.server.signal_abort):
                    self.server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
                    return False, "Abort signal recieved"

                # Wait for the port to open back up (Max wait 10s)
                start = time.time()
                while(time.time() < start + 10):
                    # Check for defer (This may be DRY, but there aren't many better ways to do this --MK)
                    self.server.defer()
                    if(self.server.signal_abort):
                        self.server.state.try_transition(Datastreamer.ServerStateController.ServerState.CLEANUP)
                        return False, "Abort signal recieved"
                    
                    try:
                        self.av_interface.TARS_port.open()
                        print("\n(job_setup) Successfully re-opened TARS port (" + self.av_interface.TARS_port.name + ")")
                        return True, "Setup Complete"
                    except:
                        time_left = abs((start + 10) - time.time())
                        print(f"(job_setup) attempting to re-open tars port.. ({time_left:.1f}s)", end="\r")
                return False, "Unable to re-open avionics COM Port"
                
            except Exception as e:
                return False, "Setup failed: " + str(e)
        elif (self.job.pull_type == pkt.JobData.GitPullType.COMMIT):
            raise NotImplementedError("Commit-based pulls are not implemented yet.")


    # Turns a raw CSV string to a Pandas dataframe
    def raw_csv_to_dataframe(self, raw_csv) -> pandas.DataFrame:
        # Get column names
        header = raw_csv.split('\n')[0].split(",")
        csv = "\n".join(raw_csv.split('\n')[1:])
        csvStringIO = io.StringIO(csv)
        return pandas.read_csv(csvStringIO, sep=",", header=None, names=header)
    

    # Initializes the HILSIM run object
    def __init__(self, datastreamer: Datastreamer.DatastreamerServer, av_interface: TARSAvionics, raw_csv: str, job: pkt.JobData) -> None:
        super().__init__(datastreamer, av_interface, raw_csv, job)
        self.flight_data_raw = raw_csv
        self.flight_data_dataframe = self.raw_csv_to_dataframe(self.flight_data_raw)
        self.flight_data_rows = self.flight_data_dataframe.iterrows()
        self.port = av_interface.TARS_port
        self.start_time = time.time()
        self.current_time = self.start_time
        self.last_packet_time = self.start_time
        self.job_data = job

    def reset_clock(self):
        self.start_time = time.time()
        self.current_time = self.start_time
        self.last_packet_time = self.start_time

    """
    Runs one iteration of the HILSIM loop, with a change in time of dt.

    @Returns a tuple: (run_finished, run_errored, return_log)
    """
    def step(self, dt: float):
        self.current_time += dt
        simulation_dt = 0.01
        # The av stack can only take a certain amount of data at a time, so we need to yield until we
        # can safely send data.
        if self.current_time > self.last_packet_time + simulation_dt:
            self.last_packet_time += simulation_dt

            if self.current_time < self.start_time + 5:
                # Wait for 5 seconds to make sure serial is connected
                pass
            else:
                if(self.current_line == 0):
                    job_status = pkt.JobStatus(pkt.JobStatus.JobState.RUNNING, "BEGIN", f"Running (Data streaming started)")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                self.current_line += 1
                
                if(self.current_line % 300 == 0):
                    # Only send a job update every 3-ish seconds
                    job_status = pkt.JobStatus(pkt.JobStatus.JobState.RUNNING, "RUNNING", f"Running ({self.current_line/len(self.flight_data_dataframe)*100:.2f}%) [{self.current_line} processed out of {len(self.flight_data_dataframe)} total]")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)

                line_num, row = next(self.flight_data_rows, (None, None))
                if line_num == None:
                    job_status = pkt.JobStatus(pkt.JobStatus.JobState.RUNNING, "RUNNING", f"Finished data streaming")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log # Finished, No Error, Log
                data = csv_datastream.csv_line_to_protobuf(row)
                if not data:
                    job_status = pkt.JobStatus(pkt.JobStatus.JobState.ERROR, "ABORTED_ERROR", f"Expected data to insert, but found none")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log # Finished, Error, Log
                try:
                    self.port.write(data)
                except:
                    job_status = pkt.JobStatus(pkt.JobStatus.JobState.ERROR, "ABORTED_ERROR", f"Exception during serial write: " + traceback.format_exc())
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log # Finished, Error, Log
                
        if self.port.in_waiting:
            data = self.port.read_all()
            string = data.decode("utf8")           
            if string:
                string = string[0 : (len(string)-1)]
                self.return_log.append(string)

        return False, False, self.return_log
        

av_instance = TARSAvionics(Datastreamer.instance)