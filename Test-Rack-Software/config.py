# This file is not a "traditional" configuration file, it instead provides runtime symbolic links to a 
# defined avionics interface. This means that by defining which stack you want to use in the
# next couple of lines, this file automatically tells `main.py` which file to access.

# Metadata needs to be imported first, so the avionics system knows what data to use for startup.
# Import all metaconfigs
import tars_rack.platform_meta as TARSmkIVmeta


# == EDIT THE VARIABLE BELOW TO CHANGE WHICH METADATA IS USED ==
use_meta = TARSmkIVmeta.meta
"""Which `platform_meta.py` file should we use?"""
# ==============================================================


# Continue by importing all interfaces
import tars_rack.interface as TARSmkIV

# == EDIT THE VARIABLE BELOW TO CHANGE WHICH INTERFACE IS USED ==
use_interface = TARSmkIV
"""Which interface should this testing rack use?"""
# ===============================================================


# Post-config setup
# nothing here lol
print("(config) Configuration loaded")
