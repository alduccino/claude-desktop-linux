# Claude Desktop for Linux - Quick Start Guide

## Installation (5 minutes)

### Option 1: Automated Install (Recommended)
```bash
# Make the installer executable
chmod +x install.sh

# Run the installer
sudo ./install.sh

# Launch the application
claude-desktop
```

### Option 2: Direct Run (No Installation)
```bash
# Install dependencies only
sudo dnf install -y python3-PyQt6 python3-PyQt6-WebEngine

# Run directly
./claude_desktop_enhanced.py
```

## First Run

1. **Launch**: Find "Claude Desktop" in your application menu under Network
2. **Login**: The embedded browser will load Claude.ai - sign in with your account
3. **Start Chatting**: Your conversations will be automatically saved

## Key Features

### Two Versions Available

**Standard Version** (`claude_desktop.py`):
- Clean, simple interface
- Local chat view + Web view
- Basic conversation management

**Enhanced Version** (`claude_desktop_enhanced.py`):
- System tray integration
- Desktop notifications
- Advanced search
- Context menus
- Fullscreen mode

Choose the version that fits your needs!

## Essential Shortcuts

| Action | Shortcut |
|--------|----------|
| New Chat | `Ctrl+N` |
| Search | `Ctrl+F` |
| Save | `Ctrl+S` |
| Settings | `Ctrl+,` |
| Toggle Sidebar | `Ctrl+B` |
| Fullscreen | `F11` |
| Quit | `Ctrl+Q` |

## Tips

1. **System Tray**: Enable "Minimize to tray" in settings to keep Claude running in background
2. **Auto-save**: Conversations are auto-saved - you never lose your work
3. **Export**: Right-click any conversation to export it
4. **Search**: Use `Ctrl+F` to search through all your conversations
5. **Themes**: Match your KDE theme automatically or force light/dark mode

## Configuration

All settings stored in: `~/.config/claude-desktop/`

- **Conversations**: Auto-saved as JSON files
- **Cache**: Browser data for Claude.ai session
- **Settings**: Your preferences and customizations

## Troubleshooting

**Can't start?**
```bash
# Check dependencies
python3 -c "import PyQt6; print('OK')"
python3 -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('OK')"
```

**Web view not loading?**
```bash
# Clear cache and restart
rm -rf ~/.config/claude-desktop/cache/
```

**Icon not showing?**
```bash
# Update icon cache
sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/
```

## Uninstall

```bash
sudo /opt/claude-desktop/uninstall.sh
```

Your conversation history in `~/.config/claude-desktop/` will be preserved.

## Next Steps

- Explore the settings (`Ctrl+,`) to customize your experience
- Try the search feature to find old conversations
- Export important chats for backup
- Enable system tray for background operation

---

**Need Help?** Check the full README.md for detailed documentation.
