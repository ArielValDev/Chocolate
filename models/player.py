from constants.network import ConnectionState
from models.network.messages.initial_connection_messages import message_handle_handshake
from models.network.tcp_connection import TCPConnection


class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
        self.connection_state: ConnectionState = ConnectionState.Handshaking
    
    def connect_to_world(self):
        message_handle_handshake(self.conn, self.connection_state)
        
