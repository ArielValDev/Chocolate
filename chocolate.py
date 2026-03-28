import json
from constants import constants
from constants.game import Dimension, Gamemode
from models.config import ServerConfig
import socket
from models.events import event_subscriber
from models.player import OfflineState, Player, PlayerGameState
from models.network.tcp_connection import TCPConnection
from models.server_interface import ServerInterface
from models.types.position import EntityPosition, Position, PositionType
from utils.client_parser import get_tags_into_file
from utils.id_generator import IDGenerator
from utils.logger import Logger
from utils.network_utils import fetch_registries_into_file, fetch_version_client
import threading

class ChocolateServer:
    def __init__(self):
        self.config: ServerConfig = ServerConfig()
        self.players: list[Player] = []
        self.day_time: int = 24000
        self.world_age: int = 24000

        self.communicator = ServerInterface(
            get_all_players = lambda: self.players,
            get_day_time = lambda: self.day_time,
            get_world_age = lambda: self.world_age,
            get_config = lambda: self.config
        )
    
    def init(self):
        Logger.info("Fetching registries and tags...")
        fetch_version_client()
        fetch_registries_into_file()
        get_tags_into_file()

        Logger.info("Creating generators...")
        IDGenerator.add_generator(constants.GeneratorIDs.EntityID)
        IDGenerator.add_generator(constants.GeneratorIDs.TeleportID)
        IDGenerator.add_generator(constants.GeneratorIDs.KeepAliveID)
        event_subscriber.subscribe_events()

        Logger.info("Loading config...")
        if self.config.load_file(constants.CONFIG_FILE_PATH): return
        with open(constants.CONFIG_FILE_PATH, "w") as f:
            json.dump(self.config.get_json(), f)

    def handle_player(self, cli: socket.socket, addr: str, player: Player):
        player.connect_to_world()
        player.load_world()
        player.game_loop()

    def start(self):
        Logger.info(f"Starting server on port {self.config.port}...")
        serv = socket.socket()
        serv.bind(("127.0.0.1", self.config.port))
        serv.listen(5)

        while True:
            cli, addr = serv.accept()
            player = Player(TCPConnection(addr, cli), self.communicator, PlayerGameState(OfflineState(Position(8, 1, 8)), Gamemode.Survival, EntityPosition(8, 1, 8, 0, 0, True, False), 0, 2))
            self.players.append(player)
            threading.Thread(target=self.handle_player, args=(cli, addr, player)).start()
            
            
