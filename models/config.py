import json
import os
from typing import Any

class ServerConfig:

    def __init__(self):
        self.port = 25565

    def load_file(self, path: str) -> bool:
        if not os.path.isfile(path): return False

        with open(path, "r") as f:
            try:
                config_dict = json.load(f)
            except json.JSONDecodeError as _:
                return False

        self.port = config_dict.get("port", self.port)

        return True

    def get_json(self) -> dict[str, Any]:
        return {
            "port": self.port
        }