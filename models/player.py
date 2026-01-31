from uuid import UUID
from constants.network import ConnectionState
from models.network.messages.initial_connection_messages import handle_message_handshake, handle_message_login
from models.network.tcp_connection import TCPConnection


class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
        self.connection_state: ConnectionState = ConnectionState.Handshaking
        self.username: str = ""
        self.uuid: UUID = UUID()
    
    def _send_game_profile(self):
        self.conn.send_mc_packet()

    def connect_to_world(self):
        handle_message_handshake(self.conn, self.connection_state)
        
        user_data = handle_message_login(self.conn, self.connection_state)
        self.username = user_data.username
        self.uuid = user_data.uuid

        
