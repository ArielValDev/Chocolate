import json
from typing import Any
from dataclasses import dataclass
from constants import network
from constants import constants
from models.network.tcp_connection import TCPConnection
from uuid import UUID
from models.buffer import Buffer, OptionalString
from utils import network_utils
from utils.logger import Logger

@dataclass
class HandshakePacketData:
    protocol_version: int
    server_address: str
    port: int
    intent: int

def handle_message_handshake(conn: TCPConnection, state: network.ConnectionState) -> HandshakePacketData:
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.HandshakingStatePacketID.Handshake.value or state != network.ConnectionState.Handshaking:
        raise ConnectionError("Unexpected packet ID or state for handshake")
    
    return HandshakePacketData(
        protocol_version=buf.consume_varint(),
        server_address=buf.consume_string(),
        port=buf.consume_unsigned_short(),
        intent=buf.consume_varint()
    )

@dataclass
class LoginPacketData:
    username: str
    uuid: UUID

def handle_message_login(conn: TCPConnection, state: network.ConnectionState) -> LoginPacketData:
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.LoginStatePacketID.LoginStart.value or state != network.ConnectionState.Login:
        raise ConnectionError("Unexpected packet ID or state for login")
    
    return LoginPacketData(
        username=buf.consume_string(),
        uuid=buf.consume_uuid()
    )

def handle_message_login_success(conn: TCPConnection, uuid: UUID, username: str):
    """
    Outgoing
    """
    login_success_msg = Buffer()
    properties = network_utils.fetch_player_properties(uuid)
    login_success_msg.add_game_profile(uuid, username, properties)

    conn.send_mc_packet(login_success_msg, network.LoginStatePacketID.LoginSuccess.value)
    
def handle_message_login_ack(conn: TCPConnection, state: network.ConnectionState):
    """
    Incoming
    """
    packet_id, _ = conn.recv_mc_packet()
    if packet_id != network.LoginStatePacketID.LoginAck.value or state != network.ConnectionState.Login:
        raise ConnectionError("Unexpected packet ID or state for login acknowledge")
    
@dataclass
class PluginMessagePacketData:
    channel: str
    data: Any

def handle_message_plugin_message(conn: TCPConnection, state: network.ConnectionState) -> PluginMessagePacketData:
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.ConfigurationStatePacketID.PluginMessage.value or state != network.ConnectionState.Configuration:
        raise ConnectionError("Unexpected packet ID or state for login acknowledge")
    
    return PluginMessagePacketData(
        channel = buf.consume_string(),
        data = buf.get_bytes()
    )

@dataclass
class ClientInformationPacketData:
    locale: str
    view_distance: int
    chat_mode: int
    chat_colors: bool
    displayed_skin_parts: int
    main_hand: int
    enable_text_filtering: bool
    allow_server_listing: bool
    particle_status: int


def handle_message_client_information(conn: TCPConnection, state: network.ConnectionState) -> ClientInformationPacketData:
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.ConfigurationStatePacketID.ClientInformation.value or state != network.ConnectionState.Configuration:
        raise ConnectionError("Unexpected packet ID or state for login acknowledge")
    
    return ClientInformationPacketData(
        locale = buf.consume_string(),
        view_distance = buf.consume_varint(),
        chat_mode = buf.consume_varint(),
        chat_colors = buf.consume_boolean(),
        displayed_skin_parts = buf.consume_varint(),
        main_hand = buf.consume_varint(),
        enable_text_filtering = buf.consume_boolean(),
        allow_server_listing = buf.consume_boolean(),
        particle_status = buf.consume_varint()
    )

def handle_message_clientbound_known_packs(conn: TCPConnection):
    """
    Outgoing
    """
    known_packs = Buffer()
    known_packs.add_prefixed_string_array([("minecraft", "core", "1.21.11")])
    conn.send_mc_packet(known_packs, network.ConfigurationStatePacketID.ClientboundKnownPacks.value)

