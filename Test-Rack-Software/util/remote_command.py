# This is a wrapper for GitPy as a script to implement clone, reset, and pull functionality for hilserv.
# Michael Karpov (2027)
#
# GitPy leaks system resources so it cannot be run constantly. As such we can instead invoke this file
# as a script (python remote-command.py clone) to do most of the heavy lifting for you.
# The biggest caveat of this script is it depending on being run from a python shell. Luckily, git-commands.py
# provides an abstraction layer for this script.
import os  # noqa
import sys  # noqa

sys.path.insert(0, os.path.abspath(  # noqa
    os.path.join(os.path.dirname(__file__), '..')))  # noqa

import util.avionics_meta  # noqa
from git import Repo  # noqa
import config  # noqa


config_meta: util.avionics_meta.PlatformMetaInterface = config.use_meta


def clone_repo():
    """
    Clone the repository defined in config into the directory defined in config. (Usually ./remote)
    """
    print("(git_commands) Cloning repository..")
    print("ASDF", config_meta.repository_url)
    Repo.clone_from(config_meta.repository_url, config_meta.remote_path)


def reset_repo():
    """
    Reset the repository back to its "master" or "main" state by stashing current changes, switching to main, then pulling.
    """
    repo = Repo(config_meta.remote_path)
    print("(git_commands) Stashing changes..")
    repo.git.checkout(".")
    print("(git_commands) Checking-out and pulling origin/master..")
    repo.git.checkout("master")
    repo.git.pull()


def pull_branch(branch):
    """
    Switch to a specific branch and pull it
    @param branch The branch to pull from the remote defined in config.
    """
    repo = Repo(config_meta.remote_path)
    print("(git_commands) Fetching repository data")
    repo.git.fetch()
    print("(git_commands) checking out and pulling origin/" + branch)
    repo.git.checkout(branch)
    repo.git.pull()


############## SCRIPT ##############
# This is where the script decides which function above to call.

argc = len(sys.argv)  # Number of arguments
if (argc == 1):  # Program requires arguments to run
    print(
        "Incorrect usage: \n- python gitpy-wrapper.py clone\n- python gitpy-wrapper.py clear \n- python gitpy-wrapper.py pull [branch-name]")

if (argc == 2):
    if (sys.argv[1] == "clone"):
        clone_repo()  # Clone command implementation
        exit(0)
    if (sys.argv[1] == "reset"):
        reset_repo()  # Reset command implementation
        exit(0)

    print(
        "Incorrect usage [1 arg]: \n- python gitpy-wrapper.py clone\n- python gitpy-wrapper.py clear")

if (argc == 3):
    if (sys.argv[1] == "pull"):
        branch_name = sys.argv[2]
        pull_branch(branch_name)  # Pull command implementation
        exit(0)
