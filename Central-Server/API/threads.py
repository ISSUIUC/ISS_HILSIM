import threading
from time import sleep
import traceback
import random
import socketio
import eventlet
import util.communication.communication_interface as communication_interface
import util.communication.ws_channel as websocket_channel
import util.communication.packets as packets
from typing import List
import database
import jobs
import datetime
import time

DEBUG = False
GLOBAL_BOARD_ID = 0

class DatastreamerConnection():
    def __init__(self, thread_name, communication_channel: communication_interface.CommunicationChannel) -> None:
        self.thread_name = thread_name
        self.communicaton_channel = communication_channel

class WebsocketThread(threading.Thread):
    socketio_server: socketio.Server = None
    """Instance for the socket.io server for board communication"""
    socketio_app: socketio.WSGIApp = None
    """WSGI app for socket.io server"""
    
    def setup_callbacks(self, on_connect_callback, on_message_callback, on_disconnect_callback):
        @self.socketio_server.event
        def connect(sid, environ):
            on_connect_callback(sid, environ)

        @self.socketio_server.event
        def my_message(sid, data):
            on_message_callback(sid, data)

        @self.socketio_server.event
        def disconnect(sid):
            on_disconnect_callback(sid)

    def __init__(self, websocket_port): 
        threading.Thread.__init__(self) 
        self.thread_name = "Datastreamer-websocket" 
        self.thread_ID = "M-ws" 
        self.running = True
        self.websocket_port = websocket_port
        # Initialize socket communication to DS
        self.socketio_server = socketio.Server(cors_allowed_origins='*', async_mode="threading")
        self.socketio_app = socketio.WSGIApp(self.socketio_server, static_files={
            '/': {'content_type': 'text/html', 'filename': './static/ws_page.html'}
        })

        print("DS-socketio server initializing")


    def run(self):
        print("DS Websocket enabled on " + str(self.websocket_port))
        eventlet.wsgi.server(eventlet.listen(('', self.websocket_port)), self.socketio_app)


class board_thread(threading.Thread): 
    packet_buffer = None
    def __init__(self, thread_name, thread_ID, board_id, communication_channel: communication_interface.CommunicationChannel): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.communication_channel = communication_channel
        self.thread_ID = thread_ID 
        self.cur_job_config: packets.DataPacket = None
        self.has_job_config = False
        self.running = True # 
        self.packet_buffer = packets.DataPacketBuffer()
        self.board_id = board_id
        self.is_ready = False
        self.job_running = False # True when actively running job
        self.board_type = ""
        self.last_check = time.time()

 
    def can_take_job(self):
        return not self.has_job_config and self.is_ready

    def take_job(self, config):
        self.cur_job_config = config
        self.has_job_config = True
    
    def terminate(self):
        self.running = False
    
    def run_job(self):
        print(f"(comm:#{self.thread_ID})", f"[run_job]", f"Using given config to initialize job on linked board")
        self.packet_buffer.add(self.cur_job_config)
        print(f"(comm:#{self.thread_ID})", f"[run_job]", f"Job initialization command sent")
        self.job_running = True

    def handle_communication(self, packet_buffer: List[packets.DataPacket]):
        for packet in packet_buffer:
            print(f"(comm:#{self.thread_ID})", f"[handle_packet]", f"Handling packet {packet}")
            if(packet.packet_type == packets.DataPacketType.IDENT):
                print(f"(comm:#{self.thread_ID})", f"[handle_packet]", f"Sent ACK to linked board")
                self.packet_buffer.add(packets.SV_ACKNOWLEDGE(self.board_id))
                self.board_type = packet.data["board_type"]
                print("sent job", self.cur_job_config)
            if(packet.packet_type == packets.DataPacketType.READY):
                print(f"(comm:#{self.thread_ID})", f"[handle_packet]", f"Recieved READY signal from linked board")
                self.is_ready = True
                self.cur_job_config = None
                self.has_job_config = False
                self.job_running = False
            if(packet.packet_type == packets.DataPacketType.HEARTBEAT):
                self.last_check = time.time()
            
    def run(self): 
        while self.running:
            try:
                self.packet_buffer.write_buffer_to_channel(self.communication_channel)
                self.packet_buffer.read_to_input_buffer(self.communication_channel)
                self.handle_communication(self.packet_buffer.input_buffer)
                if self.has_job_config and self.job_running == False and self.is_ready == True:
                    self.job_running = True
                    self.run_job()

                self.packet_buffer.clear_input_buffer()

                sleep(1)
                if (time.time() - self.last_check > 30):
                    # Remove tars if we can't detect it
                    self.running = False
            except Exception as e:
                print(f"Thread {self.thread_ID} has unexpectedly closed")
                print(traceback.format_exc())
                self.running = False
            

