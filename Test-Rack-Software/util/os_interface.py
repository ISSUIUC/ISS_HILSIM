import os
import io
import subprocess

# Makes the datastreamer only work/ run if the device we are running on is a rasberry pi
def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def get_python_root() -> str:
    """Retrieves the python root for git and pio commands. Only works on Raspberry Pi!"""
    if is_raspberrypi():
        python_root = "/home/illinoisspacesociety/.platformio/penv/bin/"
        if python_root and python_root[-1] != '/':
            python_root += "/"
        return python_root
    return ""