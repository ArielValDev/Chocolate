from enum import Enum

class GeneratorIDs(Enum):
    EntityID = 0
    TeleportID = 1
    KeepAliveID = 2

class LogLevel(Enum):
    Verbose = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4

IP = "0.0.0.0"
VERSION = "1.21.11"
ROOT = "server_files"
CONFIG_FILE_PATH = f"{ROOT}/config.json"
DB_FILE = f"{ROOT}/players.db"
VARINT_SEGMENT_BITS = 0x7F
VARINT_CONTINUE_BIT = 0x80
LOG_LEVEL = LogLevel.Verbose
NULL = 0x00
ENCRYPTING = True

SAVE_INTERVAL = 60 * 2

KNOWN_PACKS = [("minecraft", "core", "1.21.11")]

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
MOJANG_PROFILE_API = "https://sessionserver.mojang.com/session/minecraft/profile/"
REGISTRIES_FILE = "constants/registry_data.json"
TAGS_FILE = "constants/tags_data.json"
