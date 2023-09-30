# RUN SETUP (TARS)
# This is the specific run_setup.py file for the TARS avionics stack.
# @implements first_setup() -- Performs the first setup (assuming fresh install). 
# @implements code_reset() -- Resets the project to a "known" state (Usually master branch).
# @implements code_pull(str git_branch) -- Sets up the project to do a code flash.
# @implements code_flash() -- Flashes the code to the avionics stack
# @implements run_hilsim(str raw_csv) -- Runs HILSIM with flashed code and returns a string result

import util.git_commands as git

"""
This function must be implemented in all run_setup.py functions for each stack
first_setup(): Installs repository and sets up all actions outside of the repository to be ready to accept inputs.
"""
def first_setup():
    git.remote_clone()

"""
This function must be implemented in all run_setup.py functions for each stack
code_reset(): Resets the repository to a default state
TARS: Resets the TARS-Software repository to master branchd
"""
def code_reset():
    git.remote_reset()

"""
This function must be implemented in all run_setup.py functions for each stack
code_pull(str git_branch): Stashes changes and pulls a specific branch.
"""
def code_pull(git_branch: str):
    git.remote_pull_branch(git_branch)

"""
This function must be implemented in all run_setup.py functions for each stack
code_flash(): Flashes currently staged code to the avionics stack.
TARS: Uses environment mcu_hilsim
"""
def code_flash():
    # TODO: Implement
    pass

"""
This function must be implemented in all run_setup.py functions for each stack
run_hilsim(str raw_csv): Runs the HILSIM program on the current avionics stack with the given flight data
"""
def run_hilsim():
    # TODO: Implement
    pass


