from typing import TYPE_CHECKING, Generator
if TYPE_CHECKING:
    from models.player import Player
from typing import Any
from constants.game import InGameEvent
from models.events.event_manager import EventManager
from models.game.world import get_players_in_range

class PlayersManager:
    @staticmethod
    def get_ranged_players(from_player: "Player") -> Generator["Player", None, None]:
        config = from_player.server_interface.get_config()
        for player in get_players_in_range(from_player.server_interface, from_player.game_state.current_position.to_chunk(), config.render_distance):
            if player != from_player:
                yield player
    
    @staticmethod
    def get_all_other_players(from_player: "Player", event: InGameEvent, *args: Any) -> Generator["Player", None, None]:
        if event in EventManager.event_callbacks:
            for player in from_player.server_interface.get_all_players():
                if player != from_player:
                    yield player