# Test Rack Software
**Brief:** Kamaji test racks are the backbone of the Kamaji ecosystem. They are the actual interfaces to our avionics stacks. They are virtually entirely self-sufficient (as in, they can run HILSIM without explicit direction of when to do what), however, they rely on Kamaji to give them **jobs**, abstractions on **what** we want the testing racks to do and with **what data**.

In short, you can think of them as a black box, where you put in flight data and a git branch/git commit/other job configuration, and receive back a log of everything that the flight computer "thought of" during the flight.

Below is the scheme of operations:
![Kamaji-Datastreamer scheme of operations](https://i.ibb.co/sV0qTsg/Pasted-image-20231022215331.png)

The following documentation serves as a high level overview of the operations of the Test rack as a whole.

#### Useful terminology:
**Locking** (In the context of an avionics stack) is the process which occurs when an avionics stack encounters a non-recoverable error and is thus unable to accept further input. The only fix to this is usually a power cycle (or re-flash) to the avionics system.

**Peripherals** (In the context of an avionics stack) are hardware devices which do not include the altimeter, but can be otherwise tested, such as a camera board, breakout, or receiver.
# Datastreamer
The "brains" of the test rack, the Datastreamer "server" is what communicates with Kamaji and what orchestrates the setup and execution of jobs.

*Disambiguation:* Datastreamer will be referred to in these docs and in code as a "server". This is technically not entirely accurate as its primary purpose isn't to serve its own content, it is to take messages ("packets") from Kamaji and transform them into an actual HILSIM run on the avionics bay by compiling the code and running the HILSIM job. 

#### Overview

The **Datastreamer** consists mainly of two parts which work together to set up and execute jobs. The **Datastreamer Server** does not change between each test rack, and it handles all packet sending/recieveing, all server lifetime methods, and generally all functionality that does not require direct interaction with an avionics stack.

The **avionics interface** is code that will be different for every testing rack. This code is ***required*** to have an `interface.py` file in the root (`Test-Rack-Software/mytestrack/interface.py`), and furthermore, `interface.py` *MUST* expose an `av_instance` variable and a `HilsimRun` class. The specifics of this behavior is explored further in the **Avionics Interfaces** section below.

Because of the way that this code is structured, we follow a paradigm of **convention over configuration** when writing Datastreamer code, so a lot of functionality of the datastreamer server is dependent on finding certain resources in places where we expect them. For this reason, it is *extremely* important that ***all*** avionics-specific code is kept *ONLY* in its respective AV interface (i.e. `Test-Rack-Software/TARS-Rack`), while all Datastreamer code is kept in the `Test-Rack-Software` root directory or `Test-Rack-Software/util`.

As a broad rule of thumb, `Datastreamer` does the *talking*, `Avionics Interfaces` do all the *doing*.
#### Lifetime / State
Because of how predictable we need the Datastreamer server to be, the design choice has been made to lock the state of the server to a known, finite amount of states in which it can possibly be. This makes Datastreamer state part of a **Finite state machine** (https://en.wikipedia.org/wiki/Finite-state_machine). The structure of the state machine and all possible transitions are shown in the diagram below:

![Kamaji-FSM](https://i.ibb.co/kBwD8BX/Pasted-image-20231022232038.png)

The server by default begins in the **INIT** state, and each arrow between a state describes a transition between those states (internally, these transitions are called **pipes**).

The state machine works by attempting to follow a transition pipe from it's current state every tick. It does so by executing every defined **transition function** for that transition, which are defined for a transition from state A to state B. Depending on the result of each transition function, the transition might or might not happen. If the transition happens, all the associated `success events` associated with that transition are also executed

In other words, if the server wishes to transition from state A to state B, it must pass every check defined in the transition functions that link state A to state B.

During each tick, the server also executes all of the **Always events** defined for the current server state. An **Always event** is linked to a specific state, or to the `ANY` state, and defines some code that should be run in that state every time that a server tick is triggered.

##### Example:
Suppose you want to transition from the `AV_DETECT` to the `READY` state. You would define a pipe between the `AV_DETECT` and `READY` state, as well as a **Transition event** between those two states which attempts to detect an avionics stack, and returns true if it's successful in doing so (false otherwise). You may also want to define a **Success Event** that reports to Kamaji that this stack is ready. In this setup, whenever the server is in the `AV_DETECT` state, it will attempt to detect an avionics stack every tick until it is successful in doing so, after which it will switch to the `READY` state and send a response to the server.

There are additionally ways to manually trigger transitions. By invoking `ServerStateController.try_transition(to_state)` you can "ask" the Datastreamer server to transition to a specific state, even if it's not linked by a pipe. It should be noted that it isn't advised to do this often, since transitioning from a state without cleaning up can lead to undefined side effects. If you find yourself wanting to transition from one state to another often, it is better to define a pipe and transition events for those two states. Furthermore, attempting to call `try_transition` from within a transition event callback will *always* fail if the callback is successful (as the callback executing successfully will switch the server back to the previous state, and this switching is undefined behavior)

In the same vein, invoking `ServerStateController.force_transition(to_state)` will force the aforementioned transition to happen, without asking if transition events pass. This is generally used when errors are detected and you ***need*** to transition to an error state. 

#### Hardware
Physically, a test rack consists of some full-function computer (think: raspberry pi) connected to an avionics stack (Think: TARSmkIV or MIDAS). This whole system is then connected to the Kamaji server through the computer.

An **avionics stack** primarily consists of **primary hardware** and 0 or more **peripherals**. As an example, the TARS mkIV stack consists of just the TARS boards themselves connected to a singular USB port on the test rack computer, while a MIDAS stack may consist of the MIDAS board as well as the SPARK breakout.

The way that peripherals are implemented and detected is left as an exercise to the implementer, and can be either done by writing a separate AV interface or adapting the existing interface to support the new peripheral.

As of now, all connections between systems are made with serial, this may be modified later on to allow for more board peripherals (since one of the serial ports is used for server communication).

#### Packets
The datastreamer communicates to the Kamaji server through a system of packets. The purpose of each packet is well documented within `packets.py`, so it is recommended to check out what each packet does. In general, each packet has a **packet header** and an optional **raw_data** parameter. The packet header is encoded using JSON, while `raw_data` is usually encoded as a UTF-8 string.

Packets are encoded to the serial buffer in the following manner as a string: `{packet_header}[[raw==>]]{raw_data}[[pkt_end]]`. This string can then be decoded back into the relevant packet, assuming that no data corruption happens.

Because writing to serial directly can cause race conditions that corrupt packet data, you should instead write data between Kamaji and Datastreamer by using the `DataPacketBuffer` class, an instance of which is present in the singleton `Datastreamer` instance.

In the server loop, data is written into the packet buffer, decoded, and saved as a list of `DataPacket`s. Then, all outgoing packets in the output buffer are serialized and sent. Only then does the server perform its relevant tick updates. This can most clearly be seen in `DatastreamerServer`'s `tick()` method:

```py
if self.server_port != None:
    # We clear out output buffer and also populate our input buffer from the server
    self.packet_buffer.write_buffer_to_serial(self.server_port)
    self.packet_buffer.read_to_input_buffer(self.server_port)

self.state.update_always() # Run all `always` events
self.state.update_transitions()  # Run all transition tests

self.packet_buffer.clear_input_buffer() # Discard our input buffer so we can get a new one next loop
```

After performing all our server actions, we discard the input buffer so we can get the next packets sent by the server.

##### Special packet flows:
When jobs are being run, there are a couple of events which the server expects to receive. Omitting these packets won't explicitly *break* anything, however, including them will allow for easier debugging and will increase readability of what the server is doing:

While performing `HilsimRun.job_setup()`:
`JOB_UPDATE` with action `"ACCEPTED"` => This packet is already done for you in datastreamer, it signifies the datastreamer accepting the job
`JOB_UPDATE (SETUP)` with action `"COMPILE_READY"` => Signifies the datastreamer is ready to compile
`JOB_UPDATE (SETUP)` with action `"COMPILED"` => Signifies successful compilation
`JOB_UPDATE (RUNNING)` with action `"BEGIN"` => Signifies the beginning of the run

#### Deference
Due to the fact that python does not natively support asynchronous code, we have implemented **server deference**, or the idea that the current control flow of the server is owned by the scope which is currently being run. Unfortunately, a side effect of this is the fact that functions which take a long time to execute and which are generally blocking tend to decrease how responsive the server can be.

To avoid this lack of responsiveness, functions can *Defer* their execution to allow server state updates to come in and for packets to be read. If you are writing a transition event which you suspect will be blocking of the server's responsiveness, make sure to call `Server.defer()` periodically within your function so you can access the state without leaving the scope.

## Avionics Interfaces
The **avionics interface** is actually quite similar to an interface in the traditional sense, as in there is a certain amount of functionality that is *expected* from each interface, but the implementation specifics are not important to the datastreamer server.

To make a properly functioning avionics interface, there are a couple things that you ***must*** do.
For an interface that you are trying to create in `Test-Rack-Software/myinterface`, you *must* have an entrypoint file `Test-Rack-Software/myinterface/interface.py`. Furthermore, this file must expose three pieces of data: `av_interface`, an object of type (or sub-type) `AvionicsInterface`, a class called `HilsimRun`, and a reference to a **platform metadata file** (explained below) stored in `platform_meta`. Both of the abstract versions of `HilsimRun` (called `HilsimRunInterface`) and `AvionicsInterface` are defined in  `/util/avionics_interface`. You are required to override every method in both classes, and you can extend these classes using python **Abstract Base Class** notation:

```py
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer

...

class MyAvionics(AVInterface.AvionicsInterface):
	# implementation here...


class HilsimRun(AVInterface.HilsimRun):
	# implementation here...

av_interface = MyAvionics(Datastreamer.instance) # MUST have this instance!
```

The `AvionicsInterface` file contains documentation of what every overridden function must do.

In general, the avionics interface you write will be a data container and set of helper methods used by your `HilsimRun` implementation to perform different actions such as setting up, executing, and cleaning up your run.

In addition to the `interface.py` file, you must also write a `Test-Rack-Software/myinterface/platform_meta.py` file, which looks something like this:

```py
import os

board_type = "YOUR_BOARD_NAME"
repository_url = "BOARD_GITHUB_REPOSITORY_URL"
platformio_subdirectory = "PLATFORMIO_DIRECTORY" # Relative to repo root

# These usually stay the same, but can be modified if needed:
remote_path = os.path.dirname(__file__) # Where to clone ./remote
platformio_path = os.path.join(remote_path, platformio_subdirectory)
```

Once again, this is an example of convention over configuration. The datastreamer (and utility functions) *will* look for this (or, more accurately, for its reference in `platform.py`) to figure out where to put things, so it is imperative that this file is present.

Finally, you must edit `Test-Rack-Software/config.py` to expose your avionics interface and metadata.
# Avionics

In brief, this is the second part of each test rack. Because the avionics stack is unable to interpret what we want to test directly (we can't just ask the stack "can you compile branch av-30000-av-stuff"), we require Datastreamer to talk to it. Unfortunately, since the architecture of each avionics stack is different we are required to write a seperate interface between the avionics stack and datastreamer.

It should be noted that in the context of "avionics", this system refers to the **primary hardware** *and* the peripherals taken together. 

So far the avionics stacks supported on Kamaji/Hilsim server are
- **TARSmkIV**


# Getting started with development:
This is a quick-start guide to making your own avionics interface.

First, create a new subfolder under the directory `Test-Rack-Software`. For this tutorial, we will be using the name `my_test_rack`, but of course this can be called anything (but `util`).

Next, under `Test-Rack-Software/my_test_rack`, create the two **required** files `interface.py` and `platform_meta.py`

You may then copy over another test rack's code and tweak it, or work off of this skeleton:

**Test-Rack-Software/my_test_rack/platform_meta.py**
```py
import util.avionics_meta as AVMeta

class PlatformMeta(AVMeta.PlatformMetaInterface):
    board_type = "AV_TYPE" # Avionics type
    repository_url = "GIT_REPO_URL" # Software repository
    platformio_subdirectory = "./PIO_SUBDIRECTORY" # Platformio subdirectory

    def __init__(self, file: str) -> None:
        super().__init__(file)

meta = PlatformMeta(__file__)
```

**Test-Rack-Software/my_test_rack/interface.py**
```py
import util.avionics_interface as AVInterface
import util.datastreamer_server as Datastreamer

class MyAvionics(AVInterface.AvionicsInterface):
    TARS_port: serial.Serial = None

    def handle_init(self) -> None:
        return super().handle_init()

    def detect(self) -> bool:
		return super().detect()

    def first_setup(self) -> None:
		return super().first_setup()

    def code_reset(self) -> None:
		return super().code_reset()
  
    def power_cycle(self) -> bool:
		return super().power_cycle()
		
    def code_pull(self, git_target) -> None:
		return super().code_pull()

    def code_flash(self) -> None:
		return super().code_flash()
		
class HilsimRun(AVInterface.HilsimRunInterface):
    av_interface: MyAvionics # Specify your AV interface

    def get_current_log(self) -> str:
		return super().get_current_log()

    def job_setup(self):
		return super().job_setup()

    def __init__(self, datastreamer: Datastreamer.DatastreamerServer, av_interface: TARSAvionics, raw_csv: str, job: pkt.JobData) -> None:
        super().__init__(datastreamer, av_interface, raw_csv, job)
        
    def post_setup(self) -> None:
		return super().post_setup()

    def step(self, dt: float):
		return super().step()

av_instance = MyAvionics(Datastreamer.instance) # Important!
```

This should work out of the box, of course, until you implement the required methods, the base class will throw exceptions.