# AV Interface (Dummy)
# This is the A dummy interface.py file
# Implements all methods in avionics_interface
# All implementations of avionics_interface must expose an `av_instance` variable which is an instance of
# a class which derives from AvionicsInterface (from avionics_interface.py).
# HilsimRun does not need to be exposed, but must derive from avionics_interface.HilsimRun
# Michael Karpov (2027)

import util.git_commands as git
import util.pio_commands as pio
import util.serial_wrapper as server
import tars_rack.av_platform.csv_datastream as csv_datastream
import util.communication.packets as pkt
import util.communication.serial_channel as serial_interface
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer


class DummyAvionics(AVInterface.AvionicsInterface):
    # TODO: Implement
    pass

class HilsimRun(AVInterface.HilsimRunInterface):
    # TODO: Implement
    pass

av_instance = DummyAvionics(Datastreamer.instance)
