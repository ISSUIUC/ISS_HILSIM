# This is a wrapper for remote-command.py to provide an abstraction layer for git commands to be run in a running server.
# Michael Karpov (2027)
#
# This script will run the remote-command.py wrapper commands for you.

import subprocess
import os
import config as cfg
import util.avionics_meta

config: util.avionics_meta.PlatformMetaInterface = cfg.use_meta

#### Helper functions ####


def run_script(arg_list):
    """Runs remote_command.py with the given argument list
    @arg_list {List[str]} -- A list of arguments to execute the command with
    @description remote_command.py is a wrapper for GitPy, which leaks memory"""
    print(
        "(git_commands) Running script [python remote-command.py " +
        str(arg_list) +
        "]")
    script_dir = os.path.join(os.path.dirname(__file__), "./remote_command.py")
    args = ['python', script_dir]
    for arg in arg_list:
        args.append(arg)
    subprocess.check_call(args)
    print("(git_commands) Done.")


def remote_clone():
    """Clones the repository defined in the config"""
    print("Exists", config.remote_path)
    if (os.path.exists(config.remote_path)):
        print("(git_commands) Remote already exists, skipping [remote_clone]!")
    else:
        run_script(['clone'])


def remote_reset():
    """Resets the remote to `main`"""
    if (not os.path.exists(config.remote_path)):
        print("Remote does not exist! Running [remote_command.py clone]")
        remote_clone()
    run_script(['reset'])


def remote_pull_branch(branch):
    """Pulls a specific branch"""
    if (not os.path.exists(config.remote_path)):
        print("Remote does not exist! Running [remote_command.py clone]")
        remote_clone()
    run_script(['pull', branch])
