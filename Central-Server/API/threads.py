import threading
from time import sleep
import traceback
import random
import socketio
import eventlet
import util.communication.communication_interface as communication_interface
import util.communication.ws_channel as websocket_channel
import util.communication.packets as packets

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
        self.cur_job_config = None
        self.has_job_config = False
        self.running = True
        self.packet_buffer = packets.DataPacketBuffer()
        self.board_id = board_id
        self.is_ready = False
        
 
    def can_take_job(self):
        return not self.has_job_config

    def take_job(self, config):
        self.cur_job_config = config
        self.has_job_config = True
    
    def terminate(self):
        self.running = False
    
    def run_job(self):
        rand_time = round(random.random() * 15, 2)
        print(f"Sleeping thread {self.thread_ID} for {rand_time} seconds while completing job {self.cur_job_config}", flush=True)
        sleep(rand_time)
        print(f"completed job {self.cur_job_config} on thread {self.thread_ID}", flush=True)

        self.has_job_config = False
        self.cur_job_config = None

    def handle_communication(self, packet_buffer):
        if(len(packet_buffer) > 0):
            print("PB", packet_buffer)

    def run(self): 
        self.packet_buffer.add(packets.SV_ACKNOWLEDGE(self.board_id))
    

        while self.running:
            try:
                self.packet_buffer.write_buffer_to_channel(self.communication_channel)
                self.packet_buffer.read_to_input_buffer(self.communication_channel)
                self.handle_communication(self.packet_buffer.input_buffer)
                if self.has_job_config:
                    pass
                    # self.run_job()

                sleep(0.2)
            except Exception as e:
                print(f"Thread {self.thread_ID} has unexpectedly closed")
                print(traceback.format_exc())

            self.packet_buffer.clear_input_buffer()

class manager_thread(threading.Thread):
    threads = []
    spin_up_queue = []
    """Queue that holds which threads need to be spun up."""

    ws_thread: WebsocketThread = None
    def __init__(self): 
        threading.Thread.__init__(self) 
        self.thread_name = "Manager" 
        self.thread_ID = "M" 
        self.queue = []
        self.running = True

        # helper function to execute the threads
    
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

        # for t in self.threads:
        #     t.start()
        #     sleep(0.3)
    
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

    def run(self): 
        if DEBUG:
            for _ in range(1000):
                print("debug")
                # sleep(0.1)
        else:
            #for i in range(4):
            #    self.spin_up_queue.append(i)

            i = 0

            # Datastreamer websocket implementation
            def ws_on_connect(sid, environ):
                self.add_thread(DatastreamerConnection(sid, websocket_channel.ClientWebsocketConnection(self.ws_thread.socketio_server, sid)))
            
            def ws_on_message(sid, data):
                print(sid,": ",data)

            def ws_on_disconnect(sid):
                self.kill_thr(sid)

            
            self.ws_thread = WebsocketThread(5001)
            self.ws_thread.setup_callbacks(ws_on_connect, ws_on_message, ws_on_disconnect)
            self.ws_thread.start()

            while self.running:
                
                self.remove_dead_threads()
                self.create_threads()
                if len(self.queue) > 0:
                    # Find first open board
                    for t in self.threads:
                        if t.is_alive():
                            if t.can_take_job():
                                if len(self.queue) > 0:
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
