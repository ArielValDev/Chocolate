from enum import Enum
from copy import copy
import math
from constants.game import Dimension


class PositionType(Enum):
    Block = 0
    Chunk = 1
    Region = 2


class Position:
    def __init__(self, x: int, y: int, z: int, dimension: Dimension = Dimension.Overworld, type: PositionType = PositionType.Block):
        self.x = x
        self.y = y
        self.z = z
        self.dimension = dimension
        self.type = type

    def to_block(self) -> "Position":
        if self.type == PositionType.Block:
            return copy(self)

        elif self.type == PositionType.Chunk:
            return Position(
                self.x << 4,
                self.y,
                self.z << 4,
                self.dimension,
                PositionType.Block
            )

        else:
            return Position(
                self.x << 9,
                self.y,
                self.z << 9,
                self.dimension,
                PositionType.Block
            )

    def to_chunk(self) -> "Position":
        if self.type == PositionType.Chunk:
            return copy(self)

        elif self.type == PositionType.Block:
            return Position(
                self.x >> 4,
                0,
                self.z >> 4,
                self.dimension,
                PositionType.Chunk
            )

        else:
            return Position(
                self.x << 5,
                0,
                self.z << 5,
                self.dimension,
                PositionType.Chunk
            )

    def to_region(self) -> "Position":
        if self.type == PositionType.Region:
            return copy(self)

        elif self.type == PositionType.Chunk:
            return Position(
                self.x >> 5,
                0,
                self.z >> 5,
                self.dimension,
                PositionType.Region
            )

        else:
            return Position(
                self.x >> 9,
                0,
                self.z >> 9,
                self.dimension,
                PositionType.Region
            )

    def distance(self, other: "Position") -> float:
        a = self.to_block()
        b = other.to_block()

        return math.sqrt(
            (a.x - b.x) ** 2 +
            (a.y - b.y) ** 2 +
            (a.z - b.z) ** 2
        )

    def chunk_local(self) -> tuple[int, int, int]:
        """Block position inside chunk (0–15)."""
        block = self.to_block()

        return (
            block.x & 15,
            block.y,
            block.z & 15
        )

    def region_local(self) -> tuple[int, int]:
        """Chunk position inside region (0–31)."""
        chunk = self.to_chunk()

        return (
            chunk.x & 31,
            chunk.z & 31
        )

    def __repr__(self):
        return f"Position(x={self.x}, y={self.y}, z={self.z}, dim={self.dimension}, type={self.type.name})"