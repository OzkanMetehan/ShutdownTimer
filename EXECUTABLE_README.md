# Shutdown Scheduler - Executable Version

## 📁 Files Included
- `ShutdownScheduler.exe` - The main executable file (20MB)

## 🚀 How to Use

### For Testing on Another Computer:
1. **Copy the executable** to any Windows computer
2. **Double-click** `ShutdownScheduler.exe` to run
3. **No installation required** - it's a standalone executable

### Features:
- ✅ **Countdown Timer**: Set hours and minutes for immediate shutdown
- ✅ **Scheduled Timer**: Set a specific date and time for future shutdown
- ✅ **30-Second Warning**: Popup with countdown before actual shutdown
- ✅ **Cancel Option**: Easy cancellation at any time
- ✅ **Dark Theme**: Modern dark interface
- ✅ **Responsive UI**: Adapts to window resizing
- ✅ **System Tray**: Minimize to system tray (hidden icons area)
- ✅ **Tray Tooltip**: Hover to see remaining time
- ✅ **Tray Menu**: Right-click for options (Show Window, Cancel Timer, Exit)

### Safety Features:
- ⚠️ **Warning Popup**: 30-second countdown before shutdown
- 🔄 **Easy Cancel**: One-click cancellation
- 📅 **Smart Validation**: Prevents past dates/times
- 🛡️ **Error Handling**: Graceful failure handling

## 🖥️ System Tray Features

### How to Use System Tray:
1. **Start a timer** (countdown or scheduled)
2. **Click the minimize button** (X) - app goes to system tray
3. **Hover over tray icon** to see remaining time
4. **Right-click tray icon** for menu options:
   - **Show Window**: Bring app back to screen
   - **Cancel Timer**: Stop the timer
   - **Exit**: Close the app completely

### Tray Icon Behavior:
- **Only appears when timer is running**
- **Shows remaining time on hover**
- **Custom clock icon design**
- **Located in hidden icons area**

## ⚠️ Important Notes:

### For Testing:
- **Test with short timers first** (1-2 minutes)
- **Keep the cancel button ready** during testing
- **Don't test on important work computers**
- **Check system tray** when minimized

### System Requirements:
- **Windows 10/11** (64-bit)
- **No Python required** - standalone executable
- **No internet connection needed**

### File Size:
- **20MB** - Contains all necessary libraries including system tray
- **Self-contained** - No additional files needed

## 🔧 Troubleshooting:

### If the app doesn't start:
1. **Right-click** the executable
2. **Select "Run as administrator"**
3. **Check Windows Defender** - it might flag the file initially

### If shutdown doesn't work:
1. **Run as administrator**
2. **Check Windows permissions**
3. **Manual shutdown** as fallback

### If system tray doesn't work:
1. **Check hidden icons** in system tray
2. **Expand the hidden icons** to see the app
3. **Restart the app** if tray icon doesn't appear

## 📝 Version Info:
- **Version**: 1.1 (with system tray)
- **Build Date**: January 2025
- **Python Version**: 3.13.5
- **Framework**: Tkinter + pystray
- **New Features**: System tray, tray tooltip, tray menu

---
**Made with ❤️ for easy computer shutdown scheduling** 