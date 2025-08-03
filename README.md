# Shutdown Scheduler

A simple Windows desktop application for scheduling computer shutdowns with a modern dark interface.

## 🚀 Quick Start

### For Users (Executable):
1. Download `ShutdownScheduler.exe` from the `dist/` folder
2. Double-click to run (no installation required)
3. Set your timer and enjoy!

### For Developers:
1. Install Python 3.13+
2. Run `python enhanced_shutdown_timer.py`
3. Or build executable: `pyinstaller --onefile --windowed enhanced_shutdown_timer.py`

## ✨ Features

### Core Functionality:
- **Countdown Timer**: Set hours and minutes for immediate shutdown
- **Scheduled Timer**: Set a specific date and time for future shutdown
- **30-Second Warning**: Popup countdown before actual shutdown
- **Easy Cancellation**: Cancel at any time with one click

### User Experience:
- **Dark Theme**: Modern dark interface
- **Responsive Design**: Adapts to window resizing
- **Smart Validation**: Prevents past dates/times
- **System Date Format**: Automatically detects user's date format

### Safety Features:
- ⚠️ **Warning Popup**: 30-second countdown before shutdown
- 🔄 **Easy Cancel**: One-click cancellation
- 📅 **Smart Validation**: Prevents past dates/times
- 🛡️ **Error Handling**: Graceful failure handling

## 📁 Project Structure

```
ShutdownTimer/
├── enhanced_shutdown_timer.py    # Main application source
├── dist/
│   └── ShutdownScheduler.exe     # Standalone executable (9.8MB)
├── EXECUTABLE_README.md          # Instructions for executable
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── GITHUB_SETUP.md             # GitHub setup guide
```

## 🛠️ Development

### Requirements:
- Python 3.13+
- tkinter (built-in)
- subprocess (built-in)
- threading (built-in)

### Building Executable:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed enhanced_shutdown_timer.py
```

## ⚠️ Important Notes

### For Testing:
- **Test with short timers first** (1-2 minutes)
- **Keep the cancel button ready** during testing
- **Don't test on important work computers**

### System Requirements:
- **Windows 10/11** (64-bit)
- **No Python required** for executable version
- **No internet connection needed**

## 🔧 Troubleshooting

### If the app doesn't start:
1. **Right-click** the executable
2. **Select "Run as administrator"**
3. **Check Windows Defender** - it might flag the file initially

### If shutdown doesn't work:
1. **Run as administrator**
2. **Check Windows permissions**
3. **Manual shutdown** as fallback

## 📝 Version Info

- **Version**: 1.0
- **Build Date**: January 2025
- **Python Version**: 3.13.5
- **Framework**: Tkinter (built-in)
- **License**: MIT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ for easy computer shutdown scheduling** 