#!/bin/bash

# Claude Desktop Installation Script for Linux

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPIMAGE="$SCRIPT_DIR/dist/Claude Desktop-2.0.0.AppImage"
ICON="$SCRIPT_DIR/icon.png"

echo_info "Installing Claude Desktop..."

# Check if AppImage exists
if [ ! -f "$APPIMAGE" ]; then
    echo_warning "AppImage not found. Building it first..."
    npm run build
fi

# Make AppImage executable
chmod +x "$APPIMAGE"
echo_success "AppImage is executable"

# Create desktop entry
DESKTOP_FILE="$HOME/.local/share/applications/claude-desktop.desktop"
mkdir -p "$HOME/.local/share/applications"

# Note: Exec path should NOT have quotes in .desktop files - the desktop environment handles spaces
cat > "$DESKTOP_FILE" << DESKTOP_EOF
[Desktop Entry]
Name=Claude Desktop
Comment=Claude AI Desktop Application with OAuth support
Exec=$APPIMAGE
Icon=$ICON
Type=Application
Categories=Network;Chat;Office;Development;
Terminal=false
StartupWMClass=Claude Desktop
Keywords=AI;Assistant;Chat;Claude;Anthropic;
DESKTOP_EOF

echo_success "Desktop entry created at $DESKTOP_FILE"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
    echo_success "Desktop database updated"
fi

# Refresh KDE menu if running KDE
if [ "$XDG_CURRENT_DESKTOP" = "KDE" ]; then
    if command -v kbuildsycoca6 &> /dev/null; then
        kbuildsycoca6 --noincremental 2>/dev/null || true
        echo_success "KDE menu refreshed"
    fi
fi

# Create terminal launcher (optional)
read -p "Install command-line launcher? (sudo required) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo tee /usr/local/bin/claude-desktop > /dev/null << LAUNCHER_EOF
#!/bin/bash
exec "$APPIMAGE" "\$@"
LAUNCHER_EOF
    sudo chmod +x /usr/local/bin/claude-desktop
    echo_success "Command-line launcher installed: claude-desktop"
fi

echo ""
echo_success "Installation complete! 🎉"
echo ""
echo "You can now:"
echo "  • Find 'Claude Desktop' in your application menu"
echo "  • Run from terminal: \"$APPIMAGE\""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  • Or simply type: claude-desktop"
fi
echo ""
