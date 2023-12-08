# This file is not a "traditional" configuration file, it instead provides runtime symbolic links to a
# defined avionics interface. This means that by defining which stack you want to use in the
# next couple of lines, this file automatically tells `main.py` which file
# to access.
import util.dynamic_url
from util.communication.communication_interface import CommunicationChannelType

# Metadata needs to be imported first, so the avionics system knows what data to use for startup.
# Import all metaconfigs
import tars_rack.platform_meta as TARSmkIVmeta  # noqa
import midas_rack.platform_meta as MIDASmkImeta  # noqa
import dummy_rack.platform_meta as DUMMYmeta  # noqa

# == EDIT THE VARIABLE BELOW TO CHANGE WHICH METADATA IS USED ==
use_meta = MIDASmkImeta.meta
"""Which `platform_meta.py` file should we use?"""
# ==============================================================

# If it's empty then it is the default python
python_root = "~/.platformio/penv/bin/"

# Add trailing forward slash
if python_root and python_root[-1] != '/':
    python_root += "/"

# Continue by importing all interfaces
import tars_rack.interface as TARSmkIV  # noqa
import midas_rack.interface as MIDASmkI  # noqa
import dummy_rack.interface as DUMMY  # noqa

# == EDIT THE VARIABLE BELOW TO CHANGE WHICH INTERFACE IS USED ==
use_interface = MIDASmkI
"""Which interface should this testing rack use?"""
# ===================== OTHER CONFIGURATION =====================
preferred_communication_channel = CommunicationChannelType.WEBSOCKET
"""The preferred channel of communication between the datastreamer and server. This method will be tried first. Defaults to `SERIAL`"""


custom_python = ""
# ===============================================================
api_url = util.dynamic_url.get_dynamic_url()

# Post-config setup
# nothing here lol
print("(config) Configuration loaded")
