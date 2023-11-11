import util.communication.communication_interface as communication_interface
from websockets.sync.client import connect, ClientConnection

class ClientWebsocketConnection(communication_interface.CommunicationChannel):
    def __init__(self, websocket_uri: str) -> None:
        pass

class WebsocketChannel(communication_interface.CommunicationChannel):
    websocket_connection: ClientConnection = None
    """websocket ClientConnection which handles the basic communication layer"""
    websocket_uri: str = ""
    """URI stored for the websocket connection"""

    in_buffer: str = ""
    """Buffer-type object storing input data for raw packets."""

    def __init__(self, websocket_uri: str) -> None:
        self.websocket_uri = websocket_uri
        self.websocket_connection = connect(websocket_uri)
        self.is_open = True

    def open(self) -> None:
        self.websocket_connection = connect(self.websocket_uri)
        self.is_open = True

    def close(self) -> None:
        self.websocket_connection.close()
        self.is_open = False

    def waiting_in(self) -> bool:
        return len(self.in_buffer) > 0
    
    def waiting_out(self):
        """Websockets instantly send, this function will always return FALSE"""
        return False
    
    def read(self) -> str:
        out_temp = self.in_buffer
        self.in_buffer = ""
        return out_temp
    
    def write(self, data: str) -> None:
        self.websocket_connection.send(data)