class manager_thread(threading.Thread):
    threads: List[board_thread] = []
    spin_up_queue: List[DatastreamerConnection] = []
    """Queue that holds which threads need to be spun up."""

    ws_thread: WebsocketThread = None
    def __init__(self): 
        threading.Thread.__init__(self) 
        self.thread_name = "Manager" 
        self.thread_ID = "M" 
        self.queue = []
        self.running = True
        self.last_time = None

        # helper function to execute the threads
    
    def get_no_last_time_queue(self):
        # then
        conn = database.connect()
        cursor = conn.cursor()
        db_query = "SELECT * from hilsim_runs where hilsim_runs.run_status = {1}".format(database.get_db_name(), jobs.JobStatus.QUEUED.value)
        cursor.execute(db_query)
        queue = cursor.fetchall()
        # Get the current datetime, and don't check after that
        self.last_time = datetime.datetime.now()
        return queue
    
    def last_time_queue(self):
        conn = database.connect()
        cursor = conn.cursor()
        delta_t = (datetime.datetime.now() - self.last_time).total_seconds()
        db_query = "SELECT * from hilsim_runs where hilsim_runs.run_status = {1} and hilsim_runs.submitted_time > now() - interval '{2}s'".format(database.get_db_name(), jobs.JobStatus.QUEUED.value, delta_t)
        cursor.execute(db_query)
        queue = cursor.fetchall()
        self.last_time = datetime.datetime.now()
        return queue

    def some_thread_active(self):
        for t in self.threads:
            if t.is_alive():
                if not t.can_take_job():
                    return True
            else:
                del t
        return False

    def create_threads(self):
        global GLOBAL_BOARD_ID
        while len(self.spin_up_queue) > 0:
            t = self.spin_up_queue.pop(0)
            thr = board_thread(t.thread_name, t.thread_name, GLOBAL_BOARD_ID, t.communicaton_channel)
            GLOBAL_BOARD_ID += 1
            thr.start()
            self.threads.append(thr)

    # adds job to queue 
    def add_job(self, config):
        print(f"added job {config} to queues", flush=True)
        self.queue.append(config)
    
    def add_thread(self, thr):
        self.spin_up_queue.append(thr)
    
    def terminate_all(self):
        for t in self.threads:
            if t.is_alive():
                t.terminate()
                print(f"terminated thread {t.thread_ID}", flush=True)
        
        self.running = False
        print(f"terminated manager", flush=True)
        
    def remove_dead_threads(self):
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
        jobs_to_add = []
        if self.last_time == None:
            try:
                jobs_to_add = self.get_no_last_time_queue()
            except Exception as e:
                print(e, flush=True)
                # Ignore error :(
                pass
        else:
            try:
                jobs_to_add = self.last_time_queue()
            except Exception as e:
                print(e, flush=True)
                # Ignore error :(
                pass
        # Then add to queue
        for job in jobs_to_add:
            print(job, flush=True)
            job_data = packets.JobData(job[0], pull_target=job[2])
            self.add_job(packets.SV_JOB(job_data, ""))

    def run(self): 
        if DEBUG:
            for _ in range(1000):
                print("debug")
                # sleep(0.1)
        else:
            i = 0

            # Datastreamer websocket implementation
            def ws_on_connect(sid, environ):
                self.add_thread(DatastreamerConnection(sid, websocket_channel.ClientWebsocketConnection(self.ws_thread.socketio_server, sid)))
            
            def ws_on_message(sid, data):
                print(sid,": ",data)

            def ws_on_disconnect(sid):
                self.kill_thr(sid)

            print("(manager_thread) Creating websocket subthread")
            self.ws_thread = WebsocketThread(5001)
            self.ws_thread.setup_callbacks(ws_on_connect, ws_on_message, ws_on_disconnect)
            self.ws_thread.start()

            while self.running:
                self.check_jobs()
                self.remove_dead_threads()
                self.create_threads()
                if len(self.queue) > 0:
                    # Find first open board
                    for t in self.threads:
                        if t.is_alive():
                            if t.can_take_job():
                                cur_job = self.queue.pop(0)
                                t.take_job(cur_job)
                                print(f"Gave {t.thread_ID} job {cur_job}", flush=True)
                        else:
                            del t

                sleep(0.2)
                i+=1
            
                if i%100==0:
                    print("Threads: ", self.threads, flush=True)
                    print("Current queue: ", self.queue, flush=True)
        
        print("exit")
