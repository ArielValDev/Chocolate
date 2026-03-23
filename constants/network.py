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
    BundleDelimiter = 0x00
    ConfirmTeleportation = 0x00
    ChunkBatchReceived = 0x0A
    ChunkBatchFinished = 0x0B
    ChunkBatchStart = 0x0C
    ClientTickEnd = 0x0C
    SetPlayerPositionAndRotation = 0x1E
    GameEvent = 0x26
    PlayerLoaded = 0x2B
    KeepAliveToServer = 0x1B
    KeepAliveToClient = 0x2B
    ChunkDataAndLightUpdate = 0x2C
    LoginPlay = 0x30
    Ping = 0x3B
    PlayerInfoUpdate = 0x44
    SynchronizePlayerPosition = 0x46
    Respawn = 0x50
    SetCenterChunk = 0x5C
    SetTickingState = 0x7D
    StepTick = 0x7E