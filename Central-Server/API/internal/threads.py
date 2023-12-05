"""Kamaji Threads
The classes in this file are responsible for spinning up and maintaining connections to the Datastreamer.
This is done through the use of a 'Manager thread', which spins up multiple other threads to do work in parallel.

The manager thread will always spin up a thread for itself and one for the websocket server, the latter of which
is prefaced with the (DS-socketio) tag in logging. The manager thread will also spin up a thread for each datastreamer connection.

WARNING: The current state of Kamaji only allows for websocket connections to datastreamer boards!
TODO: Add back serial functionality

Developed by the Kamaji team, 2023"""

import threading
import datetime
import time
import traceback
from typing import List

import socketio
import eventlet.wsgi

import util.communication.communication_interface as communication_interface
import util.communication.ws_channel as websocket_channel
import util.communication.packets as packets
import internal.database as database
import internal.jobs as jobs


GLOBAL_BOARD_ID = 0  # Tracking ID for board numbers
"""GLOBAL_BOARD_ID describes the current tracking ID for boards active in the Kamaji service. Whenever
a new board is generated, it is assigned a new board ID equivalent to this variable value, then it is incremented."""


class DatastreamerConnection():
    """This class links a single thread to a communication channel. Instances are created and added to a list to indicate the nessecity of spinning up new datastreamer threads."""

    def __init__(
            self,
            thread_name,
            communication_channel: websocket_channel.ClientWebsocketConnection) -> None:
        self.thread_name = thread_name
        self.communicaton_channel = communication_channel


class WebsocketThread(threading.Thread):
    """This thread handles the creation and lifetime of the websocket server (Tag: (DS-socketio))"""
    socketio_server: socketio.Server = None
    """Instance for the socket.io server for board communication"""
    socketio_app: socketio.WSGIApp = None
    """WSGI app for socket.io server"""

    def setup_callbacks(
            self,
            on_connect_callback: callable,
            on_message_callback: callable,
            on_disconnect_callback: callable) -> None:
        """Registers callbacks for connection, message, and disconnect events."""
        @self.socketio_server.event
        def connect(sid: str, environ):
            """Websocket connection event, called when a client connects"""
            on_connect_callback(sid, environ)

        @self.socketio_server.event
        def my_message(sid: str, data):
            """Websocket message event, called when a message is sent CLIENT -> SERVER"""
            on_message_callback(sid, data)

        @self.socketio_server.event
        def disconnect(sid):
            """Websocket disconnect event, called when a client disconnects"""
            on_disconnect_callback(sid)

    def __init__(self, websocket_port):
        """Initializes the server on a given port"""
        threading.Thread.__init__(self)
        self.thread_name = "Datastreamer-websocket"
        # Main-websocket (thread_id doesn't matter, as long as it doesn't
        # overlap)
        self.thread_id = "M-ws"
        self.running = True
        self.websocket_port = websocket_port

        # Initialize socket communication to Datastreamer
        self.socketio_server = socketio.Server(
            cors_allowed_origins='*', async_mode="threading")

        # This line serves ./static/ws_page.html when attempting to connect to
        # the websocket page with http.
        self.socketio_app = socketio.WSGIApp(self.socketio_server, static_files={
            '/': {'content_type': 'text/html', 'filename': './static/ws_page.html'}
        })

        print("(DS-socketio) initializing server..", flush=True)

    def run(self):
        """This function is called to initialize the thread."""
        print("(DS-socketio) DS Websocket initialized on " +
              str(self.websocket_port), flush=True)
        eventlet.wsgi.server(
            eventlet.listen(
                ('',
                 self.websocket_port)),
            self.socketio_app)  # Start WSGI server for websocket


