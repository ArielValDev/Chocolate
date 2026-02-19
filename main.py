from chocolate import ChocolateServer
#from utils.protocol_type_utils import to_varint, from_varint

def main():
    chocolate_server = ChocolateServer() 
    chocolate_server.init() # TODO: handle server config from file
    chocolate_server.start()
    # #chocolate_server.save()
    # #chocolate_server.shutdown()
    #print(fetch_player_properties(UUID("58e7c8d7d09c40ef97b5d5f4f5c6eba8")))
    # TODO: add function that imports all tyhe registries from 1.21.11 in .minecraft to a json file ☻
    #       path: C:\Users\User\AppData\Roaming\.minecraft\versions\1.21.11\1.21.11\data\minecraft
    

if __name__ == "__main__":
    main()