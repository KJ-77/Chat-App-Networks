import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog, filedialog
import socket
import threading
import json
import base64
import os

class ChatGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Python Chat Application")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Chat client connection variables
        self.client_socket = None
        self.nickname = None
        self.connected = False
        self.current_room = None
        self.host = 'localhost'
        self.port = 55555
        
        # Colors and styling
        self.bg_color = "#2c3e50"
        self.text_color = "#ecf0f1"
        self.accent_color = "#3498db"
        self.success_color = "#27ae60"
        self.error_color = "#e74c3c"
        self.message_color = "#34495e"
        
        self.setup_gui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure the GUI styling"""
        self.root.configure(bg=self.bg_color)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure('Accent.TButton', 
                       background=self.accent_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Accent.TButton',
                 background=[('active', '#2980b9')])
        
        style.configure('Success.TButton',
                       background=self.success_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        
        style.configure('Error.TButton',
                       background=self.error_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        style.map('Error.TButton',
                 background=[('active', '#c0392b')])
    
    def setup_gui(self):
        """Setup the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Connection frame
        self.connection_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.connection_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connection status and controls
        self.setup_connection_frame()
        
        # Chat area frame
        chat_frame = tk.Frame(main_frame, bg=self.bg_color)
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (chat area)
        left_panel = tk.Frame(chat_frame, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right panel (users and rooms)
        right_panel = tk.Frame(chat_frame, bg=self.bg_color, width=200)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        self.setup_chat_area(left_panel)
        self.setup_right_panel(right_panel)
        self.setup_input_area(main_frame)
        
        # Initially disable chat controls
        self.toggle_chat_controls(False)
    
    def setup_connection_frame(self):
        """Setup connection controls"""
        # Status label
        self.status_label = tk.Label(self.connection_frame, 
                                   text="Not connected", 
                                   bg=self.bg_color, 
                                   fg=self.error_color,
                                   font=('Arial', 12, 'bold'))
        self.status_label.pack(side=tk.LEFT)
        
        # Connection controls
        control_frame = tk.Frame(self.connection_frame, bg=self.bg_color)
        control_frame.pack(side=tk.RIGHT)
        
        # Server input
        tk.Label(control_frame, text="Server:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 5))
        self.host_entry = tk.Entry(control_frame, width=15)
        self.host_entry.insert(0, self.host)
        self.host_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Label(control_frame, text="Port:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry = tk.Entry(control_frame, width=8)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Connect/Disconnect buttons
        self.connect_btn = ttk.Button(control_frame, text="Connect", 
                                     command=self.connect_to_server, style='Success.TButton')
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.disconnect_btn = ttk.Button(control_frame, text="Disconnect", 
                                        command=self.disconnect_from_server, style='Error.TButton')
        self.disconnect_btn.pack(side=tk.LEFT)
        self.disconnect_btn.configure(state='disabled')
    
    def setup_chat_area(self, parent):
        """Setup the main chat display area"""
        # Chat display
        chat_label = tk.Label(parent, text="Chat Messages", bg=self.bg_color, fg=self.text_color, font=('Arial', 12, 'bold'))
        chat_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.chat_display = scrolledtext.ScrolledText(parent, 
                                                     height=20,
                                                     state=tk.DISABLED,
                                                     bg='white',
                                                     fg='black',
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("system", foreground="#7f8c8d", font=('Consolas', 10, 'italic'))
        self.chat_display.tag_configure("public", foreground="#2c3e50", font=('Consolas', 10))
        self.chat_display.tag_configure("private", foreground="#8e44ad", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("user_joined", foreground="#27ae60", font=('Consolas', 10))
        self.chat_display.tag_configure("user_left", foreground="#e67e22", font=('Consolas', 10))
        self.chat_display.tag_configure("error", foreground="#e74c3c", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("timestamp", foreground="#95a5a6", font=('Consolas', 9))
        self.chat_display.tag_configure("file", foreground="#3498db", font=('Consolas', 10, 'bold'))
        self.chat_display.tag_configure("file_link", 
                                       foreground="#0066cc", 
                                       font=('Consolas', 10, 'underline'),
                                       background="#f0f8ff")
        
        # Bind click events for file links
        self.chat_display.tag_bind("file_link", "<Button-1>", self.handle_file_click)
        
        # Add hover effect for file links
        def on_enter(event):
            self.chat_display.config(cursor="hand2")
        
        def on_leave(event):
            self.chat_display.config(cursor="")
        
        self.chat_display.tag_bind("file_link", "<Enter>", on_enter)
        self.chat_display.tag_bind("file_link", "<Leave>", on_leave)
    
    def setup_right_panel(self, parent):
        """Setup the right panel with users and rooms"""
        # Current room
        room_label = tk.Label(parent, text="Current Room", bg=self.bg_color, fg=self.text_color, font=('Arial', 11, 'bold'))
        room_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.current_room_label = tk.Label(parent, text="None", bg=self.message_color, fg=self.text_color, 
                                          relief=tk.SUNKEN, padx=10, pady=5)
        self.current_room_label.pack(fill=tk.X, pady=(0, 10))
        
        # Room controls
        room_controls = tk.Frame(parent, bg=self.bg_color)
        room_controls.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(room_controls, text="Join Room", command=self.join_room_dialog, style='Accent.TButton').pack(fill=tk.X, pady=(0, 2))
        ttk.Button(room_controls, text="Leave Room", command=self.leave_current_room, style='Error.TButton').pack(fill=tk.X, pady=(0, 2))
        ttk.Button(room_controls, text="📎 Send File", command=self.send_file_to_room, style='Accent.TButton').pack(fill=tk.X)
        
        # Online users
        users_label = tk.Label(parent, text="Online Users", bg=self.bg_color, fg=self.text_color, font=('Arial', 11, 'bold'))
        users_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.users_listbox = tk.Listbox(parent, height=8, bg='white', fg='black', font=('Arial', 9))
        self.users_listbox.pack(fill=tk.X, pady=(0, 10))
        self.users_listbox.bind('<Double-Button-1>', self.private_message_dialog)
        
        # Rooms list
        rooms_label = tk.Label(parent, text="Active Rooms", bg=self.bg_color, fg=self.text_color, font=('Arial', 11, 'bold'))
        rooms_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.rooms_listbox = tk.Listbox(parent, height=6, bg='white', fg='black', font=('Arial', 9))
        self.rooms_listbox.pack(fill=tk.X, pady=(0, 10))
        self.rooms_listbox.bind('<Double-Button-1>', self.join_room_from_list)
        
        # Refresh button
        ttk.Button(parent, text="Refresh Lists", command=self.refresh_lists, style='Accent.TButton').pack(fill=tk.X)
    
    def setup_input_area(self, parent):
        """Setup message input area"""
        input_frame = tk.Frame(parent, bg=self.bg_color)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Message input
        self.message_entry = tk.Entry(input_frame, font=('Arial', 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind('<Return>', self.send_message)
        
        # File button
        self.file_btn = ttk.Button(input_frame, text="📎", 
                                  command=self.send_file_private, style='Accent.TButton')
        self.file_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Send button
        self.send_btn = ttk.Button(input_frame, text="Send Message", 
                                  command=self.send_message, style='Success.TButton')
        self.send_btn.pack(side=tk.RIGHT)
    
    def toggle_chat_controls(self, enabled):
        """Enable/disable chat controls based on connection status"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.message_entry.configure(state=state)
        self.send_btn.configure(state=state)
        self.file_btn.configure(state=state)
        self.users_listbox.configure(state=state)
        self.rooms_listbox.configure(state=state)
        
        # Toggle connection buttons
        if enabled:
            self.connect_btn.configure(state='disabled')
            self.disconnect_btn.configure(state='normal')
        else:
            self.connect_btn.configure(state='normal')
            self.disconnect_btn.configure(state='disabled')
    
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            # Get connection details
            self.host = self.host_entry.get().strip()
            try:
                self.port = int(self.port_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid port number!")
                return
            
            # Get nickname
            self.nickname = simpledialog.askstring("Nickname", "Enter your nickname:", 
                                                  parent=self.root)
            if not self.nickname or not self.nickname.strip():
                return
            
            self.nickname = self.nickname.strip()
            if ' ' in self.nickname:
                messagebox.showerror("Error", "Nickname cannot contain spaces!")
                return
            
            # Connect to server
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            
            # Start receiving messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Update UI
            self.status_label.configure(text=f"Connected as {self.nickname}", fg=self.success_color)
            self.toggle_chat_controls(True)
            self.add_message_to_chat("Connected to server!", "system")
            
            # Focus on message input
            self.message_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.connected = False
    
    def disconnect_from_server(self):
        """Disconnect from the server"""
        try:
            self.connected = False
            if self.client_socket:
                self.client_socket.close()
            
            # Update UI
            self.status_label.configure(text="Not connected", fg=self.error_color)
            self.current_room_label.configure(text="None")
            self.current_room = None
            self.toggle_chat_controls(False)
            self.add_message_to_chat("Disconnected from server", "system")
            
            # Clear lists
            self.users_listbox.delete(0, tk.END)
            self.rooms_listbox.delete(0, tk.END)
            
        except Exception as e:
            print(f"Error disconnecting: {e}")
    
    def receive_messages(self):
        """Listen for messages from the server"""
        while self.connected:
            try:
                # First, receive the length of the message
                length_data = self.client_socket.recv(4)
                if not length_data:
                    break
                
                message_length = int.from_bytes(length_data, byteorder='big')
                
                # Now receive the actual message
                message_data = b''
                while len(message_data) < message_length:
                    chunk = self.client_socket.recv(min(4096, message_length - len(message_data)))
                    if not chunk:
                        break
                    message_data += chunk
                
                if len(message_data) != message_length:
                    break
                
                message = message_data.decode('utf-8')
                if message:
                    # Handle nickname request (plain text)
                    if "Please enter your nickname:" in message or message.startswith("NICK_REQUEST"):
                        nickname_bytes = self.nickname.encode('utf-8')
                        length_bytes = len(nickname_bytes).to_bytes(4, byteorder='big')
                        self.client_socket.send(length_bytes + nickname_bytes)
                        continue
                    
                    # Parse JSON message
                    try:
                        data = json.loads(message)
                        self.handle_server_message(data)
                    except json.JSONDecodeError:
                        # Handle plain text messages
                        if "already taken" in message.lower() or "invalid" in message.lower():
                            self.root.after(0, lambda: self.add_message_to_chat(f"Error: {message}", "error"))
                            self.root.after(0, self.disconnect_from_server)
                        else:
                            self.root.after(0, lambda: self.add_message_to_chat(f"Server: {message}", "system"))
                else:
                    print("Server disconnected")
                    self.connected = False
                    break
            except ConnectionResetError:
                print("Connection to server lost")
                self.connected = False
                break
            except Exception as e:
                if self.connected:
                    print(f"Connection error: {e}")
                    self.root.after(0, lambda: self.add_message_to_chat(f"Connection error: {e}", "error"))
                    self.connected = False
                break
    
    def handle_server_message(self, data):
        """Handle different types of messages from the server"""
        msg_type = data.get('type', '')
        content = data.get('content', '')
        timestamp = data.get('timestamp', '')
        
        # Use root.after to update GUI from thread
        if msg_type == 'NICK_ACCEPTED':
            self.root.after(0, lambda: self.add_message_to_chat(content, "system"))
        elif msg_type == 'NICK_ERROR':
            self.root.after(0, lambda: self.add_message_to_chat(f"Error: {content}", "error"))
            self.root.after(0, self.disconnect_from_server)
        elif msg_type == 'ROOM_JOINED':
            room_name = content.split(': ')[1] if ': ' in content else "Unknown"
            self.current_room = room_name
            self.root.after(0, lambda: self.current_room_label.configure(text=room_name))
            self.root.after(0, lambda: self.add_message_to_chat(content, "system"))
        elif msg_type == 'ROOM_LEFT':
            self.current_room = None
            self.root.after(0, lambda: self.current_room_label.configure(text="None"))
            self.root.after(0, lambda: self.add_message_to_chat(content, "system"))
        elif msg_type == 'PUBLIC_MSG':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] {content}", "public"))
        elif msg_type == 'PRIVATE_MSG':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] 🔒 {content}", "private"))
        elif msg_type == 'USER_JOINED':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] 👋 {content}", "user_joined"))
        elif msg_type == 'USER_LEFT':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] 👋 {content}", "user_left"))
        elif msg_type == 'LIST_RESPONSE':
            self.root.after(0, lambda: self.update_lists(content))
        elif msg_type == 'ERROR':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] ❌ Error: {content}", "error"))
        elif msg_type == 'FILE_SENT':
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] 📎 {content}", "system"))
        elif msg_type == 'FILE_RECEIVED':
            self.root.after(0, lambda: self.handle_received_file(data))
        else:
            self.root.after(0, lambda: self.add_message_to_chat(f"[{timestamp}] {content}", "system"))
    
    def add_message_to_chat(self, message, tag="public"):
        """Add a message to the chat display"""
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, message + "\n", tag)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_message(self, event=None):
        """Send a message to the server"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        try:
            # Parse command or send as public message
            if message.startswith('/'):
                # Handle slash commands
                self.handle_slash_command(message[1:])
            else:
                # Send as public message
                self.send_command('MSG', message)
            
            self.message_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
    
    def handle_slash_command(self, command):
        """Handle slash commands"""
        parts = command.split(' ', 1)
        cmd = parts[0].upper()
        content = parts[1] if len(parts) > 1 else ""
        
        if cmd == 'JOIN':
            if content:
                self.send_command('JOIN', content)
            else:
                self.join_room_dialog()
        elif cmd == 'LEAVE':
            self.send_command('LEAVE')
        elif cmd == 'LIST':
            self.send_command('LIST')
        elif cmd == 'MSG' and ':' in content:
            self.send_command('MSG', content)
        elif cmd == 'HELP':
            self.show_help()
        else:
            self.add_message_to_chat("Unknown command. Type /help for help.", "error")
    
    def send_command(self, command, content=""):
        """Send a command to the server"""
        try:
            if not self.connected:
                self.add_message_to_chat("Not connected to server!", "error")
                return
                
            message = {
                'command': command,
                'content': content
            }
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            print(f"Sending command: {command} with content: {content}")  # Debug
            self.client_socket.send(length_bytes + message_bytes)
        except Exception as e:
            print(f"Error sending command: {e}")  # Debug
            self.add_message_to_chat(f"Error sending command: {e}", "error")
            self.connected = False
    
    def join_room_dialog(self):
        """Show dialog to join a room"""
        room_name = simpledialog.askstring("Join Room", "Enter room name:", parent=self.root)
        if room_name and room_name.strip():
            self.send_command('JOIN', room_name.strip())
    
    def leave_current_room(self):
        """Leave the current room"""
        if self.current_room:
            self.send_command('LEAVE')
        else:
            messagebox.showinfo("Info", "You are not in any room!")
    
    def join_room_from_list(self, event):
        """Join room from double-clicking the rooms list"""
        selection = self.rooms_listbox.curselection()
        if selection:
            room_info = self.rooms_listbox.get(selection[0])
            room_name = room_info.split(' (')[0]  # Extract room name
            self.send_command('JOIN', room_name)
    
    def private_message_dialog(self, event):
        """Send private message from double-clicking users list"""
        selection = self.users_listbox.curselection()
        if selection:
            user_info = self.users_listbox.get(selection[0])
            username = user_info.split(' (')[0]  # Extract username
            
            if username == self.nickname:
                messagebox.showinfo("Info", "You cannot send a message to yourself!")
                return
            
            message = simpledialog.askstring("Private Message", 
                                           f"Send private message to {username}:", 
                                           parent=self.root)
            if message:
                self.send_command('MSG', f"{username}:{message}")
    
    def refresh_lists(self):
        """Refresh users and rooms lists"""
        self.send_command('LIST')
    
    def update_lists(self, list_content):
        """Update users and rooms lists from server response"""
        lines = list_content.split('\n')
        
        # Clear lists
        self.users_listbox.delete(0, tk.END)
        self.rooms_listbox.delete(0, tk.END)
        
        # Parse response
        current_section = None
        for line in lines:
            line = line.strip()
            if line == "Active Users:":
                current_section = "users"
            elif line == "Active Rooms:":
                current_section = "rooms"
            elif line and current_section == "users":
                self.users_listbox.insert(tk.END, line)
            elif line and current_section == "rooms":
                self.rooms_listbox.insert(tk.END, line)
    
    def show_help(self):
        """Show help dialog"""
        help_text = """Chat Commands:
        
/join <room> - Join or create a room
/leave - Leave current room
/list - Show users and rooms
/msg <user>:<message> - Send private message
/help - Show this help

You can also:
• Type messages directly to send to current room
• Double-click a user to send private message
• Double-click a room to join it
• Use the buttons and dialogs for easy access"""
        
        messagebox.showinfo("Help", help_text)
    
    def on_closing(self):
        """Handle window closing"""
        if self.connected:
            self.disconnect_from_server()
        self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Add help text to chat
        self.add_message_to_chat("=== Welcome to Python Chat GUI ===", "system")
        self.add_message_to_chat("Click 'Connect' to join the chat server", "system")
        self.add_message_to_chat("Type /help for commands or use the GUI buttons", "system")
        self.add_message_to_chat("", "system")
        
        self.root.mainloop()

    def send_file_to_room(self):
        """Send file to current room"""
        if not self.current_room:
            messagebox.showwarning("Warning", "You must join a room first!")
            return
        
        self.send_file(target=self.current_room, is_private=False)
    
    def send_file_private(self):
        """Send file privately - either to selected user or ask for username"""
        # Check if a user is selected
        selection = self.users_listbox.curselection()
        if selection:
            user_info = self.users_listbox.get(selection[0])
            username = user_info.split(' (')[0]  # Extract username
            
            if username == self.nickname:
                messagebox.showinfo("Info", "You cannot send a file to yourself!")
                return
            
            self.send_file(target=username, is_private=True)
        else:
            # Ask for username
            username = simpledialog.askstring("Send File Privately", 
                                             "Enter username to send file to:", 
                                             parent=self.root)
            if username:
                self.send_file(target=username, is_private=True)
    
    def send_file(self, target, is_private):
        """Send file to target (room or user)"""
        if not self.connected:
            messagebox.showwarning("Warning", "Not connected to server!")
            return
        
        # Open file dialog
        filetypes = [
            ("Images", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
            ("Documents", "*.txt *.pdf *.doc *.docx *.rtf"),
            ("Archives", "*.zip *.rar *.7z"),
            ("Audio", "*.mp3 *.wav *.ogg"),
            ("Video", "*.mp4 *.avi *.mov *.webm"),
            ("Code/Data", "*.py *.js *.html *.css *.json *.xml *.csv"),
            ("All Files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=filetypes,
            parent=self.root
        )
        
        if not filepath:
            return
        
        try:
            # Check file size (5MB limit)
            file_size = os.path.getsize(filepath)
            max_size = 5 * 1024 * 1024  # 5MB
            
            if file_size > max_size:
                messagebox.showerror("Error", f"File too large! Maximum size is 5MB. Your file is {file_size / (1024*1024):.1f}MB")
                return
            
            # Check file type
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            allowed_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.txt', '.pdf', 
                           '.doc', '.docx', '.rtf', '.zip', '.rar', '.7z', '.mp3', '.wav', 
                           '.ogg', '.mp4', '.avi', '.mov', '.webm', '.py', '.js', '.html', 
                           '.css', '.json', '.xml', '.csv'}
            
            if file_ext not in allowed_types:
                messagebox.showerror("Error", f"File type '{file_ext}' not allowed!")
                return
            
            # Read and encode file
            with open(filepath, 'rb') as f:
                file_content = f.read()
            
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Send file command
            file_command = {
                'command': 'FILE',
                'target': target,
                'is_private': is_private,
                'file_data': {
                    'filename': filename,
                    'content': file_content_b64,
                    'size': file_size
                }
            }
            
            # Show progress dialog
            progress_msg = f"Sending {filename} ({'privately to ' + target if is_private else 'to room ' + target})..."
            self.add_message_to_chat(progress_msg, "system")
            
            message_json = json.dumps(file_command)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            self.client_socket.send(length_bytes + message_bytes)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")
    
    def handle_received_file(self, data):
        """Handle received file from server"""
        try:
            print(f"🔍 DEBUG: Received file data keys: {list(data.keys())}")
            
            file_info = data.get('file_info', {})
            file_content_b64 = data.get('file_content', '')
            is_private = data.get('is_private', False)
            timestamp = data.get('timestamp', '')
            
            print(f"🔍 DEBUG: file_info keys: {list(file_info.keys())}")
            print(f"🔍 DEBUG: timestamp: '{timestamp}'")
            print(f"🔍 DEBUG: file_content length: {len(file_content_b64)}")
            
            filename = file_info.get('filename', 'unknown_file')
            sender = file_info.get('sender', 'Unknown')
            file_size = file_info.get('size', 0)
            
            print(f"🔍 DEBUG: filename: '{filename}', sender: '{sender}', size: {file_size}")
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Create clickable file link
            privacy_indicator = "🔒 Private" if is_private else "📢 Room"
            file_message = f"[{timestamp}] 📎 {privacy_indicator} file from {sender}: {filename} ({size_str}) - Click to download"
            
            # Store file data for download
            if not hasattr(self, 'received_files'):
                self.received_files = {}
            
            file_id = f"{sender}_{filename}_{timestamp}"
            print(f"🔍 DEBUG: Generated file_id: '{file_id}'")
            
            self.received_files[file_id] = {
                'filename': filename,
                'content': file_content_b64,
                'sender': sender,
                'size': file_size
            }
            
            print(f"🔍 DEBUG: Stored file in received_files. Total files: {len(self.received_files)}")
            print(f"🔍 DEBUG: Available file IDs: {list(self.received_files.keys())}")
            
            # Add clickable message - make the entire line clickable
            self.chat_display.configure(state=tk.NORMAL)
            full_message = f"{file_message} (ID: {file_id})\n"
            self.chat_display.insert(tk.END, full_message, "file_link")
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_display.see(tk.END)
            
        except Exception as e:
            self.add_message_to_chat(f"Error receiving file: {e}", "error")
    
    def handle_file_click(self, event):
        """Handle clicking on file links"""
        try:
            print(f"🔍 DEBUG: File click detected!")
            
            # Get the current position
            current_pos = self.chat_display.index(tk.CURRENT)
            print(f"🔍 DEBUG: Click position: {current_pos}")
            
            # Get all text with the file_link tag
            ranges = self.chat_display.tag_ranges("file_link")
            print(f"🔍 DEBUG: Found {len(ranges)//2} file_link ranges")
            
            # Find which file link was clicked
            for i in range(0, len(ranges), 2):
                start_pos = ranges[i]
                end_pos = ranges[i + 1]
                
                # Check if the click position is within this range
                if (self.chat_display.compare(current_pos, ">=", start_pos) and 
                    self.chat_display.compare(current_pos, "<=", end_pos)):
                    
                    # Get the text for this range
                    link_text = self.chat_display.get(start_pos, end_pos)
                    print(f"🔍 DEBUG: Clicked link text: '{link_text}'")
                    
                    # Extract file ID from the text
                    if "(ID: " in link_text:
                        file_id = link_text.split("(ID: ")[1].split(")")[0]
                        print(f"🔍 DEBUG: Extracted file_id: '{file_id}'")
                        
                        if hasattr(self, 'received_files'):
                            print(f"🔍 DEBUG: Available file IDs: {list(self.received_files.keys())}")
                            if file_id in self.received_files:
                                print(f"✅ DEBUG: File found! Proceeding to download...")
                                self.download_file(file_id)
                                return
                            else:
                                print(f"❌ DEBUG: File ID not found in received_files")
                        else:
                            print(f"❌ DEBUG: No received_files attribute")
                    else:
                        print(f"❌ DEBUG: No file ID found in link text")
                    break
            else:
                print(f"❌ DEBUG: Click position not found in any file link range")
                
        except Exception as e:
            print(f"❌ DEBUG: Error handling file click: {e}")
            import traceback
            traceback.print_exc()
    
    def download_file(self, file_id):
        """Download and save received file"""
        print(f"🔧 DEBUG: download_file called with file_id: '{file_id}'")
        
        if not hasattr(self, 'received_files'):
            print(f"❌ DEBUG: No received_files attribute!")
            messagebox.showerror("Error", "File not found!")
            return
            
        if file_id not in self.received_files:
            print(f"❌ DEBUG: file_id '{file_id}' not in received_files: {list(self.received_files.keys())}")
            messagebox.showerror("Error", "File not found!")
            return
        
        file_data = self.received_files[file_id]
        filename = file_data['filename']
        print(f"🔧 DEBUG: Retrieved file data for '{filename}'")
        
        # Ask where to save
        print(f"🔧 DEBUG: Opening file save dialog...")
        save_path = filedialog.asksaveasfilename(
            title="Save file as",
            initialfile=filename,
            defaultextension=os.path.splitext(filename)[1],
            parent=self.root
        )
        
        print(f"🔧 DEBUG: User selected save path: '{save_path}'")
        
        if save_path:
            try:
                print(f"🔧 DEBUG: Decoding and saving file...")
                # Decode and save file
                file_content = base64.b64decode(file_data['content'])
                with open(save_path, 'wb') as f:
                    f.write(file_content)
                
                print(f"✅ DEBUG: File saved successfully!")
                messagebox.showinfo("Success", f"File saved as: {save_path}")
                self.add_message_to_chat(f"📥 Downloaded: {filename}", "system")
                
                # Remove from memory after successful download
                del self.received_files[file_id]
                
            except Exception as e:
                print(f"❌ DEBUG: Exception in download_file: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to save file: {e}")
        else:
            print(f"🔧 DEBUG: User cancelled file save dialog")
    
if __name__ == "__main__":
    # Start the GUI client
    app = ChatGUI()
    app.run()
