#!/usr/bin/env python3
"""
Simple test to check if Python is working
"""

import sys
import tkinter as tk

print("Python is working!")
print(f"Python version: {sys.version}")
print("Tkinter is available for GUI")

# Test if we can create a simple window
try:
    root = tk.Tk()
    root.withdraw()  # Hide the window
    print("Tkinter GUI test: SUCCESS")
    root.destroy()
except Exception as e:
    print(f"Tkinter GUI test: FAILED - {e}")

print("All tests completed!") 