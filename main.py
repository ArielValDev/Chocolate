#from chocolate import ChocolateServer
from utils.protocol_type_utils import to_varint, from_varint

def main():
    # chocolate_server = ChocolateServer() 
    # chocolate_server.init() # TODO: handle server config from file
    # chocolate_server.start()
    # #chocolate_server.save()
    # #chocolate_server.shutdown()
    a = to_varint(-1)
    print(a.hex())
    print(from_varint(bytearray(a)))
    

if __name__ == "__main__":
    main()