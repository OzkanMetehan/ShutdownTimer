#!/usr/bin/env python3
"""
Simple Shutdown Timer - Basic Working Version
This is a simple version to test the concept and get you started.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
from datetime import datetime, timedelta

class SimpleShutdownTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shutdown Timer")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Timer variables
        self.timer_running = False
        self.timer_thread = None
        self.remaining_seconds = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Shutdown Timer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Timer display
        self.timer_label = ttk.Label(main_frame, text="Set timer duration", font=("Arial", 12))
        self.timer_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Hours input
        ttk.Label(main_frame, text="Hours:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.hours_var = tk.StringVar(value="0")
        hours_spinbox = ttk.Spinbox(main_frame, from_=0, to=23, width=10, textvariable=self.hours_var)
        hours_spinbox.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Minutes input
        ttk.Label(main_frame, text="Minutes:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.minutes_var = tk.StringVar(value="30")
        minutes_spinbox = ttk.Spinbox(main_frame, from_=0, to=59, width=10, textvariable=self.minutes_var)
        minutes_spinbox.grid(row=3, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Timer", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Cancel button
        self.cancel_button = ttk.Button(button_frame, text="Cancel Timer", command=self.cancel_timer, state="disabled")
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to start", font=("Arial", 10))
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
    def start_timer(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            
            if hours == 0 and minutes == 0:
                messagebox.showwarning("Invalid Time", "Please set a time greater than 0 minutes.")
                return
                
            total_seconds = hours * 3600 + minutes * 60
            self.remaining_seconds = total_seconds
            
            # Update display
            self.update_timer_display()
            
            # Start timer thread
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
            
            # Update UI
            self.start_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.status_label.config(text="Timer running...")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours and minutes.")
    
    def cancel_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.remaining_seconds = 0
            self.timer_label.config(text="Set timer duration")
            self.start_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            self.status_label.config(text="Timer cancelled")
    
    def timer_loop(self):
        while self.timer_running and self.remaining_seconds > 0:
            time.sleep(1)
            self.remaining_seconds -= 1
            
            # Update display in main thread
            self.root.after(0, self.update_timer_display)
            
            if self.remaining_seconds <= 0:
                self.root.after(0, self.shutdown_computer)
                break
    
    def update_timer_display(self):
        if self.remaining_seconds > 0:
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            
            if hours > 0:
                display_text = f"Close the computer in {hours} hours {minutes} minutes"
            else:
                display_text = f"Close the computer in {minutes} minutes {seconds} seconds"
            
            self.timer_label.config(text=display_text)
        else:
            self.timer_label.config(text="Set timer duration")
    
    def shutdown_computer(self):
        # Show final warning
        result = messagebox.askyesno("Shutdown", "Time's up! Shutdown the computer now?")
        
        if result:
            try:
                # Windows shutdown command
                subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", "Failed to shutdown computer. Please shutdown manually.")
        else:
            self.cancel_timer()
    
    def run(self):
        self.root.mainloop()

def main():
    app = SimpleShutdownTimer()
    app.run()

if __name__ == "__main__":
    main() 