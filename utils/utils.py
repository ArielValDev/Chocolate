def float_to_angle(degrees: float) -> int:
    return int((degrees % 360) / 360 * 256) & 0xFF