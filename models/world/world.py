import random
import threading
from typing import TYPE_CHECKING
from constants import constants
if TYPE_CHECKING:
    from models.server_interface import ServerInterface
from pathlib import Path
from constants.game import WorldEvent
from models.events.event_manager import EventManager
from models.types.position import Position, PositionType
from models.world.chunk import Chunk
from models.world.region import Region
import os
from perlin_noise import PerlinNoise # type: ignore

class World:
    TERRAIN_SCALE = 200
    TYPE_SCALE = 300

    def __init__(self, path: Path, server_interface: "ServerInterface", seed: int = random.randint(0, 1000000)):
        self.loaded_regions: dict[tuple[int, int], Region] = {}
        self.root: Path = path
        self.server_interface = server_interface
        self.land_noise = PerlinNoise(octaves=4, seed=seed)
        self.detail_noise = PerlinNoise(octaves=4, seed=seed+1)
        self.mountain_noise = PerlinNoise(octaves=4, seed=seed+2)
        self.type_noise = PerlinNoise(octaves=4, seed=seed+3)
        self.revene_noise = PerlinNoise(octaves=2, seed=seed+4)


    def get_height(self, x: int, z: int) -> int:
        height = int((self.land_noise([x / (self.TERRAIN_SCALE*6), z / (self.TERRAIN_SCALE*6)]) + 1) * 32)
        height2 = int((self.detail_noise([x / self.TERRAIN_SCALE, z / self.TERRAIN_SCALE]) + 1) * 3)
        terrain_type = abs(self.type_noise([ x / self.TYPE_SCALE, z / self.TYPE_SCALE]))
        mountain = self.mountain_noise([x / self.TERRAIN_SCALE ,z / self.TERRAIN_SCALE])
        height3 = int(abs(mountain) * 80 * terrain_type)

        height += height2 + height3
        return height

    def _generate_chunk(self, chunk_pos: Position) -> Chunk:
        chunk = Chunk(chunk_pos)
        for x in range(16):
            for z in range(16):
                block_x = chunk_pos.x * 16 + x
                block_z = chunk_pos.z * 16 + z
                height = self.get_height(block_x, block_z)
                for y in range(-64, height):
                    chunk.set_block(Position(x, y, z))
        return chunk

    def _get_offline_region_positions(self) -> list[Position]:
        region_files = os.listdir(self.root)
        l: list[Position] = []
        for file in region_files:
            if not file.startswith("r.") or not file.endswith(".chc"): continue
            reg_x = int(file.split('.')[1])
            reg_z = int(file.split('.')[2])
            l.append(Position(reg_x, 0, reg_z, type = PositionType.Region))
        
        return l

    def _load_region(self, reg_pos: Position) -> Region:
        key = (reg_pos.x, reg_pos.z)
        if key in self.loaded_regions: return self.loaded_regions[key]
        path = self.root / f"r.{reg_pos.x}.{reg_pos.z}.chc"

        if path.exists(): r = Region.load_file(str(path))
        else: r = Region({}, reg_pos)

        self.loaded_regions[key] = r
        return r
        
    def load_chunk(self, chunk_pos: Position) -> Chunk:
        chunk_pos = chunk_pos.to_chunk()
        region = self._load_region(chunk_pos.to_region())
        local_key = (chunk_pos.x % 32, chunk_pos.z % 32)

        if local_key in region.chunks:
            return region.chunks[local_key]

        chunk = self._generate_chunk(chunk_pos)
        region.chunks[local_key] = chunk
        return chunk

    def set_block(self, pos: Position):
        chunk = self.load_chunk(pos.to_chunk())
        chunk.set_block(Position(*pos.chunk_local()))
        EventManager.trigger(WorldEvent.BlockChanged, self.server_interface, pos, 1)

    def clear_block(self, pos: Position):
        chunk = self.load_chunk(pos.to_chunk())
        chunk.clear_block(Position(*pos.chunk_local()))
        EventManager.trigger(WorldEvent.BlockChanged, self.server_interface, pos, 0)

    def update_block(self, pos: Position, block_id: int):
        if block_id == 0: self.clear_block(pos)
        else: self.set_block(pos)

    def save(self):
        for region in self.loaded_regions.values():
            region.save_file(str(self.root/f"r.{region.position.x}.{region.position.z}.chc"))
        EventManager.trigger(WorldEvent.WorldSaved)
        if self.server_interface.is_running():
            threading.Timer(constants.SAVE_INTERVAL, self.save).start()