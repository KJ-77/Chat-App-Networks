import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import socket
import threading
import json
from datetime import datetime
import sys

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
        ttk.Button(room_controls, text="Leave Room", command=self.leave_current_room, style='Error.TButton').pack(fill=tk.X)
        
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
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', self.send_message)
        
        # Send button
        self.send_btn = ttk.Button(input_frame, text="Send Message", 
                                  command=self.send_message, style='Success.TButton')
        self.send_btn.pack(side=tk.RIGHT)
    
    def toggle_chat_controls(self, enabled):
        """Enable/disable chat controls based on connection status"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        self.message_entry.configure(state=state)
        self.send_btn.configure(state=state)
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
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    # Handle nickname request (plain text)
                    if "Please enter your nickname:" in message or message.startswith("NICK_REQUEST"):
                        self.client_socket.send(self.nickname.encode('utf-8'))
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
            print(f"Sending command: {command} with content: {content}")  # Debug
            self.client_socket.send(message_json.encode('utf-8'))
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

def main():
    """Main function to run the GUI chat client"""
    app = ChatGUI()
    app.run()

if __name__ == "__main__":
    main()
