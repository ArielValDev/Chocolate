from constants import game
from models.events.event_manager import EventManager
from models.network.messages.entity_packets import OutgoingEntityPacket
from models.network.messages.game_loop_packet_handler import OutgoingGameLoopPacketHandler

def subscribe_events():
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingGameLoopPacketHandler.update_player_chunks)
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingEntityPacket.handle_packet_update_entity_position)

    EventManager.subscribe(game.InGameEvent.PlayerMovedAndRotated, OutgoingEntityPacket.handle_packet_update_entity_position_and_rotation)

    EventManager.subscribe(game.InGameEvent.PlayerRotated, OutgoingEntityPacket.handle_packet_update_entity_rotation)

    EventManager.subscribe(game.InGameEvent.PlayerHeadRotated, OutgoingEntityPacket.handle_packet_set_head_rotation)

    EventManager.subscribe(game.InGameEvent.SwingArm, OutgoingEntityPacket.handle_packet_entity_animation)

    EventManager.subscribe(game.InGameEvent.PlayerJoined, lambda player: OutgoingEntityPacket.handle_packet_spawn_entity(player.conn, player.eid, player.uuid, game.EntityType.Player.value, player.game_state.current_position, 0))

    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_damage_event(conn, vctm.eid, dmg_type, atkr.eid, atkr.eid, None, None, None))
    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_set_health__damage(vctm, 1/3))
    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_set_entity_velocity(conn, vctm.eid, tuple((a + b for a, b in zip(atkr.game_state.current_position.delta_vector_normalized(vctm.game_state.current_position, 0.4), (0, 0.4, 0))))))

    EventManager.subscribe(game.InGameEvent.ChatMessage, OutgoingGameLoopPacketHandler.handle_player_chat_message)

    EventManager.subscribe(game.InGameEvent.PlayerDisconnected, lambda p: p.disconnect_player())

    EventManager.subscribe(game.InGameEvent.ServerShutdown, OutgoingGameLoopPacketHandler.handle_disconnect)
