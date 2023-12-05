from enum import Enum
import serial
import time
import util.communication.communication_interface as communication_interface
import util.communication.packets as packet
import sys
import os

# Make sure ../util and ../av_platform paths can be accessed
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


class ServerStateController():
    """A class representing the server's state as a state machine.

    Consists of a few main components:

    @`Pipes (A=>B)` are transitions (to state B) that the server is constantly attempting to perform if it's in state A
    @`Transition events` are blocks of code that are run when specific transitions are performed. If using `try_transition`, they can also dictate whether the transition succeeds.
    @`Always events` are blocks of code that are executed each tick when on a specific state
    @`Success events` are identical to transition events, but are only executed once, when the transition succeeds."""
    server = None

    class ServerState(int, Enum):
        "Enum describing possible server states as an integer."
        ANY = -1
        """Any server state"""
        INIT = 0
        """State when datastreamer is initializing systems"""
        CONNECTING = 1  # Before server connection
        """State when datastreamer is detecting a Kamaji server"""
        AV_DETECT = 2  # Before detecting avionics
        """State when datastreamer is detecting an avionics stack"""
        READY = 3  # Ready to recieve jobs
        """State when datastreamer is ready for jobs/idle"""
        JOB_SETUP = 4  # Recieved a job, in setup
        """State when datastreamer is performing setup to run a job"""
        JOB_RUNNING = 5  # Running a job
        """State when datastreamer is actively running a job"""
        CLEANUP = 6  # Finished job, cleaning up environment
        """State after a job is done/after a job fails, to clean up the environment"""
        ERROR = 100  # Error state (recoverable)
        """Fail state (recoverable)"""
        FERROR = 101  # Error state (unrecoverable)
        """Fatal fail state (non-recoverable)"""
        JOB_ERROR = 102  # Error during a job
        """Job fail state (recoverable), used for logging errors when a job fails during setup or run"""

    class Always:
        """A class representing an action that should always be run in a certain state"""

        def __init__(self, server, target_state, callback) -> None:
            """Initialize an `Always event`
            @server {DatastreamerServer} -- The server to use
            @target_state {ServerStateController.ServerState} -- The state during which to run the callback
            @callback {lambda} -- The callback to call when the Always event is run."""
            self.server: DatastreamerServer = server
            self.target_state: ServerStateController.ServerState = target_state
            self.callback = callback

        def run(self, current_state):
            """Determine if this callback should be run or not"""
            if (self.target_state == current_state or self.target_state ==
                    ServerStateController.ServerState.ANY):
                self.callback(self.server)

    class StateTransition:
        """
        A class respresenting code that must be executed for a state transition to occur.
        @initial_state: The state we transition FROM
        @final_state: The state we are transitioning TO
        @callback: A function that is run, and returns TRUE if the state transition can take place, FALSE otherwise.
        """

        def __init__(
                self,
                server,
                initial_state,
                final_state,
                callback) -> None:
            self.server: DatastreamerServer = server
            self.state_a: ServerStateController.ServerState = initial_state
            self.state_b: ServerStateController.ServerState = final_state
            self.transition_callback = callback

        def run(self):
            """Execute the transition callback"""
            return self.transition_callback(self.server)

        def should_run(self, state_a, state_b):
            """Determine if a callback should run"""
            if (state_a == self.state_a and self.state_b ==
                    ServerStateController.ServerState.ANY):
                return True

            if (state_b == self.state_b and self.state_a ==
                    ServerStateController.ServerState.ANY):
                return True

            if (state_a == self.state_a and state_b == self.state_b):
                return True
            return False

    transition_events: list[StateTransition] = []
    success_events: list[StateTransition] = []
    transition_always: list[Always] = []
    error_transition_events: list[StateTransition] = []
    server_state: ServerState = ServerState.INIT
    transition_pipes: list[list[ServerState]] = []

    def __init__(self) -> None:
        """Initialize the state machine with default state ServerState.INIT"""
        self.server_state = ServerStateController.ServerState.INIT

    def add_transition_event(
            self,
            initial_state,
            final_state,
            callback) -> None:
        """Add a `transition_event` to the state machine"""
        self.transition_events.append(
            ServerStateController.StateTransition(
                self.server, initial_state, final_state, callback))

    def add_success_event(self, initial_state, final_state, callback) -> None:
        """Add a `success_event` to the state machine"""
        self.success_events.append(
            ServerStateController.StateTransition(
                self.server, initial_state, final_state, callback))

    def add_always_event(self, always_target, callback) -> None:
        """Add an `always_event` to the state machine"""
        self.transition_always.append(
            ServerStateController.Always(
                self.server, always_target, callback))

    def force_transition(self, to_state: ServerState) -> None:
        """Same as try_transition, but doesn't check for transition_events passing or not"""
        transition_checks = 0
        for transition_event in self.transition_events:
            # For each transition event, we check if its to_state matches the state we're forcing the transition to.
            # If yes, we execute the code but discard the result.
            if (transition_event.should_run(self.server_state, to_state)):
                transition_checks += 1
                transition_event.run()

        for success_event in self.success_events:
            # Since this transition is forced, we always call all success_events
            if (success_event.should_run(self.server_state, to_state)):
                transition_checks += 1
                success_event.run()

        # Report transition
        print("(server_state) Successfully transitioned to state",
              to_state, "(Executed", transition_checks, "transition functions)")
        self.server_state = to_state

    def try_transition(self, to_state: ServerState) -> bool:
        """
        Attempt a transition, return true if successful
        @to_state: State to attempt to transition to
        """
        successful_transition = True
        transition_checks = 0
        for transition_event in self.transition_events:
            # For each transition event, we check if its to_state matches what
            # state we're attempting to transition to.
            if (transition_event.should_run(self.server_state, to_state)):
                transition_checks += 1
                # If yes, we check if the transition event allows us to
                # transition.
                if (not transition_event.run()):
                    successful_transition = False

        # If all transition checks succeed, we transition to the new state.
        if successful_transition:
            print("(server_state) Successfully transitioned to state",
                  to_state, "(Passed", transition_checks, "transition checks)")
            success_events_executed = 0
            for success_event in self.success_events:
                # Call all success events if the transition succeeds
                if (success_event.should_run(self.server_state, to_state)):
                    success_events_executed += 1
                    success_event.run()

            if success_events_executed > 0:
                print(
                    "(server_state) Executed " +
                    str(success_events_executed) +
                    " success events")
            self.server_state = to_state

        return successful_transition

    def add_transition_pipe(
            self,
            from_state: ServerState,
            to_state: ServerState) -> None:
        print("(server_state) Added pipe", from_state, " ==> ", to_state)
        """
        Adds a persistent pipeline from state `from_state` to state `to_state`
        (Whenever an update is called, the state machine will attempt to transfer to state `to_state` if in state `from_state`)
        """
        self.transition_pipes.append([from_state, to_state])

    def update_transitions(self) -> None:
        """Attempt to perform all pipe transitions defined in self.transition_pipes. Returns early if one is successful"""
        for pipe in self.transition_pipes:
            from_pipe = pipe[0]
            to_pipe = pipe[1]
            # If a pipe exists from the current state, we try to transition to
            # its to_state
            if (self.server_state == from_pipe):
                if self.try_transition(to_pipe):
                    return

    def update_always(self) -> None:
        """Runs all `Always events` defined in self.transition_always"""
        for always_event in self.transition_always:
            always_event.run(self.server_state)


