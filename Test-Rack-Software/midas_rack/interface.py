# AV Interface (MIDAS)
# This is the specific interface.py file for the MIDAS avionics stack.
# Implements all methods in avionics_interface
# All implementations of avionics_interface must expose an `av_instance` variable which is an instance of
# a class which derives from AvionicsInterface (from avionics_interface.py).
# HilsimRun does not need to be exposed, but must derive from avionics_interface.HilsimRun
# Michael Karpov (2027)

import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as server
import tars_rack.av_platform.csv_datastream as csv_datastream
import traceback
import pandas
import io
import time
import serial

try:
    import RPi.GPIO as GPIO
except:
    print("(config) WARNING: unable to import RPi.GPIO (Ignoring import)")
    import midas_rack.dummyGPIO as GPIO

import util.communication.packets as pkt
import util.communication.serial_channel as serial_interface
import traceback
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer
import requests
import util.dynamic_url
import util.os_interface


class MIDASAvionics(AVInterface.AvionicsInterface):
    TARS_port: serial.Serial = None
    RESET_PIN = 21
    BOOT_PIN = 20
    def handle_init(self) -> None:
        print("(MIDAS) handle_init run, board mode set to BCM")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RESET_PIN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.BOOT_PIN, GPIO.OUT, initial=GPIO.HIGH)

    def detect(self) -> bool:
        # For MIDAS, we need to make sure that we're already connected to the
        # server
        print("(detect_avionics) Attempting to detect avionics")
        if (not self.server.server_comm_channel):
            print("(detect_avionics) No server detected!")
            self.ready = False
            return False

        ignore_ports = []
        # We should ignore the server's comport if the chosen server
        # communication channel is serial..
        if type(self.server.server_comm_channel) == serial_interface.SerialChannel:
            print("(detect_avionics) Server is using Serial Channel interface")
            ignore_ports = [self.server.server_comm_channel]

        for comport in server.connected_comports:
            if not (comport in ignore_ports):
                print(
                    "(detect_avionics) Detected viable avionics target @ " +
                    comport.serial_port.name)
                self.TARS_port = comport.serial_port
                self.ready = True
                return True

    def first_setup(self) -> None:
        git.remote_clone()
        git.remote_reset()

    def code_reset(self) -> None:
        git.remote_reset()
        # Clean build dir
        pio.pio_clean(callback=self.server.defer)

    def power_cycle(self) -> bool:
        GPIO.output(self.RESET_PIN, GPIO.LOW)
        time.sleep(3)
        GPIO.output(self.RESET_PIN, GPIO.HIGH)
        return True

    def code_pull(self, git_target) -> None:
        git.remote_pull_branch(git_target)

    def code_flash(self) -> None:
        """Flashes code to the stack. For MIDAS, uses environment `mcu_hilsim`"""
        # https://www.martinloren.com/how-to/fashing-esp32/
        if(util.os_interface.is_raspberrypi()):
            GPIO.output(self.RESET_PIN, GPIO.HIGH)
            GPIO.output(self.BOOT_PIN, GPIO.HIGH)
            pio.pio_build("mcu_hilsim", callback=self.server.defer)
            # Hold down both pins
            GPIO.output(self.RESET_PIN, GPIO.LOW)
            GPIO.output(self.BOOT_PIN, GPIO.LOW)
            time.sleep(3)
            # Release reset pin
            GPIO.output(self.RESET_PIN, GPIO.HIGH)
            pio.pio_upload("mcu_hilsim", callback=self.server.defer)
            # Release boot pin
            GPIO.output(self.BOOT_PIN, GPIO.HIGH)
        else:
            # This interface needs to set GPIO pins.
            pio.pio_build("mcu_hilsim", callback=self.server.defer)
            pio.pio_upload("mcu_hilsim", callback=self.server.defer)

