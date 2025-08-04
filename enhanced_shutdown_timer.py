#!/usr/bin/env python3
"""
Shutdown Scheduler - A simple Windows desktop application for scheduling computer shutdowns.

Features:
- Countdown timer: Set hours and minutes for immediate shutdown
- Scheduled timer: Set a specific date and time for future shutdown
- Modern interface: Clean and intuitive design
- Size constraints: Prevents window from becoming too small or large
- Single instance: Prevents multiple instances from running simultaneously
- System tray: Minimize to tray when timer is running

Author: AI Assistant
License: MIT
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
from datetime import datetime, timedelta
import pystray
from PIL import Image, ImageDraw
import signal
import sys
import os
import tempfile

# Try to import psutil for single instance detection
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class ShutdownScheduler:
    """
    Main application class for the Shutdown Scheduler.
    
    Provides a GUI for scheduling computer shutdowns with two modes:
    1. Countdown Timer: Set hours and minutes for immediate countdown
    2. Scheduled Timer: Set a specific date and time for future shutdown
    """
    
    def __init__(self):
        """Initialize the application window and variables."""
        # Check for existing instance before creating the app
        if not self.check_single_instance():
            # Exit the application if another instance is running
            sys.exit(0)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Shutdown Scheduler")
        self.root.geometry("450x400")
        self.root.resizable(True, True)
        
        # Apply default theme
        self.root.configure(bg='#f0f0f0')
        
        # Set window size constraints
        self.root.minsize(400, 350)
        self.root.maxsize(800, 600)
        
        # Bind window events
        self.root.bind('<Configure>', self.enforce_size_limits)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Center the window on screen
        self.root.eval('tk::PlaceWindow . center')
        
        # Initialize timer state variables
        self.timer_running = False
        self.timer_thread = None
        self.remaining_seconds = 0
        self.mode = "countdown"  # "countdown" or "scheduled"
        
        # Initialize system tray
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        # Setup the user interface
        self.setup_ui()
        
        # Setup system tray
        self.setup_system_tray()
        
        # Setup signal handlers for proper cleanup
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Create lock file for single instance
        self.create_lock_file()
    
    def check_single_instance(self):
        """
        Check if another instance of the app is already running.
        
        Returns:
            bool: True if this is the only instance, False if another instance exists
        """
        # If psutil is not available, use simple file-based check
        if not PSUTIL_AVAILABLE:
            lock_file_name = "shutdown_scheduler.lock"
            lock_file_path = os.path.join(tempfile.gettempdir(), lock_file_name)
            self.lock_file_path = lock_file_path
            return True
        
        # Create a unique lock file name
        lock_file_name = "shutdown_scheduler.lock"
        lock_file_path = os.path.join(tempfile.gettempdir(), lock_file_name)
        
        # Check if lock file exists
        if os.path.exists(lock_file_path):
            try:
                # Read the PID from the lock file
                with open(lock_file_path, 'r') as f:
                    pid_str = f.read().strip()
                    if pid_str.isdigit():
                        pid = int(pid_str)
                        
                        # Check if the process is still running
                        if psutil.pid_exists(pid):
                            # Check if it's actually our app by checking all processes
                            try:
                                # Get all processes and check for our app
                                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                    try:
                                        if proc.info['pid'] == pid:
                                            # This is the process from our lock file
                                            # Check if it's our app by name or command line
                                            proc_name = proc.info['name'].lower()
                                            cmdline = proc.info['cmdline']
                                            
                                            # Check for our executable or Python script
                                            if (any('shutdownscheduler' in name.lower() for name in [proc_name] + cmdline) or
                                                any('enhanced_shutdown_timer.py' in arg for arg in cmdline)):
                                                # Another instance is running
                                                self.show_instance_warning()
                                                return False
                                            break
                                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                                        continue
                            except Exception as e:
                                pass
                        
                        # Process doesn't exist, remove stale lock file
                        try:
                            os.remove(lock_file_path)
                        except:
                            pass
            except Exception as e:
                # If we can't read the lock file, try to remove it
                try:
                    os.remove(lock_file_path)
                except:
                    pass
        
        # Store lock file path for cleanup
        self.lock_file_path = lock_file_path
        return True
    
    def show_instance_warning(self):
        """Show a warning message that another instance is already running."""
        # Create a temporary root window to show the message
        temp_root = tk.Tk()
        temp_root.withdraw()  # Hide the window
        
        # Show warning message
        messagebox.showwarning(
            "Application Already Running",
            "Shutdown Scheduler is already running.\n\n"
            "Please use the existing instance instead of opening a new one.",
            parent=temp_root
        )
        
        # Destroy the temporary root
        temp_root.destroy()
        
        # Exit the application after showing the warning
        sys.exit(0)
    
    def create_lock_file(self):
        """Create a lock file with the current process ID."""
        try:
            with open(self.lock_file_path, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            pass
    
    def cleanup_lock_file(self):
        """Remove the lock file when the application exits."""
        try:
            if hasattr(self, 'lock_file_path') and os.path.exists(self.lock_file_path):
                os.remove(self.lock_file_path)
        except Exception as e:
            pass
    
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
        Enforce minimum and maximum window size limits and detect minimize.
        
        Args:
            event: The configure event containing window dimensions
        """
        # Only handle root window events
        if event.widget == self.root:
            # Check if window was minimized
            if self.root.state() == 'iconic' and self.timer_running:
                # User clicked minimize button and timer is running
                self.minimize_to_tray()
                return
            
            # Handle size limits
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
        
        # Reset UI state
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
                # Stop the timer thread before showing popup
                self.timer_running = False
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
            
            # Update tray tooltip if minimized
            if self.is_minimized_to_tray:
                self.update_tray_tooltip()
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
        self.countdown_popup.configure(bg='#f0f0f0')
        
        # Make popup modal (user must interact with it)
        self.countdown_popup.transient(self.root)
        self.countdown_popup.grab_set()
        
        # Center the popup
        self.center_popup()
        
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
    
    def center_popup(self):
        """Center the popup window on screen."""
        self.countdown_popup.update_idletasks()
        width = self.countdown_popup.winfo_width()
        height = self.countdown_popup.winfo_height()
        x = (self.countdown_popup.winfo_screenwidth() // 2) - (width // 2)
        y = (self.countdown_popup.winfo_screenheight() // 2) - (height // 2)
        self.countdown_popup.geometry(f"{width}x{height}+{x}+{y}")
    
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
    
    def create_tray_icon(self):
        """Create a simple icon for the system tray."""
        # Create a 64x64 icon with a simple design
        width = 64
        height = 64
        
        # Create image with dark background
        image = Image.new('RGBA', (width, height), (43, 43, 43, 255))
        draw = ImageDraw.Draw(image)
        
        # Draw a simple clock/timer icon
        # Outer circle
        draw.ellipse([8, 8, width-8, height-8], outline=(255, 255, 255, 255), width=3)
        
        # Clock hands
        center_x, center_y = width // 2, height // 2
        # Hour hand
        draw.line([center_x, center_y, center_x, 12], fill=(255, 255, 255, 255), width=3)
        # Minute hand
        draw.line([center_x, center_y, center_x + 8, center_y], fill=(255, 255, 255, 255), width=2)
        
        return image
    
    def setup_system_tray(self):
        """Setup the system tray icon and menu."""
        try:
            # Create tray icon
            icon_image = self.create_tray_icon()
            
            # Create tray menu with proper callbacks
            menu = pystray.Menu(
                pystray.MenuItem("Show Window", self.show_window, default=True),
                pystray.MenuItem("Cancel Timer", self.cancel_timer_from_tray),
                pystray.MenuItem("Exit", self.quit_app)
            )
            
            # Create tray icon with unique name
            import os
            unique_id = str(os.getpid())
            self.tray_icon = pystray.Icon(
                f"shutdown_scheduler_{unique_id}",
                icon_image,
                "Shutdown Scheduler",
                menu
            )
            
        except Exception as e:
            self.tray_icon = None
    

    
    def minimize_to_tray(self):
        """Minimize the window to system tray."""
        try:
            self.root.withdraw()  # Hide the window
            self.is_minimized_to_tray = True
            
            # Start tray icon if not already running
            if self.tray_icon:
                if not self.tray_icon.visible:
                    # Run tray icon in a separate thread to avoid blocking
                    import threading
                    tray_thread = threading.Thread(target=self.tray_icon.run_detached, daemon=True)
                    tray_thread.start()
                else:
                    # If already visible, update the tooltip
                    self.update_tray_tooltip()
        except Exception as e:
            pass
    
    def cleanup_tray_icon(self):
        """Clean up the tray icon properly."""
        try:
            if self.tray_icon:
                if self.tray_icon.visible:
                    self.tray_icon.stop()
                self.tray_icon = None
        except Exception as e:
            pass
    
    def __del__(self):
        """Destructor to ensure tray icon is cleaned up."""
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon:
                if self.tray_icon.visible:
                    self.tray_icon.stop()
        except:
            pass
    
    def show_window(self, icon=None, item=None):
        """Show the main window from system tray."""
        try:
            self.root.deiconify()  # Show the window
            self.root.lift()  # Bring to front
            self.root.focus_force()  # Focus the window
            self.is_minimized_to_tray = False
            
            # Don't stop the tray icon - keep it running for future minimize
            # The tray icon will be cleaned up when the app exits
                
        except Exception as e:
            pass
    
    def cancel_timer_from_tray(self, icon=None, item=None):
        """Cancel timer from system tray menu."""
        self.cancel_timer()
        if self.is_minimized_to_tray:
            self.show_window()
    
    def on_closing(self):
        """Handle window closing event."""
        if self.timer_running:
            # If timer is running, minimize to tray instead of closing
            self.minimize_to_tray()
        else:
            # If no timer running, close the app
            self.quit_app()
    
    def force_quit(self):
        """Force quit the application with proper cleanup."""
        try:
            # Stop tray icon first - this is critical
            if self.tray_icon:
                try:
                    if self.tray_icon.visible:
                        self.tray_icon.stop()
                        # Give it a moment to stop
                        import time
                        time.sleep(0.1)
                except Exception as e:
                    pass
                finally:
                    self.tray_icon = None
            
            # Clean up lock file
            self.cleanup_lock_file()
            
            # Use sys.exit for proper cleanup
            sys.exit(0)
        except:
            import os
            os._exit(0)
    
    def quit_app(self, icon=None, item=None):
        """Quit the application."""
        try:
            # Stop tray icon first - this is critical
            if self.tray_icon:
                try:
                    if self.tray_icon.visible:
                        self.tray_icon.stop()
                        # Give it a moment to stop
                        import time
                        time.sleep(0.1)
                except Exception as e:
                    pass
                finally:
                    self.tray_icon = None
            
            # Cancel any running timer
            if self.timer_running:
                self.cancel_timer()
            
            # Clean up lock file
            self.cleanup_lock_file()
            
            # Destroy the main window
            self.root.destroy()
            
            # Use sys.exit instead of os._exit for proper cleanup
            sys.exit(0)
            
        except Exception as e:
            # Clean up lock file even if there's an error
            try:
                self.cleanup_lock_file()
            except:
                pass
            # Force exit even if there's an error
            import os
            os._exit(0)
    
    def update_tray_tooltip(self):
        """Update the tray icon tooltip with remaining time."""
        if self.tray_icon and self.timer_running and self.remaining_seconds > 0:
            # Calculate remaining time
            hours = self.remaining_seconds // 3600
            minutes = (self.remaining_seconds % 3600) // 60
            seconds = self.remaining_seconds % 60
            
            # Create tooltip text
            if hours > 0:
                tooltip_text = f"Shutdown in {hours}h {minutes}m {seconds}s"
            else:
                tooltip_text = f"Shutdown in {minutes}m {seconds}s"
            
            # Update tray icon tooltip
            try:
                self.tray_icon.title = tooltip_text
            except:
                pass  # Ignore errors if tray icon is not available
    
    def signal_handler(self, signum, frame):
        """Handle system signals for proper cleanup."""
        self.force_quit()
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    app = ShutdownScheduler()
    app.run()


if __name__ == "__main__":
    main() 