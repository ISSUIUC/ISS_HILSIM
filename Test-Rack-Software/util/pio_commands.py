# This is a wrapper for remote-command.py to provide an abstraction layer for git commands to be run in a running server.
# Michael Karpov (2027)
#
# This script will run the remote-command.py wrapper commands for you.

import config as cfg
import subprocess
import os
import sys
import threading
import time

COMPILATION_CORE_USAGE = 4

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


config = cfg.use_meta

#### Helper functions ####

def run_script_threaded(arg_list, callback: callable = None):
    """Runs a platformio command in a subthread. Calls `callback` every iteration."""
    thr = threading.Thread(target=run_script, args=(arg_list,))
    thr.start()
    while thr.is_alive():
        # Allow time to set up thread and actually let thread to run, since two threads in the same process cannot execute at the same time
        # time.sleep(0.02)
        if callback is not None:
            callback()

def run_script(arg_list):
    """Runs a platformio command in a python subprocess"""
    print("(pio_commands) Running script [platformio " + str(arg_list) + "]")
    working_dir = config.platformio_path

    args = [cfg.python_root + 'platformio']
    for arg in arg_list:
        args.append(arg)
    if os.name == 'nt':
        # If windows
        command_sep = " & "
    else:
        # A posix system
        command_sep = ";"
    command_string = f"cd {working_dir}" + command_sep + " ".join(args)
    subprocess.check_call(command_string, shell=True)
    print("(pio_commands) Done.")


def pio_build(build_target=None, callback=None):
    """Shortcut for the `build` command in platformio"""
    if (build_target is None):
        run_script_threaded(['run', '-j', str(COMPILATION_CORE_USAGE)], callback=callback)
    else:
        run_script_threaded(['run', '-j', str(COMPILATION_CORE_USAGE), '--environment', build_target], callback=callback)


def pio_upload(build_target=None, callback=None):
    """Shortcut for the `upload` command in platformio, used to flash code."""
    if (build_target is None):
        run_script_threaded(['run', '--target', 'upload', '-j', str(COMPILATION_CORE_USAGE)], callback=callback)
    else:
        run_script_threaded(['run', '--target', 'upload', '-j', str(COMPILATION_CORE_USAGE), '--environment', build_target], callback=callback)


def pio_clean(build_target=None, callback=None):
    return
    """Shortcut for `build clean` in platformio."""
    if (build_target is None):
        run_script_threaded(['run', '--target', 'clean', '-s'], callback=callback)
    else:
        run_script_threaded(['run', '--target', 'clean',
                   '--environment', build_target, '-s'], callback=callback)
