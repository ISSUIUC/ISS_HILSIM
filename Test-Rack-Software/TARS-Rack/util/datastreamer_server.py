import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import av_platform.interface as avionics
import util.packets as packet
import time
import serial
from enum import Enum

class ServerStateController():
    # A state machine for the server
    server = None
    class ServerState(int, Enum):
        ANY = -1
        INIT = 0
        CONNECTING = 1 # Before server connection
        AV_DETECT = 2 # Before detecting avionics
        READY = 3 # Ready to recieve jobs
        JOB_SETUP = 4 # Recieved a job, in setup
        JOB_RUNNING = 5 # Running a job
        CLEANUP = 6 # Finished job, cleaning up environment
        ERROR = 100 # Error state (recoverable)
        FERROR = 101 # Error state (unrecoverable)
        JOB_ERROR = 102 # Error during a job

    class Always:
        """A class representing an action that should always be run in a certain state"""
        def __init__(self, server, target_state, callback) -> None:
            self.server: DatastreamerServer = server
            self.target_state: ServerStateController.ServerState = target_state
            self.callback = callback

        def run(self, current_state):
            if(self.target_state == current_state or self.target_state == ServerStateController.ServerState.ANY):
                self.callback(self.server)

    class StateTransition:
        """
        A class respresenting code that must be executed for a state transition to occur.
        @initial_state: The state we transition FROM
        @final_state: The state we are transitioning TO
        @callback: A function that is run, and returns TRUE if the state transition can take place, FALSE otherwise.
        """
        def __init__(self, server, initial_state, final_state, callback) -> None:
            self.server: DatastreamerServer = server
            self.state_a: ServerStateController.ServerState = initial_state
            self.state_b: ServerStateController.ServerState = final_state
            self.transition_callback = callback
        
        def run(self, state_a, state_b):
            if(state_a == self.state_a and self.state_b == ServerStateController.ServerState.ANY):
                # If transition A -> ANY
                return self.transition_callback(self.server)

            if(state_b == self.state_b and self.state_a == ServerStateController.ServerState.ANY):
                # If transition ANY -> B
                return self.transition_callback(self.server)

            if(state_a == self.state_a and state_b == self.state_b):
                # If transition A -> B
                return self.transition_callback(self.server)
            return True

        
    transition_events: list[StateTransition] = []
    transition_always: list[Always] = []
    error_transition_events: list[StateTransition] = []
    server_state: ServerState = ServerState.INIT
    transition_pipes:list[list[ServerState]] = []

    def __init__(self) -> None:
        self.server_state = ServerStateController.ServerState.INIT

    def add_transition_event(self, initial_state, final_state, callback) -> None:
        self.transition_events.append(ServerStateController.StateTransition(self.server, initial_state, final_state, callback))

    def add_always_event(self, always_target, callback) -> None:
        self.transition_always.append(ServerStateController.Always(self.server, always_target, callback))

    def try_transition(self, to_state: ServerState) -> bool:
        """
        Attempt a transition, return true if successful
        @to_state: State to attempt to transition to
        """
        successful_transition = True
        transition_checks = 0
        for transition_event in self.transition_events:
            if(transition_event.state_b == to_state or transition_event.state_b == ServerStateController.ServerState.ANY):
                transition_checks += 1
            if(not transition_event.run(self.server_state, to_state)):
                successful_transition = False
        
        if successful_transition:
            print("(server_state) Successfully transitioned to state", to_state, "(Passed", transition_checks, "transition checks)")
            self.server_state = to_state
        
        return successful_transition
    
    def add_transition_pipe(self, from_state: ServerState, to_state: ServerState) -> None:
        print("(server_state) Added pipe", from_state, " ==> ", to_state)
        """
        Adds a persistent pipeline from state `from_state` to state `to_state`
        (Whenever an update is called, the state machine will attempt to transfer to state `to_state` if in state `from_state`)
        """
        self.transition_pipes.append([from_state, to_state])

    def update_transitions(self) -> None:
        for always_event in self.transition_always:
            always_event.run(self.server_state)
        for pipe in self.transition_pipes:
            from_pipe = pipe[0]
            to_pipe = pipe[1]
            if(self.server_state == from_pipe):
                if self.try_transition(to_pipe):
                    return


class DatastreamerServer:
    state: ServerStateController = ServerStateController()
    board_type: str = ""
    server_port: serial.Serial = None
    board_id = -1
    current_job: avionics.HilsimRun = None
    current_job_data: dict = None
    signal_abort = False
    job_active = False
    job_clock_reset = False
    packet_buffer:packet.DataPacketBuffer = packet.DataPacketBuffer()
    server_start_time = time.time()
    last_server_connection_check = time.time()
    next_heartbeat_time = time.time()


"""Singleton object for the Datastreamer server:"""
instance = DatastreamerServer()
instance.state.server = instance
