from ast import Call
from typing import TYPE_CHECKING
from models.config import ServerConfig
from models.world.world import World

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
    get_registry_data: Callable[[], dict[str, list[str]]]
    remove_player: Callable[["Player"], None]
    get_world: Callable[[], World]
    is_running: Callable[[], bool]