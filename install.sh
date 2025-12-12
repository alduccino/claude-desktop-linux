#!/bin/bash

# Claude Desktop for Linux - Installation Script (Fixed for Fedora 43)
# For Fedora 43 KDE Edition

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/claude-desktop"
BIN_DIR="/usr/local/bin"
DESKTOP_FILE_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo_error "Please run this script as root or with sudo"
    exit 1
fi

echo_info "Starting Claude Desktop installation for Fedora 43 KDE..."

# Update system
echo_info "Updating system packages..."
dnf check-update || true

# Install dependencies (with correct Fedora 43 package names)
echo_info "Installing dependencies..."
dnf install -y \
    python3 \
    python3-pip \
    python3-devel \
    python3-pyqt6 \
    python3-pyqt6-webengine \
    qt6-qtbase \
    qt6-qtbase-gui \
    qt6-qtwebengine \
    breeze-icon-theme \
    breeze-gtk \
    fontawesome-fonts \
    liberation-fonts \
    --skip-unavailable

# Install Python packages
echo_info "Installing Python dependencies..."
pip3 install --break-system-packages \
    PyQt6 \
    PyQt6-WebEngine \
    requests || echo_warning "Some pip packages may already be installed"

# Create installation directory
echo_info "Creating installation directory..."
mkdir -p "$INSTALL_DIR"

# Determine which Python script to install
if [ -f "$SCRIPT_DIR/claude_desktop_enhanced.py" ]; then
    MAIN_SCRIPT="claude_desktop_enhanced.py"
    echo_info "Installing Enhanced version (with system tray)"
elif [ -f "$SCRIPT_DIR/claude_desktop.py" ]; then
    MAIN_SCRIPT="claude_desktop.py"
    echo_info "Installing Standard version"
else
    echo_error "Could not find claude_desktop.py or claude_desktop_enhanced.py"
    exit 1
fi

# Copy application files
echo_info "Installing application files..."
cp "$SCRIPT_DIR/$MAIN_SCRIPT" "$INSTALL_DIR/claude_desktop.py"
chmod +x "$INSTALL_DIR/claude_desktop.py"

# Create launcher script
echo_info "Creating launcher script..."
cat > "$BIN_DIR/claude-desktop" << 'EOF'
#!/bin/bash
/usr/bin/python3 /opt/claude-desktop/claude_desktop.py "$@"
EOF

chmod +x "$BIN_DIR/claude-desktop"

# Create desktop entry
echo_info "Creating desktop entry..."
cat > "$DESKTOP_FILE_DIR/claude-desktop.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Claude Desktop
Comment=Claude AI Desktop Application for Linux
Exec=/usr/local/bin/claude-desktop
Icon=claude-desktop
Terminal=false
Categories=Network;Chat;Office;
Keywords=AI;Assistant;Chat;Claude;Anthropic;
StartupWMClass=claude-desktop
StartupNotify=true
EOF

# Download or create icon
echo_info "Setting up application icon..."
# Create a simple SVG icon (you can replace this with an actual Claude icon)
mkdir -p "$ICON_DIR/scalable/apps"
cat > "$ICON_DIR/scalable/apps/claude-desktop.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect width="64" height="64" rx="12" fill="#6B46C1"/>
  <text x="32" y="45" font-family="Arial" font-size="36" font-weight="bold" fill="white" text-anchor="middle">C</text>
</svg>
EOF

# Also create PNG versions
mkdir -p "$ICON_DIR/48x48/apps"
mkdir -p "$ICON_DIR/64x64/apps"
mkdir -p "$ICON_DIR/128x128/apps"

# Try to convert SVG to PNG if possible
if command -v convert &> /dev/null; then
    echo_info "Converting icon to PNG formats..."
    convert "$ICON_DIR/scalable/apps/claude-desktop.svg" -resize 48x48 "$ICON_DIR/48x48/apps/claude-desktop.png" 2>/dev/null || true
    convert "$ICON_DIR/scalable/apps/claude-desktop.svg" -resize 64x64 "$ICON_DIR/64x64/apps/claude-desktop.png" 2>/dev/null || true
    convert "$ICON_DIR/scalable/apps/claude-desktop.svg" -resize 128x128 "$ICON_DIR/128x128/apps/claude-desktop.png" 2>/dev/null || true
