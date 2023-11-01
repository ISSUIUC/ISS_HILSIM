import threading
from time import sleep

l = ["0", "1", "2", "3"]

DEBUG = False


class board_thread(threading.Thread): 
    def __init__(self, thread_name, thread_ID): 
        threading.Thread.__init__(self) 
        self.thread_name = thread_name 
        self.thread_ID = thread_ID 
        self.cur_job_config = None
        self.has_job_config = False
 
    def can_take_job(self):
        return self.has_job_config

    def take_job(self, config):
        self.cur_job_config = config
        self.has_job_config = True

    def run(self): 
        while True:
            if self.has_job_config:


                self.has_job_config = False
                self.cur_job_config = None
                pass

            sleep(0.2)

class manager_thread(threading.Thread): 
    threads = []
    def __init__(self): 
        threading.Thread.__init__(self) 
        self.thread_name = "Manager" 
        self.thread_ID = "M" 
        self.queue = []
        # helper function to execute the threads

    def create_threads(self):
        for t in l:
            thr = board_thread(t, t)
            thr.start()
            self.threads.append(thr)

        # for t in self.threads:
        #     t.start()
        #     sleep(0.3)
    
    # adds job to queue 
    def add_job(self, config):
        self.queue.append(config)
        pass

    def run(self): 
        if DEBUG:
            for _ in range(1000):
                print("debug")
                # sleep(0.1)
        else:
            print("in run")
            self.create_threads()

            while True:
            #     print("Manager Running",i)
            #     i+=1


                # for t in self.threads:
                #     t.update_id("ab")

                # if self.num != prev:
                #     print("a thing")
                #     prev = self.num

                if self.queue.__len__() > 0:
                    # Find first open board
                    for t in self.threads:
                        if t.can_take_job():
                            t.take_job(self.queue.pop())

                sleep(0.2)
                print("running")
        
        print("exit")
