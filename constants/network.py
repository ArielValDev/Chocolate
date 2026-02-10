from enum import Enum

class ConnectionState(Enum):
    Handshaking = 0
    Login = 1

class HandshakingStatePacketID(Enum):
    Handshake = 0x00
    
class LoginStatePacketID(Enum):
    Login_Success = 0x02
