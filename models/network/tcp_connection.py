import socket

class TCPConnection:
    def __init__(self, addr: str, socket: socket.socket):
        self.addr = addr
        self.socket = socket
    
    # TODO: encryption

    def send(self, msg: bytes):
        self.socket.sendall(msg)

    def recv(self, size: int) -> bytes:
        return self.socket.recv(size)
