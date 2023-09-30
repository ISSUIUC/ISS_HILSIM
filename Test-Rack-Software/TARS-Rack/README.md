## HILSIM Data Streamer - TARS
This is the directory storing the code for the TARS data-streaming module to be used with HILSIM server. Feel free to clone this repository and edit it to suit your specific use-cases.

##### DELETEME
I've written a couple of wrapper libraries around GitPython and Platformio which should make development much simpler. They are located in `git_commands` and `pio_commands` respectively, I suggest taking a look into each one, but they're both quite simple:

**git_commands** exposes 4 functions, which each call the `remote_commands` script with different parameters. `remote_commands` is the *actual* wrapper around GitPython (if you're interested in why I chose to do it this way, feel free to ask!) and doesn't need to be edited directly unless you wish to add functionality. The other two libraries will be (to some extent) dependent on the actual architecture we're uploading stuff.

**What is implemented for you:**
`util/git_commands.py` -- This is a library that performs all the git actions you will need for this application <br/>
`util/pio_commands.py` -- Library to handle all the pio commands you will need for this application <br/>
`util/packets.py` -- Constructors for all communication packets we'll be sending. <br/>
`util/serial_wrapper.py` -- **Not fully implemented!** IDENT functionality and packet decoding is implemented for you, but you will need to handle the other packets (explained below). <br/>
`av_platform/run_setup.py` -- **Not fully implemented!** I took the liberty of doing the easy ones, you need to implement the platform-specific `flash` command and the platform specific `run_hilsim` command. <br/>

**What needs to be implemented:**
The rest of `util/serial_wrapper.py` -- Implement communication with the server (fun part)! <br/>
`main.py` -- The actual server itself <br/>
The rest of `av_platform/run_setup.py` -- Implement platform-specific code pushing and hilsim runs. <br/>

Here are your technical requirements for server communication:
- Whenever an `IDENT?` packet is recieved, IF this board was assigned an id before, send an ID-CONF packet with the board type and board id stored. OTHERWISE, send an IDENT packet.
- Whenever an `ACK` packet is recieved, store the board ID assigned and which port sent it (This will be the server port).
- Whenever a `REASSIGN` packet is recieved, change to board_id but do not terminate any jobs.
- Whenever a `TERMINATE` packet is recieved, immediately terminate all currently running jobs, then, send a `READY` packet.
- Whenever a `CYCLE` packet is recieved, terminate all currently running jobs. If the current platform supports power cycling, then power cycle the test stand, then send a `READY` packet. If the current platform cannot power cycle, immediately send a `READY` packet.
- `stream_data` runs in a while loop, so to implement the above two bullet points you will need to figure out how to communicate to the server while running a hilsim job. (I don't know exactly how to do that so go ham)
- Whenever a `JOB` packet is recieved, IF a job is currently running, send a `BUSY` packet back with the currently running job data. Otherwise, run the job and send `JOB-UPD` packets with the status of the job while it's running (The first status should always be `"Accepted"`)

Most of the places where code needs to be implemented is marked with a `TODO`. Good luck!

##### END DELETEME

## Wrapper script reference
The `util/` directory contains multiple wrapper scripts written for development convenience. They expose functions to interface with Git and with Platformio. Their exposed functions are below:

**git_commands**.py:
- `run_script(str[] args)` --> Runs `remote_command.py` with the specified arguments (Used in the definition of all the other functions)
- `remote_clone()` --> Clones the remote into the directory specified in `config.py`
- `remote_reset()` --> Discards all changes and checks out/pulls `origin/main`. Runs `remote_clone` first if the remote does not exist.
- `remote_pull_branch(str branch)` --> Checks out and pulls the branch `branch` from the remote. Runs `remote_clone` first if the remote does not exist. 

**pio_commands**.py:
- `run_script(str[] args)` --> Runs `platformio` with the specified arguments.
- `pio_build(str build_target)` --> Runs `platformio run`. If `build_target` is specified, then it adds the `--environment` flag with `build_target`.
-  `pio_upload(str build_target)` --> Runs `platformio run --target upload`. If `build_target` is specified, then it adds the `--environment` flag with `build_target`. (Flashes code once the build completes)
-  `pio_clean(str build_target)` --> Runs `platformio run --target clean`. If `build_target` is specified, then it adds the `--environment` flag with `build_target`. (Does a clean build)
