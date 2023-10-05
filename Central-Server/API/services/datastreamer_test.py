# HILSIM Datastreamer Test
# This will test all of the datastreamer functionality
# Michael Karpov (2027)

import serial_tester
import sys
import serial
import os

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.packets as pkt




comport = "COM9"

if __name__ == "__main__":
    print("Detected script running as __main__, beginning test of Data Streamer functionality")
    serial_tester.SECTION("Test setup")
    port = serial_tester.TRY_OPEN_PORT(comport)

    # Setup
    serial_tester.RESET_TEST(port)

    # > PING
    serial_tester.SECTION("PING - Signal testing") 
    serial_tester.TRY_WRITE(port, pkt.construct_ping().encode(), "Writing PING packet")
    serial_tester.TEST("Responds to PING packet", serial_tester.AWAIT_ANY_RESPONSE(port))
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("Complies to PONG packet format", serial_tester.VALID_PACKET(port, "PONG", valid, type, data))

    # > IDENT?
    serial_tester.SECTION("IDENT? - Identity confirmation") 
    serial_tester.TRY_WRITE(port, pkt.construct_ident_probe().encode(), "Writing IDENT? packet")
    serial_tester.TEST("Responds to IDENT? packet", serial_tester.AWAIT_ANY_RESPONSE(port))
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("Complies to ID-CONF packet format", serial_tester.VALID_PACKET(port, "ID-CONF", valid, type, data))

    # > ACK 1
    ack_test_boardid = 4
    serial_tester.SECTION("[1/2] ACK - Valid Acknowledge packet") 
    serial_tester.TRY_WRITE(port, pkt.construct_acknowledge(ack_test_boardid).encode(), "Writing valid ACK packet")
    serial_tester.TEST("No response from application [Success]", serial_tester.ENSURE_NO_RESPONSE(port, 1.0))
    serial_tester.TRY_WRITE(port, pkt.construct_ident_probe().encode(), "Writing IDENT? packet after ACK packet")
    serial_tester.TEST("Responds to IDENT? packet after ACK packet", serial_tester.AWAIT_ANY_RESPONSE(port))
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("IDENT? packet after ACK packet conforms to ID-CONF", serial_tester.VALID_PACKET(port, "ID-CONF", valid, type, data))
    
    cond = False
    res = "ID-CONF does not return correct board ID after ACK (Expected " + str(ack_test_boardid) + ", but got " + str(data['board_id']) + ")"
    if(data['board_id'] == ack_test_boardid):
        cond = True
        res = "ID-CONF correctly returned board ID " + str(ack_test_boardid)
    serial_tester.TEST("Connected board returns properly set ID", (cond, res))

    # > ACK 2 (invalid)
    ack_test_boardid = 0
    serial_tester.SECTION("[2/2] ACK - Acknowledge packet after ACK") 
    serial_tester.TRY_WRITE(port, pkt.construct_acknowledge(ack_test_boardid).encode(), "Writing invalid ACK packet")
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("INVALID packet after second ACK packet", serial_tester.VALID_PACKET(port, "INVALID", valid, type, data))
    
    # > REASSIGN 1
    reassign_test_boardid = 2
    serial_tester.SECTION("REASSIGN - [Valid] Assign new board ID to rack") 
    serial_tester.TRY_WRITE(port, pkt.construct_reassign(reassign_test_boardid).encode(), "Writing REASSIGN packet")
    serial_tester.TEST("No response from application [Success]", serial_tester.ENSURE_NO_RESPONSE(port, 1.0))
    serial_tester.TRY_WRITE(port, pkt.construct_ident_probe().encode(), "Writing IDENT? packet after REASSIGN packet")
    serial_tester.TEST("Responds to IDENT? packet after REASSIGN packet", serial_tester.AWAIT_ANY_RESPONSE(port))
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("IDENT? packet after REASSIGN packet conforms to ID-CONF", serial_tester.VALID_PACKET(port, "ID-CONF", valid, type, data))
    
    cond = False
    res = "ID-CONF does not return correct board ID after REASSIGN (Expected " + str(reassign_test_boardid) + ", but got " + str(data['board_id']) + ")"
    if(data['board_id'] == reassign_test_boardid):
        cond = True
        res = "ID-CONF correctly returned board ID " + str(reassign_test_boardid)
    serial_tester.TEST("Connected board returns properly set ID", (cond, res))

    # > REASSIGN 2
    reassign_test_boardid = 8
    serial_tester.RESET_TEST(port)
    serial_tester.SECTION("REASSIGN - [Invalid] Assign new board ID to fresh rack") 
    serial_tester.TRY_WRITE(port, pkt.construct_reassign(reassign_test_boardid).encode(), "Writing invalid REASSIGN packet")
    valid, type, data = serial_tester.GET_PACKET(port)
    serial_tester.TEST("INVALID packet after non-initialized REASSIGN packet", serial_tester.VALID_PACKET(port, "INVALID", valid, type, data))

    # CLEANUP
    serial_tester.SECTION("Cleanup")
    serial_tester.TEST("Ensure empty serial bus", serial_tester.ENSURE_NO_RESPONSE(port, 1.0))
    serial_tester.RESET_TEST(port)
    serial_tester.DONE()

