from uuid import UUID
from constants.network import ConnectionState
from models.network.messages.initial_connection_messages import *
from models.network.tcp_connection import TCPConnection
from utils.logger import Logger

class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
        self.connection_state: ConnectionState = ConnectionState.Handshaking
        self.username: str = ""
        self.uuid: UUID = UUID(int = 0)

    def connect_to_world(self):
        handle_message_handshake(self.conn, self.connection_state)
        
        self.connection_state = ConnectionState.Login

        user_data = handle_message_login(self.conn, self.connection_state)
        self.username = user_data.username
        self.uuid = user_data.uuid

        handle_message_login_success(self.conn, self.uuid, self.username)
        handle_message_login_ack(self.conn, self.connection_state)

        self.connection_state = ConnectionState.Configuration

        _ = handle_message_plugin_message(self.conn, self.connection_state)
        client_inforamtion=  handle_message_client_information(self.conn, self.connection_state)
        handle_message_registry_data(self.conn)
        Logger.error("finished reg")
        handle_message_finish_configuration(self.conn)
        #handle_message_ack_finish_configuration(self.conn, self.connection_state)

        self.connection_state = ConnectionState.Play
