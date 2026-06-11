import math
from constants.game import BLOCK_KIND
from models.buffer import Buffer
from models.types.mc_types import BitField
from models.types.position import Position

class Section:
    def __init__(self, block_mask: BitField | None = None):
        self.block_mask: BitField = block_mask if block_mask else BitField()

    @staticmethod
    def get_empty_section_buf() -> Buffer:
        section = Buffer()

        block_kinds_num = 2
        bpe = max(math.ceil(math.log2(block_kinds_num + 1)), 4)

        section.add_short(0)

        # Block states
        section.add_unsigned_byte(bpe)
        section.add_varint(2)  # palette length
        section.add_varint(0)  # air
        section.add_varint(BLOCK_KIND)  # very green grass

        # 4096 entries / 16 entries per long = 256 longs
        for _ in range(256):
            section.add_long(0)

        # Biomes
        section.add_unsigned_byte(0)
        section.add_varint(1)

        return section
        
    def set_block(self, rel_pos: Position):
        index = rel_pos.to_index()
        self.block_mask.set_index(index)

    def clear_block(self, rel_pos: Position):
        index = rel_pos.to_index()
        self.block_mask.clear_index(index)

    def to_buf(self, block_id: int) -> Buffer:
        section = Buffer()
        if self.block_mask.is_empty():
            return Section.get_empty_section_buf()
        block_count = 0

        longs: list[int] = []
        curr_long = 0

        block_kinds_num = 2
        bpe = max(math.ceil(math.log2(block_kinds_num + 1)), 4)
        entry_mask = (1 << bpe) - 1
        entries_per_long = 64 // bpe

        entry_index = 0
        for y in range(0, 16):
            for z in range(0, 16):
                for x in range(0, 16):
                    index = (y << 8) | (z << 4) | x
                    block = 1 if self.block_mask.check_index(index) else 0
                    block_count += block
                    bit_index = entry_index % entries_per_long * bpe
                    entry_index += 1

                    curr_long &= ~(entry_mask << bit_index)
                    curr_long |= block << bit_index
                    if bit_index + bpe >= 64:
                        longs.append(curr_long)
                        curr_long = 0
        section.add_short(block_count)

        section.add_unsigned_byte(bpe)
        section.add_varint(2) # Array length
        section.add_varint(0) # Air
        section.add_varint(block_id)

        for long in longs:
            section.add_long(long)
        
        section.add_unsigned_byte(0)    # bpe = 0 -> single value
        section.add_varint(1)           # plains = 0
        return section

    def to_raw(self) -> bytes:
        return self.block_mask.to_bytes(4096 // 8)