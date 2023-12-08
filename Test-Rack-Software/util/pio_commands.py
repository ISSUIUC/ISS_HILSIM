# This is a wrapper for remote-command.py to provide an abstraction layer for git commands to be run in a running server.
# Michael Karpov (2027)
#
# This script will run the remote-command.py wrapper commands for you.

import config as cfg
import subprocess
import os
import sys
import threading

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


config = cfg.use_meta

#### Helper functions ####


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


def pio_build(build_target=None):
    """Shortcut for the `build` command in platformio"""
    if (build_target is None):
        run_script(['run'])
    else:
        run_script(['run', '--environment', build_target])


def pio_upload(build_target=None):
    """Shortcut for the `upload` command in platformio, used to flash code."""
    if (build_target is None):
        run_script(['run', '--target', 'upload'])
    else:
        run_script(['run', '--target', 'upload', '--environment', build_target])


def pio_clean(build_target=None):
    """Shortcut for `build clean` in platformio."""
    if (build_target is None):
        run_script(['run', '--target', 'clean', '-s'])
    else:
        run_script(['run', '--target', 'clean',
                   '--environment', build_target, '-s'])
