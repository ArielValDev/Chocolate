import math
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.buffer import Buffer


MAX_QUANTIZED_VALUE = 32766.0
LPVEC3_ZERO_THRESHOLD = 1.0 / MAX_QUANTIZED_VALUE
LPVEC3_ABS_LIMIT = 1.7179869183e10


def _clamp(value: float, lo: float, hi: float) -> float:
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def _sanitize_lpvec3_component(value: float) -> float:
    if math.isnan(value):
        return 0.0
    if math.isinf(value):
        return math.copysign(LPVEC3_ABS_LIMIT, value)
    return _clamp(value, -LPVEC3_ABS_LIMIT, LPVEC3_ABS_LIMIT)


def _java_round_non_negative(value: float) -> int:
    return int(math.floor(value + 0.5))


def _pack_normalized_component(value: float) -> int:
    value = _clamp(value, -1.0, 1.0)
    return _java_round_non_negative((value * 0.5 + 0.5) * MAX_QUANTIZED_VALUE)


def _unpack_normalized_component(value: int) -> float:
    return min(value & 0x7FFF, int(MAX_QUANTIZED_VALUE)) * 2.0 / MAX_QUANTIZED_VALUE - 1.0


def read_lpvec3(buffer: "Buffer") -> tuple[float, float, float]:
    byte1 = buffer.consume_unsigned_byte()
    if byte1 == 0:
        return 0.0, 0.0, 0.0

    byte2 = buffer.consume_unsigned_byte()
    bytes3_to_6 = int.from_bytes(buffer.consume_raw(4), byteorder="big", signed=False)

    packed = (bytes3_to_6 << 16) | (byte2 << 8) | byte1

    scale_factor = byte1 & 0x03
    if byte1 & 0x04:
        scale_factor |= (buffer.consume_varint() & 0xFFFFFFFF) << 2

    scale_factor_f = float(scale_factor)

    x = _unpack_normalized_component(packed >> 3) * scale_factor_f
    y = _unpack_normalized_component(packed >> 18) * scale_factor_f
    z = _unpack_normalized_component(packed >> 33) * scale_factor_f

    return x, y, z


def write_lpvec3(buffer: "Buffer", vec3: tuple[float, float, float]) -> None:
    x = _sanitize_lpvec3_component(vec3[0])
    y = _sanitize_lpvec3_component(vec3[1])
    z = _sanitize_lpvec3_component(vec3[2])

    max_coordinate = max(abs(x), abs(y), abs(z))

    if max_coordinate < LPVEC3_ZERO_THRESHOLD:
        buffer.add_unsigned_byte(0)
        return

    max_coordinate_i = int(max_coordinate)
    scale_factor = max_coordinate_i + (1 if max_coordinate > float(max_coordinate_i) else 0)

    need_continuation = (scale_factor & 0x03) != scale_factor
    packed_scale = ((scale_factor & 0x03) | 0x04) if need_continuation else scale_factor

    packed_x = _pack_normalized_component(x / float(scale_factor)) << 3
    packed_y = _pack_normalized_component(y / float(scale_factor)) << 18
    packed_z = _pack_normalized_component(z / float(scale_factor)) << 33

    packed = packed_z | packed_y | packed_x | packed_scale

    buffer.add_unsigned_byte(packed & 0xFF)
    buffer.add_unsigned_byte((packed >> 8) & 0xFF)
    buffer.add_raw(bytearray(((packed >> 16) & 0xFFFFFFFF).to_bytes(4, byteorder="big", signed=False)))

    if need_continuation:
        buffer.add_varint(scale_factor >> 2)