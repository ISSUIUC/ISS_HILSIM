import threading
from time import sleep
import random

# Threads and names, replace with availible
l = ["0", "1", "2", "3"]

DEBUG = False


class board_thread(threading.Thread): 
    def __init__(self, thread_name, thread_ID): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 
        self.cur_job_config = None
        self.has_job_config = False
        self.running = True
 
    def can_take_job(self):
        return not self.has_job_config

    def take_job(self, config):
        self.cur_job_config = config
        self.has_job_config = True
    
    def terminate(self):
        self.running = False

    def run(self): 
        while self.running:
            try:
                if self.has_job_config:
                    rand_time = round(random.random() * 15, 2)

                    print(f"Sleeping thread {self.thread_ID} for {rand_time} seconds while completing job {self.cur_job_config}", flush=True)
                    sleep(rand_time)
                    print(f"completed job {self.cur_job_config} on thread {self.thread_ID}", flush=True)

                    self.has_job_config = False
                    self.cur_job_config = None

                sleep(0.2)
            except Exception:
                print(f"Thread {self.thread_ID} has unexpectedly closed")

class manager_thread(threading.Thread): 
    threads = []
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
        while len(l) > 0:
            t = l.pop(0)
            thr = board_thread(t, t)
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
        l.append(thr)
    
    def terminate_all(self):
        for t in self.threads:
            if t.is_alive():
                t.terminate()
                print(f"terminated thread {t.thread_ID}", flush=True)
        
        self.running = False
        print(f"terminated manager", flush=True)
        
    def remove_dead_threads(self):
        self.threads = [thr for thr in self.threads if thr.is_alive()]
    
    def kill_thr(self, idx):
        if 0 <= idx < len(self.threads):
            del self.threads[idx]

    def run(self): 
        if DEBUG:
            for _ in range(1000):
                print("debug")
                # sleep(0.1)
        else:
            i = 0
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
            
                if i%20==0:
                    print("Threads: ", self.threads, flush=True)
                    print("Current queue: ", self.queue, flush=True)
        
        print("exit")
