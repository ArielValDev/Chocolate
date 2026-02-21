from enum import Enum


class LogLevel(Enum):
    Verbose = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4

VERSION = "1.21.11"
ROOT = "server_files"
CONFIG_FILE_PATH = f"{ROOT}/config.json"
VARINT_SEGMENT_BITS = 0x7F
VARINT_CONTINUE_BIT = 0x80
LOG_LEVEL = LogLevel.Verbose
NULL = 0x00

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
MOJANG_PROFILE_API = "https://sessionserver.mojang.com/session/minecraft/profile/"
REGISTRIES_FILE = "constants/registry_data.json"