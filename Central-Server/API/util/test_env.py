import os
import requests
import unittest

import util.tests.datastreamer_comp
import util.datastreamer_connection



def is_test_environment() -> bool:
    return True
    try:
        if (os.environ['USE_TESTING_ENVIRONMENT'] == "true"):
            return True
        else:
            return False
    except:
        return False
    
def datastreamer_comp_test_hook(connection: util.datastreamer_connection.DatastreamerConnection) -> None:
    """Function that is called whenever an outside datastreamer connects.
    If the testing envrionment is active, it causes a comprehensive test to be run on the datastreamer.
    Precondition: Should only ever have 1 datastreamer connected."""
    if(not is_test_environment()):
        return
    
    print("(tests) Detected an outside Datastreamer connection", flush=True)
    try:
        util.tests.datastreamer_comp.run(connection)
        print("(tests) Test passed", flush=True)
    except Exception as e:
        print("(tests) Test failed", flush=True)
        print(".......", e, flush=True)

