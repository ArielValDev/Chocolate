from enum import Enum


class LogLevel(Enum):
    Verbose = 0
    Debug = 1
    Info = 2
    Warning = 3
    Error = 4

ROOT = "server_files"
CONFIG_FILE_PATH = f"{ROOT}/config.json"
VARINT_SEGMENT_BITS = 0x7F
VARINT_CONTINUE_BIT = 0x80
LOG_LEVEL = LogLevel.Verbose
NULL = 0x00

MOJANG_PROFILE_API = "https://sessionserver.mojang.com/session/minecraft/profile/"
REGISTRIES_URL = "https://gist.githubusercontent.com/Mansitoh/e6c5cf8bbf17e9faf4e4e75bb3f4789d/raw/43429d47aca38ed439569b2696d4236d3818746f/registry_data.json"