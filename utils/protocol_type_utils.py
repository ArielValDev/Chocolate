from constants.constants import *

def to_varint(num: int) -> bytearray:
    number_min = -1 << 31   # -2147483648
    number_max = +1 << 31   #  2147483648
    if not (number_min <= num < number_max):
        raise ValueError(f"{num} does not fit in a 32-bit varint")
    
    if num < 0:
        num += 1 << 32
    
    bytes_ = bytearray()
    while True:
        b = num & 0x7F
        num >>= 7
        bytes_.append(b | (0x80 if num > 0 else 0))
        if num == 0:
            break
    
    return bytes_


def from_varint(bytearray_: bytearray) -> int:
    value = 0
    pos = 0
    while True:
        current_byte = bytearray_.pop(0)
        value |= (current_byte & VARINT_SEGMENT_BITS) << pos

        if (current_byte & VARINT_CONTINUE_BIT) == 0:
            break

        pos += 7
        if pos >= 32:
            raise RuntimeError("varint is too big")

    # convert back to signed 32-bit
    if value & (1 << 31):
        value -= 1 << 32

    return value