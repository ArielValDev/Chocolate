import json
from constants import constants
from models.config import ServerConfig
import socket
from models.player import Player
from models.network.tcp_connection import TCPConnection
from models.server_communicator import ServerCommunicator
from utils.client_parser import get_tags_into_file
from utils.id_generator import IDGenerator
from utils.logger import Logger
from utils.network_utils import fetch_registries_into_file, fetch_version_client

class ChocolateServer:
    def __init__(self):
        self.config: ServerConfig = ServerConfig()
        self.players: list[Player] = []

        self.communicator = ServerCommunicator(
            get_all_players = lambda: self.players
        )
    
    def init(self):
        Logger.info("Fetching registries and tags...")
        fetch_version_client()
        fetch_registries_into_file()
        get_tags_into_file()

        Logger.info("Creating generators...")
        IDGenerator.add_generator(constants.GeneratorIDs.EntityID)
        IDGenerator.add_generator(constants.GeneratorIDs.TeleportID)

        Logger.info("Loading config...")
        if self.config.load_file(constants.CONFIG_FILE_PATH): return
        with open(constants.CONFIG_FILE_PATH, "w") as f:
            json.dump(self.config.get_json(), f)

    def start(self):
        Logger.info(f"Starting server on port {self.config.port}...")
        serv = socket.socket()
        serv.bind(("127.0.0.1", self.config.port))
        serv.listen(5)

        while True:
            cli, addr = serv.accept()
            player = Player(TCPConnection(addr, cli), self.communicator)
            self.players.append(player)
            player.connect_to_world()
