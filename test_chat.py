#!/usr/bin/env python3
"""
Test script for the chat application
This script helps test the chat application functionality
"""

import subprocess
import time
import sys
import os

def test_server_start():
    """Test if server starts correctly"""
    print("Testing server startup...")
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
            server_process.terminate()
            server_process.wait()
            return True
        else:
            stdout, stderr = server_process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout.decode()}")
            print(f"STDERR: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def test_client_connection():
    """Test if client can connect to server"""
    print("\nTesting client connection...")
    try:
        # Start server
        server_process = subprocess.Popen([sys.executable, 'server.py'], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        time.sleep(2)
        
        # Start client (will fail without user input, but should connect)
        client_process = subprocess.Popen([sys.executable, 'client.py'], 
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
        
        # Send nickname
        client_process.stdin.write(b"testuser\n")
        client_process.stdin.flush()
        
        time.sleep(2)
        
        # Check if both are running
        if server_process.poll() is None and client_process.poll() is None:
            print("✅ Client connected successfully!")
            success = True
        else:
            print("❌ Client connection failed")
            success = False
        
        # Cleanup
        client_process.terminate()
        server_process.terminate()
        
        try:
            client_process.wait(timeout=5)
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            client_process.kill()
            server_process.kill()
        
        return success
        
    except Exception as e:
        print(f"❌ Error testing client connection: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Chat Application Test Suite ===")
    print("This will test the basic functionality of the chat application.\n")
    
    # Change to the directory containing the chat files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if files exist
    required_files = ['server.py', 'client.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file {file} not found!")
            return
    
    print("✅ All required files found!")
    
    # Run tests
    tests_passed = 0
    total_tests = 2
    
    if test_server_start():
        tests_passed += 1
    
    if test_client_connection():
        tests_passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The chat application is working correctly.")
        print("\nTo use the application:")
        print("1. Run 'python server.py' in one terminal")
        print("2. Run 'python client.py' in another terminal")
        print("3. Enter a nickname when prompted")
        print("4. Use commands like 'JOIN general', 'MSG hello', etc.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
