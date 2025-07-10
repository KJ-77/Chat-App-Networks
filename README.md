# Real-Time Chat Application

A multithreaded chat application built with Python sockets that supports real-time messaging, private chats, and chatroom management.

## Features

- **Client-Server Architecture**: Central server managing multiple concurrent client connections
- **Real-Time Messaging**: Instant message delivery using sockets
- **Chatroom Management**: Create, join, and leave chatrooms
- **Private Messaging**: Send direct messages to specific users
- **Nickname System**: Unique usernames for each client
- **Command-Based Interface**: Simple commands for all interactions

## Project Structure

```
Chat App Networks/
├── server.py          # Chat server implementation
├── client.py          # Console chat client implementation
├── gui_client.py      # GUI chat client implementation
├── README.md          # This file
├── requirements.txt   # Python dependencies
├── demo.py           # Demo script
├── test_chat.py      # Test script
└── start_chat.bat    # Windows launcher script
```

## Installation

1. Clone or download the project files
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

Run the server first:

```bash
python server.py
```

The server will start on `localhost:55555` by default.

### Starting the Client

You now have two client options:

**Console Client** (original):

```bash
python client.py
```

**GUI Client** (new):

```bash
python gui_client.py
```

**Or use the launcher script on Windows:**

```bash
start_chat.bat
```

You can also specify a custom host and port for the console client:

```bash
python client.py <host> <port>
```

### Chat Commands

Once connected, you can use these commands:

- `JOIN <room_name>` - Join or create a chatroom
- `MSG <message>` - Send a public message to current room
- `MSG <user>:<message>` - Send a private message to a user
- `LEAVE` - Leave the current chatroom
- `LIST` - Show all active users and rooms
- `HELP` - Show available commands
- `QUIT` - Exit the chat application

### Example Usage

**Console Client:**

1. **Join a chatroom:**

   ```
   JOIN general
   ```

2. **Send a public message:**

   ```
   MSG Hello everyone!
   ```

3. **Send a private message:**

   ```
   MSG john:Hey, how are you?
   ```

4. **List active users and rooms:**

   ```
   LIST
   ```

5. **Leave current room:**
   ```
   LEAVE
   ```

**GUI Client:**

1. **Connect**: Click "Connect", enter server details and nickname
2. **Join Room**: Click "Join Room" button or type `/join roomname`
3. **Send Messages**: Type in the input box and press Enter
4. **Private Messages**: Double-click a username or type `/msg user:message`
5. **Room Navigation**: Double-click rooms to join them
6. **View Lists**: Users and rooms are automatically displayed and updated

## Architecture

### Server Components

- **ChatServer Class**: Main server class handling client connections
- **Multithreading**: Each client connection runs in its own thread
- **Data Structures**:
  - `clients`: Maps client sockets to user information
  - `rooms`: Maps room names to sets of client sockets
  - `nicknames`: Set of active nicknames

### Client Components

- **ChatClient Class**: Console-based client for server communication
- **ChatGUI Class**: Modern GUI client with tkinter interface
- **Message Handling**: Separate threads for receiving messages in both clients
- **Command Processing**: Validates and sends commands to server (console and GUI)

### Communication Protocol

Messages are exchanged in JSON format:

```json
{
  "type": "message_type",
  "content": "message_content",
  "timestamp": "HH:MM:SS"
}
```

## Key Features Implementation

### 1. Multithreading

- Server uses threading for concurrent client handling
- Each client connection spawns a new thread
- Thread-safe operations for shared data structures

### 2. Real-Time Messaging

- Instant message broadcasting to room members
- Private message delivery between users
- Real-time notifications for user join/leave events

### 3. Chatroom Management

- Dynamic room creation and deletion
- User can switch between rooms
- Room membership tracking

### 4. Command Processing

- Robust command parsing and validation
- Error handling for invalid commands
- Comprehensive help system

### 5. Connection Management

- Graceful client disconnection handling
- Automatic cleanup of resources
- Nickname uniqueness enforcement

## Technical Details

### Dependencies

- Python 3.6+
- Standard library modules: `socket`, `threading`, `json`, `datetime`

### Network Configuration

- Default host: `localhost`
- Default port: `55555`
- Protocol: TCP (reliable message delivery)

### Error Handling

- Connection failure recovery
- Invalid command handling
- Network interruption management
- Resource cleanup on disconnection

## Testing

To test the application:

1. **Start the server**: `python server.py`
2. **Choose your client type**:
   - **Console**: `python client.py` (multiple terminals)
   - **GUI**: `python gui_client.py` (multiple windows)
   - **Mixed**: Use both console and GUI clients together!
3. **Test different scenarios**:
   - Multiple users joining the same room
   - Private messaging between users
   - Room switching and management
   - User disconnection handling
   - GUI vs Console client interaction

## Future Enhancements

Potential improvements:

- ✅ **GUI interface using tkinter** - COMPLETED!
- Message history persistence
- File sharing capabilities
- User authentication
- Room passwords
- Message encryption
- Emoji support and reactions
- User status indicators (online, away, busy)
- Dark/Light theme toggle
- Sound notifications
- Message search functionality
- Chat room moderation features

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure the server is running before starting clients
2. **Port already in use**: Change the port number or kill existing processes
3. **Nickname taken**: Choose a unique nickname
4. **Command not working**: Check command syntax with `HELP`

### Debug Mode

For debugging, you can add print statements or use Python's logging module to track message flow and connection states.

## GUI Features

The new GUI client (`gui_client.py`) provides a modern, user-friendly interface with:

### 🎨 Visual Interface

- **Modern Design**: Clean, dark theme with intuitive layout
- **Real-time Chat**: Messages appear instantly with proper formatting
- **Color-coded Messages**: Different colors for system, public, private, and error messages
- **Scrollable Chat**: Auto-scrolling chat history with timestamp display

### 🔧 User-Friendly Controls

- **Connection Panel**: Easy server connection with host/port input
- **Message Input**: Large text input with Enter-to-send functionality
- **Room Management**: Join/leave rooms with button clicks
- **User Lists**: See online users and active rooms in real-time

### 💬 Enhanced Messaging

- **Click-to-Message**: Double-click users to send private messages
- **Room Quick-Join**: Double-click rooms to join instantly
- **Slash Commands**: Support for `/join`, `/leave`, `/list`, `/msg`, `/help`
- **Dialog Boxes**: User-friendly input dialogs for room names and messages

### 🎯 Smart Features

- **Auto-refresh**: Automatic updates of user and room lists
- **Error Handling**: Clear error messages and connection status
- **Help System**: Built-in help accessible via `/help` or dialog
- **Graceful Disconnect**: Clean connection handling and resource cleanup

### 📱 Interface Layout

- **Left Panel**: Main chat area with message history
- **Right Panel**: Current room, online users, and active rooms
- **Top Bar**: Connection status and server controls
- **Bottom**: Message input and send button

## License

This project is for educational purposes. Feel free to modify and enhance it for your needs.
