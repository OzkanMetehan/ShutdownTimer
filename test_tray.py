#!/usr/bin/env python3
"""
Simple test script to debug tray functionality
"""

import tkinter as tk
import pystray
from PIL import Image, ImageDraw
import threading
import time

class TrayTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tray Test")
        self.root.geometry("300x200")
        
        # Create a simple button
        self.button = tk.Button(self.root, text="Minimize to Tray", command=self.minimize_to_tray)
        self.button.pack(pady=50)
        
        # Setup tray
        self.setup_tray()
        
    def create_tray_icon(self):
        """Create a simple icon for testing."""
        width = 64
        height = 64
        image = Image.new('RGBA', (width, height), (43, 43, 43, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse([8, 8, width-8, height-8], outline=(255, 255, 255, 255), width=3)
        return image
    
    def setup_tray(self):
        """Setup the system tray icon and menu."""
        try:
            icon_image = self.create_tray_icon()
            
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", self.show_window, default=True),
                pystray.MenuItem("Exit", self.quit_app)
            )
            
            self.tray_icon = pystray.Icon(
                "tray_test",
                icon_image,
                "Tray Test",
                menu
            )
            
            print("Tray setup successful")
            
        except Exception as e:
            print(f"Failed to setup tray: {e}")
            self.tray_icon = None
    
    def minimize_to_tray(self):
        """Minimize to tray."""
        try:
            self.root.withdraw()
            print("Window hidden")
            
            if self.tray_icon:
                if not self.tray_icon.visible:
                    print("Starting tray icon...")
                    self.tray_icon.run_detached()
                    print("Tray icon started")
                else:
                    print("Tray icon already visible")
            else:
                print("No tray icon available")
                
        except Exception as e:
            print(f"Failed to minimize: {e}")
    
    def show_window(self, icon=None, item=None):
        """Show the window."""
        try:
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            print("Window shown")
        except Exception as e:
            print(f"Failed to show window: {e}")
    
    def quit_app(self, icon=None, item=None):
        """Quit the app."""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
            self.root.destroy()
        except Exception as e:
            print(f"Failed to quit: {e}")
    
    def run(self):
        """Run the app."""
        self.root.mainloop()

if __name__ == "__main__":
    app = TrayTest()
    app.run() 