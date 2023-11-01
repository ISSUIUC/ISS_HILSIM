import threading
from time import sleep

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
 
    def can_take_job(self):
        return not self.has_job_config

    def take_job(self, config):
        self.cur_job_config = config
        self.has_job_config = True

    def run(self): 
        while True:
            if self.has_job_config:
                print(f"Sleeping thread {self.thread_ID} while completing job {self.cur_job_config}")
                sleep(5)
                print(f"completed job {self.cur_job_config} on thread {self.thread_ID}")

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
        print(f"added job {config}")
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
            print("after threads")
            i = 0
            while True:
            #     print("Manager Running",i)
            #     i+=1


                # for t in self.threads:
                #     t.update_id("ab")

                # if self.num != prev:
                #     print("a thing")
                #     prev = self.num

                if len(self.queue) > 0:
                    # Find first open board
                    for t in self.threads:
                        if t.can_take_job():
                            if len(self.queue) > 0:
                                cur_job = self.queue.pop(0)
                                t.take_job(cur_job)

                                print(f"Gave {t.thread_ID} job {cur_job}")

                sleep(0.2)
                # print(f"loop #{i}")
                i+=1
        
        print("exit")
