# AV Interface (TARS)
# This is the specific interface.py file for the TARS avionics stack.
# @implements
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

ready = False # Is the stack ready to recieve data?
TARS_port: serial.Serial = None

"""This function will check if there's any serial plugged into this board that is NOT the server.
TARS only has one board, so we're good if we see any other port"""
def detect_avionics(ignore_ports: list[serial.Serial]):
    for comport in server.connected_comports:
        if not (comport in ignore_ports):
            if(comport.in_waiting):
                TARS_port = comport
                ready = True
    ready = False
    

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
    # Clean build dir
    pio.pio_clean()
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

    # Turns a raw CSV string to a Pandas dataframe
    def raw_csv_to_dataframe(raw_csv) -> pandas.DataFrame:
        # Get column names
        header = raw_csv.split('\n')[0].split(",")
        csv = "\n".join(raw_csv.split('\n')[1:])
        csvStringIO = io.StringIO(csv)
        return pandas.read_csv(csvStringIO, sep=",", header=None, names=header)

    # Initializes the HILSIM run object
    def __init__(self, raw_csv: str, serial_port: serial.Serial) -> None:
        self.flight_data_raw = raw_csv
        self.flight_data_dataframe = self.raw_csv_to_dataframe(self.flight_data_raw)
        self.flight_data_rows = self.flight_data_dataframe.iterrows()
        self.port = serial_port
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
        if self.current_time > self.last_packet_time + 10:
            self.last_packet_time += 10
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
        


