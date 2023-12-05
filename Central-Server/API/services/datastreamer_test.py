# HILSIM Datastreamer Test
# This will test all of the datastreamer functionality
# Michael Karpov (2027)

import serial_tester
import sys
import serial
import os
import time
import json
import util.packets as pkt

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


comport = "COM9"

if __name__ == "__main__":

    # Get job data
    job_data = pkt.JobData(0)

    # Open csv file
    file = open(
        os.path.join(
            os.path.dirname(__file__),
            "./datastreamer_test_data.csv"),
        'r')
    csv_data = file.read()

    print("Detected script running as __main__, beginning test of Data Streamer functionality")
    serial_tester.SECTION("Test setup")
    port = serial_tester.TRY_OPEN_PORT(comport)
    serial_tester.TEST(
        "Waiting for any packet..",
        serial_tester.AWAIT_ANY_RESPONSE(
            port,
            100,
            "Run the datastreamer script"))

    # > ACK 1
    ack_test_boardid = 4
    serial_tester.SECTION("[1/2] ACK - Valid Acknowledge packet")
    serial_tester.CLEAR(port)

    serial_tester.TRY_WRITE(port, pkt.SV_ACKNOWLEDGE(
        ack_test_boardid), "Writing valid ACK packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.READY, 10)
    serial_tester.TEST(
        "Packet after ACK is READY",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.READY))
    serial_tester.TRY_WRITE(
        port,
        pkt.SV_IDENT_PROBE(),
        "Writing IDENT? packet after ACK packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.ID_CONFIRM)

    serial_tester.TEST(
        "IDENT? packet after ACK packet conforms to ID-CONF",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.ID_CONFIRM))

    cond = False
    res = "ID-CONF does not return correct board ID after ACK (Expected " + str(
        ack_test_boardid) + ", but got " + str(packet.data['board_id']) + ")"
    if (packet.data['board_id'] == ack_test_boardid):
        cond = True
        res = "ID-CONF correctly returned board ID " + str(ack_test_boardid)
    serial_tester.TEST("Connected board returns properly set ID", (cond, res))

    # > PING
    serial_tester.SECTION("PING - Signal testing")

    serial_tester.TRY_WRITE(port, pkt.SV_PING(), "Writing PING packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(port, pkt.DataPacketType.PONG)
    serial_tester.TEST(
        "Complies to PONG packet format",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.PONG))

    # > IDENT?
    serial_tester.SECTION("IDENT? - Identity confirmation")
    serial_tester.TRY_WRITE(
        port,
        pkt.SV_IDENT_PROBE(),
        "Writing IDENT_PROBE packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.ID_CONFIRM)
    serial_tester.TEST(
        "Complies to ID-CONF packet format",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.ID_CONFIRM))

    # > ACK 2 (invalid)
    ack_test_boardid = 0
    serial_tester.SECTION("[2/2] ACK - Acknowledge packet after ACK")
    serial_tester.TRY_WRITE(port, pkt.SV_ACKNOWLEDGE(
        ack_test_boardid), "Writing invalid ACK packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.INVALID)
    serial_tester.TEST(
        "INVALID packet after second ACK packet",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.INVALID))

    # > REASSIGN 1
    reassign_test_boardid = 2
    serial_tester.SECTION("REASSIGN - [Valid] Assign new board ID to rack")
    serial_tester.TRY_WRITE(
        port,
        pkt.SV_REASSIGN(reassign_test_boardid),
        "Writing REASSIGN packet")
    serial_tester.TEST(
        "No response from application [Success]",
        serial_tester.ENSURE_NO_RESPONSE(
            port,
            1.0))
    serial_tester.TRY_WRITE(
        port,
        pkt.SV_IDENT_PROBE(),
        "Writing IDENT? packet after REASSIGN packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.ID_CONFIRM)
    serial_tester.TEST(
        "IDENT? packet after REASSIGN packet conforms to ID-CONF",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.ID_CONFIRM))

    cond = False
    res = "ID-CONF does not return correct board ID after REASSIGN (Expected " + str(
        reassign_test_boardid) + ", but got " + str(packet.data['board_id']) + ")"
    if (packet.data['board_id'] == reassign_test_boardid):
        cond = True
        res = "ID-CONF correctly returned board ID " + \
            str(reassign_test_boardid)
    serial_tester.TEST("Connected board returns properly set ID", (cond, res))

    # Job (cancel)
    serial_tester.SECTION("Cancel job test")

    serial_tester.TRY_WRITE(
        port,
        pkt.SV_JOB(
            job_data,
            csv_data),
        "Writing JOB packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.JOB_UPDATE, 30)
    serial_tester.TEST(
        "Packet after valid JOB packet complies to JOB-UPD",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.JOB_UPDATE))
    job_good = packet.data['job_status']['job_state'] == 2 and packet.data['job_status']['current_action'] == "ACCEPTED"
    serial_tester.TEST(
        "Ensure job_state is '2' and current_action is 'ACCEPTED'",
        (job_good,
         f"Got job_ok {packet.data['job_status']['job_state']} and current_action '{packet.data['job_status']['current_action']}'"))

    # Check for flash workflow
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.JOB_UPDATE, 30)
    serial_tester.TEST(
        "(part 1) Waiting for COMPILE_READY",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.JOB_UPDATE))
    job_good = packet.data['job_status']['job_state'] == 2 and packet.data['job_status']['current_action'] == "COMPILE_READY"
    serial_tester.TEST(
        "Ensure job_state is '2' and current_action is 'COMPILE_READY'",
        (job_good,
         f"Got job_ok {packet.data['job_status']['job_state']} and current_action '{packet.data['job_status']['current_action']}'"))

    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.JOB_UPDATE, 100)
    serial_tester.TEST(
        "(part 2) Waiting for COMPILED",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.JOB_UPDATE))
    job_good = packet.data['job_status']['job_state'] == 2 and packet.data['job_status']['current_action'] == "COMPILED"
    serial_tester.TEST(
        "Ensure job_state is '2' and current_action is 'COMPILED'",
        (job_good,
         f"Got job_ok {packet.data['job_status']['job_state']} and current_action '{packet.data['job_status']['current_action']}'"))

    # Job updates
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.JOB_UPDATE, 10)
    serial_tester.TEST(
        "(part 3) Waiting for BEGIN",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.JOB_UPDATE))
    job_good = packet.data['job_status']['job_state'] == 3 and (
        packet.data['job_status']['current_action'] == "BEGIN" or packet.data['job_status']['current_action'] == "RUNNING")
    serial_tester.TEST(
        "Ensure job_ok is True",
        (job_good,
         f"Got job_ok {packet.data['job_status']['job_state']}"))

    # Terminate
    serial_tester.SECTION("Terminates gracefully and successfully")
    time.sleep(1)
    serial_tester.CLEAR(port)
    serial_tester.TRY_WRITE(
        port,
        pkt.SV_TERMINATE(),
        "Writing TERMINATE packet")

    # Next packet READY?
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.READY, 10)
    serial_tester.TEST(
        "Packet after terminate is READY",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.READY))

    # Cycle test
    serial_tester.SECTION("Test of cycle")
    serial_tester.TRY_WRITE(port, pkt.SV_CYCLE(), "Writing CYCLE packet")
    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.READY, 15)
    serial_tester.TEST(
        "Packet after cycle is READY",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.READY))

    # Actual job finish
    serial_tester.SECTION("Full job run (no intermediate tests)")

    # Simulated cooldown period
    time.sleep(5)

    serial_tester.TRY_WRITE(
        port,
        pkt.SV_JOB(
            job_data,
            csv_data),
        "Writing JOB packet")

    packet = serial_tester.WAIT_FOR_PACKET_TYPE(
        port, pkt.DataPacketType.DONE, 180)  # Should finish in 3 min ideally
    serial_tester.TEST(
        "Job finishes",
        serial_tester.VALID_PACKET(
            port,
            packet,
            pkt.DataPacketType.DONE))

    print(packet.raw_data)

    # CLEANUP
    serial_tester.SECTION("Cleanup")
    serial_tester.TEST(
        "Ensure empty serial bus",
        serial_tester.ENSURE_NO_RESPONSE(
            port,
            1.0))
    serial_tester.CLEAR(port)
    serial_tester.DONE()
