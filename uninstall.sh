#!/bin/bash

# Claude Desktop Uninstallation Script

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo "Uninstalling Claude Desktop..."

# Remove desktop entry
rm -f "$HOME/.local/share/applications/claude-desktop.desktop"
echo_success "Desktop entry removed"

# Remove command-line launcher if exists
if [ -f /usr/local/bin/claude-desktop ]; then
    sudo rm -f /usr/local/bin/claude-desktop
    echo_success "Command-line launcher removed"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
fi

# Refresh KDE menu if running KDE
if [ "$XDG_CURRENT_DESKTOP" = "KDE" ]; then
    if command -v kbuildsycoca6 &> /dev/null; then
        kbuildsycoca6 --noincremental 2>/dev/null || true
    fi
fi

echo ""
echo_success "Uninstallation complete!"
echo "The AppImage and source files remain in this directory."
echo ""
