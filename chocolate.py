import json
from constants import constants
from models.config import ServerConfig
import socket
from models.player import Player
from models.network.tcp_connection import TCPConnection
from utils.client_parser import get_tags_into_file
from utils.logger import Logger
from utils.network_utils import fetch_registries_into_file, fetch_version_client

class EntityIDGenerator:
    def __init__(self):
        self.current = 0

    def next(self):
        eid = self.current
        self.current += 1
        return eid

class ChocolateServer:

    def __init__(self):
        self.config: ServerConfig = ServerConfig()
        
    
    def init(self):
        fetch_version_client()
        fetch_registries_into_file()
        get_tags_into_file()
        if self.config.load_file(constants.CONFIG_FILE_PATH): return
        with open(constants.CONFIG_FILE_PATH, "w") as f:
            json.dump(self.config.get_json(), f)

    def start(self):
        Logger.info(f"Starting server on port {self.config.port}...")
        serv = socket.socket()
        serv.bind(("127.0.0.1", self.config.port))
        serv.listen(5)

        eid_gen = EntityIDGenerator()
        while True:
            cli, addr = serv.accept()
            player = Player(TCPConnection(addr, cli), eid_gen.next())
            player.connect_to_world()
