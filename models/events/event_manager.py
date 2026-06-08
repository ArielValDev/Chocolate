from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.player import Player

from typing import Any, Callable
from constants.game import InGameEvent, WorldEvent



class EventManager:
    event_callbacks: dict[InGameEvent | WorldEvent, list[Callable[..., None]]] = {}

    @staticmethod
    def subscribe(event: InGameEvent | WorldEvent, callback: Callable[..., None]):
        if event not in EventManager.event_callbacks:
            EventManager.event_callbacks[event] = []
        EventManager.event_callbacks[event].append(callback)

    @staticmethod
    def trigger(event: InGameEvent | WorldEvent, *args: Any):
        if event not in EventManager.event_callbacks:
            return
        
        for callback in EventManager.event_callbacks[event]:
            callback(*args)
