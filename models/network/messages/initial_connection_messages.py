from dataclasses import dataclass
from constants import network
from models.network.tcp_connection import TCPConnection
from constants.network import *
from uuid import UUID
from models.buffer import Buffer
from utils import network_utils

@dataclass
class HandshakepacketData:
    protocol_version: int
    server_address: str
    port: int
    intent: int

def handle_message_handshake(conn: TCPConnection, state: ConnectionState) -> HandshakepacketData:
    """
    Incoming
    """
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
    """
    Incoming
    """
    packet_id, buf = conn.recv_mc_packet()
    if packet_id != LoginStatePacketID.LoginStart.value or state != ConnectionState.Login:
        raise ConnectionError("Unexpected packet ID or state for login")
    
    return LoginPacketData(
        username=buf.consume_string(),
        uuid=buf.consume_uuid()
    )

def handle_message_login_success(conn: TCPConnection, uuid: UUID, username: str):
    """
    Outgoing
    """
    login_success_msg = Buffer()
    properties = network_utils.fetch_player_properties(uuid)
    login_success_msg.add_game_profile(uuid, username, properties)

    conn.send_mc_packet(login_success_msg, network.LoginStatePacketID.LoginSuccess.value)
    
def handle_message_login_ack(conn: TCPConnection, state: ConnectionState):
    """
    Incoming
    """
    packet_id, _ = conn.recv_mc_packet()
    if packet_id != LoginStatePacketID.LoginAck.value or state != ConnectionState.Login:
        raise ConnectionError("Unexpected packet ID or state for login acknowledge")
    
def handle_message_registry_data(conn: TCPConnection, state: ConnectionState):
    registry_data_msg = Buffer()
    
    