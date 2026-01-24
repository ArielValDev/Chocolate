import json
from constants import constants
from models.config import ServerConfig

class ChocolateServer:

    def __init__(self):
        self.config: ServerConfig = ServerConfig()
    
    def init(self):
        if self.config.load_file(constants.CONFIG_FILE_PATH): return
        with open(constants.CONFIG_FILE_PATH, "w") as f:
            json.dump(self.config.get_json(), f)

    def start(self):
        pass
