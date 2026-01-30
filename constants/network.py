from enum import Enum

class ConnectionState(Enum):
    Handshaking = 0

class HandshakingStatePacketID(Enum):
    Handshake = 0x00
