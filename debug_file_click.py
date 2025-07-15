#!/usr/bin/env python3
"""
Debug file download functionality - Updated to match the actual implementation
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import json
import base64

def debug_file_click():
    """Test the file click functionality with exact same setup as GUI client"""
    
    # Create a test window
    root = tk.Tk()
    root.title("File Click Debug Test - Exact GUI Client Simulation")
    root.geometry("800x600")
    
    # Create a scrolled text widget (same as GUI client)
    chat_display = scrolledtext.ScrolledText(root, 
                                           height=20,
                                           state=tk.DISABLED,
                                           bg='white',
                                           fg='black',
                                           font=('Consolas', 10),
                                           wrap=tk.WORD)
    chat_display.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags exactly like GUI client
    chat_display.tag_configure("system", foreground="#7f8c8d", font=('Consolas', 10, 'italic'))
    chat_display.tag_configure("file_link", 
                              foreground="#0066cc", 
                              font=('Consolas', 10, 'underline'),
                              background="#f0f8ff")
    
    # Simulate received files storage
    received_files = {}
    
    def handle_file_click(event):
        """Exact copy of the improved file click handler"""
        try:
            print(f"🔍 DEBUG: File click detected!")
            
            # Get the current position
            current_pos = chat_display.index(tk.CURRENT)
            print(f"🔍 DEBUG: Click position: {current_pos}")
            
            # Get all text with the file_link tag
            ranges = chat_display.tag_ranges("file_link")
            print(f"🔍 DEBUG: Found {len(ranges)//2} file_link ranges")
            
            # Find which file link was clicked
            for i in range(0, len(ranges), 2):
                start_pos = ranges[i]
                end_pos = ranges[i + 1]
                
                # Check if the click position is within this range
                if (chat_display.compare(current_pos, ">=", start_pos) and 
                    chat_display.compare(current_pos, "<=", end_pos)):
                    
                    # Get the text for this range
                    link_text = chat_display.get(start_pos, end_pos)
                    print(f"🔍 DEBUG: Clicked link text: '{link_text}'")
                    
                    # Extract file ID from the text
                    if "(ID: " in link_text:
                        file_id = link_text.split("(ID: ")[1].split(")")[0]
                        print(f"🔍 DEBUG: Extracted file_id: '{file_id}'")
                        
                        print(f"🔍 DEBUG: Available file IDs: {list(received_files.keys())}")
                        if file_id in received_files:
                            file_data = received_files[file_id]
                            print(f"✅ DEBUG: File found! Data: {file_data['filename']}")
                            messagebox.showinfo("Success", f"Would download: {file_data['filename']}")
                            return
                        else:
                            print(f"❌ DEBUG: File ID not found in received_files")
                    else:
                        print(f"❌ DEBUG: No file ID found in link text")
                    break
            else:
                print(f"❌ DEBUG: Click position not found in any file link range")
                
        except Exception as e:
            print(f"❌ DEBUG: Error handling file click: {e}")
            import traceback
            traceback.print_exc()
    
    # Add hover effects
    def on_enter(event):
        chat_display.config(cursor="hand2")
    
    def on_leave(event):
        chat_display.config(cursor="")
    
    # Bind events exactly like GUI client
    chat_display.tag_bind("file_link", "<Button-1>", handle_file_click)
    chat_display.tag_bind("file_link", "<Enter>", on_enter)
    chat_display.tag_bind("file_link", "<Leave>", on_leave)
    
    # Add test data exactly like GUI client does
    chat_display.configure(state=tk.NORMAL)
    chat_display.insert(tk.END, "📋 File Download Debug Test\n\n", "system")
    
    # Create test files exactly like the GUI client creates them
    test_files = [
        {
            'filename': 'test1.txt',
            'sender': 'Alice',
            'timestamp': '10:30:45',
            'size': 1024,
            'content': base64.b64encode(b"Test file content 1").decode()
        },
        {
            'filename': 'image0.jpeg',
            'sender': 'KJ',
            'timestamp': '11:08:16',
            'size': 731136,  # 713.9 KB like in your screenshot
            'content': base64.b64encode(b"Test image content").decode()
        }
    ]
    
    for file_data in test_files:
        # Generate file ID exactly like GUI client
        file_id = f"{file_data['sender']}_{file_data['filename']}_{file_data['timestamp']}"
        received_files[file_id] = file_data
        
        # Format file size exactly like GUI client
        size = file_data['size']
        if size < 1024:
            size_str = f"{size} bytes"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"
        
        # Create the file message exactly like GUI client
        privacy_indicator = "📢 Room"
        file_message = f"[{file_data['timestamp']}] 📎 {privacy_indicator} file from {file_data['sender']}: {file_data['filename']} ({size_str}) - Click to download"
        
        # Insert exactly like the fixed GUI client (full message as one tag)
        full_message = f"{file_message} (ID: {file_id})\n"
        chat_display.insert(tk.END, full_message, "file_link")
    
    chat_display.insert(tk.END, "\n💡 Click on the blue file links above to test the download functionality.\n", "system")
    chat_display.insert(tk.END, "Check the console for debug output.\n\n", "system")
    
    print("✅ Debug test window created")
    print(f"🔍 Test files loaded: {list(received_files.keys())}")
    print("📋 Click on the file links in the window to test functionality")
    
    # Make text widget read-only
    chat_display.configure(state=tk.DISABLED)
    
    root.mainloop()

if __name__ == "__main__":
    debug_file_click()
