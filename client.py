import socket
import threading
import json
import sys
import base64
import os

class ChatClient:
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.client_socket = None
        self.nickname = None
        self.connected = False
        self.current_room = None
        
    def connect_to_server(self):
        """Connect to the chat server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    def send_message(self, command, content=""):
        """Send a message to the server"""
        try:
            if not self.connected:
                print("Not connected to server!")
                return
            
            message = {
                'command': command,
                'content': content
            }
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            self.client_socket.send(length_bytes + message_bytes)
        except Exception as e:
            print(f"Connection lost: {e}")
            self.connected = False
    
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
                    data = json.loads(message)
                    self.handle_server_message(data)
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
                    self.connected = False
                break
    
    def handle_server_message(self, data):
        """Handle different types of messages from the server"""
        msg_type = data.get('type', '')
        content = data.get('content', '')
        timestamp = data.get('timestamp', '')
        
        if msg_type == 'NICK_REQUEST':
            self.handle_nickname_request()
        elif msg_type == 'NICK_ACCEPTED':
            print(f"[{timestamp}] {content}")
            self.show_help()
        elif msg_type == 'NICK_ERROR':
            print(f"[{timestamp}] Error: {content}")
            self.connected = False
        elif msg_type == 'ROOM_JOINED':
            print(f"[{timestamp}] {content}")
            self.current_room = content.split(': ')[1]
        elif msg_type == 'ROOM_LEFT':
            print(f"[{timestamp}] {content}")
            self.current_room = None
        elif msg_type == 'PUBLIC_MSG':
            print(f"[{timestamp}] {content}")
        elif msg_type == 'PRIVATE_MSG':
            print(f"[{timestamp}] 🔒 {content}")
        elif msg_type == 'USER_JOINED':
            print(f"[{timestamp}] 👋 {content}")
        elif msg_type == 'USER_LEFT':
            print(f"[{timestamp}] 👋 {content}")
        elif msg_type == 'LIST_RESPONSE':
            print(f"[{timestamp}] \n{content}")
        elif msg_type == 'ERROR':
            print(f"[{timestamp}] ❌ Error: {content}")
        elif msg_type == 'FILE_SENT':
            print(f"[{timestamp}] ✅ {content}")
        elif msg_type == 'FILE_RECEIVED':
            self.handle_received_file(data)
        else:
            print(f"[{timestamp}] {content}")
    
    def handle_nickname_request(self):
        """Handle nickname request from server"""
        while True:
            nickname = input("Enter your nickname: ").strip()
            if nickname and ' ' not in nickname:
                self.nickname = nickname
                nickname_bytes = nickname.encode('utf-8')
                length_bytes = len(nickname_bytes).to_bytes(4, byteorder='big')
                self.client_socket.send(length_bytes + nickname_bytes)
                break
            else:
                print("Invalid nickname! Please enter a nickname without spaces.")
    
    def show_help(self):
        """Display available commands"""
        print("\n=== Chat Commands ===")
        print("JOIN <room_name>     - Join or create a chatroom")
        print("MSG <message>        - Send a public message to current room")
        print("MSG <user>:<message> - Send a private message to a user")
        print("LEAVE               - Leave the current chatroom")
        print("LIST                - Show all active users and rooms")
        print("FILE <filename>     - Send file to current room")
        print("PFILE <user> <filename> - Send file privately to a user")
        print("HELP                - Show this help message")
        print("QUIT                - Exit the chat application")
        print("=====================\n")
    
    def process_user_input(self):
        """Process user input and send commands to server"""
        while self.connected:
            try:
                # Check if still connected
                if not self.connected:
                    print("Connection lost. Exiting...")
                    break
                
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                # Handle local commands
                if user_input.upper() == 'QUIT':
                    self.disconnect()
                    break
                elif user_input.upper() == 'HELP':
                    self.show_help()
                    continue
                
                # Parse command
                parts = user_input.split(' ', 1)
                command = parts[0].upper()
                content = parts[1] if len(parts) > 1 else ""
                
                # Validate commands
                if command in ['JOIN', 'MSG', 'LEAVE', 'LIST', 'FILE', 'PFILE']:
                    if command == 'JOIN' and not content:
                        print("❌ Usage: JOIN <room_name>")
                        continue
                    elif command == 'MSG' and not content:
                        print("❌ Usage: MSG <message> or MSG <user>:<message>")
                        continue
                    elif command == 'FILE' and not content:
                        print("❌ Usage: FILE <filename>")
                        continue
                    elif command == 'PFILE':
                        if not content or len(content.split(' ', 1)) != 2:
                            print("❌ Usage: PFILE <user> <filename>")
                            continue
                    
                    # Handle file commands specially
                    if command == 'FILE':
                        if not self.current_room:
                            print("❌ You must join a room first to send files!")
                            continue
                        self.send_file(content, target=self.current_room, is_private=False)
                    elif command == 'PFILE':
                        parts = content.split(' ', 1)
                        username = parts[0]
                        filepath = parts[1]
                        self.send_file(filepath, target=username, is_private=True)
                    else:
                        self.send_message(command, content)
                else:
                    print("❌ Unknown command! Type 'HELP' for available commands.")
                    
            except KeyboardInterrupt:
                self.disconnect()
                break
            except EOFError:
                # Handle Ctrl+Z or input stream closed
                self.disconnect()
                break
            except Exception as e:
                print(f"Error processing input: {e}")
                if not self.connected:
                    break
    
    def start_client(self):
        """Start the chat client"""
        print("=== Python Chat Client ===")
        print("Connecting to server...")
        
        if not self.connect_to_server():
            return
        
        print("Connected to server!")
        
        # Start receiving messages in a separate thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Process user input
        self.process_user_input()
    
    def disconnect(self):
        """Disconnect from the server"""
        print("\nDisconnecting from server...")
        self.connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        print("Disconnected. Goodbye!")
    
    def get_status(self):
        """Get current client status"""
        if self.current_room:
            return f"Connected as {self.nickname} in room '{self.current_room}'"
        else:
            return f"Connected as {self.nickname} (no room)"
    
    def send_file(self, filepath, target=None, is_private=False):
        """Send file to server"""
        try:
            if not os.path.exists(filepath):
                print(f"❌ File not found: {filepath}")
                return
            
            # Check file size (5MB limit)
            file_size = os.path.getsize(filepath)
            max_size = 5 * 1024 * 1024  # 5MB
            
            if file_size > max_size:
                print(f"❌ File too large! Maximum size is 5MB. Your file is {file_size / (1024*1024):.1f}MB")
                return
            
            # Check file type
            filename = os.path.basename(filepath)
            file_ext = os.path.splitext(filename)[1].lower()
            allowed_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.txt', '.pdf', 
                           '.doc', '.docx', '.rtf', '.zip', '.rar', '.7z', '.mp3', '.wav', 
                           '.ogg', '.mp4', '.avi', '.mov', '.webm', '.py', '.js', '.html', 
                           '.css', '.json', '.xml', '.csv'}
            
            if file_ext not in allowed_types:
                print(f"❌ File type '{file_ext}' not allowed!")
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
            
            print(f"📤 Sending {filename} ({'privately to ' + target if is_private else 'to room'})...")
            message_json = json.dumps(file_command)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            self.client_socket.send(length_bytes + message_bytes)
            
        except Exception as e:
            print(f"❌ Failed to send file: {e}")
    
    def handle_received_file(self, data):
        """Handle received file from server"""
        try:
            file_info = data.get('file_info', {})
            file_content_b64 = data.get('file_content', '')
            is_private = data.get('is_private', False)
            timestamp = data.get('timestamp', '')
            
            filename = file_info.get('filename', 'unknown_file')
            sender = file_info.get('sender', 'Unknown')
            file_size = file_info.get('size', 0)
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            privacy_indicator = "🔒 Private" if is_private else "📢 Room"
            print(f"[{timestamp}] 📎 {privacy_indicator} file from {sender}: {filename} ({size_str})")
            
            # Ask if user wants to download
            response = input("Download this file? (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                self.download_file(file_content_b64, filename)
                
        except Exception as e:
            print(f"❌ Error receiving file: {e}")
    
    def download_file(self, file_content_b64, filename):
        """Download and save received file"""
        try:
            # Create downloads directory if it doesn't exist
            downloads_dir = "downloads"
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            
            # Generate unique filename if file exists
            save_path = os.path.join(downloads_dir, filename)
            counter = 1
            while os.path.exists(save_path):
                name, ext = os.path.splitext(filename)
                save_path = os.path.join(downloads_dir, f"{name}_{counter}{ext}")
                counter += 1
            
            # Decode and save file
            file_content = base64.b64decode(file_content_b64)
            with open(save_path, 'wb') as f:
                f.write(file_content)
            
            print(f"📥 File saved as: {save_path}")
            
        except Exception as e:
            print(f"❌ Failed to save file: {e}")

def main():
    """Main function to run the chat client"""
    host = 'localhost'
    port = 55555
    
    # Allow custom host and port via command line arguments
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Using default port 55555.")
    
    client = ChatClient(host, port)
    client.start_client()

if __name__ == "__main__":
    # Start the chat client
    client = ChatClient()
    client.start_client()
