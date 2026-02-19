import socket
from constants.constants import *
from utils.logger import Logger
from utils.protocol_type_utils import from_varint, to_varint
from models.buffer import Buffer

class TCPConnection:
    def __init__(self, addr: str, socket: socket.socket):
        self.addr = addr
        self.socket = socket
    
    # TODO: encryption

    def _send(self, msg: bytes):
        self.socket.sendall(msg)

    def _recv(self, size: int) -> bytes:
        return self.socket.recv(size)
    
    def recv_mc_packet(self) -> tuple[int, Buffer]:
        """
        returns packet id and the data
        """
        size = bytearray()
        while True:
            byte = self.socket.recv(1) # The varint of the length of message
            size.extend(byte)
            if (int.from_bytes(byte) & VARINT_CONTINUE_BIT) == 0: break
        
        Logger.error(str(size))
        msg = Buffer(bytearray(self._recv(from_varint(size))))
        packet_id = msg.consume_varint()

        Logger.verbose(f"Recieved a messege of packet id {packet_id}: {msg.get_bytes()}")
        return packet_id, msg
    
    def send_mc_packet(self, buffer: Buffer, packet_id: int):
        Logger.verbose(f"Sent packet of id {packet_id}: {buffer.get_bytes()}")
        all_data = to_varint(packet_id) + buffer.get_bytes()
        self._send(bytes(to_varint(len(all_data))) + all_data)