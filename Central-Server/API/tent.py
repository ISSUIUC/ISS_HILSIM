

# importing
import time
from threading import Thread
 
 
# making first thread of Geeks
class Geeks(Thread):
   
    def run(self):
        for x in range(4):
            print("Geeks")
             
            # adding delay of 2.2 seconds
            time.sleep(2.2)
 
# making second thread of For
class For(Thread):
   
    def run(self):
        for x in range(3):
            print('For')
             
            # adding delay of 2.3 seconds
            time.sleep(2.3)
 
def t():
    print("Hello")
    
    # making the object for both the 
    # threads separately
    g1 = Geeks()
    f1 = For()
    
    # starting the first thread
    g1.start()
    
    # starting the second thread
    f1.start()
    
    # waiting for the both thread to join
    # after completing their job
    g1.join()
    f1.join()
    
    # when threads complete their jobs
    # message will be printed
    print("All Done!!")