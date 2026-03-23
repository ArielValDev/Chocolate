from uuid import UUID
import constants
import constants.constants
from models.types.mc_types import OptionalString
from utils.logger import Logger
from utils.protocol_type_utils import *
from uuid import UUID
from amulet_nbt import StringTag
from nbt import nbt
from io import BytesIO
import struct


class Buffer:
    def __init__(self, bytearray_: bytearray | None = None):
        if bytearray_ is None: bytearray_ = bytearray()
        self.bytearray_ = bytearray_
    
    def add_buffer(self, buffer: "Buffer"):
        self.bytearray_.extend(buffer.bytearray_)

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
    
    def add_boolean(self, boolian: bool):
        self.bytearray_.extend([0x01 if boolian else 0x00])

    def consume_boolean(self) -> bool:
        return True if int.from_bytes(self.consume_raw(1)) == 1 else False
    
    def add_string(self, string: str, max_size: int = -1):
        if max_size != -1 and len(string) > max_size: raise Exception("Length of string exceeds the maximum length")
        self.bytearray_.extend(to_varint(len(string)))
        self.bytearray_.extend(string.encode("UTF-8"))
        
    def consume_string(self) -> str:
        length = self.consume_varint()
        return self.consume_raw(length).decode("UTF-8")
    
    def add_short(self, short: int):
        if short > (2**15 - 1) or short < (-1 * 2**15):
            raise ValueError("Short must be within -32768 - 32767")
        
        self.bytearray_.extend(short.to_bytes(2, signed=True))
    
    def add_unsigned_short(self, unsigned_short: int):
        if unsigned_short > 2**15 or unsigned_short < 0:
            raise ValueError("unsigned short must be within 0-65535")
        
        self.bytearray_.extend(unsigned_short.to_bytes(2))
    
    def consume_unsigned_short(self) -> int:
        short = self.consume_raw(2)
        return int.from_bytes(short)
    
    def add_long(self, long: int):
        self.bytearray_.extend(long.to_bytes(8, signed=True))
    
    def consume_long(self) -> int:
        long = self.consume_raw(8)
        return int.from_bytes(long, signed=True)
    
    def add_unsigned_byte(self, byte: int):
        self.bytearray_.extend(byte.to_bytes(1))

    def consume_unsigned_byte(self) -> int:
        byte = self.consume_raw(1)
        return int.from_bytes(byte)
    
    def add_byte(self, byte: int):
        self.bytearray_.extend(byte.to_bytes(1, signed=True))

    def consume_byte(self) -> int:
        byte = self.consume_raw(1)
        return int.from_bytes(byte, signed=True)
    
    def add_int(self, integer: int):
        self.bytearray_.extend(integer.to_bytes(4, signed = True))

    def consume_int(self) -> int:
        integer = self.consume_raw(4)
        return int.from_bytes(integer, signed = True)

    def add_float(self, value: float):
        self.bytearray_.extend(struct.pack('>f', value))

    def consume_float(self) -> float:
        raw = self.consume_raw(4)
        return struct.unpack('>f', raw)[0]

    def add_double(self, value: float):
        self.bytearray_.extend(struct.pack('>d', value))

    def consume_double(self) -> float:
        raw = self.consume_raw(8)
        return struct.unpack('>d', raw)[0]

    def add_uuid(self, uuid: UUID):
        self.bytearray_.extend(uuid.bytes)

    def consume_uuid(self) -> UUID:
        uuid = self.bytearray_[:16]
        self.bytearray_ = self.bytearray_[16:]
        return UUID(uuid.hex())
    
    def add_prefixed_string_tag_array(self, array_: list[tuple[str, "Buffer"]]):
        length = len(array_)

        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            if isinstance(var, str):
                self.add_string(var)
            else: 
                self.add_raw(var.bytearray_)

    def add_prefixed_tag_array(self, array_: list[tuple[str, list[int]]]):
        length = len(array_)

        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            if isinstance(var, str):
                self.add_string(var)
            else:
                self.add_prefixed_varint_array([(i, ) for i in var])

    def consume_prefixed_tag_array(self):
        raise NotImplemented()

    def add_prefixed_varint_array(self, array_: list[tuple[int, ...]]):
        length = len(array_)

        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            self.add_varint(var)

    def consume_prefixed_varint_array(self, non_flat_length: int = -1) -> list[int]:
        flat_length = self.consume_varint()
        if non_flat_length != -1:
            flat_length = -1
        to_return: list[int] = []

        while non_flat_length != 0 and flat_length != 0:
            curr = self.consume_varint()
            to_return.append(curr)
            curr_len = len(to_varint(curr))
            non_flat_length -= 1
            flat_length -= curr_len
        
        return to_return

    def add_prefixed_string_array(self, array_: list[tuple[str | OptionalString, ...]]):
        length = len(array_)
        
        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            if isinstance(var, OptionalString):
                self.add_prefixed_optional_string(var.s)
            else:
                self.add_string(var)

    def consume_prefixed_string_array(self, non_flat_length: int = -1) -> list[str]:

        flat_length = self.consume_varint()
        if non_flat_length != -1:
            flat_length = -1
        to_return: list[str] = []

        while non_flat_length != 0 and flat_length != 0:
            if self.bytearray_[0] == NULL or self.bytearray_[0] == 0x01:
                curr = self.consume_prefixed_optional_string()
            else:
                curr = self.consume_string()
            if curr is None: continue
            to_return.append(curr)
            curr_len = len(curr)
            non_flat_length -= 1
            flat_length -= (curr_len + len(to_varint(curr_len))) # TODO: Find better solution
        
        return to_return

    def add_game_profile(self, uuid: UUID, username: str, properties: list[tuple[str, str, OptionalString]]):
        self.add_uuid(uuid)
        self.add_string(username)        
        self.add_prefixed_string_array(properties)

    def consume_game_profile(self):
        uuid = self.consume_uuid()
        username = self.consume_string()
        properties = self.consume_prefixed_string_array()
        return uuid, username, properties
    
    def add_optional_string(self, string: str | None):
        if string is None: return
        self.add_string(string)

    def consume_optional_string(self) -> str:
        return self.consume_string()
        
    def add_prefixed_optional_string(self, string: str | None):
        if string is None:
            self.add_boolean(False)
            return
        
        self.add_boolean(True)
        self.add_string(string)
        
    def consume_prefixed_optional_string(self) -> str | None:
        exists = self.consume_boolean()
        if exists:
            return self.consume_string()
        
    def add_text_component(self, text: str):
        nbt = StringTag(text)
        nbt_bytes = nbt.to_nbt(compressed=False)
        self.bytearray_.extend(nbt_bytes)

    def consume_text_component(self) -> str:
        tag_id = self.consume_raw(1)[0]

        if tag_id != 8:
            raise Exception(f"Expected TAG_String (8), got {tag_id}")

        name_length = int.from_bytes(self.consume_raw(2))
        if name_length > 0:
            self.consume_raw(name_length)

        string_length = int.from_bytes(self.consume_raw(2))
        return self.consume_raw(string_length).decode("utf-8")

    def add_prefixed_optional_text_component(self, text: str | None):
        if text is None:
            self.add_boolean(False)
            return
        
        self.add_boolean(True)
        self.add_text_component(text)

    def consume_prefixed_optional_text_component(self) -> str | None:
        exists = self.consume_boolean()
        if exists:
            return self.consume_text_component()
        
    def add_prefixed_uuid_player_actions_array(self, array_: list[tuple[UUID, "Buffer"]]):
        length = len(array_)
        
        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            if isinstance(var, UUID):
                self.add_uuid(var)
            else:
                self.add_buffer(var)
            
    def add_prefixed_byte_array(self, array_: list[tuple[int]]):
        length = len(array_)
        
        self.add_varint(length)
        for var in [prop for t in array_ for prop in t]: # flattening the tuples in array
            self.add_byte(var)

    def consume_prefixed_byte_array(self, non_flat_length: int = -1) -> list[int]:

        flat_length = self.consume_varint()
        if non_flat_length != -1:
            flat_length = -1
        to_return: list[int] = []

        while non_flat_length != 0 and flat_length != 0:
            curr = self.consume_byte()
            to_return.append(curr)
            non_flat_length -= 1
            flat_length -= 1

        return to_return