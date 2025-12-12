#!/usr/bin/env python3
"""
Claude Desktop for Linux (Fedora 43 KDE)
A feature-complete Qt6-based desktop application for Claude.ai
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QSplitter, QListWidget, QListWidgetItem,
    QLabel, QMenuBar, QMenu, QToolBar, QStatusBar, QMessageBox,
    QInputDialog, QFileDialog, QDialog, QDialogButtonBox, QLineEdit,
    QCheckBox, QComboBox, QTextBrowser, QTabWidget, QScrollArea
)
from PyQt6.QtCore import Qt, QUrl, QSettings, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QFont, QTextCursor, QDesktopServices, QKeySequence
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage


class ClaudeAPI(QThread):
    """Handle Claude API interactions in a separate thread"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, message, conversation_history):
        super().__init__()
        self.message = message
        self.conversation_history = conversation_history
    
    def run(self):
        """Send message to Claude.ai web interface via embedded browser"""
        # This will be handled by the WebEngine view
        pass


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
    """Settings dialog for application configuration"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Theme settings
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        current_theme = self.settings.value("theme", "System")
        self.theme_combo.setCurrentText(current_theme)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QComboBox()
        self.font_size.addItems(["Small", "Medium", "Large"])
        current_size = self.settings.value("font_size", "Medium")
        self.font_size.setCurrentText(current_size)
        font_layout.addWidget(self.font_size)
        layout.addLayout(font_layout)
        
        # Auto-save conversations
        self.auto_save = QCheckBox("Auto-save conversations")
        self.auto_save.setChecked(self.settings.value("auto_save", True, type=bool))
        layout.addWidget(self.auto_save)
        
        # Show timestamps
        self.show_timestamps = QCheckBox("Show message timestamps")
        self.show_timestamps.setChecked(self.settings.value("show_timestamps", True, type=bool))
        layout.addWidget(self.show_timestamps)
        
        # Markdown rendering
        self.render_markdown = QCheckBox("Render Markdown in messages")
        self.render_markdown.setChecked(self.settings.value("render_markdown", True, type=bool))
        layout.addWidget(self.render_markdown)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def get_settings(self):
        """Return current settings"""
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.currentText(),
            'auto_save': self.auto_save.isChecked(),
            'show_timestamps': self.show_timestamps.isChecked(),
            'render_markdown': self.render_markdown.isChecked()
        }


class ClaudeDesktopApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Desktop for Linux")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize settings
        self.settings = QSettings("ClaudeDesktop", "ClaudeLinux")
        self.config_dir = Path.home() / ".config" / "claude-desktop"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize conversation manager
        self.conv_manager = ConversationManager(self.config_dir)
        self.current_conversation = None
        
        # Initialize UI
        self.init_ui()
        self.apply_theme()
        
        # Load last conversation if exists
        if self.conv_manager.conversations:
            self.load_conversation(self.conv_manager.conversations[0])
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Conversation list
        self.conversation_list = self.create_conversation_panel()
        splitter.addWidget(self.conversation_list)
        
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
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_chat_action = QAction("&New Chat", self)
        new_chat_action.setShortcut(QKeySequence("Ctrl+N"))
        new_chat_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_chat_action)
        
        open_action = QAction("&Open Chat...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_chat)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save Chat", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_current_chat)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Chat...", self)
        export_action.triggered.connect(self.export_chat)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_text)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self.paste_text)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        clear_action = QAction("Clear Chat", self)
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_sidebar = QAction("Toggle Sidebar", self)
        toggle_sidebar.setShortcut(QKeySequence("Ctrl+B"))
        toggle_sidebar.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(toggle_sidebar)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        docs_action = QAction("&Documentation", self)
        docs_action.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://docs.claude.com")))
        help_menu.addAction(docs_action)
    
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # New chat button
        new_chat_btn = QAction("New Chat", self)
        new_chat_btn.triggered.connect(self.new_chat)
        toolbar.addAction(new_chat_btn)
        
        toolbar.addSeparator()
        
        # Save button
        save_btn = QAction("Save", self)
        save_btn.triggered.connect(self.save_current_chat)
        toolbar.addAction(save_btn)
        
        toolbar.addSeparator()
        
        # Export button
        export_btn = QAction("Export", self)
        export_btn.triggered.connect(self.export_chat)
        toolbar.addAction(export_btn)
    
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
        self.update_conversation_list()
        layout.addWidget(self.conv_list_widget)
        
        panel.setLayout(layout)
        panel.setMinimumWidth(250)
        return panel
    
    def create_chat_panel(self):
        """Create the main chat panel with embedded web view"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        
        # Web view tab (main Claude.ai interface)
        self.web_view = QWebEngineView()
        self.web_profile = QWebEngineProfile.defaultProfile()
        
        # Set up persistent storage
        cache_path = str(self.config_dir / "cache")
        self.web_profile.setCachePath(cache_path)
        self.web_profile.setPersistentStoragePath(str(self.config_dir / "storage"))
        
        # Load Claude.ai
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        self.tab_widget.addTab(self.web_view, "Chat")
        
        # Local chat tab (for offline viewing/editing)
        self.local_chat = self.create_local_chat_view()
        self.tab_widget.addTab(self.local_chat, "Local View")
        
        layout.addWidget(self.tab_widget)
        panel.setLayout(layout)
        
        return panel
    
    def create_local_chat_view(self):
        """Create local chat view for offline access"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Chat display area
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setMinimumHeight(400)
        layout.addWidget(self.chat_display)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.message_input = QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.setPlaceholderText("Type your message here... (Shift+Enter for new line, Enter to send)")
        input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumWidth(80)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        
        widget.setLayout(layout)
        return widget
    
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
    
    def load_conversation(self, conversation):
        """Load a conversation into the chat display"""
        self.current_conversation = conversation
        self.chat_display.clear()
        
        html_content = "<html><body style='font-family: sans-serif;'>"
        
        for msg in conversation.get('messages', []):
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            
            if role == 'user':
                html_content += f"<div style='background-color: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
                html_content += f"<b>You</b>"
                if timestamp and self.settings.value("show_timestamps", True, type=bool):
                    html_content += f" <small style='color: #666;'>({timestamp})</small>"
                html_content += f"<br>{content}</div>"
            else:
                html_content += f"<div style='background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px;'>"
                html_content += f"<b>Claude</b>"
                if timestamp and self.settings.value("show_timestamps", True, type=bool):
                    html_content += f" <small style='color: #666;'>({timestamp})</small>"
                html_content += f"<br>{content}</div>"
        
        html_content += "</body></html>"
        self.chat_display.setHtml(html_content)
        
        # Scroll to bottom
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.chat_display.setTextCursor(cursor)
    
    def new_chat(self):
        """Create a new chat conversation"""
        title, ok = QInputDialog.getText(self, "New Chat", "Enter chat title:")
        if ok and title:
            conv = self.conv_manager.create_new_conversation(title)
            self.conv_manager.conversations.insert(0, conv)
            self.update_conversation_list()
            self.load_conversation(conv)
            self.statusBar().showMessage(f"Created new chat: {title}")
    
    def open_chat(self):
        """Open a saved chat"""
        # This is handled by the conversation list
        self.statusBar().showMessage("Select a conversation from the sidebar")
    
    def save_current_chat(self):
        """Save the current chat"""
        if self.current_conversation:
            self.conv_manager.save_conversation(self.current_conversation)
            self.statusBar().showMessage("Chat saved successfully")
        else:
            self.statusBar().showMessage("No active chat to save")
    
    def export_chat(self):
        """Export current chat to a file"""
        if not self.current_conversation:
            QMessageBox.warning(self, "Export", "No active chat to export")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Chat",
            f"{self.current_conversation.get('title', 'chat')}.txt",
            "Text Files (*.txt);;JSON Files (*.json);;Markdown Files (*.md)"
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    with open(filename, 'w') as f:
                        json.dump(self.current_conversation, f, indent=2)
                else:
                    with open(filename, 'w') as f:
                        f.write(f"# {self.current_conversation.get('title', 'Chat')}\n\n")
                        for msg in self.current_conversation.get('messages', []):
                            role = "You" if msg['role'] == 'user' else "Claude"
                            f.write(f"**{role}**: {msg['content']}\n\n")
                
                self.statusBar().showMessage(f"Chat exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export chat: {str(e)}")
    
    def send_message(self):
        """Send a message in local chat view"""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        if not self.current_conversation:
            self.new_chat()
        
        # Add message to conversation
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_conversation['messages'].append({
            'role': 'user',
            'content': message,
            'timestamp': timestamp
        })
        
        # Clear input
        self.message_input.clear()
        
        # Update display
        self.load_conversation(self.current_conversation)
        
        # Auto-save if enabled
        if self.settings.value("auto_save", True, type=bool):
            self.save_current_chat()
        
        # Note: Actual Claude API integration would happen here
        # For now, this is a placeholder for the local view
        self.statusBar().showMessage("Message sent (switch to Chat tab for live interaction)")
    
    def copy_text(self):
        """Copy selected text"""
        if self.tab_widget.currentIndex() == 1:  # Local view
            self.chat_display.copy()
    
    def paste_text(self):
        """Paste text into input"""
        if self.tab_widget.currentIndex() == 1:  # Local view
            self.message_input.paste()
    
    def clear_chat(self):
        """Clear current chat"""
        reply = QMessageBox.question(
            self,
            "Clear Chat",
            "Are you sure you want to clear the current chat?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.current_conversation:
                self.current_conversation['messages'] = []
                self.chat_display.clear()
                self.statusBar().showMessage("Chat cleared")
    
    def toggle_sidebar(self):
        """Toggle the conversation sidebar"""
        sidebar = self.conversation_list
        sidebar.setVisible(not sidebar.isVisible())
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self.settings.setValue(key, value)
            self.apply_theme()
            self.statusBar().showMessage("Settings saved")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Claude Desktop for Linux",
            "<h2>Claude Desktop for Linux</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A feature-complete Qt6-based desktop application for Claude.ai</p>"
            "<p>Built specifically for Fedora 43 KDE Edition</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Native KDE/Breeze theme integration</li>"
            "<li>Full Claude.ai web interface access</li>"
            "<li>Local conversation management</li>"
            "<li>Persistent chat history</li>"
            "<li>Export and backup capabilities</li>"
            "</ul>"
            "<p>© 2024 - Created for Linux users</p>"
        )
    
    def apply_theme(self):
        """Apply the selected theme"""
        theme = self.settings.value("theme", "System")
        font_size_setting = self.settings.value("font_size", "Medium")
        
        # Font size mapping
        font_sizes = {
            "Small": 9,
            "Medium": 10,
            "Large": 12
        }
        font_size = font_sizes.get(font_size_setting, 10)
        
        # Apply font
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)
        
        # Apply theme (KDE/Breeze handles most of this automatically)
        if theme == "Dark":
            app.setStyle("Breeze")
        elif theme == "Light":
            app.setStyle("Breeze")
        # System theme is default
    
    def closeEvent(self, event):
        """Handle application close"""
        # Save current conversation if auto-save is enabled
        if self.current_conversation and self.settings.value("auto_save", True, type=bool):
            self.save_current_chat()
        
        # Save window geometry
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Claude Desktop")
    app.setApplicationDisplayName("Claude Desktop for Linux")
    app.setOrganizationName("ClaudeDesktop")
    app.setOrganizationDomain("claude.ai")
    
    # Use native KDE/Breeze style
    app.setStyle("Breeze")
    
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
