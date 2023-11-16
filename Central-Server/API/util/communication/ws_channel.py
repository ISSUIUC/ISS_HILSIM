import util.communication.communication_interface as communication_interface
import socketio
from typing import List


class ClientWebsocketConnection(communication_interface.CommunicationChannel):
    socketio_server: socketio.Server = None
    socket_id: str = ""
    in_buffer: str = ""
    """Buffer-type object storing input data for raw packets."""

    def __init__(self, websocket_server: socketio.Server, websocket_id: str) -> None:
        self.socketio_server = websocket_server
        self.socket_id = websocket_id
        self.is_open = True
        @self.socketio_server.on('wsdataresponse')
        def message(sid, data):
            self.in_buffer += data

    def open(self) -> None:
        raise NotImplementedError("L. This function being called doesn't make sense. Something went very wrong.")

    def close(self) -> None:
        self.socketio_server.disconnect(self.socket_id)

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
        self.socketio_server.emit("wsdata", data, to=self.socket_id)


class WebsocketChannel(communication_interface.CommunicationChannel):
    websocket_client: socketio.Client = None
    """websocket ClientConnection which handles the basic communication layer"""
    websocket_location: str = ""
    """Location for the websocket connection, is the first part of the URI (i.e: http://localhost)"""

    websocket_path: str = ""
    """The path to the websocket resource, the second part of the URI (i.e '/api/dscomm/ws')"""

    in_buffer: str = ""
    """Buffer-type object storing input data for raw packets."""

    def __init__(self, websocket_location: str, websocket_path: str="") -> None:
        self.websocket_location = websocket_location
        self.websocket_path = websocket_path
        self.websocket_client = socketio.Client()

        @self.websocket_client.on('connect')
        def connect():
            print("(websocket_channel) Connected to ws at", self.websocket_location + self.websocket_path)

        @self.websocket_client.on('wsdata')
        def message(data):
            self.in_buffer += data

        self.open()

    def open(self) -> None:
        self.websocket_client.connect(self.websocket_location, socketio_path=self.websocket_path)
        self.is_open = True
        self.socket_wait()

    async def socket_wait(self):
        await self.websocket_client.wait()

    def close(self) -> None:
        self.websocket_client.disconnect()
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
        print("emit", data)
        self.websocket_client.emit("wsdata", data)


connected_websockets: List[WebsocketChannel] = []
"""The connected websockets of this channel (Type: `WebsocketChannel`)"""