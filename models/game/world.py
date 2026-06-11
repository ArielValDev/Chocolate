from typing import TYPE_CHECKING
from constants.game import BLOCK_KIND
from models.buffer import Buffer
if TYPE_CHECKING:
    from models.player import Player
from models.types.position import Position, PositionType
from models.server_interface import ServerInterface

def get_chunk_data_and_update_light_bytes_at(position: Position, server_interface: ServerInterface) -> Buffer:
    world = server_interface.get_world()
    chunk = world.load_chunk(position.to_chunk())
    return chunk.to_buf(BLOCK_KIND)


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

    