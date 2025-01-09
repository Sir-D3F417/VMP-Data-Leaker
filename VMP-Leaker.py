# Coded by D3F417
# https://github.com/Sir-D3F417
# https://d3f417.info
# https://t.me/hex_aa
import requests
import json
import customtkinter as ctk
import pyperclip
import threading
import re
import ipaddress
from typing import Optional, Dict, List, Any
from tkinter import filedialog
import csv
from datetime import datetime
import time

class Config:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "theme": "dark",
            "last_ip": "",
            "last_port": "",
            "auto_refresh": False,
            "refresh_interval": 30
        }
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            self.settings = self.default_config
            self.save_config()
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

class PlayerDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VMP Data Leaker | Dev:D3F417")
        
        
        self.status_var = ctk.StringVar()
        self.last_refresh_time = None
        self.is_loading = False
        self.player_buttons = []
        self.current_ip = ""
        self.current_port = ""
        
        
        self.load_config()
        
        
        self.colors = {
            "purple": {"main": "#8A2BE2", "hover": "#9B30FF", "pressed": "#7B1FA2"},
            "background": "#2B2B2B",
            "secondary": "#3B3B3B",
            "text": "#FFFFFF",
            "text_secondary": "#B0B0B0"
        }
        
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")  # Base theme
        
        
        self.ip_entry = None
        self.port_entry = None
        self.player_data_frame = None
        self.loading_label = None
        
        
        self.auto_refresh = self.config.get("auto_refresh", False)
        self.refresh_interval = self.config.get("refresh_interval", 30)
        self.refresh_thread = None
        
        
        self.create_gui()
        
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        """Load configuration or create default"""
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "theme": "dark",
                "auto_refresh": False,
                "refresh_interval": 30,
                "last_ip": "",
                "last_port": ""
            }

    def fetch_player_data(self, ip, port):
        url = f"http://{ip}:{port}/players.json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                self.player_data = response.json()
                return self.player_data
            else:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return []

    def show_player_data(self, player):
        try:
            player_window = ctk.CTkToplevel(self.root)
            player_window.title(f"Player Data - {player['name']}")
            player_window.geometry("400x300")
            player_json = json.dumps(player, indent=4)
            
            player_label = ctk.CTkLabel(player_window, text=player_json, justify='left')
            player_label.pack(padx=10, pady=10)

            copy_button = ctk.CTkButton(
                player_window, 
                text="Copy Data", 
                command=lambda: self.copy_to_clipboard(player_json)
            )
            copy_button.pack(pady=5)
            
            
            player_window.protocol("WM_DELETE_WINDOW", 
                                 lambda: self.safe_destroy_widget(player_window))
        except Exception as e:
            self.update_status(f"Error showing player data: {str(e)}", is_error=True)

    def copy_to_clipboard(self, data):
        pyperclip.copy(data)
        print("Data copied to clipboard!")

    def refresh_data(self):
        try:
            
            self.clear_player_buttons()
            
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            if ip and port:
                
                self.root.after(100, lambda: self.load_player_data(ip, port))
        except Exception as e:
            self.update_status(f"Refresh error: {str(e)}", is_error=True)

    def load_player_data(self, ip, port):
        try:
            player_data = self.fetch_player_data(ip, port)
            
            if player_data:
                
                self.clear_player_buttons()
                
                def create_buttons():
                    try:
                        
                        for index, player in enumerate(player_data):
                            try:
                                player_button = ctk.CTkButton(
                                    self.player_data_frame, 
                                    text=player.get('name', 'Unknown'),
                                    command=lambda p=player: self.show_player_data(p)
                                )
                                player_button.grid(row=index // 4, column=index % 4, 
                                                 padx=5, pady=5, sticky='nsew')
                                self.player_buttons.append(player_button)
                                
                                self.player_data_frame.grid_rowconfigure(index // 4, weight=1)
                                self.player_data_frame.grid_columnconfigure(index % 4, weight=1)
                            except Exception as e:
                                print(f"Error creating button for player {player.get('name', 'unknown')}: {e}")
                                
                        if hasattr(self, 'loading_label') and self.loading_label:
                            self.safe_destroy_widget(self.loading_label)
                            
                        self.update_status("Data loaded successfully")
                    except Exception as e:
                        self.update_status(f"Error creating buttons: {str(e)}", is_error=True)
                
                
                self.root.after(100, create_buttons)
                
        except Exception as e:
            self.update_status(f"Error loading player data: {str(e)}", is_error=True)

    def create_gui(self):
        
        self.root.configure(fg_color=self.colors["background"])
        
        main_frame = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        main_frame.grid(row=0, column=0, sticky='nsew')

        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="VMP Data Leaker", 
            font=("Segoe UI", 32, "bold"),
            text_color=self.colors["purple"]["main"]
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        
        welcome_label = ctk.CTkLabel(
            main_frame, 
            text="Telegram : @hex_aa", 
            font=("Segoe UI Semibold", 18),
            text_color=self.colors["text"]
        )
        welcome_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        
        input_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["secondary"])
        input_frame.grid(row=2, column=0, padx=20, pady=10, sticky='ew')

        
        ip_label = ctk.CTkLabel(
            input_frame, 
            text="Enter IP:", 
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors["text"]
        )
        ip_label.grid(row=0, column=0, padx=10, pady=5)
        self.ip_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter IP address",
            font=("Segoe UI", 12),
            fg_color=self.colors["background"],
            border_color=self.colors["purple"]["main"],
            text_color=self.colors["text"]
        )
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5)

        
        port_label = ctk.CTkLabel(
            input_frame, 
            text="Enter Port:", 
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors["text"]
        )
        port_label.grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter port number",
            font=("Segoe UI", 12),
            fg_color=self.colors["background"],
            border_color=self.colors["purple"]["main"],
            text_color=self.colors["text"]
        )
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)

        
        fetch_button = ctk.CTkButton(
            main_frame,
            text="Fetch Player Data",
            command=self.start_fetching_data,
            font=("Segoe UI", 15, "bold"),
            fg_color=self.colors["purple"]["main"],
            hover_color=self.colors["purple"]["hover"]
        )
        fetch_button.grid(row=3, column=0, padx=20, pady=15)

        
        control_frame = ctk.CTkFrame(main_frame, fg_color=self.colors["background"])
        control_frame.grid(row=4, column=0, padx=20, pady=10)

        button_configs = [
            ("Refresh", self.refresh_data),
            ("Export CSV", lambda: self.export_data('csv')),
            ("Settings", self.show_settings_dialog),
            ("Analysis", self.show_analysis)
        ]

        for text, command in button_configs:
            ctk.CTkButton(
                control_frame,
                text=text,
                command=command,
                font=("Segoe UI", 13),
                fg_color=self.colors["purple"]["main"],
                hover_color=self.colors["purple"]["hover"],
                width=120
            ).pack(side='left', padx=5)

        
        refresh_controls = ctk.CTkFrame(main_frame, fg_color=self.colors["secondary"])
        refresh_controls.grid(row=5, column=0, padx=20, pady=10, sticky='ew')
        
        self.auto_refresh_var = ctk.BooleanVar(value=self.auto_refresh)
        self.auto_refresh_cb = ctk.CTkCheckBox(
            refresh_controls,
            text="Auto Refresh",
            font=("Segoe UI", 12),
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            fg_color=self.colors["purple"]["main"],
            hover_color=self.colors["purple"]["hover"],
            text_color=self.colors["text"]
        )
        self.auto_refresh_cb.pack(side='left', padx=10, pady=5)
        
        self.refresh_status = ctk.CTkLabel(
            refresh_controls,
            text="",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"]
        )
        self.refresh_status.pack(side='right', padx=10)

        
        credits_label = ctk.CTkLabel(
            main_frame,
            text="Developed by: D3F417",
            font=("Segoe UI", 11, "italic"),
            text_color=self.colors["text_secondary"]
        )
        credits_label.grid(row=6, column=0, pady=20)

        
        self.player_data_frame = ctk.CTkFrame(
            self.root,
            fg_color=self.colors["secondary"]
        )
        self.player_data_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)

        
        status_bar = ctk.CTkFrame(self.root, fg_color=self.colors["secondary"])
        status_bar.grid(row=2, column=0, sticky='ew', padx=20, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_bar,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            text_color=self.colors["text"]
        )
        self.status_label.pack(side='left', padx=10, pady=5)
        
        self.refresh_time_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=("Segoe UI", 11),
            text_color=self.colors["text_secondary"]
        )
        self.refresh_time_label.pack(side='right', padx=10, pady=5)

        
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def start_fetching_data(self):
        try:
            ip = self.ip_entry.get()
            port = self.port_entry.get()
            if ip and port:
                if hasattr(self, 'loading_label') and self.loading_label:
                    self.safe_destroy_widget(self.loading_label)
                    
                self.loading_label = ctk.CTkLabel(self.root, text="Loading player data...", fg_color="black")
                self.loading_label.grid(row=9, column=0, padx=10, pady=10)
                
                threading.Thread(target=self.load_player_data, args=(ip, port), daemon=True).start()
        except Exception as e:
            self.update_status(f"Error starting data fetch: {str(e)}", is_error=True)

    def validate_input(self) -> tuple[bool, str]:
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        
        try:
            
            ipaddress.ip_address(ip)
            
            
            port_num = int(port)
            if not (1 <= port_num <= 65535):
                raise ValueError("Port must be between 1 and 65535")
                
            return True, ""
        except ValueError as e:
            return False, str(e)

    def update_status(self, message: str, is_error: bool = False):
        self.status_var.set(message)
        if is_error:
            self.status_label.configure(text_color="red")
        else:
            self.status_label.configure(text_color="white")

    def create_player_data_view(self):
        
        filter_frame = ctk.CTkFrame(self.player_data_frame)
        filter_frame.grid(row=0, column=0, sticky='ew', columnspan=4)
        
        self.search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Search players...")
        self.search_entry.pack(side='left', padx=5, pady=5)
        self.search_entry.bind('<KeyRelease>', self.filter_players)
        
        
        sort_options = ["Name", "Level", "Playtime"]
        self.sort_var = ctk.StringVar(value="Name")
        sort_menu = ctk.CTkOptionMenu(filter_frame, values=sort_options, 
                                    variable=self.sort_var,
                                    command=self.sort_players)
        sort_menu.pack(side='right', padx=5, pady=5)

    def filter_players(self, event=None):
        search_text = self.search_entry.get().lower()
        for widget in self.player_data_frame.winfo_children()[1:]:  # Skip filter frame
            if isinstance(widget, ctk.CTkButton):
                player_name = widget.cget("text").lower()
                widget.grid_remove() if search_text not in player_name else widget.grid()

    def export_data(self, format: str = 'json'):
        if not hasattr(self, 'player_data'):
            self.update_status("No data to export!", is_error=True)
            return
            
        try:
            if format == 'json':
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json")]
                )
                if file_path:
                    with open(file_path, 'w') as f:
                        json.dump(self.player_data, f, indent=4)
                        
            elif format == 'csv':
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")]
                )
                if file_path:
                    with open(file_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=self.player_data[0].keys())
                        writer.writeheader()
                        writer.writerows(self.player_data)
                        
            self.update_status(f"Data exported successfully to {file_path}")
        except Exception as e:
            self.update_status(f"Export failed: {str(e)}", is_error=True)

    def export_to_csv(self, player_data: List[Dict[str, Any]], file_path: str):
        try:
           
            headers = [
                'Name', 'Level', 'Playtime', 'Last Seen', 'IP Address',
                'Inventory Items', 'Stats', 'Location', 'Export Date'
            ]
            
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                
                for player in player_data:
                    row = [
                        player.get('name', 'N/A'),
                        player.get('level', 0),
                        self.format_playtime(player.get('playtime', 0)),
                        player.get('lastSeen', 'Never'),
                        player.get('ipAddress', 'Unknown'),
                        len(player.get('inventory', [])),
                        json.dumps(player.get('stats', {})),
                        f"{player.get('x', 0)}, {player.get('y', 0)}, {player.get('z', 0)}",
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                    writer.writerow(row)
                    
            self.update_status("CSV export completed successfully!")
        except Exception as e:
            self.update_status(f"CSV export failed: {str(e)}", is_error=True)

    def format_playtime(self, seconds: int) -> str:
        """Convert seconds to human-readable format"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def toggle_auto_refresh(self):
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
            
    def start_auto_refresh(self):
        if not hasattr(self, 'refresh_thread') or not self.refresh_thread or not self.refresh_thread.is_alive():
            self.auto_refresh = True
            self.refresh_thread = threading.Thread(target=self.refresh_loop, daemon=True)
            self.refresh_thread.start()
            self.update_status("Auto-refresh enabled")
            self.update_refresh_status()
            
    def stop_auto_refresh(self):
        self.auto_refresh = False
        if hasattr(self, 'refresh_thread') and self.refresh_thread and self.refresh_thread.is_alive():
            self.refresh_thread.join(timeout=1)
        self.update_status("Auto-refresh disabled")
        self.refresh_status.configure(text="")
        
    def refresh_loop(self):
        while self.auto_refresh:
            try:
                self.refresh_data()
                
                self.last_refresh_time = datetime.now()
                self.update_refresh_status()
                
                
                for _ in range(self.refresh_interval):
                    if not self.auto_refresh:
                        break
                    time.sleep(1)
                    self.update_refresh_status()
                    
            except Exception as e:
                self.update_status(f"Auto-refresh error: {str(e)}", is_error=True)
                time.sleep(5)  
                
    def update_refresh_status(self):
        if not self.auto_refresh:
            self.refresh_status.configure(text="")
            return
            
        if self.last_refresh_time:
            time_since_refresh = (datetime.now() - self.last_refresh_time).seconds
            next_refresh = max(0, self.refresh_interval - time_since_refresh)
            self.refresh_status.configure(
                text=f"Next refresh in {next_refresh}s"
            )

    def analyze_player_data(self, player_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze player data and return statistics"""
        analysis = {
            'total_players': len(player_data),
            'average_level': 0,
            'total_playtime': 0,
            'active_players': 0,
            'inventory_stats': {},
            'location_heatmap': {},
        }
        
        for player in player_data:
            
            analysis['average_level'] += player.get('level', 0)
            analysis['total_playtime'] += player.get('playtime', 0)
            
            
            last_seen = player.get('lastSeen', '')
            if last_seen:
                try:
                    last_seen_date = datetime.fromisoformat(last_seen)
                    if (datetime.now() - last_seen_date).total_seconds() < 86400:
                        analysis['active_players'] += 1
                except (ValueError, TypeError):
                    pass  
                
            
            for item in player.get('inventory', []):
                item_name = item.get('name', 'Unknown')
                analysis['inventory_stats'][item_name] = analysis['inventory_stats'].get(item_name, 0) + 1
                
            
            loc_key = f"{player.get('x', 0)//100},{player.get('z', 0)//100}"
            analysis['location_heatmap'][loc_key] = analysis['location_heatmap'].get(loc_key, 0) + 1
        
        if player_data:
            analysis['average_level'] /= len(player_data)
            
        return analysis

    def show_settings_dialog(self):
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        
        
        refresh_frame = ctk.CTkFrame(settings_window)
        refresh_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(refresh_frame, text="Refresh Interval (seconds):").pack(side='left')
        refresh_entry = ctk.CTkEntry(refresh_frame)
        refresh_entry.insert(0, str(self.refresh_interval))
        refresh_entry.pack(side='right')
        
        
        auto_refresh_var = ctk.BooleanVar(value=self.auto_refresh)
        auto_refresh_cb = ctk.CTkCheckBox(settings_window, text="Enable Auto-refresh",
                                        variable=auto_refresh_var)
        auto_refresh_cb.pack(pady=5)
        
        
        theme_frame = ctk.CTkFrame(settings_window)
        theme_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(theme_frame, text="Theme:").pack(side='left')
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=["Dark", "Light"],
                                     variable=theme_var)
        theme_menu.pack(side='right')
        
        def save_settings():
            try:
                
                valid, error_msg = self.validate_refresh_interval(refresh_entry.get())
                if not valid:
                    self.update_status(error_msg, is_error=True)
                    return
                    
                
                self.refresh_interval = int(refresh_entry.get())
                new_auto_refresh = auto_refresh_var.get()
                
                
                if new_auto_refresh != self.auto_refresh:
                    self.auto_refresh = new_auto_refresh
                    if new_auto_refresh:
                        self.start_auto_refresh()
                    else:
                        self.stop_auto_refresh()
                
                
                new_theme = theme_var.get().lower()
                ctk.set_appearance_mode(new_theme)
                self.update_theme(new_theme)
                
                
                self.config.update({
                    "refresh_interval": self.refresh_interval,
                    "auto_refresh": self.auto_refresh,
                    "theme": new_theme
                })
                
                
                self.save_config()
                
                settings_window.destroy()
                self.update_status("Settings saved successfully!")
                
            except ValueError as e:
                self.update_status("Invalid refresh interval!", is_error=True)
                
        
        save_button = ctk.CTkButton(
            settings_window, 
            text="Save Settings",
            command=save_settings,
            fg_color=self.colors["purple"]["main"],
            hover_color=self.colors["purple"]["hover"]
        )
        save_button.pack(pady=10)
        
        
        settings_window.update_idletasks()
        width = settings_window.winfo_width()
        height = settings_window.winfo_height()
        x = (settings_window.winfo_screenwidth() // 2) - (width // 2)
        y = (settings_window.winfo_screenheight() // 2) - (height // 2)
        settings_window.geometry(f'{width}x{height}+{x}+{y}')

    def update_theme(self, theme):
        """Update the application theme and refresh the UI"""
        
        if theme == "light":
            self.colors.update({
                "background": "#F0F0F0",
                "secondary": "#E0E0E0",
                "text": "#000000",
                "text_secondary": "#505050"
            })
        else:  
            self.colors.update({
                "background": "#2B2B2B",
                "secondary": "#3B3B3B",
                "text": "#FFFFFF",
                "text_secondary": "#B0B0B0"
            })

        
        self.root.configure(fg_color=self.colors["background"])
        
        
        for widget in self.root.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=self.colors["background"])
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color=self.colors["text"])
                    elif isinstance(child, ctk.CTkFrame):
                        child.configure(fg_color=self.colors["secondary"])
                        
        
        if hasattr(self, 'player_data_frame'):
            self.player_data_frame.configure(fg_color=self.colors["secondary"])
            
        
        if hasattr(self, 'status_label'):
            self.status_label.configure(text_color=self.colors["text"])
        if hasattr(self, 'refresh_time_label'):
            self.refresh_time_label.configure(text_color=self.colors["text_secondary"])
            
        
        self.root.update_idletasks()

    def show_analysis(self):
        if not hasattr(self, 'player_data') or not self.player_data:
            self.update_status("No data to analyze! Please fetch player data first.", is_error=True)
            return
            
        analysis_window = ctk.CTkToplevel(self.root)
        analysis_window.title("Player Data Analysis")
        analysis_window.geometry("500x400")
        
        try:
            
            analysis = self.analyze_player_data(self.player_data)
            
            
            scroll_frame = ctk.CTkScrollableFrame(analysis_window)
            scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
            
            
            ctk.CTkLabel(scroll_frame, text="General Statistics", 
                        font=("Arial", 16, "bold")).pack(pady=5)
            
            stats_text = (
                f"Total Players: {analysis['total_players']}\n"
                f"Average Level: {analysis['average_level']:.2f}\n"
                f"Total Playtime: {self.format_playtime(analysis['total_playtime'])}\n"
                f"Active Players (24h): {analysis['active_players']}"
            )
            
            ctk.CTkLabel(scroll_frame, text=stats_text, justify='left').pack(pady=5)
            
            
            if analysis['inventory_stats']:
                ctk.CTkLabel(scroll_frame, text="Common Items", 
                            font=("Arial", 16, "bold")).pack(pady=5)
                
                sorted_items = sorted(analysis['inventory_stats'].items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
                
                for item, count in sorted_items:
                    ctk.CTkLabel(scroll_frame, 
                                text=f"{item}: {count}",
                                justify='left').pack()
            
            
            if analysis['location_heatmap']:
                ctk.CTkLabel(scroll_frame, text="Player Distribution", 
                            font=("Arial", 16, "bold")).pack(pady=5)
                
                sorted_locations = sorted(analysis['location_heatmap'].items(), 
                                        key=lambda x: x[1], reverse=True)[:5]
                
                for loc, count in sorted_locations:
                    ctk.CTkLabel(scroll_frame, 
                                text=f"Region {loc}: {count} players",
                                justify='left').pack()
            
            
            def export_analysis():
                try:
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".txt",
                        filetypes=[("Text files", "*.txt")]
                    )
                    if file_path:
                        with open(file_path, 'w') as f:
                            f.write("Player Data Analysis\n\n")
                            f.write(stats_text + "\n\n")
                            if analysis['inventory_stats']:
                                f.write("Common Items:\n")
                                for item, count in sorted_items:
                                    f.write(f"{item}: {count}\n")
                            if analysis['location_heatmap']:
                                f.write("\nPlayer Distribution:\n")
                                for loc, count in sorted_locations:
                                    f.write(f"Region {loc}: {count} players\n")
                        self.update_status("Analysis exported successfully!")
                except Exception as e:
                    self.update_status(f"Export failed: {str(e)}", is_error=True)
            
            export_button = ctk.CTkButton(analysis_window, 
                                        text="Export Analysis",
                                        command=export_analysis)
            export_button.pack(pady=10)
            
        except Exception as e:
            self.update_status(f"Analysis failed: {str(e)}", is_error=True)
            analysis_window.destroy()

    def validate_refresh_interval(self, interval: str) -> tuple[bool, str]:
        try:
            value = int(interval)
            if value < 5:
                return False, "Refresh interval must be at least 5 seconds"
            if value > 3600:
                return False, "Refresh interval must be less than 1 hour"
            return True, ""
        except ValueError:
            return False, "Refresh interval must be a number"

    def safe_destroy_widget(self, widget):
        """Safely destroy a widget and handle any errors"""
        try:
            if widget and widget.winfo_exists():
                widget.destroy()
        except Exception:
            pass

    def clear_player_buttons(self):
        """Safely clear all player buttons"""
        try:
            
            for button in self.player_buttons:
                if button and button.winfo_exists():
                    button.after(10, button.destroy)  # Schedule destruction
            self.player_buttons.clear()
            
            
            for widget in self.player_data_frame.winfo_children():
                if widget.winfo_exists():
                    widget.after(10, widget.destroy)
        except Exception as e:
            print(f"Error clearing buttons: {e}")

    def cleanup(self):
        """Clean up resources before closing"""
        try:
            
            self.update_current_values()
            
            
            if hasattr(self, 'auto_refresh') and self.auto_refresh:
                self.stop_auto_refresh()
            
            
            self.save_config()
            
            
            if hasattr(self, 'player_buttons'):
                self.player_buttons.clear()
                
        except Exception as e:
            print(f"Cleanup error: {e}")

    def on_closing(self):
        """Handle application closing"""
        try:
            self.cleanup()
        finally:
            
            if self.root:
                self.root.destroy()

    def update_current_values(self):
        """Update stored values from widgets"""
        try:
            if hasattr(self, 'ip_entry') and self.ip_entry:
                self.current_ip = self.ip_entry.get()
            if hasattr(self, 'port_entry') and self.port_entry:
                self.current_port = self.port_entry.get()
        except Exception:
            pass

    def save_config(self):
        """Save current configuration"""
        try:
            
            self.update_current_values()
            
            
            self.config.update({
                "refresh_interval": getattr(self, 'refresh_interval', 30),
                "auto_refresh": getattr(self, 'auto_refresh', False),
                "theme": ctk.get_appearance_mode().lower(),
                "last_ip": self.current_ip,
                "last_port": self.current_port
            })
            
            # Save to file
            with open("config.json", "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

if __name__ == "__main__":
    root = ctk.CTk()
    app = None
    try:
        app = PlayerDataApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        if app:
            try:
                app.cleanup()
            except Exception as e:
                print(f"Final cleanup error: {e}")
