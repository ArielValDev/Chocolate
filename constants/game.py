from enum import Enum

class TeleportFlag(Enum):
    RelativeX = 0x0001
    RelativeY = 0x0002
    RelativeZ = 0x0004
    RelativeYaw = 0x0008
    RelativePitch = 0x0010
    RelativeVelocityX = 0x0020
    RelativeVelocityY = 0x0040
    RelativeVelocityZ = 0x0080
    RotateVelocity = 0x0100

class PlayerAction(Enum):
    AddPlayer = 0x01
    InitializeChat = 0x02
    UpdateGameMode = 0x04
    UpdateListed = 0x08
    UpdateLatency = 0x10
    UpdateDisplayName = 0x20
    UpdateListPriority = 0x40
    UpdateHat = 0x80

class GameEvent(Enum):
    NoRespawnBlockAvailable = 0
    BeginRaining = 1
    EndRaining = 2
    ChangeGameMode = 3
    WinGame = 4
    DemoEvent = 5
    ArrowHitPlayer = 6
    RainLevelChange = 7
    ThunderLevelChange = 8
    PlayPufferfishStingSound = 9
    PlayElderGuardianMobAppearance = 10
    EnableRespawnScreen = 11
    LimitedCrafting = 12
    StartWaitingForLevelChunks = 13

class ChangeGameModeEvent(Enum):
    Survival = 0
    Creative = 1
    Adventure = 2
    Spectator = 3

class WinGameEvent(Enum):
    JustRespawnPlayer = 0
    RollTheCreditsAndRespawnPlayer = 1

class DemoEventEvent(Enum):
    ShowWelcomeToDemoScreen = 0
    TellMovementsControls = 101
    TellJumpControl = 102
    TellInventoryControl = 103
    TellDemoIsOver = 104

class EnableRespawnScreenEvent(Enum):
    EnableRespawnScreen = 0
    ImmediatlyRespawn = 1

class LimitedCrafting(Enum):
    DisableLimitedCrafting = 0
    EnableLimitedCrafting = 1

class Dimension(Enum):
    Overworld = 0
    Nether = 1
    End = 2

class Gamemode(Enum):
    Survival = 0
    Creative = 1
    Adventure = 2
    Spectator = 3

class InGameEvent(Enum):
    PlayerMoved = 0
    PlayerRotated = 1
    PlayerJumped = 2
    SwingArm = 3
    PlayerAction = 4
    PlayerCommand = 5
    PlayerJoined = 6
    PlayerMovedAndRotated = 7

class EntityType(Enum):
    Player = 155
