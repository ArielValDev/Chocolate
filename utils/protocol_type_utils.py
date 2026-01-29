from constants.constants import *

def to_varint(num: int) -> bytearray:
    bytes_ = b""

    # emulate Java int (32-bit unsigned for >>>)
    num &= 0xFFFFFFFF

    while True:
        if (num & ~VARINT_SEGMENT_BITS) == 0:
            bytes_ += num.to_bytes(1, byteorder="little")
            break

        bytes_ += ((num & VARINT_SEGMENT_BITS) | VARINT_CONTINUE_BIT).to_bytes(1, byteorder="little")

        num >>= 7

    return bytearray(bytes_)


def from_varint(bytearay_: bytearray):
    value = 0
    pos = 0
    while True:
        current_byte = bytearay_.pop()
        value |= (current_byte & VARINT_SEGMENT_BITS) << pos
        
        if (current_byte & VARINT_CONTINUE_BIT) == 0: break
        
        pos += 7
        if(pos >= 32):
            raise RuntimeError("varint is too big")
    
    return value