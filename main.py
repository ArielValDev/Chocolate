from chocolate import ChocolateServer

def main():
    chocolate_server = ChocolateServer() 
    chocolate_server.init() # TODO: handle server config from file
    chocolate_server.start()
    #chocolate_server.save()
    #chocolate_server.shutdown()

if __name__ == "__main__":
    main()