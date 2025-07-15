#!/usr/bin/env python3
"""
Chat Application Demo Script
This script demonstrates the chat application by starting multiple clients automatically.
"""

import subprocess
import time
import sys
import os

def start_server():
    """Start the chat server"""
    print("Starting chat server...")
    try:
        server_process = subprocess.Popen([sys.executable, 'server.py'])
        time.sleep(2)  # Give server time to start
        return server_process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def start_client(client_name):
    """Start a chat client"""
    print(f"Starting client: {client_name}")
    try:
        client_process = subprocess.Popen([sys.executable, 'client.py'])
        return client_process
    except Exception as e:
        print(f"Failed to start client {client_name}: {e}")
        return None

def main():
    """Main demo function"""
    print("=== Chat Application Demo ===")
    print("This will start the server and demonstrate the chat application.")
    print("Press Ctrl+C to stop all processes.\n")
    
    # Change to the directory containing the chat files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    processes = []
    
    try:
        # Start server
        server_process = start_server()
        if server_process:
            processes.append(server_process)
        else:
            print("Failed to start server. Exiting.")
            return
        
        print("\nServer started successfully!")
        print("\nTo test the chat application, choose one of these options:")
        
        print("\n=== Server Options ===")
        print("• Console Server: Already running (this window)")
        print("• Admin GUI: Run 'python server_gui.py' for full admin control")
        
        print("\n=== Client Options ===")
        print("1. Run 'python client.py' for console interface")
        print("2. Run 'python gui_client.py' for modern GUI interface")
        print("3. Use both types of clients together!")
        
        print("\n=== Server Admin GUI Features ===")
        print("• Real-time monitoring of all connections")
        print("• Kick users and manage rooms")
        print("• Send global broadcasts and announcements")
        print("• View detailed logs and generate reports")
        print("• Monitor server statistics and activity")
        
        print("\n=== Test Commands ===")
        print("Try these commands in any client:")
        print("   - JOIN general")
        print("   - MSG Hello everyone!")
        print("   - MSG username:Private message")
        print("   - LIST")
        print("   - LEAVE")
        print("\nPress Ctrl+C to stop the server.")
        
        # Keep the server running
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping all processes...")
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        print("Demo stopped.")
    except Exception as e:
        print(f"Demo error: {e}")
        for process in processes:
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    main()