@dataclass
class ServerboundKnownPacks:
    namespace: list[str]
    id: list[str]
    version: list[str]

def handle_message_serverbound_known_packs(conn: TCPConnection, state: network.ConnectionState):
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != network.ConfigurationStatePacketID.ServerboundKnowPacks.value or state != network.ConnectionState.Configuration:
        raise ConnectionError("Unexpected packet ID or state for serverbound know packs")
    
    namespace: list[str] = []
    id: list[str] = []
    version: list[str] = []

    known_packs = buf.consume_prefixed_string_array(3)

    for i in range(0, len(known_packs)):
        match (i+1) % 3: # type: ignore
            case 1:
                namespace.append(known_packs[i])
            case 2:
                id.append(known_packs[i])
            case 0:
                version.append(known_packs[i])

    return ServerboundKnownPacks(
        namespace = namespace,
        id = id,
        version = version
    )


def handle_message_registry_data(conn: TCPConnection):
    """
    Outgoing
    """
    registry_data = network_utils.get_registries_from_file(constants.REGISTRIES_FILE)
    
    for reg, entries in registry_data.items():
        registry_data_msg = Buffer()
        registry_data_msg.add_string(reg)
        registry_data_msg.add_prefixed_string_array([(p, OptionalString(None)) for p in entries])
        conn.send_mc_packet(registry_data_msg, network.ConfigurationStatePacketID.RegistryData.value)
    
def handle_message_finish_configuration(conn: TCPConnection):
    conn.send_mc_packet(Buffer(), network.ConfigurationStatePacketID.FinishConfiguration.value)

def handle_message_ack_finish_configuration(conn: TCPConnection, state: network.ConnectionState):
    packet_id, _ = conn.recv_mc_packet()
    if packet_id != network.ConfigurationStatePacketID.FinishConfiguration.value or state != network.ConnectionState.Configuration:
        raise ConnectionError("Unexpected packet ID or state for finish configuration")
    
def handle_message_login_play(conn: TCPConnection, eid: int, is_hardcore: bool, max_players: int, view_distance: int, simulation_distance: int, reduced_debug_info: bool, enable_respawn_screen: bool, do_limited_crafting: bool, dimension_name: str, hashed_seed: int, game_mode: int, previouse_game_mode: int, is_debug: bool, is_flat: bool, has_death_location: bool, death_dimention_name: str, death_location: int, portal_cooldown: int, sea_level: int, enforces_secure_chat: bool):
    login_play_packet = Buffer()
    
    login_play_packet.add_raw(bytearray([eid]))
    login_play_packet.add_boolean(is_hardcore)

    with open(constants.REGISTRIES_FILE, "r") as f:
        dimensions: list[str] = []
        registries: dict[str, list[str]] = json.load(f)
        for reg, data in registries.items():
            if reg == "minecraft:dimension_type":
                dimensions = data

    login_play_packet.add_prefixed_string_array([(d, ) for d in dimensions])
    login_play_packet.add_varint(max_players)
    login_play_packet.add_varint(view_distance)
    login_play_packet.add_varint(simulation_distance)
    login_play_packet.add_boolean(reduced_debug_info)
    login_play_packet.add_boolean(enable_respawn_screen)
    login_play_packet.add_boolean(do_limited_crafting)
    login_play_packet.add_varint(0)
    login_play_packet.add_string(dimension_name)
    login_play_packet.add_long(hashed_seed)
    login_play_packet.add_unsigned_byte(game_mode)
    login_play_packet.add_byte(previouse_game_mode)
    login_play_packet.add_boolean(is_debug)
    login_play_packet.add_boolean(is_flat)
    login_play_packet.add_boolean(has_death_location)
    #login_play_packet.add_optional_string(death_dimention_name)
    #login_play_packet.add_long(death_location)
    login_play_packet.add_varint(portal_cooldown)
    login_play_packet.add_varint(sea_level)
    login_play_packet.add_boolean(enforces_secure_chat)


