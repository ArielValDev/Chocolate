import time
from uuid import UUID, uuid4
from constants.constants import GeneratorIDs
from constants.game import Gamemode, PlayerAction
from constants.network import ConnectionState
from models.db_manager import DBManager
from models.network.messages.entity_packets import OutgoingEntityPacket
from models.network.messages.game_loop_packet_handler import OutgoingGameLoopPacketHandler
from models.network.messages.game_loop_packet_handler import *
from models.network.messages.login_packets import *
from models.network.messages.player_packets import *
from models.network.tcp_connection import TCPConnection
from models.server_interface import ServerInterface
from models.encryption_manager import EncryptionManager
from models.types.position import EntityPosition, Position
from utils.id_generator import IDGenerator
from utils.logger import Logger
from utils.player import update_joined_player_others_exist, update_others_player_joined
from utils.protocol_type_utils import to_varint
from dataclasses import dataclass, field
import threading

@dataclass
class PlayerMetaData:
    awaiting_teleport_ids: list[int] = field(default_factory=list) # type: ignore
    awaiting_keep_alive_id: int | None = None
    loaded_chunks: list[Position] = field(default_factory=list) # type: ignore
    last_chunk: Position | None = None 
    global_chat_index: int = 0

@dataclass
class OfflineState:
    last_logout_position: Position
    last_health: float
    last_food: int

@dataclass
class PlayerGameState:
    offline_state: OfflineState

    gamemode: Gamemode
    current_position: EntityPosition
    current_slot: int
    render_distance: int
    health: float
    food: int
    is_dead: bool


class Player:
    def __init__(self, conn: TCPConnection, server_communicator: ServerInterface, game_state: PlayerGameState):
        self.conn = conn
        self.server_interface = server_communicator
        self.connection_state: ConnectionState = ConnectionState.Handshaking
        self.username: str = ""
        self.uuid: UUID = UUID(int = 0)
        self.eid = IDGenerator.get_id(GeneratorIDs.EntityID)
        self.meta_data: PlayerMetaData = PlayerMetaData()
        self.game_state = game_state # TODO should get the game mode from the server (the server gets the game mode from the config file)
        self.keep_alive_thread = None

    def connect_to_world(self):
        handle_login_packet_handshake(self.conn, self.connection_state)
        
        self.connection_state = ConnectionState.Login

        user_data = handle_login_packet_login(self.conn, self.connection_state)
        self.username = user_data.username
        self.uuid = user_data.uuid
        exists = DBManager.load_player_data(self)

        public_key = EncryptionManager.public_key_bytes
        verify_token = EncryptionManager.generate_verify_token()
        handle_login_packet_encryption_request(self.conn, public_key, verify_token, False)
        encryption_response = handle_login_packet_encryption_response(self.conn, self.connection_state)
        self.conn.enable_encryption(EncryptionManager.decrypt_shared_secret(encryption_response.shared_secret))

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
        handle_login_packet_login_play(self.conn, self.eid, False, 2, 10, 4, False, True, False, "minecraft:overworld", 1379429607, self.game_state.gamemode.value, -1, False, True, True, "minecraft:overworld", 0, 1, 63, False)

        tid = IDGenerator.get_id(GeneratorIDs.TeleportID)
        self.meta_data.awaiting_teleport_ids.append(tid)
        handle_player_packet_synchronize_player_position(self.conn, tid, self.game_state.current_position.x, self.game_state.current_position.y, self.game_state.current_position.z, 0, 0, 0, self.game_state.current_position.yaw, self.game_state.current_position.pitch, BitField())

        handle_player_packet_confirm_teleportation(self.conn, self.connection_state, self.meta_data.awaiting_teleport_ids)
        handle_player_packet_set_player_position_and_rotation(self.conn, self.connection_state)

        actions = BitField()
        actions.set(PlayerAction.AddPlayer.value)
        actions.set(PlayerAction.UpdateGameMode.value)
        actions.set(PlayerAction.UpdateListed.value)
        actions.set(PlayerAction.UpdateLatency.value)
        actions.set(PlayerAction.UpdateDisplayName.value)
        actions.set(PlayerAction.UpdateListPriority.value)
        actions.set(PlayerAction.UpdateHat.value)
        handle_player_packet_player_info_update(self.conn, actions, self.uuid, self.server_interface.get_all_players(), self.game_state.gamemode.value, True, 100, self.username, 1, True) # TODO get real ping of a player
        OutgoingEntityPacket.handle_packet_set_health(self, self.game_state.health, self.game_state.food)
        if not exists: DBManager.save_player(self)
    
    def load_world(self):
        center = Position(0, 0, 0)
        handle_player_packet_game_event(self.conn, game.GameEvent.StartWaitingForLevelChunks.value, 0)
        handle_player_packet_set_ticking_state(self.conn, 20.0, False)
        handle_player_packet_step_tick(self.conn, 0)
        # self.game_state.last_logout_position
        OutgoingGameLoopPacketHandler.set_center_chunk(self.conn, center)

        day_time = self.server_interface.get_day_time()
        world_age = self.server_interface.get_world_age()
        handle_player_packet_update_time(self.conn, world_age, day_time, True)

        OutgoingGameLoopPacketHandler.chunk_batch_start(self.conn)
        c=0
        for cx in range(-3, 4):  # -2, -1, 0, 1, 2
            for cz in range(-3, 4):
                c += 1
                chunk = Position(cx * 16, 0, cz * 16).to_chunk()
                self.meta_data.loaded_chunks.append(chunk)
                handle_player_packet_chunk_data_and_update_light(
                    self.conn,
                    chunk
                )
        OutgoingGameLoopPacketHandler.chunk_batch_finished(self.conn, c)

        # handle_player_packet_chunk_batch_received(self.conn, self.connection_state)

        # handle_player_packet_player_loaded(self.conn, self.connection_state)

    def _schedule_keep_alive(self):
        def _execute():
            keep_alive_id: int = IDGenerator.get_id(constants.GeneratorIDs.KeepAliveID)
            if self.meta_data.awaiting_keep_alive_id is not None : self.disconnect_player()
            self.meta_data.awaiting_keep_alive_id = keep_alive_id
            handle_player_packet_keep_alive_clientbound(self.conn, keep_alive_id)
            self._schedule_keep_alive()

        self.keep_alive_thread = threading.Timer(10, _execute)
        self.keep_alive_thread.start()

    def game_loop(self):
        running = True
        update_others_player_joined(self)
        update_joined_player_others_exist(self)
        self._schedule_keep_alive()
        while running:
            running = IncomingGameLoopPacketHandler.handle_in_game_packets(self)
        
    def disconnect_player(self):
        if self.keep_alive_thread:
            self.keep_alive_thread.cancel()
        Logger.info(f"Player {self.username} disconnected.")
        self.server_interface.remove_player(self)
        DBManager.save_player(self)
        try:
            self.conn.close_connection()
        except Exception:
            pass

    def __eq__(self, other: "Player") -> bool: # type: ignore
        return self.eid == other.eid and self.uuid == other.uuid

    def __hash__(self) -> int:
        return hash(self.eid)
        