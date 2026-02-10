from uuid import UUID
from utils.protocol_type_utils import *
from uuid import UUID

class Buffer:
    def __init__(self, bytearray_: bytearray = bytearray()):
        self.bytearray_ = bytearray_
    
    def get_bytes(self) -> bytes:
        return bytes(self.bytearray_)
    
    def consume_raw(self, length: int) -> bytearray:
        bytearray_ = self.bytearray_[:length]
        self.bytearray_ = self.bytearray_[length:]
        return bytearray_
    
    def add_raw(self, bytearray_: bytearray):
        self.bytearray_.extend(bytearray_)
    
    def add_varint(self, num: int):
        self.bytearray_.extend(to_varint(num))
    
    def consume_varint(self) -> int:
        num = from_varint(self.bytearray_)
        return num
    
    def add_string(self, string: str, max_size: int = -1):
        if max_size != -1 and len(string) > max_size: raise Exception("Length of string exceeds the maximum length")
        self.bytearray_.extend(to_varint(len(string)))
        self.bytearray_.extend(string.encode("UTF-8"))
        
    def consume_string(self) -> str:
        length = self.consume_varint()
        return self.consume_raw(length).decode("UTF-8")
    
    def add_unsigned_short(self, unsigned_short: int):
        if unsigned_short > 2**16 or unsigned_short < 0:
            raise ValueError("unsigned short must be within 0-65535")
        
        self.bytearray_.extend(unsigned_short.to_bytes(2))
    
    def consume_unsigned_short(self) -> int:
        short = self.consume_raw(2)
        return int.from_bytes(short)
    
    def add_uuid(self, uuid: UUID):
        self.bytearray_.extend(uuid.bytes)

    def consume_uuid(self) -> UUID:
        uuid = self.bytearray_[:16]
        self.bytearray_ = self.bytearray_[16:]
        return UUID(uuid.hex())
    
    def add_prefixed_string_array(self, array_: list[str]):
        length = 0
        for var in array_:
            length += len(to_varint(len(var)))
            length += len(var)
        
        self.add_varint(length)
        for var in array_:
            self.add_string(var)

    def consume_prefixed_string_array(self) -> list[str]:
        length = self.consume_varint()
        to_return: list[str] = []

        while length != 0:
            curr = self.consume_string()
            to_return.append(curr)
            curr_len = len(curr)
            length -= (curr_len + len(to_varint(curr_len))) # TODO: Find better solution
        
        return to_return

    def add_game_profile(self, uuid: UUID, username: str, properties: list[tuple[str, str]]):
        self.add_uuid(uuid)
        self.add_string(username)
        self.add_prefixed_string_array([*[p[0], p[1], None] for p in properties])

    def consume_game_profile(self):
        uuid = self.consume_uuid()
        username = self.consume_string()
        properties = self.consume_prefixed_string_array()
        return uuid, username, properties
    
    def add_optional_string(self, string: str | None):
        if string is None:
            self.add_raw(bytearray([0]))
            return
            
        self.add_raw(bytearray([1]))
        self.add_string(string)
        
    def add_prefixed_optional_string(self, string: str | None):
        if string is None:
            self.add_raw(bytearray([1,0]))
            return
        
        self.add_raw(bytearray([1 + len(to_varint(len(string)))]))
        self.add_string(string)