from uuid import UUID
from constants.network import ConnectionState
from models.network.messages.initial_connection_messages import handle_message_handshake, handle_message_login, handle_message_login_success
from models.network.tcp_connection import TCPConnection

class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
        self.connection_state: ConnectionState = ConnectionState.Handshaking
        self.username: str = ""
        self.uuid: UUID = UUID(int = 0)

    def connect_to_world(self):
        handle_message_handshake(self.conn, self.connection_state)
        
        user_data = handle_message_login(self.conn, self.connection_state)
        self.username = user_data.username
        self.uuid = user_data.uuid

        handle_message_login_success(self.conn, self.uuid, self.username)