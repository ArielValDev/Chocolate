from dataclasses import dataclass
from tcp_connection import TCPConnection
from constants.network import *

@dataclass
class HandshakeReturn:
    protocol_version: int
    server_address: str
    port: int
    intent: int

def message_handle_handshake(conn: TCPConnection, state: ConnectionState) -> HandshakeReturn:
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != HandshakingStatePacketID.Handshake.value or state != ConnectionState.Handshaking:
        raise ConnectionError("Unexpected packet ID or state for handshake")
    
    return HandshakeReturn(
        protocol_version=buf.consume_varint(),
        server_address=buf.consume_string(),
        port=buf.consume_unsigned_short(),
        intent=buf.consume_varint()
    )



    
    