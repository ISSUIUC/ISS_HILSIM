import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

import util.communication.packets as pkt

JOB_ID = -1
PULL_TYPE = pkt.JobData.GitPullType.BRANCH
PULL_TARGET = "main"
JOB_TYPE = pkt.JobData.JobType.DEFAULT
JOB_AUTHOR = "N/A"
JOB_PRIORITY = pkt.JobData.JobPriority.HIGH
JOB_TIMESTEP = 0.1
