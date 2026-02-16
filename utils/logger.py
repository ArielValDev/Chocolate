from constants.constants import LOG_LEVEL

class Logger:

    VERBOSE_PREFIX = "\x1b[90m[=]"
    DEBUG_PREFIX = "\x1b[90m[-]"
    INFO_PREFIX  = "\x1b[36m[*]\x1b[97m"
    WARN_PREFIX  = "\x1b[33m[!]"
    ERROR_PREFIX = "\x1b[41;97m[ERROR]"
    RESET = "\x1b[0m"

    @staticmethod
    def verbose(message: str) -> None:
        if LOG_LEVEL.value > 0: return
        print(f"{Logger.VERBOSE_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def debug(message: str) -> None:
        if LOG_LEVEL.value > 1: return
        print(f"{Logger.DEBUG_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def info(message: str) -> None:
        if LOG_LEVEL.value > 2: return
        print(f"{Logger.INFO_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def warn(message: str) -> None:
        if LOG_LEVEL.value > 3: return
        print(f"{Logger.WARN_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def error(message: str) -> None:
        if LOG_LEVEL.value > 4: return
        print(f"{Logger.ERROR_PREFIX} {message}{Logger.RESET}")