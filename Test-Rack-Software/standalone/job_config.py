import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.communication.packets as pkt

DATA_FILE_NAME = "data.csv"
PULL_TYPE = pkt.JobData.GitPullType.BRANCH
RETURN_LOG_OUT_FILE = "log.txt"