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
├── client.py          # Chat client implementation
├── README.md          # This file
└── requirements.txt   # Python dependencies
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

Run the client in a separate terminal:

```bash
python client.py
```

You can also specify a custom host and port:

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

## Architecture

### Server Components

- **ChatServer Class**: Main server class handling client connections
- **Multithreading**: Each client connection runs in its own thread
- **Data Structures**:
  - `clients`: Maps client sockets to user information
  - `rooms`: Maps room names to sets of client sockets
  - `nicknames`: Set of active nicknames

### Client Components

- **ChatClient Class**: Main client class for server communication
- **Message Handling**: Separate thread for receiving messages
- **Command Processing**: Validates and sends commands to server

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

1. Start the server in one terminal
2. Start multiple clients in separate terminals
3. Test different scenarios:
   - Multiple users joining the same room
   - Private messaging between users
   - Room switching
   - User disconnection handling

## Future Enhancements

Potential improvements:

- GUI interface using tkinter or PyQt
- Message history persistence
- File sharing capabilities
- User authentication
- Room passwords
- Message encryption
- Emoji support
- User status indicators

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure the server is running before starting clients
2. **Port already in use**: Change the port number or kill existing processes
3. **Nickname taken**: Choose a unique nickname
4. **Command not working**: Check command syntax with `HELP`

### Debug Mode

For debugging, you can add print statements or use Python's logging module to track message flow and connection states.

## License

This project is for educational purposes. Feel free to modify and enhance it for your needs.
