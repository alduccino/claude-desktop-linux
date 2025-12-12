#!/usr/bin/env python3
"""
Claude Desktop for Linux - OAuth Fixed Version
- Enhanced OAuth/Google login support
- Better popup handling
- Proper cookie management
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QSplitter, QListWidget, QListWidgetItem,
    QLabel, QToolBar, QStatusBar, QMessageBox,
    QInputDialog, QFileDialog, QDialog, QDialogButtonBox, QLineEdit,
    QCheckBox, QComboBox, QTextBrowser, QTabWidget, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QSettings, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QAction, QIcon, QFont, QTextCursor, QDesktopServices, QKeySequence, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings, QWebEngineScript
from PyQt6.QtNetwork import QNetworkRequest
import urllib.request


class OAuthWebPage(QWebEnginePage):
    """Web page specifically for OAuth popups"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        # Enable all features needed for OAuth
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Listen to URL changes
        self.urlChanged.connect(self.on_url_changed)
    
    def on_url_changed(self, url):
        """Monitor URL changes to detect successful login"""
        url_str = url.toString()
        print(f"OAuth URL changed: {url_str}")
        
        # If we're back at claude.ai after OAuth, close popup
        if 'claude.ai/chat' in url_str or 'claude.ai/?' in url_str:
            if self.view() and hasattr(self.view(), 'is_popup'):
                QTimer.singleShot(1000, self.view().close)


class ClaudeWebPage(QWebEnginePage):
    """Custom web page for main Claude.ai interface with full OAuth support"""
    
    popup_created = pyqtSignal(object)
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        # Enable ALL features needed for modern web apps and OAuth
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowGeolocationOnInsecureOrigins, False)
        
        # Enable DNS prefetching
        settings.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Handle navigation - allow everything Claude.ai needs"""
        url_string = url.toString()
        host = url.host()
        
        print(f"Navigation request: {url_string}")
        
        # Allow all these domains (needed for OAuth)
        allowed_domains = [
            'claude.ai',
            'anthropic.com',
            'accounts.google.com',
            'accounts.anthropic.com',
            'google.com',
            'gstatic.com',
            'googleapis.com',
            'googleusercontent.com',
            'doubleclick.net',
            'google-analytics.com'
        ]
        
        # Check if domain is allowed
        for domain in allowed_domains:
            if domain in host:
                return True
        
        # Allow OAuth and callback URLs
        if any(keyword in url_string.lower() for keyword in ['oauth', 'callback', 'auth', 'login', 'signin']):
            return True
        
        # For external links clicked by user (not navigation), open in browser
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if not any(domain in host for domain in allowed_domains):
                QDesktopServices.openUrl(url)
                return False
        
        # Allow everything else
        return True
    
    def createWindow(self, window_type):
        """Create popup windows for OAuth - CRITICAL for Google login"""
        print(f"Creating popup window of type: {window_type}")
        
        # Create OAuth-enabled page
        page = OAuthWebPage(self.profile(), None)
        
        # Create popup view
        view = QWebEngineView()
        view.setPage(page)
        view.setWindowTitle("Sign In - Claude")
        view.resize(500, 700)
        view.is_popup = True
        
        # Show the popup
        view.show()
        view.raise_()
        view.activateWindow()
        
        # Emit signal
        self.popup_created.emit(view)
        
        return page


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon with context menu"""
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.parent_window = parent
        
        # Create tray menu
        menu = QMenu()
        
        # Show/Hide action
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_window)
        menu.addAction(show_action)
        
        # New Chat action
        new_chat_action = QAction("New Chat", self)
        new_chat_action.triggered.connect(lambda: self.parent_window.new_chat() if self.parent_window else None)
        menu.addAction(new_chat_action)
        
        menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.parent_window.show_settings() if self.parent_window else None)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(lambda: self.parent_window.close_app() if self.parent_window else QApplication.quit())
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activated)
    
    def toggle_window(self):
        """Toggle main window visibility"""
        if self.parent_window:
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.parent_window.show()
                self.parent_window.activateWindow()
                self.parent_window.raise_()
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()


