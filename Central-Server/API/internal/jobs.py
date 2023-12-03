import enum

class JobStatus(enum.Enum):
    QUEUED = 0 # Job is queued and will be run on the next available TARS
    RUNNING = 1 # Job is currently running on TARS
    CANCELED = 2 # Job was canceled by someone #cancelculture
    SUCCESS = 3 # Job was successfully run
    FAILED_CRASHED = 4 # Job crashed on TARS
    FAILED_COMPILE_ERROR = 5 # Job failed to compile
    FAILED_TIMEOUT = 6 # Job timed out, cancelled #cancelculturestrikesagain
    FAILED_OTHER = 7 # Job failed for some other reason
    SETUP = 8
