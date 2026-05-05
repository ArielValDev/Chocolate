import socket
from constants.constants import *
from utils.logger import Logger
from utils.protocol_type_utils import from_varint, to_varint
from models.buffer import Buffer
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.decrepit.ciphers.modes import CFB8

class TCPConnection:
    def __init__(self, addr: str, socket: socket.socket):
        self.addr = addr
        self.socket = socket
        self.encryptor = None
        self.decryptor = None
    
    def enable_encryption(self, shared_secret: bytes):
        cipher = Cipher(
            algorithms.AES(shared_secret), 
            CFB8(shared_secret), 
            backend=default_backend()
        )
        self.encryptor = cipher.encryptor()
        self.decryptor = cipher.decryptor()

    def _send(self, msg: bytes):
        if self.encryptor:
            msg = self.encryptor.update(msg)

        try:
            self.socket.sendall(msg)
        except ConnectionAbortedError:
            #Logger.warn(f"Connection aborted while trying to send to {self.addr[0]}")
            pass

    def _recv(self, size: int) -> bytes:
        data = bytearray()
        while len(data) < size:
            chunk = self.socket.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Socket closed mid-packet")
            
            if self.decryptor:
                chunk = self.decryptor.update(chunk)
            data.extend(chunk)
        return bytes(data)
    
    def recv_mc_packet(self) -> tuple[int, Buffer | None]:
        """
        returns packet id and the data
        """
        size = bytearray()
        try:
            while True:
                byte = self._recv(1) # The varint of the length of message
                size.extend(byte)
                if (byte[0] & VARINT_CONTINUE_BIT) == 0: break
        except ConnectionAbortedError:
            return 0, None
        if len(size) == 0:
            return 0, None
        msg = Buffer(bytearray(self._recv(from_varint(size))))
        if len(msg.bytearray_) == 0:
            return 0, None
        packet_id = msg.consume_varint()
        
        
        #Logger.verbose(f"Recieved a messege of packet id {packet_id} / {hex(packet_id)}: ")#{msg.get_bytes()}")
        return packet_id, msg
    
    def send_mc_packet(self, buffer: Buffer, packet_id: int):
        #Logger.verbose(f"Sent packet of id {packet_id}: {buffer.get_bytes()}")
        all_data = to_varint(packet_id) + buffer.get_bytes()
        self._send(bytes(to_varint(len(all_data))) + all_data)

    def close_connection(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()