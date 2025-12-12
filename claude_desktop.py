#!/usr/bin/env python3
"""
Claude Desktop for Linux - Enhanced Version (Fixed)
- No menu bar
- Claude.ai logo icon
- OAuth/Google login support
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
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
from PyQt6.QtNetwork import QNetworkRequest
import urllib.request


class ClaudeWebPage(QWebEnginePage):
    """Custom web page to handle Claude.ai interactions and OAuth"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        # Enable features needed for OAuth
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Handle navigation requests - allow OAuth flows"""
        url_string = url.toString()
        
        # Allow all Claude.ai and Anthropic domains
        allowed_domains = ['claude.ai', 'anthropic.com', 'accounts.google.com', 'accounts.anthropic.com']
        
        # Check if URL is from allowed domains or OAuth flow
        if any(domain in url.host() for domain in allowed_domains):
            return True
        
        # Allow OAuth callback URLs
        if 'oauth' in url_string.lower() or 'callback' in url_string.lower():
            return True
        
        # Allow Google authentication
        if 'google' in url.host() or 'gstatic' in url.host() or 'googleapis' in url.host():
            return True
        
        # For external links clicked by user, open in default browser
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if not any(domain in url.host() for domain in allowed_domains):
                QDesktopServices.openUrl(url)
                return False
        
        return True
    
    def createWindow(self, window_type):
        """Handle popup windows for OAuth"""
        # Create a new page for popups (like Google OAuth)
        page = ClaudeWebPage(self.profile(), self.view())
        page.urlChanged.connect(lambda url: self.handle_popup_url(url, page))
        
        # Create a new view for the popup
        view = QWebEngineView()
        view.setPage(page)
        view.setWindowTitle("Sign In")
        view.resize(500, 600)
        view.show()
        
        return page
    
    def handle_popup_url(self, url, page):
        """Handle URLs in popup windows"""
        # If we're back at claude.ai after OAuth, close the popup
        if 'claude.ai' in url.toString() and 'chat' in url.toString():
            if page.view():
                page.view().close()


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
    
    def search_conversations(self, query):
        """Search conversations by content"""
        results = []
        query_lower = query.lower()
        for conv in self.conversations:
            # Search in title
            if query_lower in conv.get('title', '').lower():
                results.append(conv)
                continue
            # Search in messages
            for msg in conv.get('messages', []):
                if query_lower in msg.get('content', '').lower():
                    results.append(conv)
                    break
        return results


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
        
        # Auto-save conversations
        self.auto_save = QCheckBox("Auto-save conversations")
        self.auto_save.setChecked(self.settings.value("auto_save", True, type=bool))
        behavior_layout.addWidget(self.auto_save)
        
        # Show timestamps
        self.show_timestamps = QCheckBox("Show message timestamps")
        self.show_timestamps.setChecked(self.settings.value("show_timestamps", True, type=bool))
        behavior_layout.addWidget(self.show_timestamps)
        
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
        cache_group = QLabel("<b>Cache Management</b>")
        advanced_layout.addWidget(cache_group)
        
        clear_cache_btn = QPushButton("Clear Browser Cache")
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
            "This will clear the browser cache and log you out. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Cache Cleared", "Please restart the application for changes to take effect.")
    
    def get_settings(self):
        """Return current settings"""
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.currentText(),
            'auto_save': self.auto_save.isChecked(),
            'show_timestamps': self.show_timestamps.isChecked(),
            'minimize_to_tray': self.minimize_to_tray.isChecked(),
            'start_minimized': self.start_minimized.isChecked(),
            'show_notifications': self.show_notifications.isChecked()
        }


class SearchDialog(QDialog):
    """Search conversations dialog"""
    
    def __init__(self, conv_manager, parent=None):
        super().__init__(parent)
        self.conv_manager = conv_manager
        self.setWindowTitle("Search Conversations")
        self.setMinimumSize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search conversations...")
        self.search_input.textChanged.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_conversation)
        layout.addWidget(self.results_list)
        
        # Status label
        self.status_label = QLabel("Enter search terms to find conversations")
        layout.addWidget(self.status_label)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def perform_search(self):
        """Perform search and update results"""
        query = self.search_input.text().strip()
        if not query:
            self.results_list.clear()
            self.status_label.setText("Enter search terms to find conversations")
            return
        
        results = self.conv_manager.search_conversations(query)
        self.results_list.clear()
        
        for conv in results:
            title = conv.get('title', 'Untitled')
            updated = conv.get('updated_at', '')
            item = QListWidgetItem(f"{title} - {updated}")
            item.setData(Qt.ItemDataRole.UserRole, conv)
            self.results_list.addItem(item)
        
        self.status_label.setText(f"Found {len(results)} conversation(s)")
    
    def open_conversation(self, item):
        """Open selected conversation"""
        conv = item.data(Qt.ItemDataRole.UserRole)
        self.selected_conversation = conv
        self.accept()


class ClaudeDesktopApp(QMainWindow):
    """Main application window - No menu bar, with Claude icon"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Desktop")
        self.setGeometry(100, 100, 1400, 900)
        
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
        
        # Load last conversation if exists
        if self.conv_manager.conversations:
            self.load_conversation(self.conv_manager.conversations[0])
    
    def setup_icon(self):
        """Download and setup Claude.ai icon"""
        icon_path = self.config_dir / "claude_icon.png"
        
        # Try to download Claude.ai favicon/logo
        if not icon_path.exists():
            try:
                # Try to get Claude.ai favicon
                url = "https://claude.ai/favicon.ico"
                urllib.request.urlretrieve(url, str(icon_path))
            except Exception as e:
                print(f"Could not download icon: {e}")
                # Create a fallback icon
                self.create_fallback_icon(icon_path)
        
        # Set window icon
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
    
    def create_fallback_icon(self, icon_path):
        """Create a fallback icon if download fails"""
        # Create a simple purple "C" icon
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        from PyQt6.QtGui import QPainter, QColor, QFont as QGuiFont
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw purple circle background
        painter.setBrush(QColor(107, 70, 193))  # Claude purple
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
        # NO MENU BAR - Removed completely
        
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
        self.statusBar().showMessage("Ready")
        
        # Setup keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+N: New chat
        new_chat_shortcut = QKeySequence("Ctrl+N")
        new_action = QAction(self)
        new_action.setShortcut(new_chat_shortcut)
        new_action.triggered.connect(self.new_chat)
        self.addAction(new_action)
        
        # Ctrl+F: Search
        search_shortcut = QKeySequence("Ctrl+F")
        search_action = QAction(self)
        search_action.setShortcut(search_shortcut)
        search_action.triggered.connect(self.search_conversations)
        self.addAction(search_action)
        
        # Ctrl+B: Toggle sidebar
        toggle_shortcut = QKeySequence("Ctrl+B")
        toggle_action = QAction(self)
        toggle_action.setShortcut(toggle_shortcut)
        toggle_action.triggered.connect(self.toggle_sidebar)
        self.addAction(toggle_action)
        
        # Ctrl+,: Settings
        settings_shortcut = QKeySequence("Ctrl+,")
        settings_action = QAction(self)
        settings_action.setShortcut(settings_shortcut)
        settings_action.triggered.connect(self.show_settings)
        self.addAction(settings_action)
        
        # F11: Fullscreen
        fullscreen_shortcut = QKeySequence("F11")
        fullscreen_action = QAction(self)
        fullscreen_action.setShortcut(fullscreen_shortcut)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(fullscreen_action)
        
        # Ctrl+Q: Quit
        quit_shortcut = QKeySequence("Ctrl+Q")
        quit_action = QAction(self)
        quit_action.setShortcut(quit_shortcut)
        quit_action.triggered.connect(self.close_app)
        self.addAction(quit_action)
    
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
        
        # Search button
        search_btn = QAction("Search", self)
        search_btn.triggered.connect(self.search_conversations)
        toolbar.addAction(search_btn)
        
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
        self.conv_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.conv_list_widget.customContextMenuRequested.connect(self.show_conversation_context_menu)
        self.update_conversation_list()
        layout.addWidget(self.conv_list_widget)
        
        panel.setLayout(layout)
        panel.setMinimumWidth(250)
        return panel
    
    def create_chat_panel(self):
        """Create the main chat panel with embedded web view"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Web view for Claude.ai with OAuth support
        self.web_profile = QWebEngineProfile.defaultProfile()
        
        # Set up persistent storage
        cache_path = str(self.config_dir / "cache")
        self.web_profile.setCachePath(cache_path)
        self.web_profile.setPersistentStoragePath(str(self.config_dir / "storage"))
        self.web_profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
        
        # Create custom page with OAuth support
        self.web_page = ClaudeWebPage(self.web_profile)
        
        # Create web view
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.web_page)
        
        # Load Claude.ai
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        
        layout.addWidget(self.web_view)
        panel.setLayout(layout)
        
        return panel
    
    def update_conversation_list(self):
        """Update the conversation list widget"""
        self.conv_list_widget.clear()
        for conv in self.conv_manager.conversations:
            title = conv.get('title', 'Untitled')
            updated = conv.get('updated_at', '')
            if updated:
                try:
                    dt = datetime.fromisoformat(updated)
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                    display_text = f"{title}\n{time_str}"
                except:
                    display_text = title
            else:
                display_text = title
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, conv)
            self.conv_list_widget.addItem(item)
    
    def on_conversation_selected(self, item):
        """Handle conversation selection"""
        conv = item.data(Qt.ItemDataRole.UserRole)
        self.load_conversation(conv)
    
    def show_conversation_context_menu(self, position):
        """Show context menu for conversation list"""
        item = self.conv_list_widget.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        open_action = QAction("Open", self)
        open_action.triggered.connect(lambda: self.on_conversation_selected(item))
        menu.addAction(open_action)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_conversation(item))
        menu.addAction(rename_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_conversation(item))
        menu.addAction(delete_action)
        
        menu.exec(self.conv_list_widget.mapToGlobal(position))
    
    def rename_conversation(self, item):
        """Rename a conversation"""
        conv = item.data(Qt.ItemDataRole.UserRole)
        new_title, ok = QInputDialog.getText(
            self,
            "Rename Conversation",
            "Enter new title:",
            text=conv.get('title', '')
        )
        if ok and new_title:
            conv['title'] = new_title
            self.conv_manager.save_conversation(conv)
            self.update_conversation_list()
    
    def delete_conversation(self, item):
        """Delete a conversation"""
        conv = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Delete Conversation",
            f"Are you sure you want to delete '{conv.get('title', 'this conversation')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.conv_manager.delete_conversation(conv['id'])
            self.update_conversation_list()
    
    def load_conversation(self, conversation):
        """Load a conversation"""
        self.current_conversation = conversation
        self.statusBar().showMessage(f"Loaded: {conversation.get('title', 'Untitled')}")
    
    def new_chat(self):
        """Create a new chat - just reload Claude.ai"""
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        self.statusBar().showMessage("New chat started")
    
    def search_conversations(self):
        """Open search dialog"""
        dialog = SearchDialog(self.conv_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if hasattr(dialog, 'selected_conversation'):
                self.load_conversation(dialog.selected_conversation)
    
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
        theme = self.settings.value("theme", "System")
        font_size_setting = self.settings.value("font_size", "Medium")
        
        # Font size mapping
        font_sizes = {
            "Small": 9,
            "Medium": 10,
            "Large": 12,
            "Extra Large": 14
        }
        font_size = font_sizes.get(font_size_setting, 10)
        
        # Apply font
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)
    
    def close_app(self):
        """Properly close the application"""
        # Save current conversation if auto-save is enabled
        if self.current_conversation and self.settings.value("auto_save", True, type=bool):
            self.conv_manager.save_conversation(self.current_conversation)
        
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Quit application
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Check if should minimize to tray
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
