import time
from typing import TYPE_CHECKING
from constants.constants import *
from constants.game import *
from models.events.event_manager import EventManager
from utils.utils import float_to_angle
if TYPE_CHECKING:
    from models.player import Player
from uuid import UUID
from constants import network
from models.buffer import Buffer
from models.network.tcp_connection import TCPConnection
from models.types.position import EntityPosition
from models.network.messages.event_broadcaster import PlayersManager

class OutgoingEntityPacket:
    @staticmethod
    def handle_packet_spawn_entity(conn: TCPConnection, eid: int, UUID: UUID, type: int, entity_position: EntityPosition, data: int):
        entity_packet = Buffer()
        entity_packet.add_varint(eid)
        entity_packet.add_uuid(UUID)
        entity_packet.add_varint(type)
        entity_packet.add_double(entity_position.x)
        entity_packet.add_double(entity_position.y)
        entity_packet.add_double(entity_position.z)
        entity_packet.add_lpvec3((entity_position.x, entity_position.y, entity_position.z))
        entity_packet.add_unsigned_byte(float_to_angle(entity_position.pitch))
        entity_packet.add_unsigned_byte(float_to_angle(entity_position.yaw))
        entity_packet.add_unsigned_byte(float_to_angle(entity_position.head_yaw))
        entity_packet.add_varint(data)
        conn.send_mc_packet(entity_packet, network.PlayStatePacketID.SpawnEntity.value)

    @staticmethod
    def handle_packet_bundle_delimiter(conn: TCPConnection):
        conn.send_mc_packet(Buffer(), network.PlayStatePacketID.BundleDelimiter.value)

    @staticmethod
    def handle_packet_entity_animation(conn: TCPConnection, eid: int, animation: int):
        entity_animation_packet = Buffer()
        entity_animation_packet.add_varint(eid)
        entity_animation_packet.add_unsigned_byte(animation)
        conn.send_mc_packet(entity_animation_packet, network.PlayStatePacketID.EntityAnimation.value)

    @staticmethod
    def handle_packet_update_entity_rotation(other_player: "Player", moving_player: "Player", yaw: int, pitch: int):
        packet = Buffer()
        packet.add_varint(moving_player.eid)
        packet.add_unsigned_byte(yaw)
        packet.add_unsigned_byte(pitch)
        packet.add_boolean(moving_player.game_state.current_position.is_on_ground)
        other_player.conn.send_mc_packet(packet, network.PlayStatePacketID.UpdateEntityRotation.value)

    @staticmethod
    def handle_packet_update_entity_position(other_player: "Player", moving_player: "Player", dx: int, dy: int, dz: int):
        packet = Buffer()
        packet.add_varint(moving_player.eid)
        packet.add_short(dx)
        packet.add_short(dy)
        packet.add_short(dz)
        packet.add_boolean(moving_player.game_state.current_position.is_on_ground)
        other_player.conn.send_mc_packet(packet, network.PlayStatePacketID.UpdateEntityPosition.value)

    @staticmethod
    def handle_packet_update_entity_position_and_rotation(other_player: "Player", moving_player: "Player", dx: int, dy: int, dz: int, yaw: int, pitch: int):
        packet = Buffer()
        packet.add_varint(moving_player.eid)
        packet.add_short(dx)
        packet.add_short(dy)
        packet.add_short(dz)
        packet.add_unsigned_byte(yaw)
        packet.add_unsigned_byte(pitch)
        packet.add_boolean(moving_player.game_state.current_position.is_on_ground)
        other_player.conn.send_mc_packet(packet, network.PlayStatePacketID.UpdateEntityPositionAndRotation.value)

    @staticmethod
    def handle_packet_set_head_rotation(other_player: "Player", moving_player: "Player", head_yaw: int):
        packet = Buffer()
        packet.add_varint(moving_player.eid)
        packet.add_unsigned_byte(head_yaw)
        other_player.conn.send_mc_packet(packet, network.PlayStatePacketID.SetHeadRotation.value)
    
    @staticmethod
    def handle_packet_damage_event(conn: TCPConnection, eid: int, source_type_id: int, source_cause_id: int, source_direct_id: int, x: float | None, y: float | None, z: float | None):
        packet = Buffer()
        packet.add_varint(eid)
        packet.add_varint(source_type_id)
        packet.add_varint(source_cause_id + 1)
        packet.add_varint(source_direct_id + 1)
        if x and y and z:
            packet.add_boolean(True)
            packet.add_double(x)
            packet.add_double(y)
            packet.add_double(z)
        else:
            packet.add_boolean(False)
        
        conn.send_mc_packet(packet, network.PlayStatePacketID.DamageEvent.value)

    @staticmethod
    def handle_packet_set_entity_velocity(conn: TCPConnection, eid: int, vec3: tuple[float, float, float]):
        packet = Buffer()
        packet.add_varint(eid)
        packet.add_lpvec3(vec3)
        conn.send_mc_packet(packet, network.PlayStatePacketID.SetEntityVelocity.value)

    @staticmethod
    def handle_packet_set_health__damage(player: "Player", health_to_take: float, food_to_take: int = 0, food_saturation: float = 5.0):
        packet = Buffer()
        player.game_state.health -= health_to_take

        if player.game_state.health <= 0.0:
            player.game_state.health = 0.0

        packet.add_float(player.game_state.health)
        player.game_state.food -= food_to_take
        packet.add_varint(player.game_state.food)
        packet.add_float(food_saturation)

        player.conn.send_mc_packet(packet, network.PlayStatePacketID.SetHealth.value)
        if player.game_state.health <= 0 and not player.game_state.is_dead:
            player.game_state.is_dead = True
            EventManager.trigger(InGameEvent.PlayerDied, player)


    @staticmethod
    def handle_packet_set_health(player: "Player", health: float, food: int = 0, food_saturation: float = 5.0):
        packet = Buffer()
        player.game_state.health = health
        packet.add_float(player.game_state.health)
        player.game_state.food = food
        packet.add_varint(player.game_state.food)
        packet.add_float(food_saturation)
        player.conn.send_mc_packet(packet, network.PlayStatePacketID.SetHealth.value)

    @staticmethod
    def handle_packet_remove_entities(conn: TCPConnection, eids: list[int]):
        packet = Buffer()
        packet.add_prefixed_varint_array([(e, ) for e in eids])
        conn.send_mc_packet(packet, network.PlayStatePacketID.RemoveEntities.value)

    @staticmethod
    def handle_packet_entity_event(conn: TCPConnection, eid: int, entity_status: int):
        packet = Buffer()
        packet.add_int(eid)
        packet.add_byte(entity_status)
        conn.send_mc_packet(packet, network.PlayStatePacketID.EntityEvent.value)

class IncomingEntityPacket:
    @staticmethod
    def _handle_in_entity_packet_interact(buf: Buffer, attacker: "Player"):
        eid: int = buf.consume_varint()
        type: int = buf.consume_varint()
        if type == InteractType.InteractAt.value:
            target_x: float = buf.consume_float()
            target_y: float = buf.consume_float()
            target_z: float = buf.consume_float()
        
        if type == InteractType.Interact.value or type == InteractType.InteractAt.value:
            hand: int = buf.consume_varint()
        
        sneak_key_pressed: bool = buf.consume_boolean()


        if type == InteractType.Attack.value:
            attacked_player = next((p for p in attacker.server_interface.get_all_players() if p.eid == eid))

            if not attacked_player:
                return

            if attacked_player.game_state.is_dead:
                return

            data = attacker.server_interface.get_registry_data()
            
            source_type_id = data["minecraft:damage_type"].index("minecraft:player_attack")
            
            for other_player in PlayersManager.get_ranged_players(attacked_player, True):
                EventManager.trigger(InGameEvent.DamageEvent, other_player.conn, attacked_player, attacker, source_type_id)

