### Setting up a Datastreamer Raspberry Pi
The instructions here are presumed to be setup for Raspberry Pi OS.
You will need an SD card and an RPI. It will also be great to have a keyboard and mouse.

First things first, install python full:
`sudo apt-get install python-full`

Follow these instructions to install PlatformIO
https://docs.platformio.org/en/latest/core/installation/index.html

Then clone this repo, and open up the test rack directory.

Then install the necessary files with 
`~/.platformio/penv/bin/pip install -r requirments.txt`

Platformio installs a custom python env with Raspberry Pi OS, so we should use it.

Then we can run it
`./run.sh`

Next steps:
 - Add a service to automatically start the test rack software when the RPI boots up
 - Add a custom Debian repository to help deal with auto-updating