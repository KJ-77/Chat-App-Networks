#!/usr/bin/env python3
"""
Test script to verify the file transfer and message handling fixes
"""

import socket
import json
import base64
import threading
import time

def send_with_length(sock, data):
    """Send data with length prefix"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    length_bytes = len(data).to_bytes(4, byteorder='big')
    sock.send(length_bytes + data)

def receive_with_length(sock):
    """Receive data with length prefix"""
    length_data = sock.recv(4)
    if not length_data:
        return None
    
    message_length = int.from_bytes(length_data, byteorder='big')
    
    message_data = b''
    while len(message_data) < message_length:
        chunk = sock.recv(min(4096, message_length - len(message_data)))
        if not chunk:
            return None
        message_data += chunk
    
    return message_data.decode('utf-8')

def test_client():
    """Test client for verifying fixes"""
    try:
        # Connect to server
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 55555))
        print("✅ Connected to server")
        
        # Send nickname
        send_with_length(client, "TestUser")
        
        # Receive welcome message
        response = receive_with_length(client)
        print(f"Server response: {response}")
        
        # Join a room
        join_command = {
            'command': 'JOIN',
            'content': 'testroom'
        }
        send_with_length(client, json.dumps(join_command))
        
        # Receive join confirmation
        response = receive_with_length(client)
        print(f"Join response: {response}")
        
        # Test file transfer with a small file
        test_content = "This is a test file for verifying the fix!"
        test_file_b64 = base64.b64encode(test_content.encode()).decode()
        
        file_command = {
            'command': 'FILE',
            'target': 'testroom',
            'is_private': False,
            'file_data': {
                'filename': 'test.txt',
                'content': test_file_b64,
                'size': len(test_content)
            }
        }
        
        print("📤 Sending test file...")
        send_with_length(client, json.dumps(file_command))
        
        # Listen for responses
        for i in range(3):  # Listen for a few responses
            try:
                response = receive_with_length(client)
                if response:
                    data = json.loads(response)
                    print(f"Response {i+1}: {data.get('type', 'unknown')} - {data.get('content', 'no content')}")
                else:
                    break
            except:
                break
        
        client.close()
        print("✅ Test completed successfully")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing file transfer and protocol fixes...")
    test_client()
