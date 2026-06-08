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
    Encryption = 0x01
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
    BlockDestruction = 0x05
    BlockUpdate = 0x08
    ChatMessage = 0x08
    ChunkBatchReceived = 0x0A
    ChunkBatchFinished = 0x0B
    ClientStatus = 0x0B
    ChunkBatchStart = 0x0C
    ClientTickEnd = 0x0C
    CloseContainer = 0x12
    Interact = 0x19
    DamageEvent = 0x19
    KeepAliveToServer = 0x1B
    SetPlayerPosition = 0x1D
    SetPlayerPositionAndRotation = 0x1E
    SetPlayerRotation = 0x1F
    Disconnect = 0x20
    EntityEvent = 0x22
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
    PlayerChatMessage = 0x3F
    CombatDeath = 0x42
    PlayerInfoUpdate = 0x44
    SynchronizePlayerPosition = 0x46
    RemoveEntities = 0x4B
    Respawn = 0x50
    SetHeadRotation = 0x51
    SetCenterChunk = 0x5C
    SetEntityVelocity = 0x63
    SetHealth = 0x66
    UpdateTime = 0x6F
    SetTickingState = 0x7D
    StepTick = 0x7E