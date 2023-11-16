import threading
import database
import time
import jobs
import datetime

class JobBalancer(threading.Thread):
    # Set a chron job
    def __init__(self):
        threading.Thread.__init__(self) 
        self.job_list = []
        self.last_time = None

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
        db_query = "SELECT * from hilsim_runs where hilsim_runs.run_status = {1} and hilsim_runs.submitted_time > now() - interval '10s'".format(database.get_db_name(), jobs.JobStatus.QUEUED.value)
        cursor.execute(db_query)
        queue = cursor.fetchall()
        self.last_time = datetime.datetime.now()
        return queue

    def run(self):
        while True:
            # Now do some math to get the current available jobs...
            if self.last_time == None:
                try:
                    self.get_no_last_time_queue()
                except:
                    # Ignore error :(
                    pass
            else:
                try:
                    self.last_time_queue()
                except:
                    # Ignore error :(
                    pass
            # Add to job list...

            time.sleep(10)