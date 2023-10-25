# Utilities directory

This directory contains all utility functions and libraries written to make flashing and running code easier. In an ideal world, the contents of this directory are untouched except to add new utilities.

`avionics_interface.py`
Provides interfaces for the `AvionicsInterface` and `HilsimRun` classes.

`avionics_meta.py`
Provides an interface for the required `platform_meta.py` file.

`datastreamer_server.py`
Provides a class for state and data management for datastreamer.

`git_commands.py`
A wrapper for `remote_command.py` (itself a wrapper for GitPy).

`handle_jobs.py`
A helper file for handling all job-related functions (Hooks into datastreamer functionality)

`handle_packets.py`
A helper file for handling all server packets (Hooks into datastreamer functionality)

`packets.py`
Establishes packet communication protocol for datastreamer.

`pio_commands.py`
Wrapper for **platformio**

`remote_command.py`
Memory safe wrapper for GitPy (which leaks memory)

`serial_wrapper`
Provides some initialization functions for serial