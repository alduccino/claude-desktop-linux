# Claude Desktop for Linux

A native desktop application for Claude.ai with **full OAuth support** (including Google Sign-In).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)
![Built with](https://img.shields.io/badge/built%20with-Electron-blue.svg)

## ✨ Features

- ✅ **Google OAuth works perfectly!** (uses Electron/Chromium)
- ✅ All login methods supported
- ✅ Native desktop integration
- ✅ Persistent sessions
- ✅ Keyboard shortcuts
- ✅ System tray support

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Fedora/RHEL/Ubuntu or any modern Linux

### Installation
```bash
git clone https://github.com/alduccino/claude-desktop-linux.git
cd claude-desktop-linux

# Install Node.js (Fedora)
sudo dnf install nodejs npm

# Install dependencies
npm install

# Run
npm start
```

### Build Packages
```bash
npm run build:linux
```

This creates:
- **AppImage** (portable): `dist/Claude Desktop-2.0.0.AppImage`
- **RPM** (Fedora): `dist/claude-desktop-linux-2.0.0.x86_64.rpm`
- **DEB** (Ubuntu): `dist/claude-desktop-linux_2.0.0_amd64.deb`

#### Install on Fedora:
```bash
sudo dnf install ./dist/claude-desktop-linux-2.0.0.x86_64.rpm
```

#### Run AppImage (no installation):
```bash
chmod +x "./dist/Claude Desktop-2.0.0.AppImage"
"./dist/Claude Desktop-2.0.0.AppImage"
```

## ⌨️ Keyboard Shortcuts

- `Ctrl+N` - New chat
- `Ctrl+Q` - Quit
- `Ctrl+R` - Reload
- `F11` - Fullscreen
- `F12` - Developer Tools

## 🔄 Migrating from v1.x (Qt/PyQt6)

The previous Qt version had Google OAuth issues. **This Electron version fixes that!**

Uninstall old version:
```bash
sudo rm -rf /opt/claude-desktop/
sudo rm -f /usr/local/bin/claude-desktop
sudo rm -f /usr/share/applications/claude-desktop.desktop
```

## 📦 Distribution Formats

### AppImage
- ✅ Portable, no installation
- ✅ Works on any Linux distro
- ✅ Self-contained

### RPM/DEB
- ✅ Native package management
- ✅ System integration
- ✅ Auto-updates via package manager

## 🐛 Troubleshooting

### Google login not working?
- Clear cache: `rm -rf ~/.config/Claude\ Desktop/`
- Restart app

### App won't start?
```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## 🔒 Security

- Sandbox enabled
- Context isolation
- No Node integration in renderer
- Certificate validation

## 📄 License

MIT License - See [LICENSE](LICENSE)

## 🙏 Acknowledgments

Built with [Electron](https://www.electronjs.org/)

---

**Version 2.0** - Complete rewrite in Electron for full OAuth compatibility
