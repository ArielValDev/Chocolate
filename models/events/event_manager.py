from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.player import Player

from typing import Any, Callable
from constants.game import InGameEvent



class EventManager:
    event_callbacks: dict[InGameEvent, list[Callable[..., None]]] = {}

    @staticmethod
    def subscribe(event: InGameEvent, callback: Callable[..., None]):
        if event not in EventManager.event_callbacks:
            EventManager.event_callbacks[event] = []
        EventManager.event_callbacks[event].append(callback)

    @staticmethod
    def trigger(event: InGameEvent, *args: Any):
        if event not in EventManager.event_callbacks:
            return
        
        for callback in EventManager.event_callbacks[event]:
            callback(*args)
