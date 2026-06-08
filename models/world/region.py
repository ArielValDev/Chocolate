from dataclasses import dataclass
import io
from pathlib import Path
from models.types.position import Position, PositionType
from models.world.chunk import Chunk
import gzip

@dataclass
class Region:
    chunks: dict[tuple[int, int], Chunk]
    position: Position

    @staticmethod
    def load_file(path: str) -> "Region":
        name = Path(path).name
        region_x = int(name.split(".")[1])
        region_z = int(name.split(".")[2])

        r = Region({}, Position(region_x, 0, region_z, type=PositionType.Region))

        with gzip.open(path, "rb") as f:
            header = f.read(4 * 32 * 32)

            for hind in range(0, len(header), 4):
                chunk_offset = int.from_bytes(header[hind:hind + 4], "big")
                if chunk_offset == 0:
                    continue

                f.seek(chunk_offset)
                size = int.from_bytes(f.read(4), "big")
                chunk_data = f.read(size)

                local_x = (hind // 4) % 32
                local_z = (hind // 4) // 32

                abs_chunk_x = region_x * 32 + local_x
                abs_chunk_z = region_z * 32 + local_z

                r.chunks[(local_x, local_z)] = Chunk.from_raw(
                    Position(abs_chunk_x, 0, abs_chunk_z, type=PositionType.Chunk),
                    chunk_data
                )

        return r

    def save_file(self, path: str):
        header = bytearray(4 * 32 * 32)
        non_airs = 0

        buffer = io.BytesIO()

        buffer.seek(len(header))
        chunks = sorted(
            self.chunks.items(),
            key=lambda item: (item[0][1], item[0][0])
        )

        for (local_x, local_z), chunk in chunks:
            for section in chunk.sections.values():
                for i in range(16 * 16 * 16):
                    if section.block_mask.check_index(i):
                        non_airs += 1

            offset = buffer.tell()
            header_index = (local_z * 32 + local_x) * 4
            header[header_index:header_index + 4] = offset.to_bytes(4, "big")

            buffer.write(chunk.to_raw())

            buffer.seek(0)
            buffer.write(header)

        with gzip.open(path, "wb") as f:
            f.write(buffer.getvalue())

        print(f"Saved region ({self.position.x}, {self.position.z}) with {non_airs} non-air blocks")

            


