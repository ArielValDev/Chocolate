from enum import Enum
from xml.dom.minidom import Entity

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
    SpawnEntity = 0x01
    EntityAnimation = 0x02
    ChunkBatchReceived = 0x0A
    ChunkBatchFinished = 0x0B
    ChunkBatchStart = 0x0C
    ClientTickEnd = 0x0C
    CloseContainer = 0x12
    KeepAliveToServer = 0x1B
    SetPlayerPosition = 0x1D
    SetPlayerPositionAndRotation = 0x1E
    SetPlayerRotation = 0x1F
    UnloadChunk = 0x25
    GameEvent = 0x26
    PlayerAction = 0x28
    PlayerCommand = 0x29
    PlayerInput = 0x2A
    KeepAliveToClient = 0x2B
    PlayerLoaded = 0x2B
    ChunkDataAndLightUpdate = 0x2C
    LoginPlay = 0x30
    UpdateEntityPosition = 0x33
    UpdateEntityPositionAndRotation = 0x34
    UpdateEntityRotation = 0x36
    SetHeldItem = 0x34
    Ping = 0x3B
    SwingArm = 0x3C
    UseItemOn = 0x3F
    PlayerInfoUpdate = 0x44
    SynchronizePlayerPosition = 0x46
    Respawn = 0x50
    SetCenterChunk = 0x5C
    UpdateTime = 0x6F
    SetTickingState = 0x7D
    StepTick = 0x7E