# Contributing to Claude Desktop for Linux

Thank you for your interest in contributing to Claude Desktop for Linux! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:

1. Check if the issue already exists in the [Issues](../../issues) section
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - System information (Fedora version, KDE Plasma version, Qt version)
   - Relevant logs or screenshots

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Test your changes thoroughly

4. **Commit your changes**
   ```bash
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass

## Development Setup

### Prerequisites

```bash
# Install dependencies
sudo dnf install python3 python3-PyQt6 python3-PyQt6-WebEngine qt6-qtbase qt6-qtwebengine

# Install development tools
sudo dnf install git python3-pip
```

### Running from Source

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/claude-desktop-linux.git
cd claude-desktop-linux

# Run the application
./claude_desktop_enhanced.py
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

## Testing

Before submitting a PR:

1. Test on Fedora 43 with KDE Plasma 6.5
2. Verify all keyboard shortcuts work
3. Check that conversations save/load correctly
4. Test export functionality
5. Ensure theme changes apply correctly

## Feature Requests

We welcome feature requests! When suggesting new features:

- Explain the use case
- Describe expected behavior
- Consider impact on existing functionality
- Provide mockups or examples if applicable

## Areas for Contribution

Some areas where contributions are especially welcome:

- **Documentation**: Improve README, add tutorials
- **Translations**: Add support for multiple languages
- **Themes**: Additional color schemes
- **Export formats**: Support for more export types
- **Integrations**: KDE Activities, Plasma widgets
- **Performance**: Optimize loading and rendering
- **Accessibility**: Improve keyboard navigation, screen reader support

## Questions?

Feel free to open an issue for questions about contributing or reach out to the maintainers.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the project and community

Thank you for contributing to make Claude Desktop for Linux better! 🐧
