from enum import Enum

class TeleportFlags(Enum):
    RelativeX = 0x0001
    RelativeY = 0x0002
    RelativeZ = 0x0004
    RelativeYaw = 0x0008
    RelativePitch = 0x0010
    RelativeVelocityX = 0x0020
    RelativeVelocityY = 0x0040
    RelativeVelocityZ = 0x0080
    RotateVelocity = 0x0100

class PlayerActions(Enum):
    AddPlayer = 0x01
    InitializeChat = 0x02
    UpdateGameMode = 0x04
    UpdateListed = 0x08
    UpdateLatency = 0x10
    UpdateDisplayName = 0x20
    UpdateListPriority = 0x40
    UpdateHat = 0x80
