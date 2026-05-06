from re import L
import tkinter as tk
from tkinter import Tk, scrolledtext, messagebox
import threading
import json, queue

from constants import constants
from constants.game import InGameEvent
from models.events.event_manager import EventManager
from chocolate import ChocolateServer
from utils.logger import Logger

class ServerGUI:
    _instance = None
    def __init__(self, root: Tk, server: ChocolateServer):
        ServerGUI._instance = self

        self.root = root
        self.server = server
        self.root.title("Chocolate Server Manager")
        self.root.geometry("800x500")

        self.server.init()
        self._create_config_frame()
        self._create_console_frame()
        self._create_players_frame()
        self._create_control_frame()
        self._update_players_list()
        self._check_logger_queue()

    def _create_config_frame(self):
        config_frame = tk.LabelFrame(self.root, text="Server Configuration", padx=10, pady=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(config_frame, text="Max Players:").grid(row=0, column=0, padx=5)
        self.max_players_entry = tk.Entry(config_frame, width=10)
        curr_max = self.server.config.max_players
        self.max_players_entry.insert(0, str(curr_max))
        self.max_players_entry.grid(row=0, column=1, padx=5)
        self.max_players_entry.bind("<Return>", lambda e: self._on_config_input_change("max_players", self.max_players_entry))
        self.max_players_entry.bind("<FocusOut>", lambda e: self._on_config_input_change("max_players", self.max_players_entry))

        tk.Label(config_frame, text="Render Distance:").grid(row=0, column=2, padx=5)
        self.render_distance_entry = tk.Entry(config_frame, width=10)
        curr_render = self.server.config.render_distance
        self.render_distance_entry.insert(0, str(curr_render))
        self.render_distance_entry.grid(row=0, column=3, padx=5)
        self.render_distance_entry.bind("<Return>", lambda e: self._on_config_input_change("render_distance", self.render_distance_entry))
        self.render_distance_entry.bind("<FocusOut>", lambda e: self._on_config_input_change("render_distance", self.render_distance_entry))

        tk.Label(config_frame, text="Port:").grid(row=0, column=4, padx=5)
        self.port_entry = tk.Entry(config_frame, width=10)
        curr_port = self.server.config.port
        self.port_entry.insert(0, str(curr_port))
        self.port_entry.grid(row=0, column=5, padx=5)
        self.port_entry.bind("<Return>", lambda e: self._on_config_input_change("port", self.port_entry))
        self.port_entry.bind("<FocusOut>", lambda e: self._on_config_input_change("port", self.port_entry))

    def _on_config_input_change(self, config_key: str, entry_widget: tk.Entry):
        input_value = entry_widget.get()
        
        is_valid = True
        value = -1

        if getattr(self.server, 'is_running', False):
            is_valid = False
        elif not input_value.isdigit():
            is_valid = False
        else:
            value = int(input_value)
            if config_key == "port" and value not in range(10000, 40001):
                is_valid = False
            elif config_key != "port" and value not in range(1, 13):
                is_valid = False
        
        if is_valid:
            self.server.config.change_config(constants.CONFIG_FILE_PATH, config_key, value)
        
        else:
            valid_value = getattr(self.server.config, config_key)
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(valid_value))

    def _create_console_frame(self):
        main_console_frame = tk.Frame(self.root)
        main_console_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=10, pady=5)

        logs_frame = tk.LabelFrame(main_console_frame, text="System Logs", padx=5, pady=5)
        logs_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 5))

        self.console_text = scrolledtext.ScrolledText(logs_frame, state='disabled', width=45, bg="black", fg="lightgreen", font=("Consolas", 10))
        self.console_text.pack(fill=tk.BOTH, expand=True)

        chat_frame = tk.LabelFrame(main_console_frame, text="Player Chat", padx=5, pady=5)
        chat_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(5, 0))

        self.chat_text = scrolledtext.ScrolledText(chat_frame, state='disabled', width=35, bg="black", fg="cyan", font=("Consolas", 10))
        self.chat_text.pack(fill=tk.BOTH, expand=True)

    def _create_players_frame(self):
        self.right_container = tk.Frame(self.root)
        self.right_container.pack(fill=tk.Y, side=tk.RIGHT, padx=10, pady=5)

        players_frame = tk.LabelFrame(self.right_container, text="Online Players", padx=10, pady=10)
        players_frame.pack(fill=tk.BOTH, expand=True)

        self.players_listbox = tk.Listbox(players_frame, width=20)
        self.players_listbox.pack(fill=tk.BOTH, expand=True)

    def _update_players_list(self):
        if getattr(self.server, 'is_running', False):
            self.players_listbox.delete(0, tk.END)

            for player in self.server.players:
                player_name = player.username
                self.players_listbox.insert(tk.END, player_name)

        self.root.after(1000, self._update_players_list)

    def _create_control_frame(self):
        control_frame = tk.Frame(self.right_container)
        control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.toggle_button = tk.Button(control_frame, text="Start Server", font=("Arial", 12, "bold"), bg="green", fg="white", command=self.toggle_server)
        self.toggle_button.pack(fill=tk.X, pady=5, ipadx=5, ipady=5)

    def toggle_server(self):
        if not self.server.is_running:
            self.server.is_running = True
            
            self.toggle_button.config(text="Stop Server", bg="red")
            self.max_players_entry.config(state="disabled")
            self.render_distance_entry.config(state="disabled")
            self.port_entry.config(state="disabled")

            threading.Thread(target=self._run_server, daemon=True).start()
        
        else:
            self.server.is_running = False
            
            self.toggle_button.config(text="Start Server", bg="green")
            
            self.max_players_entry.config(state="normal")
            self.render_distance_entry.config(state="normal")
            self.port_entry.config(state="normal")
            
            self.server.save_and_shutdown()

    def _run_server(self):
        self.server.start()

    def _check_logger_queue(self):
        try:
            while True:
                msg = Logger.gui_queue.get_nowait()
                
                if msg.startswith("CHAT:"):
                    parts = msg.split(":", 2)
                    if len(parts) == 3:
                        self._write_to_chat(parts[1], parts[2])
                elif msg.startswith("SYS:"):
                    self._write_to_console(msg[4:])
                    
        except queue.Empty:
            pass

        self.root.after(100, self._check_logger_queue)

    def _write_to_console(self, message: str):
        self.console_text.config(state='normal')
        self.console_text.insert(tk.END, message + "\n")
        self.console_text.see(tk.END)
        self.console_text.config(state='disabled')

    def _write_to_chat(self, sender: str, message: str):
        self.chat_text.config(state='normal')
        self.chat_text.insert(tk.END, f"[{sender}] {message}\n")
        self.chat_text.see(tk.END)
        self.chat_text.config(state='disabled')