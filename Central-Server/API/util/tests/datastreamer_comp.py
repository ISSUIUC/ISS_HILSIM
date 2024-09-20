import unittest

import util.communication.packets as pkt
import util.datastreamer_connection

def run(connection: util.datastreamer_connection.DatastreamerConnection):
    print("(tests:datastreamer_comp) Initialized", flush=True)
    comm = connection.communicaton_channel
    buf = pkt.DataPacketBuffer()

    buf.add(pkt.SV_ACKNOWLEDGE(0))
    buf.write_buffer_to_channel(comm)

    # TODO: add an actual testing library and actual tests..


