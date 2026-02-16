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