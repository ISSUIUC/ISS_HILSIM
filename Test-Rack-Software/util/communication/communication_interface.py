from abc import ABC, abstractmethod # ABC = Abstract Base Classes 
from enum import Enum

class CommunicationChannelType(Enum):
    """Enum storing all supported communication types. Communication type must be present here to be able to be prioritized"""
    SERIAL = 0
    """Serial interface (Wired: COM)"""
    WEBSOCKET = 1
    """Websocket interface (Wireless: ws://)"""

class CommunicationChannel(ABC):
    """An extendable class representing a single communication channel. Exposes methods for 
    sending string-type data, reading string-type data, and other helper methods."""

    is_open: bool = False
    """Whether this communication channel is open"""

    @abstractmethod
    def write(self, data: str) -> None:
        """Writes data to the channel"""
        raise NotImplementedError("This communication channel's 'write' method has not been defined")

    @abstractmethod
    def read(self) -> str:
        """Reads all of the data from the channel"""
        raise NotImplementedError("This communication channel's 'read' method has not been defined")
    
    @abstractmethod
    def waiting_in(self) -> bool:
        """Returns whether or not this communication channel has data in the input buffer"""
        raise NotImplementedError("This communication channel's 'waiting_in' method has not been defined")
    
    @abstractmethod
    def waiting_out(self) -> bool:
        """Returns whether or not this communication channel has data in the output buffer"""
        raise NotImplementedError("This communication channel's 'waiting_out' method has not been defined")
    
    @abstractmethod
    def open(self) -> None:
        """Opens the channel if it is closed"""
        raise NotImplementedError("This communication channel's 'open' method has not been defined")
    
    @abstractmethod
    def close(self) -> None:
        """Closes the channel if it is open"""
        raise NotImplementedError("This communication channel's 'close' method has not been defined")