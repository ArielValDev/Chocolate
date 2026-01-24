from models.network.messages.message_types.types import MessageType
from models.network.tcp_connection import TCPConnection
from typing import Any, Callable

# TODO: handle return of type handler (what if we need value from message)

class MessageManager:
    type_handlers: dict[MessageType, Callable[[TCPConnection], Any]]

    def handle(conn: TCPConnection):
        MessageManager.type_handlers