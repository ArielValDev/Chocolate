import socket
from constants.constants import *
from utils.protocol_type_utils import from_varint

class TCPConnection:
    def __init__(self, addr: str, socket: socket.socket):
        self.addr = addr
        self.socket = socket
    
    # TODO: encryption

    def send(self, msg: bytes):
        self.socket.sendall(msg)

    def recv(self, size: int) -> bytes:
        return self.socket.recv(size)
    
    def get_message(self):
        size = bytearray()
        while True:
            byte = self.socket.recv(1) # The varint of the length of message
            if (int.from_bytes(byte) & CONTINUE_BIT) == 0: break
            size.extend(byte)
        
        msg = self.socket.recv(from_varint(size))
        return msg
            
        