fi

# Update icon cache
echo_info "Updating icon cache..."
gtk-update-icon-cache -f -t "$ICON_DIR" 2>/dev/null || true
xdg-icon-resource forceupdate 2>/dev/null || true

# Update desktop database
echo_info "Updating desktop database..."
update-desktop-database "$DESKTOP_FILE_DIR" 2>/dev/null || true

# Create uninstall script
echo_info "Creating uninstall script..."
cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash

# Claude Desktop Uninstaller

if [ "$EUID" -ne 0 ]; then 
    echo "Please run this script as root or with sudo"
    exit 1
fi

echo "Uninstalling Claude Desktop..."

# Remove files
rm -f /usr/local/bin/claude-desktop
rm -f /usr/share/applications/claude-desktop.desktop
rm -f /usr/share/icons/hicolor/scalable/apps/claude-desktop.svg
rm -f /usr/share/icons/hicolor/48x48/apps/claude-desktop.png
rm -f /usr/share/icons/hicolor/64x64/apps/claude-desktop.png
rm -f /usr/share/icons/hicolor/128x128/apps/claude-desktop.png
rm -rf /opt/claude-desktop

# Update caches
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
xdg-icon-resource forceupdate 2>/dev/null || true
update-desktop-database /usr/share/applications 2>/dev/null || true

echo "Claude Desktop has been uninstalled."
echo "Note: User configuration files in ~/.config/claude-desktop were preserved."
echo "To remove user data: rm -rf ~/.config/claude-desktop"
EOF

chmod +x "$INSTALL_DIR/uninstall.sh"

# Create README
echo_info "Creating documentation..."
cat > "$INSTALL_DIR/README.md" << 'EOF'
# Claude Desktop for Linux

## About
Claude Desktop for Linux is a feature-complete Qt6-based desktop application that provides native access to Claude.ai on Fedora 43 KDE Edition.

## Features
- Native KDE/Breeze theme integration
- Full Claude.ai web interface embedded
- Local conversation management and history
- Persistent chat storage
- Export conversations (TXT, JSON, Markdown)
- Keyboard shortcuts
- System tray integration (Enhanced version)
- Auto-save functionality

## Usage

### Starting the Application
Launch from your application menu or run:
```bash
claude-desktop
```

### Keyboard Shortcuts
- `Ctrl+N` - New chat
- `Ctrl+F` - Search conversations (Enhanced version)
- `Ctrl+S` - Save current chat
- `Ctrl+B` - Toggle sidebar
- `Ctrl+,` - Settings
- `Ctrl+Q` - Quit

### Configuration
Configuration files are stored in: `~/.config/claude-desktop/`
- Conversations: `~/.config/claude-desktop/conversations/`
- Cache: `~/.config/claude-desktop/cache/`

## Uninstalling
Run as root:
```bash
sudo /opt/claude-desktop/uninstall.sh
```

## Support
For issues and updates, visit: https://docs.claude.com
EOF

echo ""
echo_success "============================================"
echo_success "Claude Desktop installation completed!"
echo_success "============================================"
echo ""
echo_info "You can now launch Claude Desktop from:"
echo_info "  - Application Menu > Network > Claude Desktop"
echo_info "  - Command line: claude-desktop"
echo ""
echo_info "Configuration directory: ~/.config/claude-desktop/"
echo_info "Uninstall command: sudo $INSTALL_DIR/uninstall.sh"
echo ""
echo_info "Installed version: $MAIN_SCRIPT"
echo ""
echo_warning "Note: You may need to restart your session or run 'kbuildsycoca6' for the"
echo_warning "application to appear in the KDE menu immediately."
echo ""
echo_info "To start using Claude Desktop, simply launch it from your application menu!"
echo ""
