import socket
import threading
import json
import sys

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
            message = {
                'command': command,
                'content': content
            }
            message_json = json.dumps(message)
            self.client_socket.send(message_json.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def receive_messages(self):
        """Listen for messages from the server"""
        while self.connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message:
                    data = json.loads(message)
                    self.handle_server_message(data)
                else:
                    break
            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
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
        else:
            print(f"[{timestamp}] {content}")
    
    def handle_nickname_request(self):
        """Handle nickname request from server"""
        while True:
            nickname = input("Enter your nickname: ").strip()
            if nickname and ' ' not in nickname:
                self.nickname = nickname
                self.client_socket.send(nickname.encode('utf-8'))
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
        print("HELP                - Show this help message")
        print("QUIT                - Exit the chat application")
        print("=====================\n")
    
    def process_user_input(self):
        """Process user input and send commands to server"""
        while self.connected:
            try:
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
                if command in ['JOIN', 'MSG', 'LEAVE', 'LIST']:
                    if command == 'JOIN' and not content:
                        print("❌ Usage: JOIN <room_name>")
                        continue
                    elif command == 'MSG' and not content:
                        print("❌ Usage: MSG <message> or MSG <user>:<message>")
                        continue
                    
                    self.send_message(command, content)
                else:
                    print("❌ Unknown command! Type 'HELP' for available commands.")
                    
            except KeyboardInterrupt:
                self.disconnect()
                break
            except Exception as e:
                print(f"Error processing input: {e}")
    
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
    main()
