# A small library to test for responses from serial when sent specific data.
import util.packets as pkt
import serial
import time
import traceback
import json
import sys
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


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
    if (result == False):
        print("SERIAL TEST \033[91mFAIL\033[0m")
        print(
            "Test breakdown: \033[92m" +
            str(success) +
            " passed\033[0m, \033[91m" +
            str(fails) +
            " failed\033[0m\n")
    else:
        print("ALL TESTS \033[92mSUCCESSFUL\033[0m")
        print("Test breakdown: \033[92m" + str(success) + " passed\033[0m\n")


def TRY_WRITE(port: serial.Serial, data: pkt.DataPacket, component):
    wait_text(port.name, "Attempting to write " +
              str(len(data)) + " bytes (" + component + ")")
    try:
        port.write(data.serialize().encode())
        PASS("Write:" + port.name, component)
    except serial.SerialTimeoutException as exc:
        FAIL("Write:" + port.name, "Timeout while writing data (" + component + ")")


def RESET_TEST(port: serial.Serial):
    if (port.in_waiting):
        port.read_all()
    port.write("!test_reset".encode())


def CLEAR(port: serial.Serial):
    port.reset_input_buffer()


def FAIL(component, reason):
    global fails, cur_wait_text
    print("\033[91mX\033[0m" + cur_wait_text.replace("#", ""))
    add_test_result(
        "  \033[91mX FAIL\033[0m (\033[90m" +
        component +
        "\033[0m) " +
        reason)
    fails += 1
    display(False)
    exit(255)


def PASS(component, test_text):
    global success, cur_wait_text
    print("\033[92m✓\033[0m" + cur_wait_text.replace("#", ""))
    res = "  \033[92m✓ PASS\033[0m (\033[90m" + \
        component + "\033[0m) " + test_text
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
    if (condition[0]):
        PASS(component, condition[1])
    else:
        FAIL(component, condition[1])


def AWAIT_ANY_RESPONSE(port: serial.Serial, timeout=3.0, comment=""):
    wait_text("COM:" + port.name, "Awaiting a response from port.. " + comment)
    try:
        start_time = time.time()
        while (time.time() - start_time < timeout):
            if port.in_waiting:
                return True, "AWAIT_ANY_RESPONSE recieved a response."
        return False, "AWAIT_ANY_RESPONSE timed out while waiting for serial data"
    except BaseException:
        return False, "AWAIT_ANY_RESPONSE ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc(
        ) + "\033[0m"


def ENSURE_NO_RESPONSE(port: serial.Serial, timeout=3.0):
    wait_text(
        "COM:" + port.name,
        "Checking that the application doesn't respond.")
    try:
        start_time = time.time()
        while (time.time() - start_time < timeout):
            if port.in_waiting:
                data = port.read_all()
                string = data.decode("utf8")
                return False, "ENSURE_NO_RESPONSE recieved a response: " + string
        return True, "ENSURE_NO_RESPONSE succeeded, no data was transferred."
    except BaseException:
        return False, "ENSURE_NO_RESPONSE ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc(
        ) + "\033[0m"


def TRY_OPEN_PORT(port_name):
    wait_text(port_name, "Attempting to open port")
    try:
        port = serial.Serial(port_name, timeout=5, write_timeout=0)
        PASS(
            "COMPORT " +
            port_name,
            "Successfully connected to COM:" +
            port_name)
        return port
    except BaseException:
        FAIL(
            "COMPORT " +
            port_name,
            "Unable to open port:\033[90m\n\n" +
            traceback.format_exc() +
            "\033[0m")


def GET_PACKETS(port: serial.Serial, ignore_heartbeat=True,
                silent=False) -> list[pkt.DataPacket] | None:
    if not silent:
        wait_text("Read:" + port.name, "Decoding Serial Packet")
    try:
        list = pkt.DataPacketBuffer.serial_to_packet_list(port)
        new_list = []
        if ignore_heartbeat:
            for packet in list:
                if (packet.packet_type != pkt.DataPacketType.HEARTBEAT):
                    new_list.append(packet)
        else:
            new_list = list

        return new_list
    except BaseException:
        FAIL(
            "Read:" +
            port.name,
            "GET_PACKETS ran into a non-recoverable error:\033[90m\n\n" +
            traceback.format_exc() +
            "\033[0m")


