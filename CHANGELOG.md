# Changelog

All notable changes to Claude Desktop for Linux will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-12

### Added
- Initial release of Claude Desktop for Linux
- Two versions: Standard and Enhanced
- Full Claude.ai web interface integration
- Native KDE Breeze theme support
- Conversation management (save/load/organize)
- Persistent chat history with auto-save
- Export conversations to TXT, JSON, Markdown
- Keyboard shortcuts for common actions
- Settings panel with customization options
- System tray integration (Enhanced version)
- Desktop notifications (Enhanced version)
- Conversation search functionality (Enhanced version)
- Context menus for conversation management (Enhanced version)
- Fullscreen mode (Enhanced version)
- Automated installation script
- Desktop entry and icon integration
- Comprehensive documentation

### Features
- **Core Functionality**
  - Embedded QWebEngineView for Claude.ai
  - Persistent session management
  - Local conversation storage
  - XDG-compliant configuration
  
- **User Interface**
  - Split-panel layout (conversations + chat)
  - Resizable panels
  - Native Qt6 widgets
  - Breeze theme integration
  
- **Conversation Management**
  - Create, rename, delete conversations
  - Auto-save functionality
  - Manual save option
  - Search through all conversations
  - Export in multiple formats
  
- **Customization**
  - Theme selection (System, Light, Dark, Breeze)
  - Font size adjustment
  - Timestamp display toggle
  - Markdown rendering option
  - System tray behavior
  - Notification preferences
  
- **Keyboard Shortcuts**
  - Ctrl+N: New chat
  - Ctrl+F: Search conversations
  - Ctrl+S: Save chat
  - Ctrl+E: Export chat
  - Ctrl+B: Toggle sidebar
  - Ctrl+,: Settings
  - Ctrl+Q: Quit
  - F11: Fullscreen

### System Requirements
- Fedora 43 (or compatible)
- KDE Plasma 6.5+
- Python 3.11+
- Qt 6.6+
- PyQt6 6.6+

### Installation
- Automated installation script
- System-wide installation to /opt/claude-desktop
- Desktop entry creation
- Icon installation
- Uninstall script included

### Documentation
- Comprehensive README with full feature documentation
- Quick start guide
- Troubleshooting section
- Contributing guidelines
- MIT License

## [Unreleased]

### Planned Features
- Multi-account support
- Conversation tags and categories
- Advanced search filters
- Custom keyboard shortcuts
- Plugin system
- KDE Activities integration
- Plasma widget
- Wayland optimization
- Flatpak packaging
- Additional export formats (PDF, HTML)
- Conversation analytics
- Backup and sync options
- Command-line interface
- Accessibility improvements

---

[1.0.0]: https://github.com/YOUR_USERNAME/claude-desktop-linux/releases/tag/v1.0.0
