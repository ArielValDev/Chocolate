import json
import os
from typing import Any
from utils.logger import Logger

class ServerConfig:

    def __init__(self):
        self.port = 25565
        self.render_distance = 12
        self.max_players = 5

    def load_file(self, path: str) -> bool:
        if not os.path.isfile(path): return False

        with open(path, "r") as f:
            try:
                config_dict = json.load(f)
            except json.JSONDecodeError as _:
                return False

        self.port = config_dict.get("port", self.port)
        self.render_distance = config_dict.get("render_distance", self.render_distance)
        self.max_players = config_dict.get("max_players", self.max_players)

        return True

    def change_config(self, path: str, key: str, value: int):
        if hasattr(self, key):
            setattr(self, key, value)
            
            try:
                with open(path, "w") as f:
                    json.dump(self.get_json(), f)
            except Exception as e:
                Logger.error(f"Error saving config: {e}")

    def get_json(self) -> dict[str, Any]:
        return {
            "port": self.port,
            "render_distance": self.render_distance,
            "max_players": self.max_players
        }