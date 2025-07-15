import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import json
from datetime import datetime
import sys
import os

# Import the ChatServer class
from server import ChatServer

class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chat Server Administration Panel")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Server instance
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Colors and styling
        self.bg_color = "#1a1a1a"
        self.text_color = "#ffffff"
        self.accent_color = "#0d7377"
        self.success_color = "#28a745"
        self.error_color = "#dc3545"
        self.warning_color = "#ffc107"
        self.info_color = "#17a2b8"
        self.panel_color = "#2d2d2d"
        
        # Data for monitoring
        self.client_data = {}
        self.room_data = {}
        self.message_log = []
        
        self.setup_gui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure the GUI styling"""
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure('Success.TButton', 
                       background=self.success_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Success.TButton',
                 background=[('active', '#218838')])
        
        style.configure('Error.TButton',
                       background=self.error_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Error.TButton',
                 background=[('active', '#c82333')])
        
        style.configure('Warning.TButton',
                       background=self.warning_color,
                       foreground='black',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Warning.TButton',
                 background=[('active', '#e0a800')])
        
        style.configure('Info.TButton',
                       background=self.info_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Info.TButton',
                 background=[('active', '#138496')])
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Server control frame
        self.setup_server_control(main_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Setup tabs
        self.setup_overview_tab()
        self.setup_clients_tab()
        self.setup_rooms_tab()
        self.setup_logs_tab()
        self.setup_admin_tab()
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_server_control(self, parent):
        """Setup server control panel"""
        control_frame = tk.Frame(parent, bg=self.panel_color, relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = tk.Label(control_frame, text="🖥️ Server Control Panel", 
                              bg=self.panel_color, fg=self.text_color, 
                              font=('Arial', 14, 'bold'))
        title_label.pack(pady=10)
        
        # Server settings
        settings_frame = tk.Frame(control_frame, bg=self.panel_color)
        settings_frame.pack(pady=(0, 10))
        
        tk.Label(settings_frame, text="Host:", bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT, padx=(10, 5))
        self.host_entry = tk.Entry(settings_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Label(settings_frame, text="Port:", bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry = tk.Entry(settings_frame, width=8)
        self.port_entry.insert(0, "55555")
        self.port_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=self.panel_color)
        button_frame.pack(pady=(0, 10))
        
        self.start_btn = ttk.Button(button_frame, text="🚀 Start Server", 
                                   command=self.start_server, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(10, 5))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Server", 
                                  command=self.stop_server, style='Error.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=(5, 5))
        self.stop_btn.configure(state='disabled')
        
        self.restart_btn = ttk.Button(button_frame, text="🔄 Restart Server", 
                                     command=self.restart_server, style='Warning.TButton')
        self.restart_btn.pack(side=tk.LEFT, padx=(5, 10))
        self.restart_btn.configure(state='disabled')
        
        # Server status
        self.server_status = tk.Label(control_frame, text="⚫ Server Stopped", 
                                     bg=self.panel_color, fg=self.error_color,
                                     font=('Arial', 12, 'bold'))
        self.server_status.pack(pady=(0, 10))
    
    def setup_overview_tab(self):
        """Setup overview tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📊 Overview")
        
        # Statistics frame
        stats_frame = tk.Frame(overview_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(stats_frame, text="📈 Server Statistics", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Stats grid
        stats_grid = tk.Frame(stats_frame, bg=self.panel_color)
        stats_grid.pack(pady=(0, 10))
        
        # Connected clients
        self.clients_count_label = tk.Label(stats_grid, text="Connected Clients: 0", 
                                           bg=self.panel_color, fg=self.text_color, 
                                           font=('Arial', 10))
        self.clients_count_label.grid(row=0, column=0, padx=20, pady=5, sticky='w')
        
        # Active rooms
        self.rooms_count_label = tk.Label(stats_grid, text="Active Rooms: 0", 
                                         bg=self.panel_color, fg=self.text_color, 
                                         font=('Arial', 10))
        self.rooms_count_label.grid(row=0, column=1, padx=20, pady=5, sticky='w')
        
        # Messages sent
        self.messages_count_label = tk.Label(stats_grid, text="Messages Sent: 0", 
                                            bg=self.panel_color, fg=self.text_color, 
                                            font=('Arial', 10))
        self.messages_count_label.grid(row=1, column=0, padx=20, pady=5, sticky='w')
        
        # Server uptime
        self.uptime_label = tk.Label(stats_grid, text="Uptime: 00:00:00", 
                                    bg=self.panel_color, fg=self.text_color, 
                                    font=('Arial', 10))
        self.uptime_label.grid(row=1, column=1, padx=20, pady=5, sticky='w')
        
        # Real-time activity feed
        activity_frame = tk.Frame(overview_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        tk.Label(activity_frame, text="🔔 Real-time Activity", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        self.activity_display = scrolledtext.ScrolledText(activity_frame, 
                                                         height=15,
                                                         state=tk.DISABLED,
                                                         bg='#000000',
                                                         fg='#00ff00',
                                                         font=('Consolas', 9),
                                                         wrap=tk.WORD)
        self.activity_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure activity text tags
        self.activity_display.tag_configure("connect", foreground="#00ff00")
        self.activity_display.tag_configure("disconnect", foreground="#ff6666")
        self.activity_display.tag_configure("message", foreground="#66ccff")
        self.activity_display.tag_configure("room", foreground="#ffcc66")
        self.activity_display.tag_configure("admin", foreground="#ff66ff")
    
    def setup_clients_tab(self):
        """Setup clients management tab"""
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="👥 Clients")
        
        # Client list
        list_frame = tk.Frame(clients_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(list_frame, text="👥 Connected Clients", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        # Treeview for clients
        columns = ('Nickname', 'Address', 'Room', 'Connected Since', 'Messages Sent')
        self.clients_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.clients_tree.heading(col, text=col)
            self.clients_tree.column(col, width=100)
        
        # Scrollbars for treeview
        clients_scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.clients_tree.yview)
        clients_scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.clients_tree.xview)
        self.clients_tree.configure(yscrollcommand=clients_scrollbar_y.set, xscrollcommand=clients_scrollbar_x.set)
        
        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        clients_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        clients_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, padx=(10, 0))
        
        # Client management buttons
        client_buttons = tk.Frame(clients_frame, bg=self.bg_color)
        client_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(client_buttons, text="📨 Message Client", 
                  command=self.message_client, style='Info.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(client_buttons, text="🚫 Kick Client", 
                  command=self.kick_client, style='Error.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(client_buttons, text="🔄 Refresh", 
                  command=self.refresh_clients, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_rooms_tab(self):
        """Setup rooms management tab"""
        rooms_frame = ttk.Frame(self.notebook)
        self.notebook.add(rooms_frame, text="🏠 Rooms")
        
        # Rooms list
        rooms_list_frame = tk.Frame(rooms_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        rooms_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(rooms_list_frame, text="🏠 Active Rooms", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        # Treeview for rooms
        room_columns = ('Room Name', 'Users Count', 'Created', 'Last Activity')
        self.rooms_tree = ttk.Treeview(rooms_list_frame, columns=room_columns, show='headings', height=15)
        
        for col in room_columns:
            self.rooms_tree.heading(col, text=col)
            self.rooms_tree.column(col, width=120)
        
        # Scrollbars for rooms treeview
        rooms_scrollbar_y = ttk.Scrollbar(rooms_list_frame, orient=tk.VERTICAL, command=self.rooms_tree.yview)
        rooms_scrollbar_x = ttk.Scrollbar(rooms_list_frame, orient=tk.HORIZONTAL, command=self.rooms_tree.xview)
        self.rooms_tree.configure(yscrollcommand=rooms_scrollbar_y.set, xscrollcommand=rooms_scrollbar_x.set)
        
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        rooms_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        rooms_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X, padx=(10, 0))
        
        # Room management buttons
        room_buttons = tk.Frame(rooms_frame, bg=self.bg_color)
        room_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(room_buttons, text="📢 Broadcast to Room", 
                  command=self.broadcast_to_room, style='Info.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(room_buttons, text="🗑️ Delete Room", 
                  command=self.delete_room, style='Error.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(room_buttons, text="🔄 Refresh", 
                  command=self.refresh_rooms, style='Success.TButton').pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_logs_tab(self):
        """Setup logs tab"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="📜 Logs")
        
        # Log controls
        log_controls = tk.Frame(logs_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        log_controls.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(log_controls, text="📜 Message Logs", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10, pady=10)
        
        ttk.Button(log_controls, text="🗑️ Clear Logs", 
                  command=self.clear_logs, style='Warning.TButton').pack(side=tk.RIGHT, padx=10, pady=10)
        ttk.Button(log_controls, text="💾 Export Logs", 
                  command=self.export_logs, style='Info.TButton').pack(side=tk.RIGHT, padx=(0, 5), pady=10)
        
        # Logs display
        self.logs_display = scrolledtext.ScrolledText(logs_frame, 
                                                     height=25,
                                                     state=tk.DISABLED,
                                                     bg='#000000',
                                                     fg='#ffffff',
                                                     font=('Consolas', 9),
                                                     wrap=tk.WORD)
        self.logs_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Configure log text tags
        self.logs_display.tag_configure("public", foreground="#66ccff")
        self.logs_display.tag_configure("private", foreground="#ff66ff")
        self.logs_display.tag_configure("system", foreground="#ffcc66")
        self.logs_display.tag_configure("admin", foreground="#ff6666")
    
    def setup_admin_tab(self):
        """Setup admin tools tab"""
        admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(admin_frame, text="🛠️ Admin Tools")
        
        # Broadcast section
        broadcast_frame = tk.Frame(admin_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        broadcast_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(broadcast_frame, text="📢 Global Broadcast", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        broadcast_input_frame = tk.Frame(broadcast_frame, bg=self.panel_color)
        broadcast_input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.broadcast_entry = tk.Entry(broadcast_input_frame, font=('Arial', 11))
        self.broadcast_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.broadcast_entry.bind('<Return>', lambda e: self.global_broadcast())
        
        ttk.Button(broadcast_input_frame, text="📢 Send", 
                  command=self.global_broadcast, style='Info.TButton').pack(side=tk.RIGHT)
        
        # Server management
        management_frame = tk.Frame(admin_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        management_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(management_frame, text="🛠️ Server Management", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        management_buttons = tk.Frame(management_frame, bg=self.panel_color)
        management_buttons.pack(pady=(0, 10))
        
        ttk.Button(management_buttons, text="🚫 Kick All Users", 
                  command=self.kick_all_users, style='Error.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(management_buttons, text="🗑️ Clear All Rooms", 
                  command=self.clear_all_rooms, style='Warning.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(management_buttons, text="📊 Generate Report", 
                  command=self.generate_report, style='Info.TButton').pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh settings
        auto_frame = tk.Frame(admin_frame, bg=self.panel_color, relief=tk.RAISED, bd=1)
        auto_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(auto_frame, text="⚙️ Auto-Refresh Settings", 
                bg=self.panel_color, fg=self.text_color, 
                font=('Arial', 12, 'bold')).pack(pady=(10, 5))
        
        auto_controls = tk.Frame(auto_frame, bg=self.panel_color)
        auto_controls.pack(pady=(0, 10))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_checkbox = tk.Checkbutton(auto_controls, text="Auto-refresh every 5 seconds", 
                                      variable=self.auto_refresh_var,
                                      bg=self.panel_color, fg=self.text_color,
                                      selectcolor=self.panel_color,
                                      command=self.toggle_auto_refresh)
        auto_checkbox.pack(side=tk.LEFT, padx=10)
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_bar = tk.Label(parent, text="Ready", 
                                  bg=self.panel_color, fg=self.text_color,
                                  relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def start_server(self):
        """Start the chat server"""
        try:
            host = self.host_entry.get().strip()
            try:
                port = int(self.port_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid port number!")
                return
            
            # Create enhanced server instance
            self.server = EnhancedChatServer(host, port, self)
            self.server_thread = threading.Thread(target=self.server.start_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            self.server_status.configure(text="🟢 Server Running", fg=self.success_color)
            self.start_btn.configure(state='disabled')
            self.stop_btn.configure(state='normal')
            self.restart_btn.configure(state='normal')
            
            self.log_activity("Server started", "admin")
            self.update_status(f"Server running on {host}:{port}")
            
            # Start auto-refresh
            if self.auto_refresh_var.get():
                self.auto_refresh()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")
    
    def stop_server(self):
        """Stop the chat server"""
        try:
            if self.server:
                self.server.shutdown_server()
            
            self.running = False
            self.server_status.configure(text="⚫ Server Stopped", fg=self.error_color)
            self.start_btn.configure(state='normal')
            self.stop_btn.configure(state='disabled')
            self.restart_btn.configure(state='disabled')
            
            self.log_activity("Server stopped", "admin")
            self.update_status("Server stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {e}")
    
    def restart_server(self):
        """Restart the chat server"""
        self.log_activity("Server restarting...", "admin")
        self.stop_server()
        self.root.after(2000, self.start_server)  # Wait 2 seconds before restarting
    
    def log_activity(self, message, tag="system"):
        """Log activity to the activity display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.activity_display.configure(state=tk.NORMAL)
        self.activity_display.insert(tk.END, formatted_message, tag)
        self.activity_display.configure(state=tk.DISABLED)
        self.activity_display.see(tk.END)
    
    def log_message(self, message, tag="system"):
        """Log message to the logs display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.logs_display.configure(state=tk.NORMAL)
        self.logs_display.insert(tk.END, formatted_message, tag)
        self.logs_display.configure(state=tk.DISABLED)
        self.logs_display.see(tk.END)
        
        # Store in message log
        self.message_log.append({
            'timestamp': timestamp,
            'message': message,
            'tag': tag
        })
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.configure(text=message)
    
    def update_statistics(self):
        """Update server statistics"""
        if self.server and self.running:
            client_count = len(self.server.clients)
            room_count = len(self.server.rooms)
            message_count = len(self.message_log)
            
            self.clients_count_label.configure(text=f"Connected Clients: {client_count}")
            self.rooms_count_label.configure(text=f"Active Rooms: {room_count}")
            self.messages_count_label.configure(text=f"Messages Sent: {message_count}")
    
    def refresh_clients(self):
        """Refresh clients list"""
        # Clear existing items
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)
        
        if self.server and self.running:
            for client_socket, info in self.server.clients.items():
                try:
                    address = client_socket.getpeername()
                    nickname = info['nickname']
                    room = info['room'] or "None"
                    connected_since = "N/A"  # Could be tracked if needed
                    messages_sent = "N/A"    # Could be tracked if needed
                    
                    self.clients_tree.insert('', tk.END, values=(
                        nickname, f"{address[0]}:{address[1]}", room, 
                        connected_since, messages_sent
                    ))
                except:
                    pass
    
    def refresh_rooms(self):
        """Refresh rooms list"""
        # Clear existing items
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
        
        if self.server and self.running:
            for room_name, clients in self.server.rooms.items():
                user_count = len(clients)
                created = "N/A"  # Could be tracked if needed
                last_activity = "N/A"  # Could be tracked if needed
                
                self.rooms_tree.insert('', tk.END, values=(
                    room_name, user_count, created, last_activity
                ))
    
    def auto_refresh(self):
        """Auto-refresh data"""
        if self.running and self.auto_refresh_var.get():
            self.update_statistics()
            self.refresh_clients()
            self.refresh_rooms()
            self.root.after(5000, self.auto_refresh)  # Refresh every 5 seconds
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        if self.auto_refresh_var.get() and self.running:
            self.auto_refresh()
    
    def global_broadcast(self):
        """Send global broadcast message"""
        message = self.broadcast_entry.get().strip()
        if not message:
            return
        
        if self.server and self.running:
            self.server.global_broadcast(message)
            self.broadcast_entry.delete(0, tk.END)
            self.log_activity(f"Global broadcast: {message}", "admin")
            self.log_message(f"ADMIN BROADCAST: {message}", "admin")
        else:
            messagebox.showwarning("Warning", "Server is not running!")
    
    def message_client(self):
        """Send message to selected client"""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a client!")
            return
        
        item = self.clients_tree.item(selection[0])
        nickname = item['values'][0]
        
        message = simpledialog.askstring("Message Client", 
                                       f"Send message to {nickname}:", 
                                       parent=self.root)
        if message and self.server:
            self.server.message_client(nickname, message)
            self.log_activity(f"Sent message to {nickname}: {message}", "admin")
    
    def kick_client(self):
        """Kick selected client"""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a client!")
            return
        
        item = self.clients_tree.item(selection[0])
        nickname = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Kick user {nickname}?"):
            if self.server:
                self.server.kick_client(nickname)
                self.log_activity(f"Kicked user: {nickname}", "admin")
                self.refresh_clients()
    
    def broadcast_to_room(self):
        """Broadcast to selected room"""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a room!")
            return
        
        item = self.rooms_tree.item(selection[0])
        room_name = item['values'][0]
        
        message = simpledialog.askstring("Broadcast to Room", 
                                       f"Broadcast to room '{room_name}':", 
                                       parent=self.root)
        if message and self.server:
            self.server.broadcast_to_room(room_name, "ADMIN_MSG", f"ADMIN: {message}")
            self.log_activity(f"Broadcast to {room_name}: {message}", "admin")
    
    def delete_room(self):
        """Delete selected room"""
        selection = self.rooms_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a room!")
            return
        
        item = self.rooms_tree.item(selection[0])
        room_name = item['values'][0]
        
        if messagebox.askyesno("Confirm", f"Delete room '{room_name}' and kick all users?"):
            if self.server:
                self.server.delete_room(room_name)
                self.log_activity(f"Deleted room: {room_name}", "admin")
                self.refresh_rooms()
    
    def kick_all_users(self):
        """Kick all users"""
        if messagebox.askyesno("Confirm", "Kick ALL users from the server?"):
            if self.server:
                self.server.kick_all_users()
                self.log_activity("Kicked all users", "admin")
                self.refresh_clients()
    
    def clear_all_rooms(self):
        """Clear all rooms"""
        if messagebox.askyesno("Confirm", "Delete ALL rooms?"):
            if self.server:
                self.server.clear_all_rooms()
                self.log_activity("Cleared all rooms", "admin")
                self.refresh_rooms()
    
    def clear_logs(self):
        """Clear all logs"""
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            self.logs_display.configure(state=tk.NORMAL)
            self.logs_display.delete(1.0, tk.END)
            self.logs_display.configure(state=tk.DISABLED)
            self.message_log.clear()
            self.log_activity("Logs cleared", "admin")
    
    def export_logs(self):
        """Export logs to file"""
        if not self.message_log:
            messagebox.showinfo("Info", "No logs to export!")
            return
        
        try:
            filename = f"chat_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(f"Chat Server Logs - Exported on {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                for log_entry in self.message_log:
                    f.write(f"[{log_entry['timestamp']}] {log_entry['message']}\n")
            
            messagebox.showinfo("Success", f"Logs exported to {filename}")
            self.log_activity(f"Logs exported to {filename}", "admin")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def generate_report(self):
        """Generate server report"""
        if not self.running:
            messagebox.showwarning("Warning", "Server is not running!")
            return
        
        try:
            report = f"""
CHAT SERVER REPORT
Generated: {datetime.now()}
=====================================

SERVER STATUS:
- Status: Running
- Host: {self.host_entry.get()}
- Port: {self.port_entry.get()}

STATISTICS:
- Connected Clients: {len(self.server.clients) if self.server else 0}
- Active Rooms: {len(self.server.rooms) if self.server else 0}
- Total Messages: {len(self.message_log)}

RECENT ACTIVITY:
{chr(10).join([f"[{entry['timestamp']}] {entry['message']}" for entry in self.message_log[-10:]])}
"""
            
            filename = f"server_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(report)
            
            messagebox.showinfo("Success", f"Report generated: {filename}")
            self.log_activity(f"Generated report: {filename}", "admin")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            if messagebox.askyesno("Confirm", "Server is running. Stop server and exit?"):
                self.stop_server()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add welcome message
        self.log_activity("Server Admin Panel started", "admin")
        self.update_status("Ready to start server")
        
        self.root.mainloop()


class EnhancedChatServer(ChatServer):
    """Enhanced chat server with admin features"""
    
    def __init__(self, host='localhost', port=55555, gui=None):
        super().__init__(host, port)
        self.gui = gui
    
    def handle_client(self, client_socket, address):
        """Enhanced client handling with GUI logging"""
        try:
            # Call parent method but with logging
            if self.gui:
                self.gui.log_activity(f"New connection from {address}", "connect")
            
            super().handle_client(client_socket, address)
            
        except Exception as e:
            if self.gui:
                self.gui.log_activity(f"Client handling error: {e}", "disconnect")
    
    def send_message(self, client_socket, msg_type, content):
        """Enhanced message sending with logging"""
        super().send_message(client_socket, msg_type, content)
        
        # Only log non-echo messages (don't log "You: ..." messages)
        if self.gui and msg_type in ['PUBLIC_MSG', 'PRIVATE_MSG'] and not content.startswith('You: '):
            self.gui.log_message(content, msg_type.lower().replace('_msg', ''))
    
    def disconnect_client(self, client_socket):
        """Enhanced client disconnection with logging"""
        if client_socket in self.clients and self.gui:
            nickname = self.clients[client_socket]['nickname']
            self.gui.log_activity(f"Client {nickname} disconnected", "disconnect")
        
        super().disconnect_client(client_socket)
    
    def global_broadcast(self, message):
        """Send global broadcast to all clients"""
        for client_socket in list(self.clients.keys()):
            self.send_message(client_socket, "ADMIN_MSG", f"📢 ADMIN: {message}")
    
    def message_client(self, nickname, message):
        """Send private message to specific client"""
        for client_socket, info in self.clients.items():
            if info['nickname'] == nickname:
                self.send_message(client_socket, "ADMIN_MSG", f"👤 ADMIN: {message}")
                return True
        return False
    
    def kick_client(self, nickname):
        """Kick a specific client"""
        for client_socket, info in list(self.clients.items()):
            if info['nickname'] == nickname:
                self.send_message(client_socket, "ADMIN_MSG", "You have been kicked by an administrator.")
                self.disconnect_client(client_socket)
                return True
        return False
    
    def delete_room(self, room_name):
        """Delete a room and kick all users"""
        if room_name in self.rooms:
            clients_in_room = list(self.rooms[room_name])
            for client in clients_in_room:
                self.send_message(client, "ADMIN_MSG", f"Room '{room_name}' has been deleted by an administrator.")
                self.clients[client]['room'] = None
            del self.rooms[room_name]
    
    def kick_all_users(self):
        """Kick all users from the server"""
        for client_socket in list(self.clients.keys()):
            self.send_message(client_socket, "ADMIN_MSG", "Server maintenance. All users disconnected.")
            self.disconnect_client(client_socket)
    
    def clear_all_rooms(self):
        """Clear all rooms"""
        for room_name in list(self.rooms.keys()):
            self.delete_room(room_name)


def main():
    """Main function to run the server GUI"""
    app = ServerGUI()
    app.run()


if __name__ == "__main__":
    main()
