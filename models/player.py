from models.network.tcp_connection import TCPConnection
from models.network.messages.message_manager import MessageManager


class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
    
    def setup(self):
        MessageManager.handle(self.conn, )
