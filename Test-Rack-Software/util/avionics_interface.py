import util.datastreamer_server as Datastreamer
import util.packets as pkt
from abc import ABC, abstractmethod # ABC = Abstract Base Classes 
import os


class AvionicsInterface(ABC):
    """An interface class for all av_interface stacks. Allows for standardization of HILSIM runs.
    Provides basic functionality, but stacks will have to implement their own methods."""
    ready: bool = False # Is this avionics stack ready?
    server: Datastreamer.DatastreamerServer = None

    def __init__(self, datastreamer: Datastreamer.DatastreamerServer) -> None:
        self.server = datastreamer

    @abstractmethod
    def handle_init(self) -> None:
        """Some boards may have initialization packets, this function will handle
        those packets and perform any av-stack specific setup."""
        raise NotImplementedError("AvionicsInterface.handle_init method not implemented")
    
    @abstractmethod
    def detect(self) -> bool:
        """Detects any specific avionics stack. Updates `ready` depending on the result.
        Additionally, returns the result."""
        raise NotImplementedError("AvionicsInterface.detect method not implemented")
    
    @abstractmethod
    def first_setup(self) -> None:
        """Performs any specific setup for this stack."""
        raise NotImplementedError("AvionicsInterface.first_setup method not implemented")
    
    @abstractmethod
    def code_reset(self) -> None:
        """Resets the repo and stack to its default state"""
        raise NotImplementedError("AvionicsInterface.code_reset method not implemented")
    
    @abstractmethod
    def code_pull(self, git_target: str) -> None:
        """Stashes current changes and pulls a specific branch or commit"""
        raise NotImplementedError("AvionicsInterface.code_pull method not implemented")
    
    @abstractmethod
    def code_flash(self) -> None:
        """Flashes currently staged code to the AV stack"""
        raise NotImplementedError("AvionicsInterface.code_flash method not implemented")
    

    @abstractmethod
    def power_cycle(self) -> bool:
        """Attempt to power cycle the avionics stack. Make sure to call server.defer() if it's a blocking action

        @returns whether power cycling was successful"""
        raise NotImplementedError("AvionicsInterface.HilsimRun.power_cycle method not implemented")

    
class HilsimRunInterface(ABC):
    """The server to defer to"""
    server: Datastreamer.DatastreamerServer = None

    """The avionics stack to refer to when performing runs and setup"""
    av_interface: AvionicsInterface = None

    """The csv data to stream to the stack, as a string"""
    raw_data: str

    """JobData packet data"""
    job: pkt.JobData = None

    @abstractmethod
    def get_current_log(self) -> str:
        """Returns the current log output from the AV stack"""
        raise NotImplementedError("AvionicsInterface.HilsimRun.get_current_log method not implemented")
    
    @abstractmethod
    def job_setup(self) -> tuple[bool, str]:
        """Sets up a job to run (This code will usually be blocking, so it will have to manually call server.defer()!)

        
        @returns A tuple: [job_setup_successful, job_setup_fail_reason]"""
        raise NotImplementedError("AvionicsInterface.HilsimRun.job_setup method not implemented")

    # Initializes the HILSIM run object
    def __init__(self, datastreamer: Datastreamer.DatastreamerServer, av_interface: AvionicsInterface, raw_csv: str, job: pkt.JobData) -> None:
        """Base constructor for the HILSIM run object. Children may have additional setup."""
        self.raw_data = raw_csv
        self.av_interface = av_interface
        self.job = job
        self.server = datastreamer
    
    def post_setup(self) -> None:
        """Dictates code that runs after setup is complete. Not required."""
        pass

    @abstractmethod
    def step(self, dt: float, send_status) -> tuple[bool, bool, str]:
        """
        Runs one iteration of the HILSIM loop, with a change in time of dt.

        @Returns a tuple: (run_finished, run_errored, return_log)
        """
        raise NotImplementedError("AvionicsInterface.HilsimRun.step method not implemented")

