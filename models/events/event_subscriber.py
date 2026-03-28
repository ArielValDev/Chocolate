from constants import game
from models.events.event_manager import EventManager
from models.network.messages.entity_packets import OutgoingEntityPacket
from models.network.messages.game_loop_packet_handler import OutgoingGameLoopPacketHandler

def subscribe_events():
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingGameLoopPacketHandler.update_player_chunks)
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingEntityPacket.handle_packet_update_entity_position)
    EventManager.subscribe(game.InGameEvent.PlayerMovedAndRotated, OutgoingEntityPacket.handle_packet_update_entity_position_and_rotation)
    EventManager.subscribe(game.InGameEvent.PlayerRotated, OutgoingEntityPacket.handle_packet_update_entity_rotation)
    # EventManager.subscribe(game.InGameEvent.PlayerHeadRotated, OutgoingEntityPacket.handle_packet_set_head_rotation)
    EventManager.subscribe(game.InGameEvent.SwingArm, OutgoingEntityPacket.handle_packet_entity_animation)
    EventManager.subscribe(game.InGameEvent.PlayerJoined, lambda player: OutgoingEntityPacket.handle_packet_spawn_entity(player.conn, player.eid, player.uuid, game.EntityType.Player.value, player.game_state.current_position, 0))