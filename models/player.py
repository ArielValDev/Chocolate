from uuid import UUID
from constants.constants import GeneratorIDs
from constants.game import PlayerActions
from constants.network import ConnectionState
from models.network.messages.login_packets import *
from models.network.messages.player_packets import *
from models.network.tcp_connection import TCPConnection
from models.server_communicator import ServerCommunicator
from utils.id_generator import IDGenerator
from utils.logger import Logger
from utils.protocol_type_utils import to_varint

class PlayerMetaData:
    def __init__(self):
        self.awaiting_teleport_ids: list[int] = []

class PlayerGameState:
    def __init__(self, game_mode: int):
        self.game_mode = game_mode

class Player:
    def __init__(self, conn: TCPConnection, server_communicator: ServerCommunicator):
        self.conn = conn
        self.server_communicator = server_communicator
        self.connection_state: ConnectionState = ConnectionState.Handshaking
        self.username: str = ""
        self.uuid: UUID = UUID(int = 0)
        self.eid = IDGenerator.get_id(GeneratorIDs.EntityID)
        self.meta_data = PlayerMetaData()
        self.game_state = PlayerGameState(0) # TODO should get the game mode from the server (the server gets the game mode from the config file)

    def connect_to_world(self):
        handle_login_packet_handshake(self.conn, self.connection_state)
        
        self.connection_state = ConnectionState.Login

        user_data = handle_login_packet_login(self.conn, self.connection_state)
        self.username = user_data.username
        self.uuid = user_data.uuid


        self.conn.send_mc_packet(Buffer(to_varint(-1)), 0x03)
        handle_login_packet_login_success(self.conn, self.uuid, self.username)
        handle_login_packet_login_ack(self.conn, self.connection_state)

        self.connection_state = ConnectionState.Configuration

        _ = handle_login_packet_plugin_message(self.conn, self.connection_state)
        client_inforamtion = handle_login_packet_client_information(self.conn, self.connection_state) # type: ignore

        handle_login_packet_clientbound_known_packs(self.conn)
        client_known_packs = handle_login_packet_serverbound_known_packs(self.conn, self.connection_state) # type: ignore

        #if not same_known_packs(client_known_packs):
        handle_login_packet_registry_data(self.conn)
        handle_login_packet_update_tags(self.conn)

        handle_login_packet_finish_configuration(self.conn)
        handle_login_packet_ack_finish_configuration(self.conn, self.connection_state)

        self.connection_state = ConnectionState.Play
        handle_login_packet_login_play(self.conn, self.eid, False, 2, 4, 4, False, True, False, "minecraft:overworld", 1379429607, self.game_state.game_mode, -1, False, True, True, "minecraft:overworld", 0, 1, 62, False)

        tid = IDGenerator.get_id(GeneratorIDs.TeleportID)
        self.meta_data.awaiting_teleport_ids.append(tid)
        handle_player_packet_synchronize_player_position(self.conn, tid, 0, 0, 0, 0, 0, 0, 0, 0, BitField())
        handle_player_packet_confirm_teleportation(self.conn, self.connection_state, self.meta_data.awaiting_teleport_ids)
        handle_player_packet_set_player_position_and_rotation(self.conn, self.connection_state)

        actions = BitField()
        actions.set(PlayerActions.AddPlayer.value)
        actions.set(PlayerActions.UpdateGameMode.value)
        actions.set(PlayerActions.UpdateListed.value)
        actions.set(PlayerActions.UpdateLatency.value)
        # actions.set(PlayerActions.UpdateDisplayName.value)
        actions.set(PlayerActions.UpdateListPriority.value)
        actions.set(PlayerActions.UpdateHat.value)
        handle_player_packet_player_info_update(self.conn, actions, self.uuid, self.username, self.server_communicator.get_all_players(), self.game_state.game_mode, True, 100, self.username, 1, True) # TODO get real ping of a player
        handle_player_packet_game_event(self.conn, 13, 0)
