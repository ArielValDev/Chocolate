from typing import TYPE_CHECKING, Callable, Generator

from models.server_interface import ServerInterface
from models.types.position import Position
if TYPE_CHECKING:
    from models.player import Player
from typing import Any
from constants.game import InGameEvent
from models.events.event_manager import EventManager
from models.game.world import get_players_in_range

class PlayersManager:
    @staticmethod
    def get_ranged_players(from_player: "Player", include_player: bool = False) -> Generator["Player", None, None]:
        config = from_player.server_interface.get_config()
        for player in get_players_in_range(from_player.server_interface, from_player.game_state.current_position.to_chunk(), config.render_distance):
            if player == from_player and not include_player: continue
            yield player

    @staticmethod
    def get_ranged_players_pos(server_interface: ServerInterface, position: Position) -> Generator["Player", None, None]:
        config = server_interface.get_config()
        for player in get_players_in_range(server_interface, position.to_chunk(), config.render_distance):
            yield player
    
    @staticmethod
    def get_all_other_players(from_player: "Player", include_player: bool = False) -> Generator["Player", None, None]:
        for player in from_player.server_interface.get_all_players():
            if player == from_player and not include_player: continue
            yield player

    @staticmethod
    def send_to_players(players: list["Player"], func: Callable[[Any], None], *args: Any):
        for player in players:
            if player.game_state.is_loaded:
                func(player.conn, *args)

    
