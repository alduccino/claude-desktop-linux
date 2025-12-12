# Claude Desktop for Linux

A native desktop application for Claude.ai with **full OAuth support** (including Google Sign-In).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)
![Built with](https://img.shields.io/badge/built%20with-Electron-blue.svg)

## ✨ Features

- ✅ **Google OAuth works perfectly!** (uses Electron/Chromium)
- ✅ All login methods supported
- ✅ Native desktop integration
- ✅ Clean interface (no menu bar clutter)
- ✅ Persistent sessions
- ✅ Custom Claude AI icon

## 🚀 Quick Install

### Option 1: Quick Install (Recommended)
```bash
git clone https://github.com/alduccino/claude-desktop-linux.git
cd claude-desktop-linux
npm install
npm run build
./install.sh
```

The installer will:
- Build the AppImage
- Create desktop menu entry
- Optionally install terminal command

### Option 2: Run from Source
```bash
git clone https://github.com/alduccino/claude-desktop-linux.git
cd claude-desktop-linux
npm install
npm start
```

### Option 3: Download Release

1. Download the latest AppImage from [Releases](https://github.com/alduccino/claude-desktop-linux/releases)
2. Make it executable: `chmod +x "Claude Desktop-2.0.0.AppImage"`
3. Run it: `./Claude Desktop-2.0.0.AppImage`
4. Run `./install.sh` to create desktop shortcut

## 🗑️ Uninstall
```bash
./uninstall.sh
```

## 📦 Building from Source
```bash
# Install dependencies
npm install

# Run in development
npm start

# Build AppImage
npm run build
```

## ⌨️ Keyboard Shortcuts

- `Ctrl+N` - New chat (when menu enabled)
- `Ctrl+Q` - Quit (when menu enabled)
- `F11` - Fullscreen
- `F12` - Developer Tools

## 🔧 Requirements

- Node.js 18+
- npm
- Fedora 43 or any modern Linux distro

## 🐛 Troubleshooting

### Google login not working?
It should work! But if not:
- Clear cache: `rm -rf ~/.config/Claude\ Desktop/`
- Restart the app

### App won't start?
```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Desktop shortcut not appearing?
```bash
# Refresh KDE menu
kbuildsycoca6 --noincremental

# Or run install script again
./install.sh
```

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Acknowledgments

Built with [Electron](https://www.electronjs.org/)

---

**Version 2.0** - Electron rewrite with full OAuth compatibility
