from uuid import uuid4

from constants import game
from models.network.messages.entity_packets import OutgoingEntityPacket
from typing import TYPE_CHECKING

from models.network.messages.player_packets import handle_player_packet_player_info_update
from models.types.mc_types import BitField
from models.types.position import EntityPosition
if TYPE_CHECKING:
    from models.player import Player

# TODO: make things like handle_player_packet_player_info_update in class
def update_others_player_joined(player: "Player"):
    actions = BitField()
    actions.set(game.PlayerAction.AddPlayer.value)
    actions.set(game.PlayerAction.UpdateListed.value)
    actions.set(game.PlayerAction.UpdateListed.value)
    actions.set(game.PlayerAction.UpdateHat.value)
    for other in player.server_interface.get_all_players():
        if other != player:
            handle_player_packet_player_info_update(other.conn, actions, other.uuid, [player], -1, True, 100, "", 1, True) # TODO get real ping
            OutgoingEntityPacket.handle_packet_spawn_entity(other.conn, player.eid, player.uuid, game.EntityType.Player.value, player.game_state.current_position, 0)

def update_joined_player_others_exist(player: "Player"):
    for other in player.server_interface.get_all_players():
        if other != player:
            OutgoingEntityPacket.handle_packet_spawn_entity(player.conn, other.eid, other.uuid, game.EntityType.Player.value, other.game_state.current_position, 0)