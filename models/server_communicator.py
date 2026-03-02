from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.player import Player
from dataclasses import dataclass
from typing import Callable

@dataclass
class ServerCommunicator:
    get_all_players: Callable[[], list["Player"]]