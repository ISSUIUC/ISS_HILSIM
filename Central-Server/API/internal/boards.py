from apiflask import Schema
from apiflask.fields import Integer, String, Boolean

class BoardOuputSchema(Schema):
    id = Integer() # The id of the board
    is_ready = Boolean()  # True when in READY state (? TODO: check if this is true)
    job_running = Boolean() # True when actively running job
    board_type = String() # The type of board
    running = Boolean() # Is the thread currently running
