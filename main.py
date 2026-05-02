import tkinter as tk
from chocolate import ChocolateServer
from server_gui import ServerGUI

def main():
    chocolate_server = ChocolateServer() 
    root = tk.Tk()
    app = ServerGUI(root, chocolate_server)
    root.mainloop()
    
if __name__ == "__main__":
    main()