class BoardThread(threading.Thread):
    """Signifies a single datastreamer board connection."""
    packet_buffer = None  # The output buffer of this thread

    def __init__(
            self,
            thread_name: str,
            thread_id: str,
            board_id: int,
            communication_channel: communication_interface.CommunicationChannel,
            pop_back_callback: callable) -> None:
        """Generates a datastreamer board thread
        @thread_name: The name to give to this thread (arbitrary)
        @thread_id: The ID for this thread (must be unique!)
        @board_id: The ID of the board to which this thread is connected (must be unique!)
        @communication_channel: The method that is used to communicate with the Datastreamer
        @pop_back_callback: The function to be called when this thread needs to pop a job back in the queue."""
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.communication_channel = communication_channel
        self.thread_id = thread_id
        self.cur_job_config: packets.DataPacket = None
        self.has_job_config = False
        self.running = True
        self.packet_buffer = packets.DataPacketBuffer()
        self.board_id = board_id
        # True when in READY state (? TODO: check if this is true)
        self.is_ready = False
        self.job_running = False  # True when actively running job
        self.board_type = ""
        self.last_check = time.time()
        self.callback = pop_back_callback
        self.job_status: packets.JobStatus = None

    def can_take_job(self):
        """Whether the board associated to this thread is ready to take a job"""
        return not self.has_job_config and self.is_ready

    def take_job(self, config: packets.DataPacket):
        """Assign the given job config to this board
        @config: The JOB packet that contains this config"""
        # Set all flags
        self.cur_job_config = config
        self.has_job_config = True

        # Update the job status in the database
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE hilsim_runs set run_status = %s, run_start = now() where run_id = %s",
            (jobs.JobStatus.RUNNING.value,
             config.data["job_data"]["job_id"]))
        conn.commit()

    def terminate(self) -> packets.DataPacket:
        """Drop this thread"""
        # TODO make sure this works properly every time
        self.running = False
        if self.has_job_config:
            self.callback(self.cur_job_config)

    def run_job(self):
        """Run the currently assigned job by sending the JOB packet to the Datastreamer"""
        print(
            f"(comm:#{self.thread_id})",
            f"[run_job]",
            f"Using given config to initialize job on linked board")
        # Send the job by adding it to the packet buffer (See:
        # packets.DataPacketBuffer)
        self.packet_buffer.add(self.cur_job_config)
        print(
            f"(comm:#{self.thread_id})",
            f"[run_job]",
            f"Job initialization command sent",
            flush=True)
        self.job_running = True  # Set job flags

    def complete_job(self, packet: packets.DataPacket):
        """Called when a job is complete"""
        # Update the job state in the database
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE hilsim_runs set run_status = %s, run_end = now() where run_id = %s ",
            (jobs.JobStatus.SUCCESS.value,
             packet.data["job_data"]["job_id"]))
        conn.commit()

    def handle_packet(self, packet):
        if (packet.packet_type == packets.DataPacketType.IDENT):
            # Identify this board to the server, send ACK packet.
            print(
                f"(comm:#{self.thread_id})",
                f"[handle_packet]",
                f"Sent ACK to linked board")
            self.packet_buffer.add(packets.SV_ACKNOWLEDGE(self.board_id))
            self.board_type = packet.data["board_type"]
        elif (packet.packet_type == packets.DataPacketType.READY):
            # The board is ready for a job
            print(
                f"(comm:#{self.thread_id})",
                f"[handle_packet]",
                f"Recieved READY signal from linked board")
            # Reset all job flags
            self.is_ready = True
            self.cur_job_config = None
            self.has_job_config = False
            self.job_running = False
        elif (packet.packet_type == packets.DataPacketType.HEARTBEAT):
            # Datastreamer packet containing server data.
            # self.last_check = time.time()
            pass
        elif (packet.packet_type == packets.DataPacketType.BUSY):
            # raise RuntimeError("Tried to give job when a board already had a packet")
            # TODO: Figure out why jobs are sent twice (BUSY packet recieved
            # from every board)
            pass
            """in theory we should never run into this issue, but it is here so that we do not run into errors"""
        elif (packet.packet_type == packets.DataPacketType.ID_CONFIRM):
            # This packet will only be recieved in the case of server failure.
            self.board_id = packet.data["board_id"]
            self.board_type = packet.data["board_type"]
        elif (packet.packet_type == packets.DataPacketType.DONE):
            # This packet signifies that a job has finished running
            self.job_running = False
            self.complete_job(packet)
            print(
                f"(comm:#{self.thread_id})",
                f"[job done]",
                f"This board has finished a job and has moved into cleanup")
        elif (packet.packet_type == packets.DataPacketType.JOB_UPDATE):
            print(packet.data, flush=True)
            # self.job_status.current_action = packet.data["job_status"]["current_action"]
            # self.job_status.status_text = packet.data["job_status"]["status_text"]
            """to be implemented, this is just the board giving updates on the status of a job"""
        elif (packet.packet_type == packets.DataPacketType.PONG):
            self.last_check = time.time()
            """will probably not be used, a relic of the early packet system."""

    def handle_communication(self, packet_buffer: List[packets.DataPacket]):
        """Handles Datastreamer communication with the packet system"""
        for packet in packet_buffer:
            # For every incoming packet:
            print(
                f"(comm:#{self.thread_id})",
                f"[handle_packet]",
                f"Handling packet {packet}")
            self.last_check = time.time()
            self.handle_packet(packet)

    def job_runner_loop(self):
        while self.running:
            # Handle packet buffer, reading and writing
            self.packet_buffer.write_buffer_to_channel(
                self.communication_channel)
            self.packet_buffer.read_to_input_buffer(self.communication_channel)

            # Handle all recieved packets
            self.handle_communication(self.packet_buffer.input_buffer)

            # If a board is primed to run a job, run it.
            if self.has_job_config and self.job_running == False and self.is_ready:
                self.job_running = True
                self.run_job()

            self.packet_buffer.clear_input_buffer()

            time.sleep(1)
            if (time.time() - self.last_check > 120):
                # Remove tars if we can't detect it
                print("Terminated", flush=True)
                self.terminate()
            if not self.communication_channel.socket_open():
                print(
                    "Terminated due to communication channel termination",
                    flush=True)
                self.terminate()

    def run(self):
        try:
            self.job_runner_loop()
        except Exception as e:
            print(f"Thread {self.thread_id} has unexpectedly closed")
            print(traceback.format_exc())
            self.running = False
        print("Thread has died", flush=True)