def ACCUMULATE_PACKETS(
        port: serial.Serial,
        stop_packet_type: pkt.DataPacketType,
        timeout=3.0):
    wait_text(port.name, "Hooking into packet buffer (reading all packets)")
    try:
        all_packets = []
        start_time = time.time()
        while (time.time() - start_time < timeout):
            p_in_buffer = GET_PACKETS(port, False, True)
            should_stop = False
            for p in p_in_buffer:
                all_packets.append(p)
                if (p.packet_type == stop_packet_type):
                    should_stop = True

            if should_stop:
                PASS("Collect packets (stop)", "(stop packet reached) Collected " +
                     str(len(all_packets)) + " packets from buffer")
                return all_packets
        if (len(all_packets) > 0):
            PASS("Collect packets", "Collected " +
                 str(len(all_packets)) + " packets from buffer")
            return all_packets
        else:
            FAIL("Collect packets", "Serial timed out while waiting for packets")
    except Exception as e:
        print(e)
        FAIL(
            "Wait for packet",
            "Wait for packet Encountered a non-recoverable error")


def WAIT_FOR_PACKET_TYPE_ACCUM(
        packet_accum: list[pkt.DataPacket], packet_type: pkt.DataPacketType):
    for packet in packet_accum:
        if (packet.packet_type == packet_type):
            return packet
    FAIL(
        "Wait for packet",
        "No packet of type " +
        str(packet_type) +
        " found in buffer")


def WAIT_FOR_PACKET_TYPE(
        port: serial.Serial,
        packet_type: pkt.DataPacketType,
        timeout=3.0):
    wait_text(port.name, "Waiting for packet of type " + str(packet_type))
    try:
        start_time = time.time()
        while (time.time() - start_time < timeout):
            all_packets = GET_PACKETS(port, False, True)
            for packet in all_packets:
                if (packet.packet_type == packet_type):
                    return packet
        FAIL("Wait for packet " + str(packet_type), "Timed out")
    except BaseException:
        FAIL("Wait for packet " + str(packet_type),
             "Encountered a non-recoverable error")


def GET_PACKET(
        port: serial.Serial,
        ignore_heartbeat=True,
        timeout=3.0) -> pkt.DataPacket | None:
    wait_text("Read:" + port.name, "Decoding Serial Packet")
    try:
        list = pkt.DataPacketBuffer.serial_to_packet_list(port)
        new_list = []
        if ignore_heartbeat:
            for packet in list:
                if (packet.packet_type != pkt.DataPacketType.HEARTBEAT):
                    new_list.append(packet)
        else:
            new_list = list

        return new_list[0]
    except BaseException:
        FAIL(
            "Read:" +
            port.name,
            "GET_PACKET ran into a non-recoverable error:\033[90m\n\n" +
            traceback.format_exc() +
            "\033[0m")


# Reads last packet and detects if it's of a valid format
def VALID_PACKET(
        port: serial.Serial,
        packet: pkt.DataPacket,
        packet_type: pkt.DataPacketType,
        timeout=3.0):
    wait_text(
        "Check packet format",
        "Checking validity of " +
        str(packet_type) +
        " packet")

    try:
        if (packet.packet_type == packet_type):
            if (pkt.PacketValidator.is_client_packet(packet)
                    and pkt.PacketValidator.validate_client_packet):
                return True, "Packet complies to type " + str(packet_type)
            else:
                return False, "VALID_FORMAT FAILED for " + \
                    str(packet_type) + ", got \033[90m\n\n" + str(packet.packet_type) + ": " + str(packet) + "\033[0m"
        else:
            return False, "VALID_FORMAT recieved a different packet type than " + \
                str(packet_type)
    except BaseException:
        return False, "VALID_FORMAT ran into a non-recoverable error:\033[90m\n\n" + traceback.format_exc(
        ) + "\033[0m"
