import socket
import threading
import json
from datetime import datetime

class ChatServer:
    def __init__(self, host='localhost', port=55555):
        self.host = host
        self.port = port
        self.clients = {}  # {client_socket: {'nickname': str, 'room': str}}
        self.rooms = {}    # {room_name: set of client_sockets}
        self.nicknames = set()  # Set of active nicknames
        self.server_socket = None
        
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
            client_socket.send(message_json.encode('utf-8'))
        except ConnectionResetError:
            print(f"Client disconnected while sending message")
            self.disconnect_client(client_socket)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect_client(client_socket)
    
    def receive_message(self, client_socket):
        """Receive a message from a client"""
        try:
            message = client_socket.recv(1024).decode('utf-8')
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

if __name__ == "__main__":
    server = ChatServer()
    server.start_server()
