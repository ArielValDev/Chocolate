from dataclasses import dataclass
import math
from typing import TYPE_CHECKING

from requests import get
from constants import game
from models.game.world import get_chunk_data_and_update_light_bytes_at
from models.types.position import Position
from utils.logger import Logger

if TYPE_CHECKING:
    from models.player import Player
from uuid import UUID
from constants import network
from constants.game import PlayerAction
from models.buffer import Buffer
from models.types.mc_types import *
from models.network.tcp_connection import TCPConnection
from utils.network_utils import fetch_player_properties

def send_debug_bytes(conn: TCPConnection, bytes_: bytearray):
    """
    Outgoing
    """
    Logger.debug(str(bytes(bytes_)))
    conn._send(bytes(bytes_)) # type: ignore


def debug_recieve(conn: TCPConnection):
    """
    Incomming
    """
    _, _ = conn.recv_mc_packet()

def handle_player_packet_ping(conn: TCPConnection, id: int):
    """
    Outgoing
    """
    ping = Buffer()
    ping.add_int(id)
    conn.send_mc_packet(ping, network.PlayStatePacketID.Ping.value)


def handle_player_packet_synchronize_player_position(conn: TCPConnection, tpid: int, x: float, y: float, z: float, velocity_x: float, velocity_y: float, velocity_z: float, yaw: float, pitch: float, flags: BitField):
    """
    Outgoing
    """
    sync_pos = Buffer()

    sync_pos.add_varint(tpid)
    sync_pos.add_double(x)
    sync_pos.add_double(y)
    sync_pos.add_double(z)
    sync_pos.add_double(velocity_x)
    sync_pos.add_double(velocity_y)
    sync_pos.add_double(velocity_z)
    sync_pos.add_float(yaw)
    sync_pos.add_float(pitch)
    sync_pos.add_raw(bytearray(flags.to_bytes(4)))

    conn.send_mc_packet(sync_pos, network.PlayStatePacketID.SynchronizePlayerPosition.value)

def handle_player_packet_confirm_teleportation(conn: TCPConnection, state: network.ConnectionState, awaiting_tids: list[int]):
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.PlayStatePacketID.ConfirmTeleportation.value or state != network.ConnectionState.Play:
        raise ConnectionError("Unexpected packet ID or state for confirm teleportation")
    
    tid = buf.consume_varint()
    if tid not in awaiting_tids: raise ValueError("Invalid teleport confirmation")
    awaiting_tids.remove(tid)

def handle_player_packet_set_player_position_and_rotation(conn: TCPConnection, state: network.ConnectionState):
    """
    Incoming
    """
    packet_id, _ = conn.recv_mc_packet()
    if packet_id != network.PlayStatePacketID.SetPlayerPositionAndRotation.value or state != network.ConnectionState.Play:
        raise ConnectionError("Unexpected packet ID or state for set player position and rotation")
    
def handle_player_packet_player_info_update(conn: TCPConnection, actions: BitField, uuid: UUID, players: list["Player"], game_mode: int, should_be_listed: bool, ping: int, display_name: str, priority: int, visible_hat: bool):
    """
    Outgoing
    """
    info_update = Buffer()
    info_update.add_raw(bytearray(actions.to_bytes(1)))

    players_list: list[tuple[UUID, Buffer]] = []
    for player in players:
        player_actions = Buffer()

        if actions.check(PlayerAction.AddPlayer.value):
            add_player = Buffer()
            player_props = fetch_player_properties(player.uuid)
            add_player.add_string(player.username)
            add_player.add_prefixed_string_array(player_props)
            player_actions.add_buffer(add_player)

        if actions.check(PlayerAction.InitializeChat.value):
            raise NotImplemented("Chat not implemented")
            initialize_chat = Buffer()
            player_actions.add_buffer(initialize_chat)

        if actions.check(PlayerAction.UpdateGameMode.value):
            update_game_mode = Buffer()
            update_game_mode.add_varint(game_mode)
            player_actions.add_buffer(update_game_mode)
        
        if actions.check(PlayerAction.UpdateListed.value):
            update_listed = Buffer()
            update_listed.add_boolean(should_be_listed)
            player_actions.add_buffer(update_listed)

        if actions.check(PlayerAction.UpdateLatency.value):
            update_latency = Buffer()
            update_latency.add_varint(ping)
            player_actions.add_buffer(update_latency)

        if actions.check(PlayerAction.UpdateDisplayName.value):
            update_display_name = Buffer()
            update_display_name.add_prefixed_optional_text_component(display_name)
            player_actions.add_buffer(update_display_name)

        if actions.check(PlayerAction.UpdateListPriority.value):
            update_list_priority = Buffer()
            update_list_priority.add_varint(priority)
            player_actions.add_buffer(update_list_priority)
        
        if actions.check(PlayerAction.UpdateHat.value):
            update_hat = Buffer()
            update_hat.add_boolean(visible_hat)
            player_actions.add_buffer(update_hat)

        players_list.append((player.uuid, player_actions))
    
    info_update.add_prefixed_uuid_player_actions_array(players_list)
    conn.send_mc_packet(info_update, network.PlayStatePacketID.PlayerInfoUpdate.value)