class DatastreamerServer:
    """A singleton-designed class that holds all relevant information about the Datastreamer."""
    state: ServerStateController = ServerStateController()
    """Datastreamer server's state machine reference"""
    board_type: str = ""

    # COMMUNICATION
    server_comm_channel: communication_interface.CommunicationChannel = None
    """Serial port reference to the serial port that connects to the Kamaji server."""
    server_preferred_comm_method: communication_interface.CommunicationChannelType = communication_interface.CommunicationChannelType.SERIAL
    """The preferred method for datastreamer boards to communicate to Kamaji. Defaults to `SERIAL`"""
    board_id = -1
    """Board ID assigned by the Kamaji server"""
    do_wide_ident = True
    """Should the Datastreamer be attempting to IDENT?"""

    current_job = None  # HilsimRun
    """The job that is currently being setup/run"""
    current_job_data: packet.JobData = None
    """The data for the current job"""

    signal_abort = False
    """Standin for a process SIGABRT. If set to true, jobs will attempt to stop as soon as it's gracefully possible to do so"""
    signal_cycle = False
    """Signal to cycle the board when avaliable"""
    job_active = False
    """Boolean to check if a job is currently being run"""
    job_clock_reset = False
    """Boolean that forces a job's internal clock to reset. WARNING: Doing so in the middle of a job will cause overwrites"""

    packet_buffer: packet.DataPacketBuffer = packet.DataPacketBuffer()
    """Reference to the server's packet buffer, a utility object that helps handle packets"""
    server_start_time = time.time()
    """Time that this server started"""
    last_server_connection_check = time.time()
    """Time of last heartbeat packet"""
    next_heartbeat_time = time.time()
    """Time when next heartbeat packet will be sent."""

    last_job_step_time = time.time()
    """The last time that a job step() was completed"""

    def tick(self):
        """Generic single action on the server. Will perform all server actions by calling transition events and always events.

        This function will generally be run within an infinite while loop."""
        if self.server_comm_channel is not None:
            # We clear out output buffer and also populate our input buffer from
            # the server
            self.packet_buffer.write_buffer_to_channel(self.server_comm_channel)
            self.packet_buffer.read_to_input_buffer(self.server_comm_channel)

        self.state.update_always()  # Run all `always` events
        self.state.update_transitions()  # Run all transition tests
        # Discard our input buffer so we can get a new one next loop
        self.packet_buffer.clear_input_buffer()

    def defer(self):
        """
        This function allows a single execution of the server tick from any scope that has access to the server.
        This server tick does not do any transitions, since that control is held by the scope you call this function from.
        """
        if self.server_comm_channel is not None:
            # We clear out output buffer and also populate our input buffer from
            # the server
            self.packet_buffer.write_buffer_to_channel(self.server_comm_channel)
            self.packet_buffer.read_to_input_buffer(self.server_comm_channel)
            if (len(self.packet_buffer.input_buffer) > 0):
                for p in self.packet_buffer.input_buffer:
                    print("pbuf", p)

        self.state.update_always()  # Run all `always` events
        self.packet_buffer.clear_input_buffer()


instance = DatastreamerServer()
"""Singleton object for the Datastreamer server"""

# Set the serverstate's internal server object to a cyclical reference.
instance.state.server = instance
