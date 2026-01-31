from dataclasses import dataclass
from tcp_connection import TCPConnection
from constants.network import *
from uuid import UUID

@dataclass
class HandshakepacketData:
    protocol_version: int
    server_address: str
    port: int
    intent: int

def handle_message_handshake(conn: TCPConnection, state: ConnectionState) -> HandshakepacketData:
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != HandshakingStatePacketID.Handshake.value or state != ConnectionState.Handshaking:
        raise ConnectionError("Unexpected packet ID or state for handshake")
    
    return HandshakepacketData(
        protocol_version=buf.consume_varint(),
        server_address=buf.consume_string(),
        port=buf.consume_unsigned_short(),
        intent=buf.consume_varint()
    )

@dataclass
class LoginPacketData:
    username: str
    uuid: UUID

def handle_message_login(conn: TCPConnection, state: ConnectionState) -> LoginPacketData:
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != HandshakingStatePacketID.Handshake.value or state != ConnectionState.Handshaking:
        raise ConnectionError("Unexpected packet ID or state for handshake")
    
    return LoginPacketData(
        username=buf.consume_string(),
        uuid=buf.consume_uuid()
    )

def handle_message_login_success(conn: TCPConnection, uuid: UUID, username: str):

