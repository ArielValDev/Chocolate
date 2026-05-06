import json
from constants import constants
from constants import game
from constants.game import Gamemode
from models.config import ServerConfig
import socket
from models.db_manager import DBManager
from models.events import event_subscriber
from models.events.event_manager import EventManager
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
        self.registry_data: dict[str, list[str]] = {}
        self.is_running: bool = False

        self.communicator = ServerInterface(
            get_all_players = lambda: self.players,
            get_day_time = lambda: self.day_time,
            get_world_age = lambda: self.world_age,
            get_config = lambda: self.config,
            get_registry_data = lambda: self.registry_data,
            remove_player = lambda player: self.players.remove(player)
        )
    
    def init(self):
        Logger.info("Fetching registries and tags...")
        fetch_version_client()
        fetch_registries_into_file()
        get_tags_into_file()

        Logger.info("Creating databases...")
        DBManager.init()

        with open(constants.REGISTRIES_FILE, 'r') as f:
            self.registry_data = json.load(f)

        Logger.info("Creating generators...")
        IDGenerator.add_generator(constants.GeneratorIDs.EntityID)
        IDGenerator.add_generator(constants.GeneratorIDs.TeleportID)
        IDGenerator.add_generator(constants.GeneratorIDs.KeepAliveID)
        event_subscriber.subscribe_events()

        Logger.info("Loading config...")
        if self.config.load_file(constants.CONFIG_FILE_PATH): return
        with open(constants.CONFIG_FILE_PATH, "w") as f:
            json.dump(self.config.get_json(), f)

    def handle_player(self, player: Player):
        try:
            player.connect_to_world()
            #EventManager.trigger(game.InGameEvent.PlayerConnected, player)
            Logger.info(f"{player.username} joined the world!")
            player.load_world()
        except:
            Logger.error("Failed to load player. Please try again...")
            player.disconnect_player()
            return
        player.game_loop()

    def start(self):
        Logger.info(f"Starting server on address {constants.IP}:{self.config.port}...")
        self.serv = socket.socket()
        self.serv.bind((constants.IP, self.config.port))
        self.serv.listen(5)

        self.is_running = True
        while self.is_running:
            try:
                cli, addr = self.serv.accept()
                if len(self.players) == self.config.max_players:
                    cli.close()
                    continue
                player = Player(TCPConnection(addr, cli), self.communicator, PlayerGameState(OfflineState(Position(8, 1, 8), 20, 20), Gamemode.Survival, EntityPosition(8, 1, 8, 0, 0, True, False), 0, self.config.render_distance, 20, 20, False))
                self.players.append(player)
                threading.Thread(target=self.handle_player, args=(player, )).start()
            except:
                pass

    def save_and_shutdown(self):
        for player in self.players:
            DBManager.save_player(player)
            EventManager.trigger(game.InGameEvent.ServerShutdown, player, "Server closed")

        Logger.info("Saving players before shutting down...")
        try:
            self.serv.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass 
        finally:
            self.serv.close()
        Logger.info("Server is closing...")