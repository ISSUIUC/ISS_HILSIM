# A small library to test for responses from serial when sent specific data.
import serial
import time
import traceback
import json
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.packets as pkt
import util.client_packets as cl_pkt

success = 0
fails = 0

cur_wait_text = ""

test_results = []
def add_test_result(text):
    test_results.append(text)

def display(result):
    global success, fails
    print("\n")
    print("Job Constructor Serial Test Results\n")
    for test in test_results:
        print(test)
    print("\n")
    if(result == False):
        print("SERIAL TEST \033[91mFAIL\033[0m")
        print("Test breakdown: \033[92m" + str(success) + " passed\033[0m, \033[91m" + str(fails) + " failed\033[0m\n")
    else:
        print("ALL TESTS \033[92mSUCCESSFUL\033[0m")
        print("Test breakdown: \033[92m" + str(success) + " passed\033[0m\n")

def TRY_WRITE(port: serial.Serial, data, component):
    wait_text(port.name, "Attempting to write " + str(len(data)) + " bytes (" + component + ")")
    try:
        port.write(data)
        PASS("Write:" + port.name, component)
    except serial.SerialTimeoutException as exc:
        FAIL("Write:" + port.name, "Timeout while writing data (" + component + ")")

def RESET_TEST(port: serial.Serial):
    port.write("!test_reset".encode())

def FAIL(component, reason):
    global fails, cur_wait_text
    print("\033[91mX\033[0m" + cur_wait_text.replace("#", ""))
    add_test_result("  \033[91mX FAIL\033[0m (\033[90m" + component + "\033[0m) " + reason)
    fails += 1
    display(False)
    exit(255)

def PASS(component, test_text):
    global success, cur_wait_text
    print("\033[92m✓\033[0m" + cur_wait_text.replace("#", ""))
    res = "  \033[92m✓ PASS\033[0m (\033[90m" + component + "\033[0m) " + test_text
    success += 1
    add_test_result(res)
    return res


def SECTION(text):
    res = "> \033[90m" + text + "\033[0m:"
    add_test_result(res)
    return res

def DONE():
    display(True)
    exit(0)

def wait_text(component, text):
    global cur_wait_text
    cur_wait_text = "  # \033[90m(" + component + ")\033[0m " + text
    print(cur_wait_text, end="\r")


def TEST(component, condition):
    if(condition[0]):
        PASS(component, condition[1])
    else:
        FAIL(component, condition[1])


def AWAIT_ANY_RESPONSE(port: serial.Serial, timeout=3.0):
    wait_text("COM:" + port.name, "Awaiting a response from port..")
    try:
        start_time = time.time()
        while(time.time() - start_time < timeout):
            if port.in_waiting:
                return True, "AWAIT_ANY_RESPONSE recieved a response."
        return False, "AWAIT_ANY_RESPONSE timed out while waiting for serial data"
    except:
        return False, "AWAIT_ANY_RESPONSE ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc() + "\033[0m"
    
def ENSURE_NO_RESPONSE(port: serial.Serial, timeout=3.0):
    wait_text("COM:" + port.name, "Checking that the application doesn't respond.")
    try:
        start_time = time.time()
        while(time.time() - start_time < timeout):
            if port.in_waiting:
                return False, "ENSURE_NO_RESPONSE recieved a response."
        return True, "ENSURE_NO_RESPONSE succeeded, no data was transferred."
    except:
        return False, "ENSURE_NO_RESPONSE ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc() + "\033[0m"
    

def TRY_OPEN_PORT(port_name):
    wait_text(port_name, "Attempting to open port")
    try:
        port = serial.Serial(port_name, timeout=5, write_timeout=2)
        PASS("COMPORT " + port_name, "Successfully connected to COM:" + port_name)
        return port
    except:
        FAIL("COMPORT " + port_name, "Unable to open port:\033[90m\n\n" + traceback.format_exc()  + "\033[0m")
    
def GET_PACKET(port: serial.Serial, timeout=3.0):
    wait_text("Read:" + port.name, "Decoding Serial Packet")

    try:
        start_time = time.time()
        while(time.time() - start_time < timeout):
            if port.in_waiting:
                data = port.read_until(b"\n")
                string = data.decode("utf8")
        
                if string:
                    valid, type, data = pkt.decode_packet(string)
                    if(valid):
                        return valid, type, data
                    else:
                        FAIL("Read:" + port.name, "Failed to decode packet")

        FAIL("Read:" + port.name, "Read timeout")
    except:
        FAIL("Read:" + port.name, "VALID_FORMAT ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc() + "\033[0m")
    
# Reads last packet and detects if it's of a valid format
def VALID_PACKET(port: serial.Serial, packet_type, valid, type, data, timeout=3.0):
    wait_text("Check packet format", "Checking validity of " + packet_type + " packet")

    try:
        if(type == packet_type):
            if(valid):
                return True, "Packet complies to type " + packet_type
            else:
                return False, "VALID_FORMAT FAILED for " + packet_type + ", got \033[90m\n\n" + type + ": " + data + "\033[0m"
        else:
            return False, "VALID_FORMAT recieved a different packet type than " + packet_type
    except:
        return False, "VALID_FORMAT ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc() + "\033[0m"
    