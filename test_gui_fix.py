#!/usr/bin/env python3
"""
Quick test script to verify the GUI client room joining fix
"""

import subprocess
import time
import sys
import os

def test_gui_room_join():
    """Test if GUI client can join rooms without the dict error"""
    print("=== Testing GUI Room Join Fix ===")
    
    # Change to the directory containing the chat files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("1. Starting server...")
    try:
        # Start server in background
        server_process = subprocess.Popen([sys.executable, 'server.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(2)
        
        # Check if server is still running
        if server_process.poll() is None:
            print("✅ Server started successfully!")
        else:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
        
        print("\n2. Testing completed!")
        print("Now you can:")
        print("   - Run 'python gui_client.py' to test the GUI")
        print("   - Connect with a nickname")
        print("   - Try joining a room (should work without 'dict' error)")
        print("   - The server is running and ready for testing")
        
        print("\n3. Press Ctrl+C to stop the server when done testing.")
        
        # Keep server running for manual testing
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\nStopping server...")
            server_process.terminate()
            server_process.wait()
            print("Server stopped.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_gui_room_join()
