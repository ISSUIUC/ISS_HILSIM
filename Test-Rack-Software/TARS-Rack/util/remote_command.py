# This is a wrapper for GitPy as a script to implement clone, reset, and pull functionality for hilserv.
# Michael Karpov (2027)
#
# GitPy leaks system resources so it cannot be run constantly. As such we can instead invoke this file
# as a script (python remote-command.py clone) to do most of the heavy lifting for you.
# The biggest caveat of this script is it depending on being run from a python shell. Luckily, git-commands.py
# provides an abstraction layer for this script.

import config
from git import Repo
import sys
import os, shutil

"""
Clone the repository defined in config into the directory defined in config. (Usually ./remote)
"""
def clone_repo():
    print("(git_commands) Cloning repository..")
    Repo.clone_from(config.repository_url, config.remote_path)

"""
Reset the repository back to its "master" or "main" state by stashing current changes, switching to main, then pulling.
"""
def reset_repo():
    repo = Repo(config.remote_path)
    print("(git_commands) Stashing changes..")
    repo.git.checkout(".")
    print("(git_commands) Checking-out and pulling origin/master..")
    repo.git.checkout("master")
    repo.git.pull()

"""
Switch to a specific branch and pull it
@param branch The branch to pull from the remote defined in config.
"""
def pull_branch(branch):
    repo = Repo(config.remote_path)
    print("(git_commands) Fetching repository data")
    repo.git.fetch()
    print("(git_commands) checking out and pulling origin/" + branch)
    repo.git.checkout(branch)
    repo.git.pull()


############## SCRIPT ##############
# This is where the script decides which function above to call.

argc = len(sys.argv) # Number of arguments
if(argc == 1): # Program requires arguments to run
    print("Incorrect usage: \n- python gitpy-wrapper.py clone\n- python gitpy-wrapper.py clear \n- python gitpy-wrapper.py pull [branch-name]")

if(argc == 2):
    if(sys.argv[1] == "clone"):
        clone_repo() # Clone command implementation
        exit(0)
    if(sys.argv[1] == "reset"):
        reset_repo() # Reset command implementation
        exit(0)
    
    print("Incorrect usage [1 arg]: \n- python gitpy-wrapper.py clone\n- python gitpy-wrapper.py clear")

if(argc == 3):
    if(sys.argv[1] == "pull"):
        branch_name = sys.argv[2]
        pull_branch(branch_name) # Pull command implementation
        exit(0)




