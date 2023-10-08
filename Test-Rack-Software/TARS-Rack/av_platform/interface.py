# AV Interface (TARS)
# This is the specific interface.py file for the TARS avionics stack.
# @implements handle_raw(str raw_string) -- Determines what to do when a raw string is recieved from the stack.
# @implements detect_avionics(serial.Serial[] ignorePorts) -- Scans all ports for a connection, sets ready status if connected to an avionics stack.
# @implements first_setup() -- Performs the first setup (assuming fresh install). 
# @implements code_reset() -- Resets the project to a "known" state (Usually master branch).
# @implements code_pull(str git_branch) -- Sets up the project to do a code flash.
# @implements code_flash() -- Flashes the code to the avionics stack
# @implements HilsimRun -- Class that stores the data for a Hilsim run

import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as server
import av_platform.csv_datastream as csv_datastream
import pandas
import io 
import time
import serial
import util.packets as packet
import traceback

ready = False # Is the stack ready to recieve data?
TARS_port: serial.Serial = None

"""This function handles all raw input BEFORE all initialization is complete."""
# Doesn't do anything for TARS, but other boards may have initialization packets.
def handle_raw(raw_string: str):
    pass

"""This function will check if there's any serial plugged into this board that is NOT the server.
TARS only has one board, so we're good if we see any other port"""
def detect_avionics(ignore_ports: list[serial.Serial], connected_to_server: bool):
    global ready, TARS_port
    # For TARS, we need to make sure that we're already connected to the server
    if(not connected_to_server):
        ready = False
        return
    print("(detect_avionics) Attempting to detect avionics")
    for comport in server.connected_comports:
        if not (comport in ignore_ports):
            print("(detect_avionics) Detected viable target @ " + comport.name)
            TARS_port = comport
            ready = True
    

"""
This function must be implemented in all run_setup.py functions for each stack
first_setup(): Installs repository and sets up all actions outside of the repository to be ready to accept inputs.
"""
def first_setup():
    git.remote_clone()
    git.remote_reset()

"""
This function must be implemented in all run_setup.py functions for each stack
code_reset(): Resets the repository to a default state
TARS: Resets the TARS-Software repository to master branchd
"""
def code_reset():
    git.remote_reset()
    # Clean build dir
    pio.pio_clean()

"""
This function must be implemented in all run_setup.py functions for each stack
code_pull(str git_branch): Stashes changes and pulls a specific branch.
"""
def code_pull(git_branch: str):
    git.remote_pull_branch(git_branch)

"""
This function must be implemented in all run_setup.py functions for each stack
code_flash(): Flashes currently staged code to the avionics stack.
TARS: Uses environment mcu_hilsim
"""
def code_flash():
    # For TARS, we need to attempt the code flash twice, since it always fails the first time.
    try:
        pio.pio_upload("mcu_hilsim")
    except:
        pio.pio_upload("mcu_hilsim")


"""
This object stores all of the required information and functionality of a HILSIM run. This class
must be implemented in all run_setup.py scripts.
"""
class HilsimRun:
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

    # Getter for current log
    def get_current_log(self):
        return self.return_log

    # Sets up job to run (Cannot be canceled)
    # @param cancel_callback: Function that returns whether the job should be terminated.
    def job_setup(self, cancel_callback):
        job = self.job_data
        # Temporarily close port so code can flash
        TARS_port.close()
        if(job['pull_type'] == "branch"):
            try:
                code_reset()
                if(cancel_callback()):
                    return False, "Terminate signal sent during setup"
                code_pull(job['pull_target'])
                if(cancel_callback()):
                    return False, "Terminate signal sent during setup"
                code_flash()

                # Wait for the port to open back up (Max wait 10s)
                start = time.time()
                while(time.time() < start + 10):
                    if(cancel_callback()):
                        return False, "Terminate signal sent during COMPort setup"
                    try:
                        TARS_port.open()
                        print("\n(job_setup) Successfully re-opened TARS port (" + TARS_port.name + ")")
                        return True, "Setup Complete"
                    except:
                        time_left = abs((start + 10) - time.time())
                        print(f"(job_setup) attempting to re-open tars port.. ({time_left:.1f}s)", end="\r")
                return False, "Unable to re-open avionics COM Port"
                
            except Exception as e:
                return False, "Setup failed: " + str(e)
        elif (job['pull_type'] == "commit"):
            # Not implemented yet
            pass


    # Turns a raw CSV string to a Pandas dataframe
    def raw_csv_to_dataframe(self, raw_csv) -> pandas.DataFrame:
        # Get column names
        header = raw_csv.split('\n')[0].split(",")
        csv = "\n".join(raw_csv.split('\n')[1:])
        csvStringIO = io.StringIO(csv)
        return pandas.read_csv(csvStringIO, sep=",", header=None, names=header)

    # Initializes the HILSIM run object
    def __init__(self, raw_csv: str, job: dict) -> None:
        global TARS_port
        self.flight_data_raw = raw_csv
        self.flight_data_dataframe = self.raw_csv_to_dataframe(self.flight_data_raw)
        self.flight_data_rows = self.flight_data_dataframe.iterrows()
        self.port = TARS_port
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
    callback_func is a function to communicate back to the main process mid-step.

    @Returns a tuple: (run_finished, run_errored, return_log)
    """
    def step(self, dt: float, callback_func):
        self.current_time += dt
        simulation_dt = 0.01
        if self.current_time > self.last_packet_time + simulation_dt:
            self.last_packet_time += simulation_dt

            if self.current_time < self.start_time + 5:
                # Wait for 5 seconds to make sure serial is connected
                pass
            else:
                if(self.current_line == 0):
                    callback_func(packet.construct_job_status(True, "running", f"Running (Data streaming started)"))
                self.current_line += 1
                
                if(self.current_line % 300 == 0):
                    # Only send a job update every 3-ish seconds
                    callback_func(packet.construct_job_status(True, "running", f"Running ({self.current_line/len(self.flight_data_dataframe)*100:.2f}%) [{self.current_line} processed out of {len(self.flight_data_dataframe)} total]"))

                line_num, row = next(self.flight_data_rows, (None, None))
                if line_num == None:
                    callback_func(packet.construct_job_status(True, "done", f"Finished data streaming"))
                    return True, False, self.return_log # Finished, No Error, Log
                data = csv_datastream.csv_line_to_protobuf(row)
                if not data:
                    callback_func(packet.construct_job_status(True, "error", f"Expected data to insert, but found none."))
                    return True, False, self.return_log # Finished, Error, Log
                try:
                    self.port.write(data)
                except:
                    callback_func(packet.construct_job_status(True, "error", f"Exception during serial write: " + traceback.format_exc()))
                    return True, False, self.return_log # Finished, Error, Log
                
        if self.port.in_waiting:
            data = self.port.read_all()
            string = data.decode("utf8")           
            if string:
                string = string[0 : (len(string)-1)]
                self.return_log.append(string)

        return False, False, self.return_log
        


