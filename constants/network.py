from enum import Enum

class ConnectionState(Enum):
    Handshaking = 0
    Login = 1
    Configuration = 2
    Play = 3

class HandshakingStatePacketID(Enum):
    Handshake = 0x00
    
class LoginStatePacketID(Enum):
    LoginStart = 0x00
    LoginSuccess = 0x02
    LoginAck = 0x03
    
class ConfigurationStatePacketID(Enum):
    ClientInformation = 0x00
    PluginMessage = 0x02
    FinishConfiguration = 0x03
    RegistryData = 0x07
    ServerboundKnowPacks = 0x07
    ClientboundKnownPacks = 0x0E
    UpdateTags = 0x0D

class PlayStatePacketID(Enum):
    LoginPlay = 0x30
    SynchronizePlayerPosition = 0x46