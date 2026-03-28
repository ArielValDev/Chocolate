import math
from typing import TYPE_CHECKING
from models.buffer import Buffer
if TYPE_CHECKING:
    from models.player import Player
from models.types.mc_types import BitField
from models.types.position import Position, PositionType
from models.server_interface import ServerInterface


def get_chunk_data_and_update_light_bytes_at(position: Position) -> Buffer:
    chunk_and_light_data = Buffer()

    chunk = position.to_chunk()
    chunk_and_light_data.add_int(chunk.x)
    chunk_and_light_data.add_int(chunk.z)

    # Data:
        # Heightmaps:
    chunk_and_light_data.add_raw(bytearray([0]))
        # Data:
    data = Buffer()
    block_kinds_num = 2
    bpe = max(math.ceil(math.log2(block_kinds_num + 1)), 4)
    entry_mask = (1 << bpe) - 1
    entries_per_long = 64 // bpe


    for i in range(-4, 20):
        section = Buffer()
        block_count = 0
        block_states = Buffer()
        biomes = Buffer()

        longs: list[int] = []
        curr_long = 0

        entry_index = 0
        for y in range(0, 16):
            for z in range(0, 16):
                for x in range(0, 16):
                    block = 1 if (y + i * 16) <= 0 else 0
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
        section.add_varint(8) # Stone

        for long in longs:
            section.add_long(long)
        
        section.add_unsigned_byte(0)    # bpe = 0 -> single value
        section.add_varint(1)           # plains = 0

        data.add_buffer(section)

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

def get_chunk_positions_in_range(center: Position, view_distance: int) -> list[Position]:
    center = center.to_chunk()

    chunks: list[Position] = []

    for dx in range(-view_distance, view_distance + 1):
        for dz in range(-view_distance, view_distance + 1):
            chunks.append(Position(
                center.x + dx,
                0,
                center.z + dz,
                center.dimension,
                PositionType.Chunk
            ))

    return chunks

def get_players_in_range(server_interface: ServerInterface, center: Position, view_distance: int) -> list["Player"]:
    players_in_range: list["Player"] = []
    center_chunk = center.to_chunk()

    for player in server_interface.get_all_players():
        player_chunk = player.game_state.current_position.to_chunk()
        if abs(player_chunk.x - center_chunk.x) <= view_distance and abs(player_chunk.z - center_chunk.z) <= view_distance:
            players_in_range.append(player)

    return players_in_range

    