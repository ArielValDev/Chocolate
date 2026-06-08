from models.buffer import Buffer
from models.types.mc_types import BitField
from models.types.position import Position
from models.world.section import Section


class Chunk:
    MIN_SECTION_Y = -4

    def __init__(self, position: Position, sections: dict[int, Section] | None = None):
        self.sections: dict[int, Section] = sections if sections else {}
        self.position: Position = position.to_chunk()

    def _get_section(self, y: int) -> Section:
        if y in self.sections:
            return self.sections[y]
        s = Section()
        self.sections[y] = s
        return s

    def set_block(self, rel_pos: Position):
        sec_index = rel_pos.y // 16
        rel_pos.y = rel_pos.y % 16
        self._get_section(sec_index).set_block(rel_pos)

    def clear_block(self, rel_pos: Position):
        sec_index = rel_pos.y // 16
        rel_pos.y = rel_pos.y % 16
        self._get_section(sec_index).clear_block(rel_pos)

    def to_buf(self, block_id: int) -> Buffer:
        chunk_and_light_data = Buffer()
        chunk_and_light_data.add_int(self.position.x)
        chunk_and_light_data.add_int(self.position.z)

        # Data:
            # Heightmaps:
        chunk_and_light_data.add_raw(bytearray([0]))
            # Data:
        data = Buffer()
        for sec_y in range(-4, 20):
            if sec_y in self.sections:
                data.add_buffer(self.sections[sec_y].to_buf(block_id))
            else:
                data.add_buffer(Section.get_empty_section_buf())
        
        chunk_and_light_data.add_varint(len(data.bytearray_)) # PREFIXED DATA - always 24 sections
        chunk_and_light_data.add_buffer(data)
            # Block entities:
        chunk_and_light_data.add_varint(0)

        # Light Data:
        all_sections_mask = (1 << 26) - 1  # bits 0-25 all set

        chunk_and_light_data.add_varint(1)           # 1 long in bitset
        chunk_and_light_data.add_long(all_sections_mask)

        # Block Light Mask — no block light
        chunk_and_light_data.add_varint(1)
        chunk_and_light_data.add_long(0)

        chunk_and_light_data.add_varint(1)
        chunk_and_light_data.add_long(0)

        chunk_and_light_data.add_varint(1)
        chunk_and_light_data.add_long(all_sections_mask)

        chunk_and_light_data.add_varint(26)
        for _ in range(26):
            chunk_and_light_data.add_varint(2048)    # array length
            for _ in range(2048):
                chunk_and_light_data.add_unsigned_byte(0xFF)

        # Block Light Arrays — 0 arrays
        chunk_and_light_data.add_varint(0)

        return chunk_and_light_data

    @staticmethod
    def from_raw(pos: Position, raw_chunk: bytes) -> "Chunk":
        curr = 0
        sec_y = Chunk.MIN_SECTION_Y
        sections: dict[int, Section] = {}
        while curr < len(raw_chunk):
            curr += 1 
            if raw_chunk[curr - 1] == 0:
                sec_y += 1
                continue

            field = BitField()
            field.set(int.from_bytes(raw_chunk[curr: curr + 4096 // 8]))
            curr += 4096 // 8
            s = Section(field)
            sections[sec_y] = s
            sec_y += 1
        
        return Chunk(pos, sections)

    def to_raw(self) -> bytes:
        raw = bytearray()
        for sec_y in range(Chunk.MIN_SECTION_Y, 20):
            if sec_y in self.sections:
                raw += bytearray([1])
                raw += self.sections[sec_y].to_raw()
            else:
                raw += bytearray([0])
        return len(raw).to_bytes(4) + bytes(raw)
