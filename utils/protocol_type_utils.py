SEGMENT_BITS = 0x7F
CONTINUE_BIT = 0x80

def to_varint(num: int) -> bytearray:
    bytes_ = b""

    # emulate Java int (32-bit unsigned for >>>)
    num &= 0xFFFFFFFF

    while True:
        if (num & ~SEGMENT_BITS) == 0:
            bytes_ += num.to_bytes(1, byteorder="little")
            break

        bytes_ += ((num & SEGMENT_BITS) | CONTINUE_BIT).to_bytes(1, byteorder="little")

        num >>= 7

    return bytearray(bytes_)


def consume_varint(bytearay_: bytearray):
    value = 0
    pos = 0
    while True:
        currentByte = bytearay_.pop()
        value |= (currentByte & SEGMENT_BITS) << pos
        
        if (currentByte & CONTINUE_BIT) == 0: break
        
        pos += 7
        if(pos >= 32):
            raise RuntimeError("varint is too big")
    
    return value