class HilsimRun(AVInterface.HilsimRunInterface):
    av_interface: MIDASAvionics  # Specify av_interface is TARS-specific!
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
        return "\n".join(self.return_log)

    def job_setup(self):
        print("(job_setup) ABORT flag: ", self.server.signal_abort)
        if (self.job is None):
            raise Exception("Setup error: Server.current_job is not defined.")

        # get csv data
        api_url = util.dynamic_url.get_dynamic_url()
        print("(job_setup TEMP) retrieving dynamic API url @", api_url)
        print("(job_setup TEMP) Retrieving sample datastreamer data")
        csv_object = requests.get(
            f"{api_url}/api/temp/data")
        csv = csv_object.text
        self.flight_data_raw = csv
        self.flight_data_dataframe = self.raw_csv_to_dataframe(
            self.flight_data_raw)
        self.flight_data_rows = self.flight_data_dataframe.iterrows()
        print("(job_setup TEMP) Successfully retrieved sample data")

        # Temporarily close port so code can flash
        self.av_interface.TARS_port.close()
        print("(job_setup) deferred TARS port control to platformio")

        if (self.job.pull_type == pkt.JobData.GitPullType.BRANCH):
            return self.pull_branch()
        elif (self.job.pull_type == pkt.JobData.GitPullType.COMMIT):
            raise NotImplementedError(
                "Commit-based pulls are not implemented yet.")

    # Turns a raw CSV string to a Pandas dataframe
    def pull_branch(self):
        try:
            self.av_interface.code_reset()

            # Check for defer (This may be DRY, but there aren't many better
            # ways to do this --MK)
            self.server.defer()
            if (self.server.signal_abort):
                self.server.state.try_transition(
                    Datastreamer.ServerStateController.ServerState.JOB_ERROR)
                return False, "Abort signal recieved"

            self.av_interface.code_pull(self.job.pull_target)
            job = self.server.current_job_data
            accepted_status = pkt.JobStatus(
                pkt.JobStatus.JobState.SETUP,
                "COMPILE_READY",
                f"Finished pre-compile setup on job {str(job.job_id)}")
            self.server.packet_buffer.add(
                pkt.CL_JOB_UPDATE(accepted_status, ""))

            # Check for defer (This may be DRY, but there aren't many better
            # ways to do this --MK)
            self.server.defer()
            if (self.server.signal_abort):
                self.server.state.try_transition(
                    Datastreamer.ServerStateController.ServerState.JOB_ERROR)
                return False, "Abort signal recieved"

            self.av_interface.code_flash()

            job = self.server.current_job_data
            accepted_status = pkt.JobStatus(
                pkt.JobStatus.JobState.SETUP,
                "COMPILED",
                f"Finished code flash on job {str(job.job_id)}")
            self.server.packet_buffer.add(
                pkt.CL_JOB_UPDATE(accepted_status, ""))

            # Check for defer (This may be DRY, but there aren't many better
            # ways to do this --MK)
            self.server.defer()
            if (self.server.signal_abort):
                self.server.state.try_transition(
                    Datastreamer.ServerStateController.ServerState.JOB_ERROR)
                return False, "Abort signal recieved"

            # Wait for the port to open back up (Max wait 10s)
            start = time.time()
            while (time.time() < start + 10):
                # Check for defer (This may be DRY, but there aren't many
                # better ways to do this --MK)
                self.server.defer()
                if (self.server.signal_abort):
                    self.server.state.try_transition(
                        Datastreamer.ServerStateController.ServerState.JOB_ERROR)
                    return False, "Abort signal recieved"

                try:
                    if (self.av_interface.TARS_port.is_open):
                        return True, "Setup Complete"
                    self.av_interface.TARS_port.open()
                    print("(Interface) Opening port")
                    magic_id = [69, 110, 117, 109, 99, 108, 97, 119]
                    self.av_interface.TARS_port.write([69, 110, 117, 109, 99, 108, 97, 119])
                    #self.av_interface.TARS_port.baudrate = 9600
                    magic = self.av_interface.TARS_port.read(len(magic_id))
                    if magic.decode().strip() != magic_id:
                        # Then it's the same
                        print(str(magic), flush=True)
                        print("Error: Magic number mismatch, it might not be MIDAS", flush=True)
                    # Some other miscellaneous data
                    git_hash = self.av_interface.TARS_port.read_until().decode().strip()
                    compile_time = self.av_interface.TARS_port.read_until().decode().strip()
                    compile_date = self.av_interface.TARS_port.read_until().decode().strip()
                    print("(Interface) Pulling ", git_hash, " from ", compile_date, " ", compile_time, flush=True)
                    print(
                        "\n(job_setup) Successfully re-opened MIDAS port (" +
                        self.av_interface.TARS_port.name +
                        ")")
                    return True, "Setup Complete"
                except Exception as e:
                    print("(non-fatal) unable to open port: ", e)
                    print(traceback.format_exc())
                    print("")
                    time_left = abs((start + 10) - time.time())
                    print(
                        f"(job_setup) attempting to re-open tars port.. ({time_left:.1f}s)",
                        end="\r")
            return False, "Unable to re-open avionics COM Port"

        except Exception as e:
            print("(job_setup) Job setup failed")
            print(e)
            print(traceback.format_exc())
            return False, "Setup failed: " + str(e)

    def raw_csv_to_dataframe(self, raw_csv) -> pandas.DataFrame:
        # Get column names
        header = raw_csv.split('\n')[0].split(",")
        csv = "\n".join(raw_csv.split('\n')[1:])
        csvStringIO = io.StringIO(csv)
        return pandas.read_csv(csvStringIO, sep=",", header=None, names=header)

    # Initializes the HILSIM run object

    def __init__(
            self,
            datastreamer: Datastreamer.DatastreamerServer,
            av_interface: MIDASAvionics,
            raw_csv: str,
            job: pkt.JobData) -> None:
        super().__init__(datastreamer, av_interface, raw_csv, job)
        self.flight_data_raw = raw_csv
        self.flight_data_dataframe = self.raw_csv_to_dataframe(
            self.flight_data_raw)
        self.flight_data_rows = self.flight_data_dataframe.iterrows()
        self.port = av_interface.TARS_port
        self.start_time = time.time()
        self.current_time = self.start_time
        self.last_packet_time = self.start_time
        self.job_data = job

    def reset_clock(self):
        """Resets start time to current time"""
        print("clock reset")
        self.start_time = time.time()
        self.current_time = self.start_time
        self.last_packet_time = self.start_time

    def post_setup(self) -> None:
        self.reset_clock()

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
                if (self.current_line == 0):
                    self.last_packet_time = self.current_time
                    job_status = pkt.JobStatus(
                        pkt.JobStatus.JobState.RUNNING,
                        "BEGIN",
                        f"Running (Data streaming started)")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(
                        job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                self.current_line += 1

                if (self.current_line % 300 == 0):
                    # Only send a job update every 3-ish seconds
                    job_status = pkt.JobStatus(
                        pkt.JobStatus.JobState.RUNNING,
                        "RUNNING",
                        f"Running ({self.current_line/len(self.flight_data_dataframe)*100:.2f}%) [{self.current_line} processed out of {len(self.flight_data_dataframe)} total]")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(
                        job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)

                    print(
                        f"Running ({self.current_line/len(self.flight_data_dataframe)*100:.2f}%) [{self.current_line} processed out of {len(self.flight_data_dataframe)} total]")

                line_num, row = next(self.flight_data_rows, (None, None))
                if line_num is None:
                    job_status = pkt.JobStatus(
                        pkt.JobStatus.JobState.RUNNING,
                        "RUNNING",
                        f"Finished data streaming")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(
                        job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log  # Finished, No Error, Log
                data = csv_datastream.csv_line_to_protobuf(row)
                if not data:
                    job_status = pkt.JobStatus(
                        pkt.JobStatus.JobState.ERROR,
                        "ABORTED_ERROR",
                        f"Expected data to insert, but found none")
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(
                        job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log  # Finished, Error, Log
                try:
                    self.port.write(data)
                except BaseException:
                    job_status = pkt.JobStatus(
                        pkt.JobStatus.JobState.ERROR,
                        "ABORTED_ERROR",
                        f"Exception during serial write: " +
                        traceback.format_exc())
                    status_packet: pkt.DataPacket = pkt.CL_JOB_UPDATE(
                        job_status, "\n".join(self.return_log))
                    self.av_interface.server.packet_buffer.add(status_packet)
                    return True, False, self.return_log  # Finished, Error, Log

        if self.port.in_waiting:
            data = self.port.read_all()
            string = data.decode("utf8")
            if string:
                string = string[0: (len(string) - 1)]
                self.return_log.append(string)

        return False, False, self.return_log


av_instance = MIDASAvionics(Datastreamer.instance)
