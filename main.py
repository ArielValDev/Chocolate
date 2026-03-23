import socket

from chocolate import ChocolateServer
from models.network.messages.player_packets import handle_player_packet_chunk_data_and_update_light
from models.network.tcp_connection import TCPConnection
from models.types.position import Position
#from utils.protocol_type_utils import to_varint, from_varint

def main():
    chocolate_server = ChocolateServer() 
    chocolate_server.init() # TODO: handle server config from file
    chocolate_server.start()
    #chocolate_server.save()
    #chocolate_server.shutdown()
    #print(fetch_player_properties(UUID("58e7c8d7d09c40ef97b5d5f4f5c6eba8")))
    

if __name__ == "__main__":
    main()