from uuid import UUID
from typing import Union


class OptionalString:
    def __init__(self, s: str | None):
        self.s = s

class BitField:
    def __init__(self):
        self.field = 0x00

    def set(self, bit: int):
        self.field |= bit
    
    def clear(self, bit: int):
        self.field &= ~bit

    def check(self, bit: int) -> bool:
        return self.field & bit != 0
    
    def to_bytes(self, length: int):
        return self.field.to_bytes(length)

AddPlayerAction = tuple[str, list[tuple[str, str, OptionalString]]]
InitializeChatAction = UUID
UpdateGameModeAction = int
UpdateListedAction = bool
UpdateLatencyAction = int
UpdateDisplayNameAction = str
UpdateListPriorityAction = int
UpdateHatAction = bool
PlayerActionsType = list[Union[AddPlayerAction, InitializeChatAction, UpdateGameModeAction, UpdateListedAction, UpdateLatencyAction, UpdateDisplayNameAction, UpdateListPriorityAction, UpdateHatAction]]