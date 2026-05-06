from sched import Event

from constants import game
from models import server_interface
from models.events.event_manager import EventManager
from models.game.world import get_players_in_range
from models.network.messages.entity_packets import OutgoingEntityPacket
from models.network.messages.game_loop_packet_handler import OutgoingGameLoopPacketHandler
from models.network.messages.event_broadcaster import PlayersManager
from models.network.messages.player_packets import handle_player_packet_respawn, handle_player_packet_synchronize_player_position
from models.types.mc_types import BitField

def subscribe_events():
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingGameLoopPacketHandler.update_player_chunks)
    EventManager.subscribe(game.InGameEvent.PlayerMoved, OutgoingEntityPacket.handle_packet_update_entity_position)

    EventManager.subscribe(game.InGameEvent.PlayerMovedAndRotated, OutgoingEntityPacket.handle_packet_update_entity_position_and_rotation)

    EventManager.subscribe(game.InGameEvent.PlayerRotated, OutgoingEntityPacket.handle_packet_update_entity_rotation)

    EventManager.subscribe(game.InGameEvent.PlayerHeadRotated, OutgoingEntityPacket.handle_packet_set_head_rotation)

    EventManager.subscribe(game.InGameEvent.SwingArm, OutgoingEntityPacket.handle_packet_entity_animation)

    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_damage_event(conn, vctm.eid, dmg_type, atkr.eid, atkr.eid, None, None, None))
    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_set_health__damage(vctm, 1/3))
    EventManager.subscribe(game.InGameEvent.DamageEvent, lambda conn, vctm, atkr, dmg_type: OutgoingEntityPacket.handle_packet_set_entity_velocity(conn, vctm.eid, tuple((a + b for a, b in zip(atkr.game_state.current_position.delta_vector_normalized(vctm.game_state.current_position, 0.4), (0, 0.4, 0))))))

    EventManager.subscribe(game.InGameEvent.ChatMessage, OutgoingGameLoopPacketHandler.handle_player_chat_message)

    EventManager.subscribe(game.InGameEvent.PlayerDisconnected, lambda p: p.disconnect_player())
    EventManager.subscribe(game.InGameEvent.PlayerDisconnected, lambda p: PlayersManager.send_to_players(p.server_interface.get_all_players(), OutgoingEntityPacket.handle_packet_remove_entities, [p.eid]))

    EventManager.subscribe(game.InGameEvent.ServerShutdown, OutgoingGameLoopPacketHandler.handle_disconnect)

    EventManager.subscribe(game.InGameEvent.PlayerDied, lambda player: PlayersManager.send_to_players(list(PlayersManager.get_ranged_players(player, True)) ,OutgoingEntityPacket.handle_packet_entity_event, player.eid, game.EntityStatus.DeathSoundAnimation.value))
    EventManager.subscribe(game.InGameEvent.PlayerDied, lambda player: PlayersManager.send_to_players(list(PlayersManager.get_ranged_players(player, True)) ,OutgoingEntityPacket.handle_packet_entity_event, player.eid, game.EntityStatus.DeathSmokeParticles.value))
    EventManager.subscribe(game.InGameEvent.PlayerDied, lambda player: OutgoingGameLoopPacketHandler.handle_packet_combat_death(player, "you have been killed!"))
    EventManager.subscribe(game.InGameEvent.PlayerDied, lambda player: PlayersManager.send_to_players(player.server_interface.get_all_players(), OutgoingEntityPacket.handle_packet_remove_entities, [player.eid]))
    EventManager.subscribe(game.InGameEvent.PlayerDied, lambda player: OutgoingEntityPacket.handle_packet_remove_entities(player.conn, [p.eid for p in player.server_interface.get_all_players() if p != player]))


    EventManager.subscribe(game.InGameEvent.PlayerRespawn, lambda p, tid: handle_player_packet_respawn(p.conn, game.Dimension.Overworld.value, "minecraft:overworld", 1379429607, p.game_state.gamemode.value, p.game_state.gamemode.value, True, True, False, None, 0, 1, 63, 0))
    EventManager.subscribe(game.InGameEvent.PlayerRespawn, lambda p, tid: handle_player_packet_synchronize_player_position(p.conn, tid, p.game_state.current_position.x, p.game_state.current_position.y, p.game_state.current_position.z, 0, 0, 0, p.game_state.current_position.yaw, p.game_state.current_position.pitch, BitField()))
    EventManager.subscribe(game.InGameEvent.PlayerRespawn, lambda p, tid: OutgoingEntityPacket.handle_packet_set_health(p, 20, 20))