# HILSIM Job Constructor
# This service will be responsible for taking in job IDs and sending raw job data over Serial to the Data Streamer app
# running on the Raspberry Pi devices that we're running.
# Michael Karpov (2027)

import serial_tester
import sys
import serial
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.packets as pkt



if __name__ == "__main__":
    pass