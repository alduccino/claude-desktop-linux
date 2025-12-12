<div align="center">

# Claude Desktop for Linux

### A feature-complete, native desktop application for Claude.ai

**Built specifically for Fedora 43 with KDE Plasma 6.5**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Qt6](https://img.shields.io/badge/Qt-6.6+-green.svg)](https://www.qt.io/)
[![KDE Plasma](https://img.shields.io/badge/KDE-Plasma%206.5-blue.svg)](https://kde.org/plasma-desktop/)

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Contributing](CONTRIBUTING.md) • [License](LICENSE)

![Claude Desktop Screenshot](https://via.placeholder.com/800x450/6B46C1/FFFFFF?text=Claude+Desktop+for+Linux)

</div>

---

A feature-complete, native Qt6-based desktop application for Claude.ai, specifically optimized for Fedora 43 with KDE Plasma integration.

## 🎯 Features

### Core Features (Matching Windows Version)
- ✅ **Full Claude.ai Web Interface** - Embedded browser with full functionality
- ✅ **Native KDE Integration** - Breeze theme support, native widgets
- ✅ **Conversation Management** - Save, load, and organize chat histories
- ✅ **Persistent Storage** - All conversations saved locally
- ✅ **Multiple Views** - Web interface + local offline view
- ✅ **Export Capabilities** - Export to TXT, JSON, Markdown
- ✅ **Keyboard Shortcuts** - Full keyboard navigation
- ✅ **Settings Panel** - Customizable themes, fonts, behavior
- ✅ **Auto-save** - Automatic conversation backup
- ✅ **System Integration** - Desktop entry, application menu

### Linux-Specific Enhancements
- 🐧 Native Qt6 implementation
- 🎨 Full Breeze theme integration
- 💾 XDG-compliant configuration storage
- 🔒 Persistent session management
- 📦 System-wide installation support

## 📋 Requirements

### System Requirements
- **OS**: Fedora 43 (or compatible)
- **Desktop**: KDE Plasma 6.5+
- **Python**: 3.11+
- **Qt**: Qt6.6+

### Dependencies
All dependencies are automatically installed by the installation script:
- `python3-PyQt6`
- `python3-PyQt6-WebEngine`
- `qt6-qtbase`
- `qt6-qtwebengine`
- `breeze-icon-theme`
- `breeze-gtk`

## 🚀 Installation

### Quick Install
```bash
# Clone or download the files
cd /path/to/claude-desktop

# Run installation (requires sudo)
sudo ./install.sh
```

### Manual Installation
```bash
# Install dependencies
sudo dnf install -y python3 python3-pip python3-PyQt6 python3-PyQt6-WebEngine \
    qt6-qtbase qt6-qtwebengine breeze-icon-theme

# Install Python packages
pip3 install --break-system-packages -r requirements.txt

# Make executable
chmod +x claude_desktop.py

# Run directly
./claude_desktop.py
```

## 📖 Usage

### Starting the Application

**From Application Menu:**
- Open Application Menu → Network → Claude Desktop

**From Command Line:**
```bash
claude-desktop
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New chat |
| `Ctrl+O` | Open chat |
| `Ctrl+S` | Save current chat |
| `Ctrl+B` | Toggle sidebar |
| `Ctrl+,` | Open settings |
| `Ctrl+Q` | Quit application |
| `Ctrl+C` | Copy selected text |
| `Ctrl+V` | Paste text |

### Menu Options

#### File Menu
- **New Chat**: Create a new conversation
- **Open Chat**: Browse saved conversations
- **Save Chat**: Manually save current conversation
- **Export Chat**: Export to TXT, JSON, or Markdown
- **Quit**: Exit application

#### Edit Menu
- **Copy**: Copy selected text
- **Paste**: Paste into input field
- **Clear Chat**: Clear current conversation

#### View Menu
- **Toggle Sidebar**: Show/hide conversation list

#### Tools Menu
- **Settings**: Configure application preferences
  - Theme: System, Light, Dark
  - Font Size: Small, Medium, Large
  - Auto-save conversations
  - Show timestamps
  - Render Markdown

#### Help Menu
- **About**: Application information
- **Documentation**: Open Claude.ai docs

## 📁 File Locations

### User Configuration
```
~/.config/claude-desktop/
├── conversations/          # Saved chat histories
│   ├── 20241212_143022.json
│   └── 20241212_150315.json
├── cache/                  # Web browser cache
└── storage/                # Persistent storage
```

### System Installation
```
/opt/claude-desktop/        # Application files
/usr/local/bin/claude-desktop  # Launcher script
/usr/share/applications/claude-desktop.desktop  # Desktop entry
/usr/share/icons/hicolor/scalable/apps/claude-desktop.svg  # Icon
```

## 🎨 Themes and Customization

The application automatically integrates with your KDE Plasma theme:

1. **System Theme** (default): Follows your KDE settings
2. **Light Theme**: Force light Breeze theme
3. **Dark Theme**: Force dark Breeze theme

Access settings via `Ctrl+,` or Tools → Settings

## 💾 Conversation Management

### Saving Conversations
- **Auto-save**: Enabled by default, saves after each message
- **Manual save**: Press `Ctrl+S` or File → Save Chat
- **Format**: JSON files with metadata

### Exporting Conversations
Export your chats in multiple formats:
- **Text (.txt)**: Plain text format
- **JSON (.json)**: Full conversation data
- **Markdown (.md)**: Formatted Markdown

### Conversation Storage
Each conversation is saved as a JSON file:
```json
{
  "id": "20241212_143022",
  "title": "Python Programming Help",
  "messages": [
    {
      "role": "user",
      "content": "How do I...",
      "timestamp": "2024-12-12 14:30:22"
    }
  ],
  "created_at": "2024-12-12T14:30:22",
  "updated_at": "2024-12-12T14:35:10"
}
```

## 🔧 Advanced Usage

### Running from Source
```bash
python3 claude_desktop.py
```

### Custom Configuration Directory
```bash
# Set custom config location
export XDG_CONFIG_HOME=/custom/path
python3 claude_desktop.py
```

### Debug Mode
```bash
# Run with Python debug output
python3 -v claude_desktop.py
```

## 🗑️ Uninstallation

### Complete Removal
```bash
sudo /opt/claude-desktop/uninstall.sh
```

### Keep User Data
The uninstaller preserves your configuration and conversations in `~/.config/claude-desktop/`

### Remove User Data
```bash
# After uninstalling, remove user data
rm -rf ~/.config/claude-desktop/
```

## 🐛 Troubleshooting

### Application Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.11+

# Check dependencies
python3 -c "import PyQt6; print('PyQt6 OK')"
python3 -c "from PyQt6.QtWebEngineWidgets import QWebEngineView; print('WebEngine OK')"

# Check Qt libraries
ldd /usr/lib64/python3.*/site-packages/PyQt6/QtWebEngineWidgets.*.so
```

### Web View Not Loading
```bash
# Check network connectivity
ping -c 3 claude.ai

# Check QtWebEngine
ls /usr/lib64/qt6/libexec/QtWebEngineProcess

# Clear cache
rm -rf ~/.config/claude-desktop/cache/
```

### Missing Dependencies
```bash
# Reinstall dependencies
sudo dnf install -y python3-PyQt6 python3-PyQt6-WebEngine qt6-qtwebengine
```

### Icon Not Showing
```bash
# Update icon cache
sudo gtk-update-icon-cache -f -t /usr/share/icons/hicolor/
```

## 📝 Development

### Project Structure
```
claude-desktop/
├── claude_desktop.py      # Main application
├── install.sh            # Installation script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

### Key Components
1. **ClaudeDesktopApp**: Main application window
2. **ConversationManager**: Handle conversation persistence
3. **SettingsDialog**: Application settings
4. **QWebEngineView**: Embedded browser for Claude.ai

### Extending the Application
The application is built with modularity in mind. Key areas for extension:
- Custom themes in `apply_theme()`
- Additional export formats in `export_chat()`
- Plugin system for conversation analysis
- Integration with KDE activities

## 🤝 Contributing

This application was created for the Linux community. Feel free to:
- Report bugs and issues
- Suggest new features
- Submit improvements
- Share your experience

## 📄 License

This is an independent desktop wrapper for Claude.ai. Claude and Claude.ai are trademarks of Anthropic.

## 🙏 Credits

- Built specifically for Fedora 43 KDE Plasma
- Uses Qt6 and PyQt6 for native Linux integration
- Inspired by the official Claude desktop applications
- Designed with Linux desktop environment best practices

## 📚 Resources

- [Claude.ai](https://claude.ai)
- [Anthropic Documentation](https://docs.claude.com)
- [Qt6 Documentation](https://doc.qt.io/qt-6/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [KDE Plasma](https://kde.org/plasma-desktop/)

## ⚡ Quick Start Guide

1. **Install**: `sudo ./install.sh`
2. **Launch**: Open from application menu or run `claude-desktop`
3. **Login**: The embedded browser will load Claude.ai - log in normally
4. **Chat**: Start chatting! Conversations are auto-saved
5. **Organize**: Use the sidebar to manage your chat history

---

**Version**: 1.0.0  
**Last Updated**: December 2024  
**Tested On**: Fedora 43 with KDE Plasma 6.5
