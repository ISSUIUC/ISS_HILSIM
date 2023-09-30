# This is a wrapper for remote-command.py to provide an abstraction layer for git commands to be run in a running server.
# Michael Karpov (2027)
#
# This script will run the remote-command.py wrapper commands for you.

import subprocess
import os
import util.config as config

#### Helper functions ####
def run_script(arg_list):
    print("(git_commands) Running script [python remote-command.py " + str(arg_list) +  "]")
    script_dir = os.path.join(os.path.dirname(__file__), "./remote_command.py")
    args = ['python', script_dir]
    for arg in arg_list:
        args.append(arg)
    subprocess.check_call(args)
    print("(git_commands) Done.")

def remote_clone():
    if(os.path.exists(config.remote_path)):
        print("(git_commands) Remote already exists, skipping [remote_clone]!")
    else:
        run_script(['clone'])

def remote_reset():
    if(not os.path.exists(config.remote_path)):
        print("Remote does not exist! Running [remote_command.py clone]")
        remote_clone()
    run_script(['reset'])
        

def remote_pull_branch(branch):
    if(not os.path.exists(config.remote_path)):
        print("Remote does not exist! Running [remote_command.py clone]")
        remote_clone()
    run_script(['pull', branch])