#from chocolate import ChocolateServer
from uuid import UUID
from utils.protocol_type_utils import to_varint, from_varint
from utils.network_utils import fetch_player_properties

def main():
    # chocolate_server = ChocolateServer() 
    # chocolate_server.init() # TODO: handle server config from file
    # chocolate_server.start()
    # #chocolate_server.save()
    # #chocolate_server.shutdown()
    print(fetch_player_properties(UUID("58e7c8d7d09c40ef97b5d5f4f5c6eba8")))
    

if __name__ == "__main__":
    main()