class ConversationManager:
    """Manage conversation history and persistence"""
    
    def __init__(self, config_dir):
        self.config_dir = Path(config_dir)
        self.conversations_dir = self.config_dir / "conversations"
        self.conversations_dir.mkdir(parents=True, exist_ok=True)
        self.current_conversation = None
        self.conversations = self.load_conversations()
    
    def load_conversations(self):
        """Load all saved conversations"""
        conversations = []
        for file in self.conversations_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    conv = json.load(f)
                    conversations.append(conv)
            except Exception as e:
                print(f"Error loading conversation {file}: {e}")
        return sorted(conversations, key=lambda x: x.get('updated_at', ''), reverse=True)
    
    def save_conversation(self, conversation):
        """Save a conversation to disk"""
        conv_id = conversation.get('id', datetime.now().strftime("%Y%m%d_%H%M%S"))
        filename = self.conversations_dir / f"{conv_id}.json"
        conversation['updated_at'] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(conversation, f, indent=2)
        
        return conversation
    
    def delete_conversation(self, conv_id):
        """Delete a conversation"""
        filename = self.conversations_dir / f"{conv_id}.json"
        if filename.exists():
            filename.unlink()
            self.conversations = [c for c in self.conversations if c.get('id') != conv_id]
    
    def create_new_conversation(self, title="New Chat"):
        """Create a new conversation"""
        conv_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        conversation = {
            'id': conv_id,
            'title': title,
            'messages': [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        return self.save_conversation(conversation)


class SettingsDialog(QDialog):
    """Enhanced settings dialog"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Create tab widget for organized settings
        tabs = QTabWidget()
        
        # Appearance tab
        appearance_widget = QWidget()
        appearance_layout = QVBoxLayout()
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark", "Breeze", "Breeze Dark"])
        current_theme = self.settings.value("theme", "System")
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        appearance_layout.addLayout(theme_layout)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QComboBox()
        self.font_size.addItems(["Small", "Medium", "Large", "Extra Large"])
        current_size = self.settings.value("font_size", "Medium")
        self.font_size.setCurrentText(current_size)
        font_layout.addWidget(self.font_size)
        font_layout.addStretch()
        appearance_layout.addLayout(font_layout)
        
        appearance_layout.addStretch()
        appearance_widget.setLayout(appearance_layout)
        tabs.addTab(appearance_widget, "Appearance")
        
        # Behavior tab
        behavior_widget = QWidget()
        behavior_layout = QVBoxLayout()
        
        # System tray
        self.minimize_to_tray = QCheckBox("Minimize to system tray")
        self.minimize_to_tray.setChecked(self.settings.value("minimize_to_tray", True, type=bool))
        behavior_layout.addWidget(self.minimize_to_tray)
        
        # Start minimized
        self.start_minimized = QCheckBox("Start minimized to tray")
        self.start_minimized.setChecked(self.settings.value("start_minimized", False, type=bool))
        behavior_layout.addWidget(self.start_minimized)
        
        # Show notifications
        self.show_notifications = QCheckBox("Show desktop notifications")
        self.show_notifications.setChecked(self.settings.value("show_notifications", True, type=bool))
        behavior_layout.addWidget(self.show_notifications)
        
        behavior_layout.addStretch()
        behavior_widget.setLayout(behavior_layout)
        tabs.addTab(behavior_widget, "Behavior")
        
        # Advanced tab
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout()
        
        # Cache management
        cache_group = QLabel("<b>Cache & Cookies</b>")
        advanced_layout.addWidget(cache_group)
        
        info_label = QLabel("Clear cache and cookies if you have login issues")
        info_label.setWordWrap(True)
        advanced_layout.addWidget(info_label)
        
        clear_cache_btn = QPushButton("Clear Cache & Cookies")
        clear_cache_btn.clicked.connect(self.clear_cache)
        advanced_layout.addWidget(clear_cache_btn)
        
        advanced_layout.addStretch()
        advanced_widget.setLayout(advanced_layout)
        tabs.addTab(advanced_widget, "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def clear_cache(self):
        """Clear browser cache"""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "This will clear the browser cache and cookies and log you out. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Clear cache directories
            cache_dir = Path.home() / ".config" / "claude-desktop" / "cache"
            storage_dir = Path.home() / ".config" / "claude-desktop" / "storage"
            
            try:
                import shutil
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                if storage_dir.exists():
                    shutil.rmtree(storage_dir)
                QMessageBox.information(self, "Cache Cleared", "Cache and cookies cleared. Please restart the application.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not clear cache: {e}")
    
    def get_settings(self):
        """Return current settings"""
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.currentText(),
            'minimize_to_tray': self.minimize_to_tray.isChecked(),
            'start_minimized': self.start_minimized.isChecked(),
            'show_notifications': self.show_notifications.isChecked()
        }


class ClaudeDesktopApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Desktop")
        self.setGeometry(100, 100, 1400, 900)
        
        # Track popup windows
        self.popup_windows = []
        
        # Initialize settings
        self.settings = QSettings("ClaudeDesktop", "ClaudeLinux")
        self.config_dir = Path.home() / ".config" / "claude-desktop"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize conversation manager
        self.conv_manager = ConversationManager(self.config_dir)
        self.current_conversation = None
        
        # Download and set Claude.ai icon
        self.setup_icon()
        
        # Initialize system tray
        self.tray_icon = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.setup_tray_icon()
        
        # Initialize UI (NO MENU BAR)
        self.init_ui()
        self.apply_theme()
        
        # Check if should start minimized
        if self.settings.value("start_minimized", False, type=bool) and self.tray_icon:
            self.hide()
    
    def setup_icon(self):
        """Download and setup Claude.ai icon"""
        icon_path = self.config_dir / "claude_icon.png"
        
        # Try to download Claude.ai favicon
        if not icon_path.exists():
            try:
                url = "https://claude.ai/favicon.ico"
                urllib.request.urlretrieve(url, str(icon_path))
            except Exception as e:
                print(f"Could not download icon: {e}")
                self.create_fallback_icon(icon_path)
        
        # Set window icon
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
    
    def create_fallback_icon(self, icon_path):
        """Create a fallback icon if download fails"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        from PyQt6.QtGui import QPainter, QColor, QFont as QGuiFont
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw purple circle background
        painter.setBrush(QColor(107, 70, 193))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        
        # Draw white "C"
        painter.setPen(QColor(255, 255, 255))
        font = QGuiFont("Arial", 36, QGuiFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "C")
        
        painter.end()
        pixmap.save(str(icon_path))
    
    def setup_tray_icon(self):
        """Setup system tray icon"""
        icon_path = self.config_dir / "claude_icon.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            icon = QIcon.fromTheme("application-chat")
        
        self.tray_icon = SystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Claude Desktop")
        self.tray_icon.show()
    
    def init_ui(self):
        """Initialize the user interface - NO MENU BAR"""
        # Create toolbar (minimal)
        self.create_toolbar()
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Conversation list
        self.conversation_panel = self.create_conversation_panel()
        splitter.addWidget(self.conversation_panel)
        
        # Right panel - Chat interface
        chat_widget = self.create_chat_panel()
        splitter.addWidget(chat_widget)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        
        # Create status bar
        self.statusBar().showMessage("Ready - If login doesn't work, try Settings > Clear Cache & Cookies")
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        shortcuts = [
            ("Ctrl+N", self.new_chat),
            ("Ctrl+B", self.toggle_sidebar),
            ("Ctrl+,", self.show_settings),
            ("F11", self.toggle_fullscreen),
            ("Ctrl+Q", self.close_app),
            ("F5", self.reload_page)
        ]
        
        for shortcut_key, handler in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(shortcut_key))
            action.triggered.connect(handler)
            self.addAction(action)
    
    def create_toolbar(self):
        """Create minimal toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # New chat button
        new_chat_btn = QAction("New Chat", self)
        new_chat_btn.triggered.connect(self.new_chat)
        toolbar.addAction(new_chat_btn)
        
        # Reload button
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        toolbar.addAction(reload_btn)
        
        toolbar.addSeparator()
        
        # Toggle sidebar
        toggle_btn = QAction("Toggle Sidebar", self)
        toggle_btn.triggered.connect(self.toggle_sidebar)
        toolbar.addAction(toggle_btn)
        
        toolbar.addSeparator()
        
        # Settings button
        settings_btn = QAction("Settings", self)
        settings_btn.triggered.connect(self.show_settings)
        toolbar.addAction(settings_btn)
    
    def create_conversation_panel(self):
        """Create the left conversation list panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Conversations")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(header)
        
        # New chat button
        new_btn = QPushButton("+ New Chat")
        new_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_btn)
        
        # Conversation list
        self.conv_list_widget = QListWidget()
        self.conv_list_widget.itemClicked.connect(self.on_conversation_selected)
        layout.addWidget(self.conv_list_widget)
        
        panel.setLayout(layout)
        panel.setMinimumWidth(250)
        return panel
    
    def create_chat_panel(self):
        """Create the main chat panel with embedded web view"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create dedicated profile for this app
        self.web_profile = QWebEngineProfile("ClaudeDesktop", self)
        
        # Set up persistent storage with proper paths
        cache_path = str(self.config_dir / "cache")
        storage_path = str(self.config_dir / "storage")
        
        self.web_profile.setCachePath(cache_path)
        self.web_profile.setPersistentStoragePath(storage_path)
        self.web_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        
        # Enable third-party cookies (needed for OAuth)
        self.web_profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalStorageEnabled, True
        )
        
        # Create custom page with full OAuth support
        self.web_page = ClaudeWebPage(self.web_profile)
        self.web_page.popup_created.connect(self.on_popup_created)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.web_page)
        
        # Load Claude.ai
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        
        layout.addWidget(self.web_view)
        panel.setLayout(layout)
        
        return panel
    
    def on_popup_created(self, view):
        """Track popup windows"""
        self.popup_windows.append(view)
        print(f"Popup window created and shown")
    
    def on_conversation_selected(self, item):
        """Handle conversation selection"""
        pass
    
    def new_chat(self):
        """Create a new chat"""
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        self.statusBar().showMessage("Loading new chat...")
    
    def reload_page(self):
        """Reload the current page"""
        self.web_view.reload()
        self.statusBar().showMessage("Reloading...")
    
    def toggle_sidebar(self):
        """Toggle the conversation sidebar"""
        self.conversation_panel.setVisible(not self.conversation_panel.isVisible())
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self.settings.setValue(key, value)
            self.apply_theme()
            self.statusBar().showMessage("Settings saved")
    
    def apply_theme(self):
        """Apply the selected theme"""
        font_size_setting = self.settings.value("font_size", "Medium")
        
        font_sizes = {
            "Small": 9,
            "Medium": 10,
            "Large": 12,
            "Extra Large": 14
        }
        font_size = font_sizes.get(font_size_setting, 10)
        
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)
    
    def close_app(self):
        """Properly close the application"""
        # Close all popup windows
        for popup in self.popup_windows:
            if popup and not popup.isHidden():
                popup.close()
        
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if (self.settings.value("minimize_to_tray", True, type=bool) and 
            self.tray_icon and 
            self.tray_icon.isVisible()):
            
            event.ignore()
            self.hide()
            
            if self.settings.value("show_notifications", True, type=bool):
                self.tray_icon.showMessage(
                    "Claude Desktop",
                    "Application minimized to tray",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            self.close_app()
            event.accept()


def main():
    """Main application entry point"""
    # Enable better OAuth support
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-features=ThirdPartyCookies'
    
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Claude Desktop")
    app.setApplicationDisplayName("Claude Desktop")
    app.setOrganizationName("ClaudeDesktop")
    app.setOrganizationDomain("claude.ai")
    
    # Use native KDE/Breeze style
    app.setStyle("Breeze")
    
    # Handle quit on last window closed
    app.setQuitOnLastWindowClosed(False)
    
    # Create and show main window
    window = ClaudeDesktopApp()
    
    # Restore window geometry if saved
    settings = QSettings("ClaudeDesktop", "ClaudeLinux")
    if settings.contains("geometry"):
        window.restoreGeometry(settings.value("geometry"))
    if settings.contains("windowState"):
        window.restoreState(settings.value("windowState"))
    
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
