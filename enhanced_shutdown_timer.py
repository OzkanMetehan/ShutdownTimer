#!/usr/bin/env python3
"""
Enhanced Shutdown Timer - With Countdown and Scheduled Time Modes
This version includes both timer modes and improved UI.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
from datetime import datetime, timedelta
import calendar

class EnhancedShutdownTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Shutdown Scheduler")
        self.root.geometry("450x400")
        self.root.resizable(True, True)
        
        # Set minimum and maximum window sizes
        self.root.minsize(400, 350)  # Minimum width: 400px, height: 350px
        self.root.maxsize(800, 600)  # Maximum width: 800px, height: 600px
        
        # Bind resize events to enforce size limits
        self.root.bind('<Configure>', self.enforce_size_limits)
        
        # Center the window
        self.root.eval('tk::PlaceWindow . center')
        
        # Timer variables
        self.timer_running = False
        self.timer_thread = None
        self.remaining_seconds = 0
        self.mode = "countdown"  # "countdown" or "scheduled"
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame to expand in all directions
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure main frame grid weights for proper centering
        main_frame.grid_rowconfigure(0, weight=1)  # Top space
        main_frame.grid_rowconfigure(1, weight=0)  # Title
        main_frame.grid_rowconfigure(2, weight=0)  # Mode frame
        main_frame.grid_rowconfigure(3, weight=0)  # Timer label
        main_frame.grid_rowconfigure(4, weight=0)  # Settings frame
        main_frame.grid_rowconfigure(5, weight=0)  # Buttons
        main_frame.grid_rowconfigure(6, weight=1)  # Bottom space
        
        main_frame.grid_columnconfigure(0, weight=1)  # Left space
        main_frame.grid_columnconfigure(1, weight=0)  # Content
        main_frame.grid_columnconfigure(2, weight=1)  # Right space
        
        # Title
        title_label = ttk.Label(main_frame, text="Shutdown Scheduler", font=("Arial", 18, "bold"))
        title_label.grid(row=1, column=1, pady=(0, 20))
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Timer Mode", padding="10")
        mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Configure mode frame grid weights BEFORE placing widgets
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        self.mode_var = tk.StringVar(value="countdown")
        countdown_radio = ttk.Radiobutton(mode_frame, text="Countdown Timer", variable=self.mode_var, 
                                        value="countdown", command=self.on_mode_change)
        countdown_radio.grid(row=0, column=0, sticky=tk.EW, padx=(0, 20))
        
        scheduled_radio = ttk.Radiobutton(mode_frame, text="Scheduled Time", variable=self.mode_var, 
                                        value="scheduled", command=self.on_mode_change)
        scheduled_radio.grid(row=0, column=1, sticky=tk.EW)
        
        # Timer display
        self.timer_label = ttk.Label(main_frame, text="Set timer duration", font=("Arial", 14))
        self.timer_label.grid(row=3, column=1, pady=(0, 20))
        
        # Configure timer label to center
        self.timer_label.configure(anchor="center")
        
        # Countdown mode frame
        self.countdown_frame = ttk.LabelFrame(main_frame, text="Countdown Settings", padding="10")
        self.countdown_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure countdown frame grid weights BEFORE placing widgets
        self.countdown_frame.columnconfigure(0, weight=1)
        self.countdown_frame.columnconfigure(1, weight=2)
        
        # Hours input
        ttk.Label(self.countdown_frame, text="Hours:").grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        self.hours_var = tk.StringVar(value="0")
        hours_spinbox = ttk.Spinbox(self.countdown_frame, from_=0, to=23, width=10, textvariable=self.hours_var)
        hours_spinbox.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Minutes input
        ttk.Label(self.countdown_frame, text="Minutes:").grid(row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        self.minutes_var = tk.StringVar(value="30")
        minutes_spinbox = ttk.Spinbox(self.countdown_frame, from_=0, to=59, width=10, textvariable=self.minutes_var)
        minutes_spinbox.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Scheduled mode frame
        self.scheduled_frame = ttk.LabelFrame(main_frame, text="Scheduled Settings", padding="10")
        self.scheduled_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure scheduled frame grid weights BEFORE placing widgets
        self.scheduled_frame.columnconfigure(0, weight=1)
        self.scheduled_frame.columnconfigure(1, weight=2)
        self.scheduled_frame.columnconfigure(2, weight=1)
        
        # Date input with spinboxes
        ttk.Label(self.scheduled_frame, text="Date:").grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        # Date frame for spinboxes
        date_frame = ttk.Frame(self.scheduled_frame)
        date_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Get tomorrow's date for defaults
        tomorrow = datetime.now() + timedelta(days=1)
        
        # Get current date for validation
        current_date = datetime.now()
        
        # Day spinbox
        self.day_var = tk.StringVar(value=str(tomorrow.day))
        day_spinbox = ttk.Spinbox(date_frame, from_=1, to=31, width=5, textvariable=self.day_var)
        day_spinbox.grid(row=0, column=0, padx=(0, 2))
        
        # Month spinbox
        self.month_var = tk.StringVar(value=str(tomorrow.month))
        month_spinbox = ttk.Spinbox(date_frame, from_=1, to=12, width=5, textvariable=self.month_var)
        month_spinbox.grid(row=0, column=1, padx=(2, 2))
        
        # Year spinbox
        self.year_var = tk.StringVar(value=str(tomorrow.year))
        year_spinbox = ttk.Spinbox(date_frame, from_=current_date.year, to=2030, width=7, textvariable=self.year_var)
        year_spinbox.grid(row=0, column=2, padx=(2, 0))
        
        # Get system date format for the label
        system_format = self.get_system_date_format()
        ttk.Label(self.scheduled_frame, text=f"({system_format})").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Time input with spinboxes
        ttk.Label(self.scheduled_frame, text="Time:").grid(row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        # Time frame for spinboxes
        time_frame = ttk.Frame(self.scheduled_frame)
        time_frame.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Hour spinbox
        self.hour_var = tk.StringVar(value="22")
        hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, width=5, textvariable=self.hour_var)
        hour_spinbox.grid(row=0, column=0, padx=(0, 2))
        
        # Minute spinbox
        self.minute_var = tk.StringVar(value="00")
        minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, width=5, textvariable=self.minute_var)
        minute_spinbox.grid(row=0, column=1, padx=(2, 0))
        
        # Store spinbox references for dynamic validation
        self.day_spinbox = day_spinbox
        self.month_spinbox = month_spinbox
        self.year_spinbox = year_spinbox
        self.hour_spinbox = hour_spinbox
        self.minute_spinbox = minute_spinbox
        
        ttk.Label(self.scheduled_frame, text="(HH:MM)").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=1, pady=20)
        
        # Configure button frame grid weights
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Timer", command=self.start_timer, style="Accent.TButton")
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Cancel button
        self.cancel_button = ttk.Button(button_frame, text="Cancel Timer", command=self.cancel_timer, state="disabled")
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Initialize UI
        self.on_mode_change()
        
    def enforce_size_limits(self, event):
        """Enforce minimum and maximum window size limits"""
        # Only handle window resize events (not child widget events)
        if event.widget == self.root:
            width = event.width
            height = event.height
            
            # Check if size is outside limits
            new_width = width
            new_height = height
            
            # Enforce minimum size
            if width < 400:
                new_width = 400
            if height < 350:
                new_height = 350
                
            # Enforce maximum size
            if width > 800:
                new_width = 800
            if height > 600:
                new_height = 600
            
            # If size needs to be adjusted, update it
            if new_width != width or new_height != height:
                self.root.geometry(f"{new_width}x{new_height}")
        
    def get_tomorrow_date(self):
        """Get tomorrow's date in system format"""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime("%x")  # Use system date format
    
    def get_system_date_format(self):
        """Detect the system's date format"""
        import locale
        try:
            # Get system locale
            system_locale = locale.getlocale()
            if system_locale[0]:
                locale.setlocale(locale.LC_TIME, system_locale[0])
            
            # Test with a known date to see the format
            test_date = datetime(2024, 12, 25)  # December 25, 2024
            formatted = test_date.strftime("%x")
            
            # Parse the formatted date to determine the actual format
            parts = formatted.replace("-", "/").split("/")
            if len(parts) == 3:
                # Check if December (12) is in the first position (MM/DD/YYYY)
                if "12" in parts[0]:
                    return "MM/DD/YYYY"  # US format
                # Check if December (12) is in the second position (DD/MM/YYYY)
                elif "12" in parts[1]:
                    return "DD/MM/YYYY"  # European format
                # Check if year (2024) is in the first position (YYYY-MM-DD)
                elif "2024" in parts[0]:
                    return "YYYY-MM-DD"  # ISO format
                else:
                    # Fallback: check the length of first part
                    if len(parts[0]) == 4:  # Year is first
                        return "YYYY-MM-DD"
                    elif len(parts[0]) == 2:  # Could be either MM or DD
                        # If second part is also 2 digits, assume MM/DD/YYYY
                        return "MM/DD/YYYY"
                    else:
                        return "DD/MM/YYYY"  # Default to European
            else:
                return "DD/MM/YYYY"  # Default to European format
        except:
            return "DD/MM/YYYY"  # Default to European format
    
    def update_day_range(self):
        """Update the day spinbox range based on selected month and year"""
        try:
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            
            # Get the last day of the selected month
            if month == 2:  # February
                if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                    max_day = 29  # Leap year
                else:
                    max_day = 28
            elif month in [4, 6, 9, 11]:  # April, June, September, November
                max_day = 30
            else:
                max_day = 31
            
            # Update day spinbox range
            current_day = int(self.day_var.get())
            if current_day > max_day:
                self.day_var.set(str(max_day))
            
            # Update the spinbox configuration
            self.day_spinbox.config(to=max_day)
            
        except ValueError:
            pass  # Ignore if values are not valid numbers yet
    
    def on_mode_change(self):
        """Handle mode change between countdown and scheduled"""
        mode = self.mode_var.get()
        if mode == "countdown":
            self.countdown_frame.grid()
            self.scheduled_frame.grid_remove()
            self.timer_label.config(text="Set countdown duration")
        else:
            self.countdown_frame.grid_remove()
            self.scheduled_frame.grid()
            self.timer_label.config(text="Set scheduled time")
    
    def start_timer(self):
        mode = self.mode_var.get()
        
        if mode == "countdown":
            self.start_countdown_timer()
        else:
            self.start_scheduled_timer()
    
    def start_countdown_timer(self):
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            
            if hours == 0 and minutes == 0:
                messagebox.showwarning("Invalid Time", "Please set a time greater than 0 minutes.")
                return
                
            total_seconds = hours * 3600 + minutes * 60
            self.remaining_seconds = total_seconds
            self.mode = "countdown"
            
            # Update display
            self.update_timer_display()
            
            # Start timer thread
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
            
            # Update UI
            self.start_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours and minutes.")
    
    def start_scheduled_timer(self):
        try:
            # Get values from spinboxes
            day = int(self.day_var.get())
            month = int(self.month_var.get())
            year = int(self.year_var.get())
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            
            # Validate date
            try:
                scheduled_datetime = datetime(year, month, day, hour, minute)
            except ValueError:
                messagebox.showerror("Invalid Date", "Please enter a valid date.")
                return
            
            current_datetime = datetime.now()
            
            # Smart validation for today's date
            if scheduled_datetime.date() == current_datetime.date():
                # If it's today, check if time is in the future
                if scheduled_datetime.time() <= current_datetime.time():
                    messagebox.showwarning("Invalid Time", "Scheduled time must be in the future.")
                    return
            elif scheduled_datetime <= current_datetime:
                messagebox.showwarning("Invalid Time", "Scheduled time must be in the future.")
                return
            
            # Calculate seconds until scheduled time
            time_diff = scheduled_datetime - current_datetime
            self.remaining_seconds = int(time_diff.total_seconds())
            self.mode = "scheduled"
            
            # Update display
            self.update_timer_display()
            
            # Start timer thread
            self.timer_running = True
            self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
            self.timer_thread.start()
            
            # Update UI
            self.start_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for date and time.")
    
    def cancel_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.remaining_seconds = 0
            self.timer_label.config(text="Set timer duration")
            self.start_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            # Reset mode display
            self.on_mode_change()
    
    def timer_loop(self):
        while self.timer_running and self.remaining_seconds > 0:
            time.sleep(1)
            self.remaining_seconds -= 1
            
            # Update display in main thread
            self.root.after(0, self.update_timer_display)
            
            if self.remaining_seconds <= 0 and self.timer_running:
                self.root.after(0, self.shutdown_computer)
                break
    
    def update_timer_display(self):
        if self.remaining_seconds > 0:
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            
            if self.mode == "countdown":
                if hours > 0:
                    display_text = f"Close the computer in {hours} hours {minutes} minutes"
                else:
                    display_text = f"Close the computer in {minutes} minutes {seconds} seconds"
            else:  # scheduled mode
                if hours > 0:
                    display_text = f"Close the computer in {hours} hours {minutes} minutes"
                else:
                    display_text = f"Close the computer in {minutes} minutes {seconds} seconds"
            
            self.timer_label.config(text=display_text)
        else:
            mode_text = "countdown duration" if self.mode == "countdown" else "scheduled time"
            self.timer_label.config(text=f"Set {mode_text}")
    
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
    app = EnhancedShutdownTimer()
    app.run()

if __name__ == "__main__":
    main() 