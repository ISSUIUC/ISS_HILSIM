# AV Interface (Dummy)
# This is the A dummy interface.py file
# Implements all methods in avionics_interface
# All implementations of avionics_interface must expose an `av_instance` variable which is an instance of
# a class which derives from AvionicsInterface (from avionics_interface.py).
# HilsimRun does not need to be exposed, but must derive from avionics_interface.HilsimRun
# Michael Karpov (2027)

import time

import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as server
import tars_rack.av_platform.csv_datastream as csv_datastream
import util.communication.packets as pkt
import util.communication.serial_channel as serial_interface
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer


class DummyAvionics(AVInterface.AvionicsInterface):
    def handle_init(self) -> None:
        pass
    
    def detect(self) -> bool:
        return True # Emulate successful avionics connection
    
    def first_setup(self) -> None:
        time.sleep(1) # Emulate a synchronous git clone

    def code_reset(self) -> None:
        time.sleep(1) # Emulate a synchronous code reset

    def power_cycle(self) -> bool:
        time.sleep(1) # Emulate a synchronous power cycle
        return True

    def code_pull(self, git_target: str) -> None:
        time.sleep(1) # Emulate a synchronous code pull
    
    def code_flash(self) -> None:
        time.sleep(3) # Emulate a synchronous code flash



class HilsimRun(AVInterface.HilsimRunInterface):
    def get_current_log(self) -> str:
        return "Dummy hilsim run log"
    
    def job_setup(self) -> tuple[bool, str]:
        time.sleep(20) # Emulate a synchronous job setup
        return True, "Setup Complete"
    
    def __init__(
            self,
            datastreamer: Datastreamer.DatastreamerServer,
            av_interface: DummyAvionics,
            raw_csv: str,
            job: pkt.JobData) -> None:
        super().__init__(datastreamer, av_interface, raw_csv, job)
        self.total_time = 0
        self.max_time = 1
    
    def post_setup(self) -> None:
        pass # Do nothing

    def step(self, dt: float) -> tuple[bool, bool, str]:
        self.total_time += dt
        if(self.total_time >= self.max_time):
            return True, False, "Dummy return log"  # Finished, Error, Log
        else:
            return False, False, "Dummy defer in progress"

av_instance = DummyAvionics(Datastreamer.instance)
