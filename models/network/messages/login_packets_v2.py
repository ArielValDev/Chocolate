import json
from constants import network
from constants import constants
from models.network.tcp_connection import TCPConnection
from uuid import UUID
from models.buffer import Buffer, OptionalString
from utils import network_utils
from utils.logger import Logger
from models.encryption_manager import EncryptionManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.player import Player


def handle_login_packet_encryption_request(conn: TCPConnection, public_key: bytes, verify_token: bytes, should_auth: bool):
    """
    Outgoing
    """
    encryption_request_packet = Buffer()
    
    encryption_request_packet.add_string("")
    
    public_key_tuples = [((b - 256 if b > 127 else b),) for b in public_key]
    encryption_request_packet.add_prefixed_byte_array(public_key_tuples)
    
    verify_token_tuples = [((b - 256 if b > 127 else b),) for b in verify_token]
    encryption_request_packet.add_prefixed_byte_array(verify_token_tuples)
    
    encryption_request_packet.add_boolean(should_auth)
    
    conn.send_mc_packet(encryption_request_packet, network.LoginStatePacketID.Encryption.value)

def handle_login_packet_login_success(conn: TCPConnection, uuid: UUID, username: str):
    """
    Outgoing
    """
    login_success_msg = Buffer()
    properties = network_utils.fetch_player_properties(uuid)
    login_success_msg.add_game_profile(uuid, username, properties)

    conn.send_mc_packet(login_success_msg, network.LoginStatePacketID.LoginSuccess.value)

def handle_login_packet_clientbound_known_packs(conn: TCPConnection):
    """
    Outgoing
    """
    known_packs = Buffer()
    known_packs.add_prefixed_string_array(constants.KNOWN_PACKS) # type: ignore
    conn.send_mc_packet(known_packs, network.ConfigurationStatePacketID.ClientboundKnownPacks.value)

def handle_login_packet_registry_data(conn: TCPConnection):
    """
    Outgoing
    """
    registry_data = network_utils.get_registries_from_file(constants.REGISTRIES_FILE)
    
    for reg, entries in registry_data.items():
        registry_data_msg = Buffer()
        registry_data_msg.add_string(reg)
        registry_data_msg.add_prefixed_string_array([(p, OptionalString(None)) for p in entries])
        if (reg == "minecraft:timeline"):
            conn.send_mc_packet(registry_data_msg, network.ConfigurationStatePacketID.RegistryData.value)
        else:
            conn.send_mc_packet(registry_data_msg, network.ConfigurationStatePacketID.RegistryData.value)

def handle_login_packet_update_tags(conn: TCPConnection):
    """
    Outgoing
    """
    update_tags = Buffer()
    update_tags_array: list[tuple[str, Buffer]] = []
    with open(constants.TAGS_FILE, 'r') as file:
        tags_data = json.load(file)
    

    for reg in tags_data:
        tags = Buffer()
        tags_array: list[tuple[str, list[int]]] = []
        for tag in tags_data[reg]:
            tags_array.append((tag, tags_data[reg][tag]))
        
        tags.add_prefixed_tag_array(tags_array)
        update_tags_array.append((reg, tags))

    update_tags.add_prefixed_string_tag_array(update_tags_array)
    conn.send_mc_packet(update_tags, network.ConfigurationStatePacketID.UpdateTags.value)
    
def handle_login_packet_finish_configuration(conn: TCPConnection):
    """
    Outgoing
    """
    conn.send_mc_packet(Buffer(), network.ConfigurationStatePacketID.FinishConfiguration.value)

def handle_login_packet_login_play(conn: TCPConnection, eid: int, is_hardcore: bool, max_players: int, view_distance: int, simulation_distance: int, reduced_debug_info: bool, enable_respawn_screen: bool, do_limited_crafting: bool, dimension_name: str, hashed_seed: int, game_mode: int, previouse_game_mode: int, is_debug: bool, is_flat: bool, has_death_location: bool, death_dimention_name: str, death_location: int, portal_cooldown: int, sea_level: int, enforces_secure_chat: bool):
    """
    Outgoing
    """
    login_play_packet = Buffer()
    
    login_play_packet.add_int(eid)
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
    if has_death_location:
        login_play_packet.add_optional_string(death_dimention_name)
        login_play_packet.add_long(death_location)
    login_play_packet.add_varint(portal_cooldown)
    login_play_packet.add_varint(sea_level)
    login_play_packet.add_boolean(enforces_secure_chat)

    conn.send_mc_packet(login_play_packet, network.PlayStatePacketID.LoginPlay.value)