class BoardManagerThread(threading.Thread):
    """This thread is the main export of `threads.py`, it handles all datastreamer communication internally."""
    threads: List[BoardThread] = []
    """Datastreamer threads"""
    spin_up_queue: List[DatastreamerConnection] = []
    """Queue that holds which threads need to be spun up."""

    ws_thread: WebsocketThread = None

    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_name = "Manager"
        self.thread_id = "M"
        self.queue = []
        self.running = True
        self.last_time = datetime.datetime(2005, 7, 2)

    def pop_killed_job_back_to_queue(self, job: packets.DataPacket):
        """Used as a callback for board threads, makes unfinished/errored jobs pop back into the queue instead of going into limbo/being discarded"""
        print(
            f"Inserted job with job_id {job.data['job_data']['job_id']} back to the queue",
            flush=True)
        self.queue.insert(0, job)  # Insert job into the front of the queue

        # Update the status of the job in the database.
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE hilsim_runs set run_status = %s, run_start = now() where run_id = %s",
            (jobs.JobStatus.QUEUED.value,
             job.data["job_data"]["job_id"]))
        cursor.close()

    def get_recent_queue(self) -> List:  # List of what? TODO: check
        """Gets all jobs in the queue that happened after the last time the queue was checked by the server"""
        conn = database.connect()
        cursor = conn.cursor()
        delta_t = (datetime.datetime.now() - self.last_time).total_seconds()
        db_query = "SELECT * from hilsim_runs where hilsim_runs.run_status = %s and hilsim_runs.submitted_time > %s ORDER BY submitted_time"
        cursor.execute(db_query, (jobs.JobStatus.QUEUED.value, self.last_time))
        queued_jobs = cursor.fetchall()
        if len(queued_jobs) > 0:
            # Then get the last one
            struct = database.convert_database_tuple(cursor, queued_jobs[-1])
            self.last_time = struct.submitted_time
        return database.convert_database_list(cursor, queued_jobs)

    def some_thread_active(self) -> bool:
        """Returns TRUE if there exists a thread capable of taking a job. Otherwise FALSE"""
        for t in self.threads:
            if t.is_alive():
                if not t.can_take_job():
                    return True
            else:
                del t
        return False

    def create_threads(self):
        """Create all threads queued for initialization"""
        global GLOBAL_BOARD_ID
        while len(self.spin_up_queue) > 0:
            t = self.spin_up_queue.pop(0)
            thr = BoardThread(
                t.thread_name,
                t.thread_name,
                GLOBAL_BOARD_ID,
                t.communicaton_channel,
                self.pop_killed_job_back_to_queue)
            GLOBAL_BOARD_ID += 1  # Assign a new board ID and increment the global id
            thr.start()
            self.threads.append(thr)

    def add_job(self, config):
        """Adds a job to the queue"""
        print(f"added job {config} to queues", flush=True)
        self.queue.append(config)

    def add_thread(self, thr):
        """Adds a thread to be spun up"""
        self.spin_up_queue.append(thr)

    def terminate_all(self):
        """Destroy all threads and manager thread"""
        for t in self.threads:
            if t.is_alive():
                t.terminate()
                print(f"terminated thread {t.thread_id}", flush=True)

        self.running = False
        print(f"terminated manager", flush=True)

    def remove_dead_threads(self):
        """Remove threads that are not 'alive'"""
        self.threads = [thr for thr in self.threads if thr.is_alive()]

    def kill_thr(self, ident):
        # TODO
        """if 0 <= ident < len(self.threads):
            self.threads[ident].terminate()
            del self.threads[ident]
        else:
            for i, t in enumerate(self.threads):
                if ident == t.thread_name:
                    t.terminate()
                    del self.threads[i]"""

    def check_jobs(self):
        """Check the queue for jobs to add to the 'active queue'"""
        jobs_to_add = []
        try:
            jobs_to_add = self.get_recent_queue()
        except Exception as e:
            print(e, flush=True)
            # Most likely, we were unable to connect to the db.
            # maybe the database is down for now, so we will just wait until
            # it's up
            pass

        # Then add to queue
        for job in jobs_to_add:
            print(job, flush=True)
            job_data = packets.JobData(
                job.run_id,
                pull_target=job.branch,
                job_author_id=job.user_id)
            packet = packets.SV_JOB(job_data, "")
            self.add_job(packet)

    def run(self):
        """Execute the main manager thread"""
        i = 0

        # Datastreamer websocket implementation
        def ws_on_connect(sid, environ):
            self.add_thread(
                DatastreamerConnection(
                    sid, websocket_channel.ClientWebsocketConnection(
                        self.ws_thread.socketio_server, sid)))

        def ws_on_message(sid, data):
            print(sid, ": ", data)

        def ws_on_disconnect(sid):
            self.kill_thr(sid)

        print("(board_manager_thread) Creating websocket subthread")
        self.ws_thread = WebsocketThread(5001)
        self.ws_thread.setup_callbacks(
            ws_on_connect, ws_on_message, ws_on_disconnect)
        self.ws_thread.start()

        while self.running:
            # Main manager thread loop
            time.sleep(0.2)
            self.check_jobs()
            self.remove_dead_threads()
            self.create_threads()
            if len(self.queue) == 0:
                continue

            # Find first open board
            for t in self.threads:
                if t.is_alive():
                    if t.can_take_job():
                        cur_job = self.queue.pop(0)
                        t.take_job(cur_job)
                        print(f"Gave {t.thread_id} job {cur_job}", flush=True)
                else:
                    del t

            i += 1

            if i % 100 == 0:
                # Periodically print the queue, for debug purposes
                print("Threads: ", self.threads, flush=True)
                print("Current queue: ", self.queue, flush=True)

        print("(board_manager_thread) Exited!", flush=True)
