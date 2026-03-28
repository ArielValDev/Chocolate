from typing import TYPE_CHECKING

from utils.utils import float_to_angle
if TYPE_CHECKING:
    from models.player import Player
from uuid import UUID
from constants import network
from models.buffer import Buffer
from models.network.tcp_connection import TCPConnection
from models.types.position import EntityPosition


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
        entity_packet.add_byte(entity_position.head_yaw)
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
        packet.add_boolean(moving_player.game_state.current_position.is_on_ground)
        other_player.conn.send_mc_packet(packet, network.PlayStatePacketID.UpdateEntityRotation.value)

        