def handle_player_packet_game_event(conn: TCPConnection, event: int, value: float):
    """
    Outgoing
    """
    game_event = Buffer()
    game_event.add_unsigned_byte(event)
    game_event.add_float(value)
    conn.send_mc_packet(game_event, network.PlayStatePacketID.GameEvent.value)

# TODO: world generation
@dataclass
class PalettedContainer:
    bits_per__entry: int
    palette: list[int]
    data_array: list[int]

@dataclass
class Section:
    block_count: int
    block_states: PalettedContainer
    biomes: PalettedContainer

def handle_player_packet_chunk_data_and_update_light(conn: TCPConnection, position: Position):
    chunk_and_light_data = get_chunk_data_and_update_light_bytes_at(position)
    conn.send_mc_packet(chunk_and_light_data, network.PlayStatePacketID.ChunkDataAndLightUpdate.value)

def handle_player_packet_player_loaded(conn: TCPConnection, state: network.ConnectionState):
    """
    Incoming
    """
    packet_id, _ = conn.recv_mc_packet()
    if packet_id != network.PlayStatePacketID.PlayerLoaded.value and packet_id != network.PlayStatePacketID.ClientTickEnd.value or state != network.ConnectionState.Play:
        raise ConnectionError("Unexpected packet ID or state for player loaded")

def handle_player_packet_respawn(conn: TCPConnection, dimension_type: int, dimension_name: str, hashed_seed: int, game_mode: int, previouse_game_mode: int, is_debug: bool, is_flat: bool, has_death_location: bool, death_dimention_name: str, death_location: int, portal_cooldown: int, sea_level: int, data_kept: int):
    respawn_packet = Buffer()

    respawn_packet.add_varint(dimension_type)
    respawn_packet.add_string(dimension_name)
    respawn_packet.add_long(hashed_seed)
    respawn_packet.add_unsigned_byte(game_mode)
    respawn_packet.add_byte(previouse_game_mode)
    respawn_packet.add_boolean(is_debug)
    respawn_packet.add_boolean(is_flat)
    respawn_packet.add_boolean(has_death_location)
    respawn_packet.add_optional_string(death_dimention_name)
    respawn_packet.add_long(death_location)
    respawn_packet.add_varint(portal_cooldown)
    respawn_packet.add_varint(sea_level)
    respawn_packet.add_byte(data_kept)

    conn.send_mc_packet(respawn_packet, network.PlayStatePacketID.Respawn.value)

def handle_player_packet_chunk_batch_received(conn: TCPConnection, state: network.ConnectionState) -> float:
    """
    Incoming
    """
    packet_id, data = conn.recv_mc_packet()

    if packet_id != network.PlayStatePacketID.ChunkBatchReceived.value or state != network.ConnectionState.Play:
        raise ConnectionError(f"Unexpected packet ID or state for chunk batch recieve")

    return data.consume_float()

def handle_player_packet_keep_alive_clientbound(conn: TCPConnection, id: int):
    """
    Outgoing
    """
    keep_alive_packet = Buffer()
    keep_alive_packet.add_long(id)
    conn.send_mc_packet(keep_alive_packet, network.PlayStatePacketID.KeepAliveToClient.value)

def handle_player_packet_update_time(conn: TCPConnection, world_age: int, time_of_day: int, time_of_day_increasing: bool):
    time_packet = Buffer()
    time_packet.add_long(world_age)
    time_packet.add_long(time_of_day)
    time_packet.add_boolean(time_of_day_increasing)
    conn.send_mc_packet(time_packet, network.PlayStatePacketID.UpdateTime.value)

def handle_player_packet_set_ticking_state(conn: TCPConnection, tick_rate: float, is_frozen: bool):
    """
    Outgoing
    """
    tick_state_packet = Buffer()
    tick_state_packet.add_float(tick_rate)
    tick_state_packet.add_boolean(is_frozen)

    conn.send_mc_packet(tick_state_packet, network.PlayStatePacketID.SetTickingState.value)

def handle_player_packet_step_tick(conn: TCPConnection, tick_steps: int):
    """
    Outgoing
    """
    step_tick_packet = Buffer()
    step_tick_packet.add_varint(tick_steps)

    conn.send_mc_packet(step_tick_packet, network.PlayStatePacketID.StepTick.value)

