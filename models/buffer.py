from utils.protocol_type_utils import *

class Buffer:
    def __init__(self, bytearray_: bytearray):
        self.bytearray_ = bytearray_
    
    def consume_raw(self, length: int) -> bytearray:
        bytearray_ = self.bytearray_[:length]
        self.bytearray_ = self.bytearray_[length:]
        return bytearray_
    
    def add_varint(self, num: int):
        self.bytearray_.extend(to_varint(num))
    
    def consume_varint(self) -> int:
        num = from_varint(self.bytearray_)
        return num
    
    def add_string(self, string: str):
        self.bytearray_.extend(to_varint(len(string)))
        self.bytearray_.extend(string.encode("UTF-8"))
        
    def consume_string(self) -> str:
        length = self.consume_varint()
        return self.consume_raw(length).decode("UTF-8")
    
    def add_unsigned_short(self, unsigned_short: int):
        if unsigned_short > 2**16 or unsigned_short < 0:
            raise ValueError("unsigned short must be within 0-65535")
        
        self.bytearray_.extend(unsigned_short.to_bytes(2))
        
        # TODO consume unsigned short
    
        
        