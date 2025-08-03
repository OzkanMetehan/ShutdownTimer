#!/usr/bin/env python3
"""
Shutdown Scheduler - A simple Windows desktop application for scheduling computer shutdowns.

Features:
- Countdown timer: Set hours and minutes for immediate shutdown
- Scheduled timer: Set a specific date and time for future shutdown
- Adaptive UI: Responsive layout that centers content
- Dark theme: Modern dark interface
- Size constraints: Prevents window from becoming too small or large

Author: AI Assistant
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
from datetime import datetime, timedelta

class ShutdownScheduler:
    """
    Main application class for the Shutdown Scheduler.
    
    Provides a GUI for scheduling computer shutdowns with two modes:
    1. Countdown Timer: Set hours and minutes for immediate countdown
    2. Scheduled Timer: Set a specific date and time for future shutdown
    """
    
    def __init__(self):
        """Initialize the application window and variables."""
        # Create main window
        self.root = tk.Tk()
        self.root.title("Shutdown Scheduler")
        self.root.geometry("450x400")
        self.root.resizable(True, True)
        
        # Apply dark theme
        self.root.configure(bg='#2b2b2b')
        
        # Set window size constraints
        self.root.minsize(400, 350)
        self.root.maxsize(800, 600)
        
        # Bind resize events to enforce size limits
        self.root.bind('<Configure>', self.enforce_size_limits)
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        # Initialize timer state variables
        self.timer_running = False
        self.timer_thread = None
        self.remaining_seconds = 0
        self.mode = "countdown"  # "countdown" or "scheduled"
        
        # Setup the user interface
        self.setup_ui()
        
    def setup_ui(self):
        """Create and configure the user interface layout."""
        # Main container frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure root window to expand main frame
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Configure main frame grid for centered layout
        # Rows: 0=top space, 1=title, 2=mode, 3=timer, 4=settings, 5=buttons, 6=bottom space
        main_frame.grid_rowconfigure(0, weight=1)  # Top space
        main_frame.grid_rowconfigure(1, weight=0)  # Title
        main_frame.grid_rowconfigure(2, weight=0)  # Mode frame
        main_frame.grid_rowconfigure(3, weight=0)  # Timer label
        main_frame.grid_rowconfigure(4, weight=0)  # Settings frame
        main_frame.grid_rowconfigure(5, weight=0)  # Buttons
        main_frame.grid_rowconfigure(6, weight=1)  # Bottom space
        
        # Columns: 0=left space, 1=content, 2=right space
        main_frame.grid_columnconfigure(0, weight=1)  # Left space
        main_frame.grid_columnconfigure(1, weight=0)  # Content
        main_frame.grid_columnconfigure(2, weight=1)  # Right space
        
        # Application title
        title_label = ttk.Label(main_frame, text="Shutdown Scheduler", font=("Arial", 18, "bold"))
        title_label.grid(row=1, column=1, pady=(0, 20))
        
        # Timer mode selection frame
        mode_frame = ttk.LabelFrame(main_frame, text="Timer Mode", padding="10")
        mode_frame.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Configure mode frame for equal button distribution
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)
        
        # Mode selection radio buttons
        self.mode_var = tk.StringVar(value="countdown")
        
        countdown_radio = ttk.Radiobutton(
            mode_frame, 
            text="Countdown Timer", 
            variable=self.mode_var, 
            value="countdown", 
            command=self.on_mode_change
        )
        countdown_radio.grid(row=0, column=0, sticky=tk.EW, padx=(0, 20))
        
        scheduled_radio = ttk.Radiobutton(
            mode_frame, 
            text="Scheduled Time", 
            variable=self.mode_var, 
            value="scheduled", 
            command=self.on_mode_change
        )
        scheduled_radio.grid(row=0, column=1, sticky=tk.EW)
        
        # Timer display label
        self.timer_label = ttk.Label(main_frame, text="Set timer duration", font=("Arial", 14))
        self.timer_label.grid(row=3, column=1, pady=(0, 20))
        self.timer_label.configure(anchor="center")
        
        # Countdown settings frame
        self.countdown_frame = ttk.LabelFrame(main_frame, text="Countdown Settings", padding="10")
        self.countdown_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure countdown frame layout
        self.countdown_frame.columnconfigure(0, weight=1)  # Labels
        self.countdown_frame.columnconfigure(1, weight=2)  # Input fields
        
        # Hours input
        hours_label = ttk.Label(self.countdown_frame, text="Hours:")
        hours_label.grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        self.hours_var = tk.StringVar(value="0")
        hours_spinbox = ttk.Spinbox(
            self.countdown_frame, 
            from_=0, to=23, 
            width=10, 
            textvariable=self.hours_var
        )
        hours_spinbox.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Minutes input
        minutes_label = ttk.Label(self.countdown_frame, text="Minutes:")
        minutes_label.grid(row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        self.minutes_var = tk.StringVar(value="30")
        minutes_spinbox = ttk.Spinbox(
            self.countdown_frame, 
            from_=0, to=59, 
            width=10, 
            textvariable=self.minutes_var
        )
        minutes_spinbox.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Scheduled settings frame
        self.scheduled_frame = ttk.LabelFrame(main_frame, text="Scheduled Settings", padding="10")
        self.scheduled_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Configure scheduled frame layout
        self.scheduled_frame.columnconfigure(0, weight=1)  # Labels
        self.scheduled_frame.columnconfigure(1, weight=2)  # Input fields
        self.scheduled_frame.columnconfigure(2, weight=1)  # Format labels
        
        # Date input section
        date_label = ttk.Label(self.scheduled_frame, text="Date:")
        date_label.grid(row=0, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        # Date input frame for spinboxes
        date_frame = ttk.Frame(self.scheduled_frame)
        date_frame.grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        # Get tomorrow's date for default values
        tomorrow = datetime.now() + timedelta(days=1)
        current_date = datetime.now()
        
        # Day spinbox
        self.day_var = tk.StringVar(value=str(tomorrow.day))
        day_spinbox = ttk.Spinbox(
            date_frame, 
            from_=1, to=31, 
            width=5, 
            textvariable=self.day_var
        )
        day_spinbox.grid(row=0, column=0, padx=(0, 2))
        
        # Month spinbox
        self.month_var = tk.StringVar(value=str(tomorrow.month))
        month_spinbox = ttk.Spinbox(
            date_frame, 
            from_=1, to=12, 
            width=5, 
            textvariable=self.month_var
        )
        month_spinbox.grid(row=0, column=1, padx=(2, 2))
        
        # Year spinbox
        self.year_var = tk.StringVar(value=str(tomorrow.year))
        year_spinbox = ttk.Spinbox(
            date_frame, 
            from_=current_date.year, to=2030, 
            width=7, 
            textvariable=self.year_var
        )
        year_spinbox.grid(row=0, column=2, padx=(2, 0))
        
        # Date format label
        system_format = self.get_system_date_format()
        format_label = ttk.Label(self.scheduled_frame, text=f"({system_format})")
        format_label.grid(row=0, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Time input section
        time_label = ttk.Label(self.scheduled_frame, text="Time:")
        time_label.grid(row=1, column=0, sticky=tk.E, pady=5, padx=(0, 10))
        
        # Time input frame for spinboxes
        time_frame = ttk.Frame(self.scheduled_frame)
        time_frame.grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        # Hour spinbox
        self.hour_var = tk.StringVar(value="22")
        hour_spinbox = ttk.Spinbox(
            time_frame, 
            from_=0, to=23, 
            width=5, 
            textvariable=self.hour_var
        )
        hour_spinbox.grid(row=0, column=0, padx=(0, 2))
        
        # Minute spinbox
        self.minute_var = tk.StringVar(value="00")
        minute_spinbox = ttk.Spinbox(
            time_frame, 
            from_=0, to=59, 
            width=5, 
            textvariable=self.minute_var
        )
        minute_spinbox.grid(row=0, column=1, padx=(2, 0))
        
        # Time format label
        time_format_label = ttk.Label(self.scheduled_frame, text="(HH:MM)")
        time_format_label.grid(row=1, column=2, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=1, pady=20)
        
        # Configure button frame for equal button distribution
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Start timer button
        self.start_button = ttk.Button(
            button_frame, 
            text="Start Timer", 
            command=self.start_timer
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Cancel timer button
        self.cancel_button = ttk.Button(
            button_frame, 
            text="Cancel Timer", 
            command=self.cancel_timer, 
            state="disabled"
        )
        self.cancel_button.grid(row=0, column=1, padx=5)
        
        # Initialize UI to show countdown mode by default
        self.on_mode_change()
    
    def enforce_size_limits(self, event):
        """
        Enforce minimum and maximum window size limits.
        
        Args:
            event: The configure event containing window dimensions
        """
        # Only handle window resize events (not child widget events)
        if event.widget == self.root:
            width = event.width
            height = event.height
            
            # Check if size is outside limits
            new_width = width
            new_height = height
            
            # Enforce minimum size (400x350)
            if width < 400:
                new_width = 400
            if height < 350:
                new_height = 350
                
            # Enforce maximum size (800x600)
            if width > 800:
                new_width = 800
            if height > 600:
                new_height = 600
            
            # If size needs to be adjusted, update it
            if new_width != width or new_height != height:
                self.root.geometry(f"{new_width}x{new_height}")
    
    def get_system_date_format(self):
        """
        Detect the system's date format for display purposes.
        
        Returns:
            str: The detected date format (MM/DD/YYYY, DD/MM/YYYY, or YYYY-MM-DD)
        """
        import locale
        try:
            # Get system locale
            system_locale = locale.getlocale()
            if system_locale[0]:
                locale.setlocale(locale.LC_TIME, system_locale[0])
            
            # Test with a known date to determine the format
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
    
    def on_mode_change(self):
        """Handle mode change between countdown and scheduled timer modes."""
        mode = self.mode_var.get()
        if mode == "countdown":
            # Show countdown settings, hide scheduled settings
            self.countdown_frame.grid()
            self.scheduled_frame.grid_remove()
            self.timer_label.config(text="Set countdown duration")
        else:
            # Show scheduled settings, hide countdown settings
            self.countdown_frame.grid_remove()
            self.scheduled_frame.grid()
            self.timer_label.config(text="Set scheduled time")
    
    def start_timer(self):
        """Start the timer based on the selected mode."""
        mode = self.mode_var.get()
        
        if mode == "countdown":
            self.start_countdown_timer()
        else:
            self.start_scheduled_timer()
    
    def start_countdown_timer(self):
        """Start a countdown timer with the specified hours and minutes."""
        try:
            hours = int(self.hours_var.get())
            minutes = int(self.minutes_var.get())
            
            # Validate that at least some time is set
            if hours == 0 and minutes == 0:
                messagebox.showwarning("Invalid Time", "Please set a time greater than 0 minutes.")
                return
                
            # Calculate total seconds
            total_seconds = hours * 3600 + minutes * 60
            self.remaining_seconds = total_seconds
            self.mode = "countdown"
            
            # Update display and start timer
            self.update_timer_display()
            self.start_timer_thread()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hours and minutes.")
    
    def start_scheduled_timer(self):
        """Start a scheduled timer for the specified date and time."""
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
            
            # Update display and start timer
            self.update_timer_display()
            self.start_timer_thread()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for date and time.")
    
    def start_timer_thread(self):
        """Start the timer thread and update UI state."""
        # Start timer thread
        self.timer_running = True
        self.timer_thread = threading.Thread(target=self.timer_loop, daemon=True)
        self.timer_thread.start()
        
        # Update UI
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")
    
    def cancel_timer(self):
        """Cancel the running timer and reset UI state."""
        if self.timer_running:
            self.timer_running = False
            self.remaining_seconds = 0
            self.timer_label.config(text="Set timer duration")
            self.start_button.config(state="normal")
            self.cancel_button.config(state="disabled")
            # Reset mode display
            self.on_mode_change()
    
    def timer_loop(self):
        """Main timer loop that runs in a separate thread."""
        while self.timer_running and self.remaining_seconds > 0:
            time.sleep(1)
            self.remaining_seconds -= 1
            
            # Update display in main thread
            self.root.after(0, self.update_timer_display)
            
            # Check if timer has finished
            if self.remaining_seconds <= 0 and self.timer_running:
                self.root.after(0, self.shutdown_computer)
                break
    
    def update_timer_display(self):
        """Update the timer display label with current countdown."""
        if self.remaining_seconds > 0:
            # Calculate hours, minutes, and seconds
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            
            # Create display text based on remaining time
            if hours > 0:
                display_text = f"Close the computer in {hours} hours {minutes} minutes"
            else:
                display_text = f"Close the computer in {minutes} minutes {seconds} seconds"
            
            self.timer_label.config(text=display_text)
        else:
            # Reset display when timer is not running
            mode_text = "countdown duration" if self.mode == "countdown" else "scheduled time"
            self.timer_label.config(text=f"Set {mode_text}")
    
    def shutdown_computer(self):
        """Show shutdown countdown popup and execute shutdown after 30 seconds."""
        # Create shutdown countdown popup
        self.show_shutdown_countdown()
    
    def show_shutdown_countdown(self):
        """Display a countdown popup with 30 seconds to cancel shutdown."""
        # Create popup window
        self.countdown_popup = tk.Toplevel(self.root)
        self.countdown_popup.title("Shutdown Countdown")
        self.countdown_popup.geometry("400x200")
        self.countdown_popup.resizable(False, False)
        self.countdown_popup.configure(bg='#2b2b2b')
        
        # Make popup modal (user must interact with it)
        self.countdown_popup.transient(self.root)
        self.countdown_popup.grab_set()
        
        # Center the popup
        self.countdown_popup.eval('tk::PlaceWindow . center')
        
        # Configure popup grid
        self.countdown_popup.grid_rowconfigure(0, weight=1)
        self.countdown_popup.grid_rowconfigure(1, weight=1)
        self.countdown_popup.grid_rowconfigure(2, weight=1)
        self.countdown_popup.grid_columnconfigure(0, weight=1)
        
        # Warning message
        warning_label = ttk.Label(
            self.countdown_popup, 
            text="⚠️ WARNING: Computer will shutdown!", 
            font=("Arial", 14, "bold"),
            foreground="red"
        )
        warning_label.grid(row=0, column=0, pady=(20, 10))
        
        # Countdown label
        self.countdown_label = ttk.Label(
            self.countdown_popup, 
            text="Computer will shutdown in 30 seconds", 
            font=("Arial", 12)
        )
        self.countdown_label.grid(row=1, column=0, pady=10)
        
        # Cancel button
        cancel_button = ttk.Button(
            self.countdown_popup, 
            text="Cancel Shutdown", 
            command=self.cancel_shutdown_countdown,
            style="Accent.TButton"
        )
        cancel_button.grid(row=2, column=0, pady=(10, 20))
        
        # Start countdown
        self.countdown_seconds = 30
        self.countdown_popup_running = True
        self.update_shutdown_countdown()
    
    def update_shutdown_countdown(self):
        """Update the countdown display and handle shutdown."""
        if self.countdown_popup_running and self.countdown_seconds > 0:
            # Update countdown label
            self.countdown_label.config(text=f"Computer will shutdown in {self.countdown_seconds} seconds")
            
            # Decrease countdown
            self.countdown_seconds -= 1
            
            # Schedule next update in 1 second
            self.countdown_popup.after(1000, self.update_shutdown_countdown)
        elif self.countdown_popup_running and self.countdown_seconds <= 0:
            # Time's up - execute shutdown
            self.execute_shutdown()
    
    def cancel_shutdown_countdown(self):
        """Cancel the shutdown countdown and close popup."""
        self.countdown_popup_running = False
        
        # Close popup
        if hasattr(self, 'countdown_popup'):
            self.countdown_popup.destroy()
        
        # Reset timer state
        self.cancel_timer()
    
    def execute_shutdown(self):
        """Execute the actual shutdown command."""
        try:
            # Close popup first
            if hasattr(self, 'countdown_popup'):
                self.countdown_popup.destroy()
            
            # Windows shutdown command
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to shutdown computer. Please shutdown manually.")
            self.cancel_timer()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    app = ShutdownScheduler()
    app.run()


if __name__ == "__main__":
    main() 