from constants.constants import LOG_LEVEL
import queue

class Logger:
    gui_queue: queue.Queue[str] = queue.Queue()
    VERBOSE_PREFIX = "\x1b[90m[=]"
    DEBUG_PREFIX = "\x1b[90m[-]"
    INFO_PREFIX  = "\x1b[36m[*]\x1b[97m"
    WARN_PREFIX  = "\x1b[33m[!]"
    ERROR_PREFIX = "\x1b[41;97m[ERROR]"
    RESET = "\x1b[0m"

    @staticmethod
    def get_time() -> str:
        from datetime import datetime
        return "\x1b[90m<" + datetime.now().strftime("%H:%M:%S") + ">"

    @staticmethod
    def verbose(message: str) -> None:
        if LOG_LEVEL.value > 0: return
        print(f"{Logger.get_time()} {Logger.VERBOSE_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def debug(message: str) -> None:
        if LOG_LEVEL.value > 1: return
        print(f"{Logger.get_time()} {Logger.DEBUG_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def info(message: str) -> None:
        if LOG_LEVEL.value > 2: return
        print(f"{Logger.get_time()} {Logger.INFO_PREFIX} {message}{Logger.RESET}")
        Logger.gui_queue.put(f"SYS:[*] {message}")

    @staticmethod
    def warn(message: str) -> None:
        if LOG_LEVEL.value > 3: return
        print(f"{Logger.get_time()} {Logger.WARN_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def error(message: str) -> None:
        if LOG_LEVEL.value > 4: return
        print(f"{Logger.get_time()} {Logger.ERROR_PREFIX} {message}{Logger.RESET}")

    @staticmethod
    def chat(sender: str, message: str):
        Logger.gui_queue.put(f"{Logger.get_time()} CHAT:{sender}:{message}")