class IncomingLoginPacketHandler:
    @staticmethod
    def handle_handshake(buf: Buffer, player: "Player"):
        protocol_version = buf.consume_varint()
        server_address = buf.consume_string()
        port = buf.consume_unsigned_short()
        intent = buf.consume_varint()
        
        if intent == 2:
            player.connection_state = network.ConnectionState.Login

    @staticmethod
    def handle_login_start(buf: Buffer, player: "Player"):
        player.username = buf.consume_string()
        player.uuid = buf.consume_uuid()

        if constants.ENCRYPTING:
            public_key = EncryptionManager.public_key_bytes
            verify_token = EncryptionManager.generate_verify_token()
            handle_login_packet_encryption_request(player.conn, public_key, verify_token, False)
        else:
            handle_login_packet_login_success(player.conn, player.uuid, player.username)


    @staticmethod
    def handle_encryption_response(buf: Buffer, player: "Player"):        
        raw_shared_secret = buf.consume_prefixed_byte_array()
        unsigned_shared_secret = [b + 256 if b < 0 else b for b in raw_shared_secret]
        shared_secret = bytes(unsigned_shared_secret)
        
        raw_verify_token = buf.consume_prefixed_byte_array()
        unsigned_verify_token = [b + 256 if b < 0 else b for b in raw_verify_token]
        verify_token = bytes(unsigned_verify_token)

        decrypted_secret = EncryptionManager.decrypt_shared_secret(shared_secret)
        player.conn.enable_encryption(decrypted_secret)
        
        handle_login_packet_login_success(player.conn, player.uuid, player.username)

    @staticmethod
    def handle_login_ack(buf: Buffer, player: "Player"):
        player.connection_state = network.ConnectionState.Configuration
        handle_login_packet_clientbound_known_packs(player.conn)
        handle_login_packet_registry_data(player.conn)
        handle_login_packet_update_tags(player.conn)
        handle_login_packet_finish_configuration(player.conn)
        

    @staticmethod
    def handle_client_information(buf: Buffer, player: "Player"):
        buf.consume_string()
        player.game_state.render_distance = buf.consume_varint()

    @staticmethod
    def handle_plugin_message(buf: Buffer, player: "Player"):
        pass

    @staticmethod
    def handle_serverbound_known_packs(buf: Buffer, player: "Player"):
        pass

    @staticmethod
    def handle_ack_finish_configuration(buf: Buffer, player: "Player"):
        player.connection_state = network.ConnectionState.Play


HANDSHAKE_ROUTER = { network.HandshakingStatePacketID.Handshake.value: IncomingLoginPacketHandler.handle_handshake }
LOGIN_ROUTER = {
    network.LoginStatePacketID.LoginStart.value: IncomingLoginPacketHandler.handle_login_start,
    network.LoginStatePacketID.Encryption.value: IncomingLoginPacketHandler.handle_encryption_response,
    network.LoginStatePacketID.LoginAck.value: IncomingLoginPacketHandler.handle_login_ack
}
CONFIG_ROUTER = {
    network.ConfigurationStatePacketID.ClientInformation.value: IncomingLoginPacketHandler.handle_client_information,
    network.ConfigurationStatePacketID.PluginMessage.value: IncomingLoginPacketHandler.handle_plugin_message,
    network.ConfigurationStatePacketID.ServerboundKnowPacks.value: IncomingLoginPacketHandler.handle_serverbound_known_packs,
    network.ConfigurationStatePacketID.FinishConfiguration.value: IncomingLoginPacketHandler.handle_ack_finish_configuration
}

def process_login_phase(player: "Player") -> bool:
    while player.connection_state != network.ConnectionState.Play:
        packet_id, buf = player.conn.recv_mc_packet()
        if buf is None:
            return False

        handler = None
        if player.connection_state == network.ConnectionState.Handshaking:
            handler = HANDSHAKE_ROUTER.get(packet_id)
        elif player.connection_state == network.ConnectionState.Login:
            handler = LOGIN_ROUTER.get(packet_id)
        elif player.connection_state == network.ConnectionState.Configuration:
            handler = CONFIG_ROUTER.get(packet_id)

        if handler:
            handler(buf, player)
        else:
            Logger.warn(f"Skipped unhandled login packet: {hex(packet_id)} in state {player.connection_state}")

    return True