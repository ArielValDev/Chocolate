import socket
from constants.constants import *
from utils.protocol_type_utils import from_varint, to_varint
from buffer import Buffer

class TCPConnection:
    def __init__(self, addr: str, socket: socket.socket):
        self.addr = addr
        self.socket = socket
    
    # TODO: encryption

    def send(self, msg: bytes):
        self.socket.sendall(msg)

    def recv(self, size: int) -> bytes:
        return self.socket.recv(size)
    
    def recv_mc_packet(self) -> tuple[int, Buffer]:
        """
        returns packet id and the data
        """

        size = bytearray()
        while True:
            byte = self.socket.recv(1) # The varint of the length of message
            if (int.from_bytes(byte) & VARINT_CONTINUE_BIT) == 0: break
            size.extend(byte)
        
        msg = Buffer(bytearray(self.socket.recv(from_varint(size))))
        packet_id = msg.consume_varint()
        return packet_id, msg
    
    def send_mc_packet(self, buffer: Buffer, packet_id: int):
        all_data = to_varint(packet_id) + buffer.get_bytes()
        self.send(bytes(to_varint(len(all_data))) + all_data)