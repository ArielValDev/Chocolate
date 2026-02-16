import json
from constants import constants
from models.config import ServerConfig
import socket
from models.player import Player
from models.network.tcp_connection import TCPConnection
from utils.logger import Logger


class ChocolateServer:

    def __init__(self):
        self.config: ServerConfig = ServerConfig()
        
    
    def init(self):
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
            player = Player(TCPConnection(addr, cli))
            player.connect_to_world()
