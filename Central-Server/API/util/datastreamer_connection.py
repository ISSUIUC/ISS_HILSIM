import util.communication.ws_channel as websocket_channel

class DatastreamerConnection():
    """This class links a single thread to a communication channel. Instances are created and added to a list to indicate the nessecity of spinning up new datastreamer threads."""

    def __init__(
            self,
            thread_name,
            communication_channel: websocket_channel.ClientWebsocketConnection) -> None:
        self.thread_name = thread_name
        self.communicaton_channel = communication_channel