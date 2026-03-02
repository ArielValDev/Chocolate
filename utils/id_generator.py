from threading import Lock
from constants.constants import GeneratorIDs

class IDGenerator:
    ids: dict[GeneratorIDs, int] = {}
    _lock = Lock()

    @staticmethod
    def add_generator(gid: GeneratorIDs):
        IDGenerator.ids[gid] = -1

    @staticmethod
    def get_id(gid: GeneratorIDs) -> int:
        with IDGenerator._lock:
            IDGenerator.ids[gid] += 1
            return IDGenerator.ids[gid]