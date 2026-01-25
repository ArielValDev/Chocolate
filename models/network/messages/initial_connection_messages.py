from tcp_connection import TCPConnection

@dataclass
class HandshakeReturn:
    protocol_version: int
    server_address: str
    port: int
    intent: int

def message_handle_handshake(conn: TCPConnection):
    msg = conn.get_message()
    