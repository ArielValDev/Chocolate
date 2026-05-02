import sqlite3
from typing import Any
from constants.constants import DB_FILE
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.player import Player

class DBManager:

    db_file = DB_FILE
    
    @staticmethod
    def init():
        DBManager._create_table()
    
    @staticmethod
    def _get_connection():
        return sqlite3.connect(DBManager.db_file)
    
    @staticmethod
    def _execute_write(query: str, params: tuple[Any, ...] = ()):
        with DBManager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    @staticmethod
    def _execute_read(query: str, params: tuple[Any, ...] = ()):
        with DBManager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def _create_table():
        query = """
        CREATE TABLE IF NOT EXISTS players (
            UUID TEXT PRIMARY KEY,
            Username TEXT,
            Last_Pos_X REAL,
            Last_Pos_Y REAL,
            Last_Pos_Z REAL,
            Yaw REAL,
            Head_Yaw REAL,
            Pitch REAL,
            Health REAL
        )
        """

        DBManager._execute_write(query)

    @staticmethod
    def save_player(player: "Player"):
        query = """
        INSERT INTO players (UUID, Username, Last_Pos_X, Last_Pos_Y, Last_Pos_Z, Yaw, Head_Yaw, Pitch, Health)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(UUID) DO UPDATE SET
            Username=excluded.Username,
            Last_Pos_X=excluded.Last_Pos_X,
            Last_Pos_Y=excluded.Last_Pos_Y,
            Last_Pos_Z=excluded.Last_Pos_Z,
            Yaw=excluded.Yaw,
            Head_Yaw=excluded.Head_Yaw,
            Pitch=excluded.Pitch,
            Health=excluded.Health
        """
        
        params: tuple[Any, ...] = (
            str(player.uuid),
            player.username,
            player.game_state.current_position.x,
            player.game_state.current_position.y,
            player.game_state.current_position.z,
            player.game_state.current_position.yaw,
            player.game_state.current_position.head_yaw,
            player.game_state.current_position.pitch,
            player.game_state.health
        )

        DBManager._execute_write(query, params)

    @staticmethod
    def load_player_data(player: "Player") -> bool:
        query = "SELECT Username, Last_Pos_X, Last_Pos_Y, Last_Pos_Z, Yaw, Head_Yaw, Pitch, Health FROM players WHERE UUID = ?"
        result = DBManager._execute_read(query, (str(player.uuid),))
            
        if result:
            player.username = result[0]
            player.game_state.current_position.x = result[1]
            player.game_state.current_position.y = result[2]
            player.game_state.current_position.z = result[3]
            player.game_state.current_position.yaw = result[4]
            player.game_state.current_position.head_yaw = result[5]
            player.game_state.current_position.pitch = result[6]
            player.game_state.health = result[7]
            return True
            
        return False