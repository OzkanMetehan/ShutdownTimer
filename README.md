# Shutdown Timer App

A simple Windows desktop application that allows you to schedule computer shutdown with a countdown timer.

## Quick Start

### Prerequisites
1. **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
2. **Windows 10/11** - This app is designed for Windows
3. **GitHub Desktop** (Optional) - For version control and GitHub integration

### How to Run

#### Option 1: Run the Simple Version (Recommended for testing)
1. Open Command Prompt (cmd)
2. Navigate to this folder: `cd "path\to\ShutdownTimer"`
3. Run the app: `python simple_shutdown_timer.py`

#### Option 2: Using VS Code
1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Open VS Code
3. Go to File → Open Folder → Select this ShutdownTimer folder
4. Install Python extension in VS Code
5. Open `simple_shutdown_timer.py`
6. Press F5 or click the "Run" button

#### Option 3: Using GitHub Desktop (Recommended for version control)
1. Open GitHub Desktop
2. Go to File → Add Local Repository
3. Browse to this ShutdownTimer folder
4. Click "Add Repository"
5. Now you can commit changes and push to GitHub
6. To run the app: Right-click in the folder → Open in Command Prompt → `python simple_shutdown_timer.py`

## Features

### Current Features (Simple Version)
- ✅ Set countdown timer in hours and minutes
- ✅ Real-time countdown display
- ✅ Start/Cancel timer functionality
- ✅ Windows shutdown integration
- ✅ Confirmation dialog before shutdown
- ✅ Clean, simple interface

### Planned Features
- 📅 Scheduled time mode (specific date/time)
- 🎯 System tray integration
- ⚙️ Settings persistence
- 🔔 Sound notifications
- 📱 Modern UI design

## How to Use

1. **Set Timer Duration**
   - Enter hours (0-23)
   - Enter minutes (0-59)
   - Default is 30 minutes

2. **Start Timer**
   - Click "Start Timer"
   - The app will show countdown: "Close the computer in X hours X minutes"

3. **Cancel Timer**
   - Click "Cancel Timer" to stop the countdown
   - Timer will reset to default

4. **Shutdown**
   - When time runs out, you'll get a confirmation dialog
   - Click "Yes" to shutdown, "No" to cancel

## Safety Features

- **Confirmation Dialog**: Always asks before shutting down
- **Easy Cancellation**: Can cancel timer at any time
- **Input Validation**: Prevents invalid time settings
- **Error Handling**: Graceful handling of system errors

## Development

### Project Structure
```
ShutdownTimer/
├── simple_shutdown_timer.py  # Working version (run this!)
├── SHUTDOWN_TIMER_PLAN.md   # Development plan
├── requirements.txt          # Dependencies
├── .gitignore               # Git ignore file
└── README.md               # This file
```

### Next Steps
1. Test the simple version
2. Follow the development plan in `SHUTDOWN_TIMER_PLAN.md`
3. Build the full-featured version

## Troubleshooting

### Common Issues

**"python is not recognized"**
- Make sure Python is installed and added to PATH
- Try using `python3` instead of `python`

**"Permission denied"**
- Run Command Prompt as Administrator
- The app needs admin rights to shutdown the computer

**"App doesn't start"**
- Make sure you're in the correct folder
- Check that Python is installed correctly

## Contributing

This is a personal project that will be open-sourced. Feel free to:
- Test the app and report bugs
- Suggest new features
- Contribute code improvements

## License

This project will be released under the MIT License.

---

**Note**: This is a working prototype. The full version will have more features and better UI design. 