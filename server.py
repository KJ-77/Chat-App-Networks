import socket
import threading
import json
from datetime import datetime
import base64
import os
import mimetypes

class ChatServer:
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.clients = {}  # {client_socket: {'nickname': str, 'room': str}}
        self.rooms = {}    # {room_name: set of client_sockets}
        self.nicknames = set()  # Set of active nicknames
        self.server_socket = None
        
        # File sharing settings
        self.max_file_size = 5 * 1024 * 1024  # 5MB max file size
        self.allowed_file_types = {
            # Images
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp',
            # Documents
            '.txt', '.pdf', '.doc', '.docx', '.rtf',
            # Archives
            '.zip', '.rar', '.7z',
            # Audio
            '.mp3', '.wav', '.ogg',
            # Video (small files only)
            '.mp4', '.avi', '.mov', '.webm',
            # Code/Data
            '.py', '.js', '.html', '.css', '.json', '.xml', '.csv'
        }
        
        # Create uploads directory if it doesn't exist
        self.uploads_dir = "server_uploads"
        if not os.path.exists(self.uploads_dir):
            os.makedirs(self.uploads_dir)
        
    def start_server(self):
        """Initialize and start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"Server started on {self.host}:{self.port}")
        print("Waiting for connections...")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connected with {str(address)}")
                
                # Start a new thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.shutdown_server()
        except Exception as e:
            print(f"Server error: {e}")
            self.shutdown_server()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connections"""
        try:
            # Request nickname
            self.send_message(client_socket, "NICK_REQUEST", "Please enter your nickname:")
            
            # Wait for nickname response
            nickname_response = self.receive_message(client_socket)
            
            # Extract nickname from response
            if isinstance(nickname_response, str):
                nickname = nickname_response.strip()
            else:
                # If it's a dict, it might be a command - reject
                self.send_message(client_socket, "NICK_ERROR", "Invalid nickname format!")
                client_socket.close()
                return
            
            # Validate nickname
            if not nickname or nickname in self.nicknames or ' ' in nickname:
                self.send_message(client_socket, "NICK_ERROR", "Nickname already taken or invalid!")
                client_socket.close()
                return
            
            # Add client to server data structures
            self.clients[client_socket] = {'nickname': nickname, 'room': None}
            self.nicknames.add(nickname)
            
            print(f"Client {nickname} connected from {address}")
            self.send_message(client_socket, "NICK_ACCEPTED", f"Welcome {nickname}!")
            
            # Listen for messages from this client
            while True:
                try:
                    message = self.receive_message(client_socket)
                    if message:
                        self.process_command(client_socket, message)
                    else:
                        break
                except ConnectionResetError:
                    break
                except Exception as e:
                    print(f"Error handling client {nickname}: {e}")
                    break
                    
        except Exception as e:
            print(f"Error in handle_client: {e}")
        finally:
            self.disconnect_client(client_socket)
    
    def send_message(self, client_socket, msg_type, content):
        """Send a message to a client"""
        try:
            message = {
                'type': msg_type,
                'content': content,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            # Send length first, then message
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            client_socket.send(length_bytes + message_bytes)
        except ConnectionResetError:
            print(f"Client disconnected while sending message")
            self.disconnect_client(client_socket)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect_client(client_socket)
    
    def receive_message(self, client_socket):
        """Receive a message from a client"""
        try:
            # First, receive the length of the message
            length_data = client_socket.recv(4)
            if not length_data:
                return None
            
            message_length = int.from_bytes(length_data, byteorder='big')
            
            # Now receive the actual message
            message_data = b''
            while len(message_data) < message_length:
                chunk = client_socket.recv(min(4096, message_length - len(message_data)))
                if not chunk:
                    return None
                message_data += chunk
            
            message = message_data.decode('utf-8')
            if message:
                # Try to parse as JSON first
                try:
                    return json.loads(message)
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text (for nickname)
                    return message
            return None
        except Exception as e:
            print(f"Error receiving message: {e}")
            return None
    
    def process_command(self, client_socket, message):
        """Process commands from clients"""
        try:
            # Handle plain text messages (nicknames) - ignore them in this context
            if isinstance(message, str):
                # This might be a stray nickname or plain text - log it
                print(f"Received plain text message: {message}")
                return
            
            # Handle dictionary messages (commands)
            if not isinstance(message, dict):
                print(f"Received non-dict message: {type(message)}")
                return
            
            command = message.get('command', '').upper()
            content = message.get('content', '')
            
            # Check if client is still connected
            if client_socket not in self.clients:
                print(f"Received command from unknown client")
                return
                
            nickname = self.clients[client_socket]['nickname']
            
            print(f"Processing command '{command}' from {nickname}")
            
            if command == 'JOIN':
                self.handle_join_room(client_socket, content)
            elif command == 'MSG':
                self.handle_message(client_socket, content)
            elif command == 'LEAVE':
                self.handle_leave_room(client_socket)
            elif command == 'LIST':
                self.handle_list_command(client_socket)
            elif command == 'FILE':
                self.handle_file_transfer(client_socket, message)
            else:
                self.send_message(client_socket, "ERROR", "Unknown command!")
                
        except Exception as e:
            print(f"Error processing command: {e}")
            print(f"Message type: {type(message)}")
            print(f"Message content: {message}")
    
    def handle_join_room(self, client_socket, room_name):
        """Handle JOIN command"""
        if not room_name:
            self.send_message(client_socket, "ERROR", "Room name cannot be empty!")
            return
        
        nickname = self.clients[client_socket]['nickname']
        current_room = self.clients[client_socket]['room']
        
        # Leave current room if in one
        if current_room:
            self.leave_room(client_socket, current_room)
        
        # Join new room
        if room_name not in self.rooms:
            self.rooms[room_name] = set()
        
        self.rooms[room_name].add(client_socket)
        self.clients[client_socket]['room'] = room_name
        
        # Notify user
        self.send_message(client_socket, "ROOM_JOINED", f"Joined room: {room_name}")
        
        # Notify other users in the room
        self.broadcast_to_room(room_name, "USER_JOINED", 
                              f"{nickname} joined the room", exclude=client_socket)
        
        print(f"{nickname} joined room {room_name}")
    
    def handle_message(self, client_socket, content):
        """Handle MSG command"""
        nickname = self.clients[client_socket]['nickname']
        
        # Check if it's a private message (contains ':')
        if ':' in content:
            parts = content.split(':', 1)
            target_user = parts[0].strip()
            message = parts[1].strip()
            
            # Send private message
            self.send_private_message(client_socket, target_user, message)
        else:
            # Send public message to current room
            current_room = self.clients[client_socket]['room']
            if current_room:
                self.broadcast_to_room(current_room, "PUBLIC_MSG", 
                                     f"{nickname}: {content}", exclude=client_socket)
                # Echo back to sender
                self.send_message(client_socket, "PUBLIC_MSG", f"You: {content}")
            else:
                self.send_message(client_socket, "ERROR", "You must join a room first!")
    
    def handle_leave_room(self, client_socket):
        """Handle LEAVE command"""
        current_room = self.clients[client_socket]['room']
        if current_room:
            self.leave_room(client_socket, current_room)
            self.send_message(client_socket, "ROOM_LEFT", f"Left room: {current_room}")
        else:
            self.send_message(client_socket, "ERROR", "You are not in any room!")
    
    def handle_list_command(self, client_socket):
        """Handle LIST command"""
        # List all active users and rooms
        users_info = []
        rooms_info = []
        
        for client, info in self.clients.items():
            room = info['room'] if info['room'] else "No room"
            users_info.append(f"{info['nickname']} ({room})")
        
        for room, clients in self.rooms.items():
            rooms_info.append(f"{room} ({len(clients)} users)")
        
        response = f"Active Users:\n" + "\n".join(users_info) + "\n\nActive Rooms:\n" + "\n".join(rooms_info)
        self.send_message(client_socket, "LIST_RESPONSE", response)
    
    def send_private_message(self, sender_socket, target_nickname, message):
        """Send a private message to a specific user"""
        sender_nickname = self.clients[sender_socket]['nickname']
        target_socket = None
        
        # Find target client
        for client, info in self.clients.items():
            if info['nickname'] == target_nickname:
                target_socket = client
                break
        
        if target_socket:
            # Send to target
            self.send_message(target_socket, "PRIVATE_MSG", 
                            f"Private from {sender_nickname}: {message}")
            # Send confirmation to sender
            self.send_message(sender_socket, "PRIVATE_MSG", 
                            f"Private to {target_nickname}: {message}")
        else:
            self.send_message(sender_socket, "ERROR", f"User {target_nickname} not found!")
    
    def broadcast_to_room(self, room_name, msg_type, content, exclude=None):
        """Broadcast message to all clients in a room"""
        if room_name in self.rooms:
            # Make a copy of the set to avoid modification during iteration
            clients_to_notify = self.rooms[room_name].copy()
            for client in clients_to_notify:
                if client != exclude:
                    # Check if client is still connected
                    if client in self.clients:
                        self.send_message(client, msg_type, content)
                    else:
                        # Remove disconnected client from room
                        self.rooms[room_name].discard(client)
    
    def leave_room(self, client_socket, room_name):
        """Remove client from a room"""
        if room_name in self.rooms:
            self.rooms[room_name].discard(client_socket)
            
            # Remove empty rooms
            if not self.rooms[room_name]:
                del self.rooms[room_name]
            else:
                # Notify other users
                nickname = self.clients[client_socket]['nickname']
                self.broadcast_to_room(room_name, "USER_LEFT", 
                                     f"{nickname} left the room", exclude=client_socket)
        
        self.clients[client_socket]['room'] = None
    
    def disconnect_client(self, client_socket):
        """Clean up when a client disconnects"""
        try:
            if client_socket in self.clients:
                nickname = self.clients[client_socket]['nickname']
                current_room = self.clients[client_socket]['room']
                
                # Leave current room
                if current_room:
                    self.leave_room(client_socket, current_room)
                
                # Remove from server data structures
                del self.clients[client_socket]
                self.nicknames.discard(nickname)
                
                print(f"Client {nickname} disconnected")
            
            # Close socket
            try:
                client_socket.close()
            except:
                pass
        except Exception as e:
            print(f"Error disconnecting client: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def shutdown_server(self):
        """Gracefully shutdown the server"""
        print("Shutting down server...")
        
        # Close all client connections
        for client in list(self.clients.keys()):
            self.disconnect_client(client)
        
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
    
    def handle_file_transfer(self, client_socket, message):
        """Handle file transfer command"""
        try:
            nickname = self.clients[client_socket]['nickname']
            file_data = message.get('file_data', {})
            
            filename = file_data.get('filename', '')
            file_content_b64 = file_data.get('content', '')
            file_size = file_data.get('size', 0)
            target = message.get('target', '')  # Room name or username for private
            is_private = message.get('is_private', False)
            
            # Validate file
            validation_result = self.validate_file(filename, file_size)
            if not validation_result['valid']:
                self.send_message(client_socket, "ERROR", validation_result['error'])
                return
            
            # Decode file content
            try:
                file_content = base64.b64decode(file_content_b64)
            except Exception as e:
                self.send_message(client_socket, "ERROR", "Invalid file data!")
                return
            
            # Save file to server
            safe_filename = self.save_file(nickname, filename, file_content)
            if not safe_filename:
                self.send_message(client_socket, "ERROR", "Failed to save file!")
                return
            
            # Create file message
            file_info = {
                'filename': filename,
                'size': file_size,
                'sender': nickname,
                'file_id': safe_filename,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            if is_private:
                # Send file privately
                self.send_private_file(client_socket, target, file_info, file_content_b64)
            else:
                # Send file to room
                self.send_file_to_room(client_socket, target, file_info, file_content_b64)
                
            print(f"{nickname} shared file {filename} ({'private to ' + target if is_private else 'in room ' + target})")
            
        except Exception as e:
            print(f"Error handling file transfer: {e}")
            self.send_message(client_socket, "ERROR", "File transfer failed!")
    
    def validate_file(self, filename, file_size):
        """Validate file based on size and type restrictions"""
        if not filename:
            return {'valid': False, 'error': 'Filename cannot be empty!'}
        
        # Check file size
        if file_size > self.max_file_size:
            size_mb = self.max_file_size / (1024 * 1024)
            return {'valid': False, 'error': f'File too large! Maximum size is {size_mb:.1f}MB'}
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in self.allowed_file_types:
            allowed_types = ', '.join(sorted(self.allowed_file_types))
            return {'valid': False, 'error': f'File type not allowed! Allowed types: {allowed_types}'}
        
        return {'valid': True, 'error': None}
    
    def save_file(self, sender_nickname, filename, file_content):
        """Save file to server storage"""
        try:
            # Create safe filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{sender_nickname}_{filename}"
            filepath = os.path.join(self.uploads_dir, safe_filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_content)
            
            return safe_filename
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def send_private_file(self, sender_socket, target_nickname, file_info, file_content_b64):
        """Send file privately to a specific user"""
        sender_nickname = self.clients[sender_socket]['nickname']
        target_socket = None
        
        # Find target client
        for client, info in self.clients.items():
            if info['nickname'] == target_nickname:
                target_socket = client
                break
        
        if target_socket:
            # Send file to target using proper protocol
            file_message = {
                'type': 'FILE_RECEIVED',
                'file_info': file_info,
                'file_content': file_content_b64,
                'is_private': True,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            message_json = json.dumps(file_message)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            target_socket.send(length_bytes + message_bytes)
            
            # Send confirmation to sender
            self.send_message(sender_socket, "FILE_SENT", 
                            f"File '{file_info['filename']}' sent privately to {target_nickname}")
        else:
            self.send_message(sender_socket, "ERROR", f"User {target_nickname} not found!")
    
    def send_file_to_room(self, sender_socket, room_name, file_info, file_content_b64):
        """Send file to all users in a room"""
        sender_nickname = self.clients[sender_socket]['nickname']
        current_room = self.clients[sender_socket]['room']
        
        # Check if sender is in the specified room
        if current_room != room_name:
            self.send_message(sender_socket, "ERROR", f"You must be in room '{room_name}' to share files there!")
            return
        
        if room_name in self.rooms:
            file_message = {
                'type': 'FILE_RECEIVED',
                'file_info': file_info,
                'file_content': file_content_b64,
                'is_private': False,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            }
            
            # Send to all clients in room except sender
            clients_to_notify = self.rooms[room_name].copy()
            message_json = json.dumps(file_message)
            message_bytes = message_json.encode('utf-8')
            length_bytes = len(message_bytes).to_bytes(4, byteorder='big')
            
            for client in clients_to_notify:
                if client != sender_socket and client in self.clients:
                    try:
                        client.send(length_bytes + message_bytes)
                    except:
                        self.rooms[room_name].discard(client)
            
            # Send confirmation to sender
            self.send_message(sender_socket, "FILE_SENT", 
                            f"File '{file_info['filename']}' shared in room {room_name}")
        else:
            self.send_message(sender_socket, "ERROR", f"Room '{room_name}' not found!")
    
    def get_file_info(self):
        """Get information about file sharing settings"""
        size_mb = self.max_file_size / (1024 * 1024)
        allowed_types = ', '.join(sorted(self.allowed_file_types))
        return {
            'max_size_mb': size_mb,
            'allowed_types': allowed_types
        }

if __name__ == "__main__":
    # Start the chat server
    print("=== Python Chat Server ===")
    print("Starting server on localhost:55555...")
    
    server = ChatServer()
    try:
        server.start_server()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown_server()
    except Exception as e:
        print(f"Server error: {e}")
        server.shutdown_server()
