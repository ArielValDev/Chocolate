import copy
from typing import TYPE_CHECKING

from utils.utils import float_to_angle
if TYPE_CHECKING:
    from models.player import Player
from models.events.event_manager import EventManager
from models.game import world
from models.network.messages.event_broadcaster import PlayersManager
from models.network.tcp_connection import TCPConnection
from models.types.position import Position, EntityPosition
from constants import game, network
from models.buffer import Buffer
from models.types.mc_types import *
from typing import Callable, Any

class OutgoingGameLoopPacketHandler:

    @staticmethod
    def unload_chunk(conn: TCPConnection, chunk: Position):
        chunk = chunk.to_chunk()
        packet = Buffer()
        packet.add_int(chunk.z)
        packet.add_int(chunk.x)
        conn.send_mc_packet(packet, network.PlayStatePacketID.UnloadChunk.value)
    
    @staticmethod
    def set_center_chunk(conn: TCPConnection, chunk: Position):
        """
        Outgoing
        """
        chunk = chunk.to_chunk()
        set_center_chunk = Buffer()
        set_center_chunk.add_varint(chunk.x)
        set_center_chunk.add_varint(chunk.z)
        conn.send_mc_packet(set_center_chunk, network.PlayStatePacketID.SetCenterChunk.value)

    @staticmethod
    def chunk_batch_start(conn: TCPConnection):
        """
        Outgoing
        """
        conn.send_mc_packet(Buffer(), network.PlayStatePacketID.ChunkBatchStart.value)

    @staticmethod
    def chunk_batch_finished(conn: TCPConnection, batch_size: int):
        """
        Outgoing
        """
        packet = Buffer()
        packet.add_varint(batch_size)
        conn.send_mc_packet(packet, network.PlayStatePacketID.ChunkBatchFinished.value)

    @staticmethod
    def update_player_chunks(player: "Player", moving_player: "Player", dx: int, dy: int, dz: int):
        current_chunk: Position = player.game_state.current_position.to_chunk()

        if player.meta_data.last_chunk == current_chunk:
            return
        player.meta_data.last_chunk = current_chunk

        view_distance: int = player.game_state.render_distance
        
        needed_chunks = set(world.get_chunk_positions_in_range(current_chunk, view_distance))
        loaded_chunks = set(player.meta_data.loaded_chunks)

        to_load = needed_chunks - loaded_chunks
        to_unload = loaded_chunks - needed_chunks


        OutgoingGameLoopPacketHandler.set_center_chunk(player.conn, current_chunk)
        for chunk in to_unload:
            OutgoingGameLoopPacketHandler.unload_chunk(
                player.conn,
                chunk
            )
            player.meta_data.loaded_chunks.remove(chunk)

        if not to_load:
            return

        OutgoingGameLoopPacketHandler.chunk_batch_start(player.conn)
        to_load_sorted = sorted(to_load, key=lambda c: (c.x - current_chunk.x) ** 2 + (c.z - current_chunk.z) ** 2)
        for chunk in to_load_sorted:
            chunk_buf = world.get_chunk_data_and_update_light_bytes_at(chunk)
            player.conn.send_mc_packet(chunk_buf, network.PlayStatePacketID.ChunkDataAndLightUpdate.value)
            player.meta_data.loaded_chunks.append(chunk)
        OutgoingGameLoopPacketHandler.chunk_batch_finished(player.conn, len(to_load_sorted))

