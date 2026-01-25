from models.network.tcp_connection import TCPConnection

class Player:
    def __init__(self, conn: TCPConnection):
        self.conn = conn
    
    def connect_to_world(self):
        
