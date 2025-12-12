#!/bin/bash

# GitHub Repository Setup Script
# Run this to create the repository on GitHub and push the code

echo "=========================================="
echo "Claude Desktop for Linux - GitHub Setup"
echo "=========================================="
echo ""

# Repository details
REPO_NAME="claude-desktop-linux"
REPO_DESCRIPTION="Native Qt6 desktop application for Claude.ai on Fedora 43 KDE Plasma"

echo "This script will help you create a GitHub repository and push the code."
echo ""
echo "Repository Name: $REPO_NAME"
echo "Description: $REPO_DESCRIPTION"
echo ""

# Check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) detected!"
    echo ""
    read -p "Do you want to create the repository using GitHub CLI? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating repository on GitHub..."
        gh repo create "$REPO_NAME" --public --description "$REPO_DESCRIPTION" --source=. --remote=origin --push
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ Repository created and code pushed successfully!"
            echo "✓ Repository URL: https://github.com/$(gh api user -q .login)/$REPO_NAME"
            echo ""
            echo "Next steps:"
            echo "1. Visit your repository on GitHub"
            echo "2. Add topics: qt6, pyqt6, claude-ai, kde-plasma, fedora, linux-desktop"
            echo "3. Update repository description and website if needed"
            echo "4. Add a screenshot to the README"
            exit 0
        else
            echo "✗ Failed to create repository with GitHub CLI"
            echo "Falling back to manual instructions..."
        fi
    fi
fi

# Manual instructions
echo ""
echo "=========================================="
echo "Manual Setup Instructions"
echo "=========================================="
echo ""
echo "1. Create a new repository on GitHub:"
echo "   - Go to https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: $REPO_DESCRIPTION"
echo "   - Make it Public"
echo "   - DO NOT initialize with README, .gitignore, or license"
echo "   - Click 'Create repository'"
echo ""
echo "2. Push your local repository:"
echo "   Run these commands in this directory:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. After pushing, add these repository topics on GitHub:"
echo "   - qt6"
echo "   - pyqt6"
echo "   - claude-ai"
echo "   - kde-plasma"
echo "   - fedora"
echo "   - linux-desktop"
echo "   - desktop-application"
echo "   - breeze-theme"
echo ""
echo "4. Optional enhancements:"
echo "   - Add a screenshot to the repository"
echo "   - Enable GitHub Issues"
echo "   - Set up GitHub Pages for documentation"
echo "   - Add repository social preview image"
echo ""
echo "=========================================="
echo ""

# Alternative: Direct git commands
echo "Quick copy-paste commands (replace YOUR_USERNAME):"
echo ""
echo "cd /home/claude/claude-desktop-linux"
echo "git remote add origin https://github.com/YOUR_USERNAME/$REPO_NAME.git"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "=========================================="