class IncomingGameLoopPacketHandler:

    @staticmethod
    def _handle_in_game_packet_chunk_batch_recieved(buf: Buffer, player: "Player"):
        chunks_per_tick: float = buf.consume_float()


    @staticmethod
    def _handle_in_game_packet_close_container(buf: Buffer, player: "Player"):
        window_id: int = buf.consume_varint()

    @staticmethod
    def _handle_in_game_packet_use_item_on(buf: Buffer, player: "Player"):
        hand: int = buf.consume_varint()
        location: Position = buf.consume_position()
        face: int = buf.consume_varint()
        cursor_pos_x: float = buf.consume_float()
        cursor_pos_y: float = buf.consume_float()
        cursor_pos_z: float = buf.consume_float()
        inside_block: bool = buf.consume_boolean()
        world_border_hit: bool = buf.consume_boolean()
        sequence: int = buf.consume_varint()

    @staticmethod
    def _handle_in_game_packet_set_held_item(buf: Buffer, player: "Player"):
        slot: int = buf.consume_short()
        player.game_state.current_slot = slot

    @staticmethod
    def _handle_in_game_packet_player_action(buf: Buffer, player: "Player"):
        status: int = buf.consume_varint()
        location: Position = buf.consume_position()
        face: int = buf.consume_byte()
        sequence: int = buf.consume_varint()

    @staticmethod
    def _handle_in_game_packet_swing_arm(buf: Buffer, player: "Player"):
        hand: int = buf.consume_varint()
        hand_id = 0 if hand == 0 else 3
        for other_p in PlayersManager.get_ranged_players(player):
            EventManager.trigger(game.InGameEvent.SwingArm, other_p.conn, player.eid, hand_id)
    @staticmethod
    def _handle_in_game_packet_player_command(buf: Buffer, player: "Player"):
        eid: int = buf.consume_varint()
        action_id: int = buf.consume_varint()
        jump_boost: int = buf.consume_varint()

        EventManager.trigger(game.InGameEvent.PlayerCommand, action_id, jump_boost)

    @staticmethod
    def _handle_in_game_packet_set_player_position(buf: Buffer, player: "Player"):
        x: float = buf.consume_double()
        feet_y: float = buf.consume_double()
        z: float = buf.consume_double()
        flags: BitField = BitField()
        flags.set(buf.consume_byte())

        dx = int(x * 4096 - player.game_state.current_position.x * 4096)
        dy = int(feet_y * 4096 - player.game_state.current_position.y * 4096)
        dz = int(z * 4096 - player.game_state.current_position.z * 4096)

        player.game_state.current_position.y = feet_y
        player.game_state.current_position.z = z
        player.game_state.current_position.x = x
        player.game_state.current_position.is_on_ground = flags.check(0x01)
        player.game_state.current_position.is_pushing_against_wall = flags.check(0x02)
        for other_p in PlayersManager.get_ranged_players(player):
            EventManager.trigger(game.InGameEvent.PlayerMoved, other_p, player, dx, dy, dz)

    @staticmethod
    def _handle_in_game_packet_set_player_rotation(buf: Buffer, player: "Player"):
        yaw: float = buf.consume_float()
        pitch: float = buf.consume_float()
        flags: BitField = BitField()
        flags.set(buf.consume_byte())

        player.game_state.current_position.yaw = yaw
        player.game_state.current_position.pitch = pitch
        player.game_state.current_position.is_on_ground = flags.check(0x01)
        player.game_state.current_position.is_pushing_against_wall = flags.check(0x02)

        angled_yaw = float_to_angle(yaw)
        angled_pitch = float_to_angle(pitch)
        print(f"(2) raw_yaw: {yaw}, raw_pitch: {pitch}, angled_yaw: {angled_yaw}, angled_pitch: {angled_pitch}")

        for other_p in PlayersManager.get_ranged_players(player):
            EventManager.trigger(game.InGameEvent.PlayerRotated, other_p, player, angled_yaw, angled_pitch)

    @staticmethod
    def _handle_in_game_packet_set_player_position_and_rotation(buf: Buffer, player: "Player"):
        x: float = buf.consume_double()
        y: float = buf.consume_double()
        z: float = buf.consume_double()
        yaw: float = buf.consume_float()
        pitch: float = buf.consume_float()

        flags: BitField = BitField()
        flags.set(buf.consume_byte())

        dx = int(x - player.game_state.current_position.x)
        dy = int(y - player.game_state.current_position.y)
        dz = int(z - player.game_state.current_position.z)

        angled_yaw = float_to_angle(yaw)
        angled_pitch = float_to_angle(pitch)
        print(f"(1) raw_yaw: {yaw}, raw_pitch: {pitch}, angled_yaw: {angled_yaw}, angled_pitch: {angled_pitch}")

        player.game_state.current_position = EntityPosition(x, y, z, yaw, pitch, flags.check(0x01), flags.check(0x02), player.game_state.current_position.dimension, player.game_state.current_position.head_yaw)
        for other_p in PlayersManager.get_ranged_players(player):
            EventManager.trigger(game.InGameEvent.PlayerMovedAndRotated, other_p, player, dx, dy, dz, angled_yaw, angled_pitch)

    @staticmethod
    def _handle_in_game_packet_player_input(buf: Buffer, player: "Player"):
        flags = buf.consume_unsigned_byte()

    @staticmethod
    def _handle_in_game_packet_player_loaded(buf: Buffer, player: "Player"):
        pass

    @staticmethod
    def _handle_in_game_packet_client_tick_end(buf: Buffer, player: "Player"):
        pass

    @staticmethod
    def _handle_in_game_packet_keep_alive_serverbound(buf: Buffer, player: "Player"):
        keep_alive_id = buf.consume_long()
        if keep_alive_id != player.meta_data.awaiting_keep_alive_id:
            player.disconnect_player()
        player.meta_data.awaiting_keep_alive_id = None

    @staticmethod
    def handle_in_game_packets(player: "Player"):
        """
        Incoming
        """
        packet_id, buf = player.conn.recv_mc_packet()

        handler = PACKET_HANDLER.get(packet_id)
        if handler:
            handler(buf, player)
        else:

            pass
            #print(f"Unhandled packet: {hex(packet_id)}")
            #exit()

