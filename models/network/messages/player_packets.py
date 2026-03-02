from typing import TYPE_CHECKING

from constants import game

if TYPE_CHECKING:
    from models.player import Player
from uuid import UUID
from constants import network
from constants.game import PlayerActions
from models.buffer import Buffer
from models.mc_types import *
from models.network.tcp_connection import TCPConnection
from utils.network_utils import fetch_player_properties


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
    
def handle_player_packet_player_info_update(conn: TCPConnection, actions: BitField, uuid: UUID, username: str, players: list["Player"], game_mode: int, should_be_listed: bool, ping: int, display_name: str, priority: int, visible_hat: bool):
    """
    Outgoing
    """
    info_update = Buffer()
    info_update.add_raw(bytearray(actions.to_bytes(1)))

    players_list: list[tuple[UUID, Buffer]] = []
    for player in players:
        player_actions = Buffer()

        if actions.check(PlayerActions.AddPlayer.value):
            add_player = Buffer()
            player_props = fetch_player_properties(player.uuid)
            add_player.add_string(player.username)
            add_player.add_prefixed_string_array(player_props)
            player_actions.add_buffer(add_player)

        if actions.check(PlayerActions.InitializeChat.value):
            raise NotImplemented("Chat not implemented")
            initialize_chat = Buffer()
            player_actions.add_buffer(initialize_chat)

        if actions.check(PlayerActions.UpdateGameMode.value):
            update_game_mode = Buffer()
            update_game_mode.add_varint(game_mode)
            player_actions.add_buffer(update_game_mode)
        
        if actions.check(PlayerActions.UpdateListed.value):
            update_listed = Buffer()
            update_listed.add_boolean(should_be_listed)
            player_actions.add_buffer(update_listed)

        if actions.check(PlayerActions.UpdateLatency.value):
            update_latency = Buffer()
            update_latency.add_varint(ping)
            player_actions.add_buffer(update_latency)

        if actions.check(PlayerActions.UpdateDisplayName.value):
            update_display_name = Buffer()
            update_display_name.add_prefixed_optional_text_component(display_name)
            player_actions.add_buffer(update_display_name)

        if actions.check(PlayerActions.UpdateListPriority.value):
            update_list_priority = Buffer()
            update_list_priority.add_varint(priority)
            player_actions.add_buffer(update_list_priority)
        
        if actions.check(PlayerActions.UpdateHat.value):
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
