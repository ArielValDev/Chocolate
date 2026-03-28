from typing import TYPE_CHECKING
from models.config import ServerConfig

if TYPE_CHECKING:
    from models.player import Player
from dataclasses import dataclass
from typing import Callable

@dataclass
class ServerInterface:
    get_all_players: Callable[[], list["Player"]]
    get_day_time: Callable[[], int]
    get_world_age: Callable[[], int]
    get_config: Callable[[], ServerConfig]