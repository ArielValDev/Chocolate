from enum import Enum

class ConnectionState(Enum):
    Handshaking = 0
    Login = 1

class HandshakingStatePacketID(Enum):
    Handshake = 0x00
    
class LoginStatePacketID(Enum):
    LoginStart = 0x00
    LoginSuccess = 0x02
    LoginAck = 0x03
    
class ConfigurationStatePacketID(Enum):
    RegistryData = 0x07