PACKET_HANDLER: dict[int, Callable[[Buffer, "Player"], Any]] = {
    network.PlayStatePacketID.ClientTickEnd.value: IncomingGameLoopPacketHandler._handle_in_game_packet_client_tick_end,
    network.PlayStatePacketID.PlayerLoaded.value: IncomingGameLoopPacketHandler._handle_in_game_packet_player_loaded,
    network.PlayStatePacketID.SetPlayerPosition.value: IncomingGameLoopPacketHandler._handle_in_game_packet_set_player_position,
    network.PlayStatePacketID.SetPlayerRotation.value: IncomingGameLoopPacketHandler._handle_in_game_packet_set_player_rotation,
    network.PlayStatePacketID.SetPlayerPositionAndRotation.value: IncomingGameLoopPacketHandler._handle_in_game_packet_set_player_position_and_rotation,
    network.PlayStatePacketID.PlayerInput.value: IncomingGameLoopPacketHandler._handle_in_game_packet_player_input,
    network.PlayStatePacketID.KeepAliveToServer.value: IncomingGameLoopPacketHandler._handle_in_game_packet_keep_alive_serverbound,
    network.PlayStatePacketID.PlayerCommand.value: IncomingGameLoopPacketHandler._handle_in_game_packet_player_command,
    network.PlayStatePacketID.SwingArm.value: IncomingGameLoopPacketHandler._handle_in_game_packet_swing_arm,
    network.PlayStatePacketID.PlayerAction.value: IncomingGameLoopPacketHandler._handle_in_game_packet_player_action,
    network.PlayStatePacketID.SetHeldItem.value: IncomingGameLoopPacketHandler._handle_in_game_packet_set_held_item,
    network.PlayStatePacketID.UseItemOn.value: IncomingGameLoopPacketHandler._handle_in_game_packet_use_item_on,
    network.PlayStatePacketID.CloseContainer.value: IncomingGameLoopPacketHandler._handle_in_game_packet_close_container,
    network.PlayStatePacketID.ChunkBatchReceived.value: IncomingGameLoopPacketHandler._handle_in_game_packet_chunk_batch_recieved
    }