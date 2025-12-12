#!/usr/bin/env python3
"""
Claude Desktop for Linux - FedCM Disabled Version
Disables FedCM to force traditional OAuth popup flow for Google login
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSplitter, QListWidget, QListWidgetItem,
    QLabel, QToolBar, QStatusBar, QMessageBox,
    QInputDialog, QFileDialog, QDialog, QDialogButtonBox, QLineEdit,
    QCheckBox, QComboBox, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, QUrl, QSettings, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage, QWebEngineSettings
import urllib.request


class OAuthWebPage(QWebEnginePage):
    """Web page for OAuth popups"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        
        self.urlChanged.connect(self.on_url_changed)
    
    def on_url_changed(self, url):
        """Close popup when returning to Claude"""
        url_str = url.toString()
        if 'claude.ai/chat' in url_str or 'claude.ai/?' in url_str:
            if self.view() and hasattr(self.view(), 'is_popup'):
                QTimer.singleShot(1000, self.view().close)


class ClaudeWebPage(QWebEnginePage):
    """Main web page with OAuth support"""
    
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Allow all Claude and Google domains"""
        host = url.host()
        
        allowed_domains = [
            'claude.ai', 'anthropic.com',
            'accounts.google.com', 'google.com',
            'gstatic.com', 'googleapis.com', 'googleusercontent.com'
        ]
        
        for domain in allowed_domains:
            if domain in host:
                return True
        
        if any(keyword in url.toString().lower() for keyword in ['oauth', 'callback', 'auth', 'login']):
            return True
        
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if not any(domain in host for domain in allowed_domains):
                QDesktopServices.openUrl(url)
                return False
        
        return True
    
    def createWindow(self, window_type):
        """Create OAuth popup windows"""
        page = OAuthWebPage(self.profile(), None)
        
        view = QWebEngineView()
        view.setPage(page)
        view.setWindowTitle("Sign In - Claude")
        view.resize(500, 700)
        view.is_popup = True
        view.show()
        view.raise_()
        view.activateWindow()
        
        return page


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon"""
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.parent_window = parent
        
        menu = QMenu()
        
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.toggle_window)
        menu.addAction(show_action)
        
        new_chat_action = QAction("New Chat", self)
        new_chat_action.triggered.connect(lambda: self.parent_window.new_chat() if self.parent_window else None)
        menu.addAction(new_chat_action)
        
        menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(lambda: self.parent_window.force_quit() if self.parent_window else QApplication.quit())
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        self.activated.connect(self.on_tray_activated)
    
    def toggle_window(self):
        if self.parent_window:
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.parent_window.show()
                self.parent_window.activateWindow()
                self.parent_window.raise_()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        self.theme_combo.setCurrentText(self.settings.value("theme", "System"))
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)
        
        # Font size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QComboBox()
        self.font_size.addItems(["Small", "Medium", "Large"])
        self.font_size.setCurrentText(self.settings.value("font_size", "Medium"))
        font_layout.addWidget(self.font_size)
        layout.addLayout(font_layout)
        
        # System tray
        self.minimize_to_tray = QCheckBox("Minimize to system tray")
        self.minimize_to_tray.setChecked(self.settings.value("minimize_to_tray", True, type=bool))
        layout.addWidget(self.minimize_to_tray)
        
        # Clear cache button
        layout.addWidget(QLabel(""))
        clear_btn = QPushButton("Clear Cache & Cookies")
        clear_btn.clicked.connect(self.clear_cache)
        layout.addWidget(clear_btn)
        
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
        reply = QMessageBox.question(
            self, "Clear Cache",
            "Clear cache and cookies? You will be logged out.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                import shutil
                cache_dir = Path.home() / ".config" / "claude-desktop" / "cache"
                storage_dir = Path.home() / ".config" / "claude-desktop" / "storage"
                
                if cache_dir.exists():
                    shutil.rmtree(cache_dir)
                if storage_dir.exists():
                    shutil.rmtree(storage_dir)
                
                QMessageBox.information(self, "Done", "Restart the app for changes to take effect")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))
    
    def get_settings(self):
        return {
            'theme': self.theme_combo.currentText(),
            'font_size': self.font_size.currentText(),
            'minimize_to_tray': self.minimize_to_tray.isChecked()
        }


class ClaudeDesktopApp(QMainWindow):
    """Main application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude Desktop")
        self.setGeometry(100, 100, 1400, 900)
        
        self.popup_windows = []
        self.settings = QSettings("ClaudeDesktop", "ClaudeLinux")
        self.config_dir = Path.home() / ".config" / "claude-desktop"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.setup_icon()
        
        self.tray_icon = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.setup_tray_icon()
        
        self.init_ui()
        self.apply_theme()
    
    def setup_icon(self):
        icon_path = self.config_dir / "claude_icon.png"
        
        if not icon_path.exists():
            try:
                urllib.request.urlretrieve("https://claude.ai/favicon.ico", str(icon_path))
            except:
                self.create_fallback_icon(icon_path)
        
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            self.setWindowIcon(icon)
            QApplication.instance().setWindowIcon(icon)
    
    def create_fallback_icon(self, icon_path):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        from PyQt6.QtGui import QPainter, QColor, QFont as QGuiFont
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(107, 70, 193))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 60, 60)
        painter.setPen(QColor(255, 255, 255))
        font = QGuiFont("Arial", 36, QGuiFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "C")
        painter.end()
        pixmap.save(str(icon_path))
    
    def setup_tray_icon(self):
        icon_path = self.config_dir / "claude_icon.png"
        if icon_path.exists():
            icon = QIcon(str(icon_path))
        else:
            icon = QIcon.fromTheme("application-chat")
        
        self.tray_icon = SystemTrayIcon(icon, self)
        self.tray_icon.setToolTip("Claude Desktop")
        self.tray_icon.show()
    
    def init_ui(self):
        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        new_btn = QAction("New Chat", self)
        new_btn.triggered.connect(self.new_chat)
        toolbar.addAction(new_btn)
        
        reload_btn = QAction("Reload", self)
        reload_btn.triggered.connect(self.reload_page)
        toolbar.addAction(reload_btn)
        
        toolbar.addSeparator()
        
        sidebar_btn = QAction("Toggle Sidebar", self)
        sidebar_btn.triggered.connect(self.toggle_sidebar)
        toolbar.addAction(sidebar_btn)
        
        settings_btn = QAction("Settings", self)
        settings_btn.triggered.connect(self.show_settings)
        toolbar.addAction(settings_btn)
        
        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Sidebar
        self.sidebar = self.create_sidebar()
        splitter.addWidget(self.sidebar)
        
        # Web view
        web_widget = self.create_webview()
        splitter.addWidget(web_widget)
        
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        
        self.statusBar().showMessage("Ready - Google login should now work!")
        
        # Shortcuts
        self.setup_shortcuts()
    
    def create_sidebar(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        header = QLabel("Conversations")
        header.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        new_btn = QPushButton("+ New Chat")
        new_btn.clicked.connect(self.new_chat)
        layout.addWidget(new_btn)
        
        self.conv_list = QListWidget()
        layout.addWidget(self.conv_list)
        
        widget.setLayout(layout)
        widget.setMinimumWidth(250)
        return widget
    
    def create_webview(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create profile
        self.web_profile = QWebEngineProfile("ClaudeDesktop", self)
        
        cache_path = str(self.config_dir / "cache")
        storage_path = str(self.config_dir / "storage")
        
        self.web_profile.setCachePath(cache_path)
        self.web_profile.setPersistentStoragePath(storage_path)
        self.web_profile.setPersistentCookiesPolicy(
            QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
        )
        
        # Create page
        self.web_page = ClaudeWebPage(self.web_profile)
        
        # Create view
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.web_page)
        self.web_view.setUrl(QUrl("https://claude.ai/"))
        
        layout.addWidget(self.web_view)
        widget.setLayout(layout)
        return widget
    
    def setup_shortcuts(self):
        shortcuts = [
            ("Ctrl+N", self.new_chat),
            ("F5", self.reload_page),
            ("Ctrl+B", self.toggle_sidebar),
            ("Ctrl+,", self.show_settings),
            ("F11", self.toggle_fullscreen),
            ("Ctrl+Q", self.force_quit)
        ]
        
        for key, handler in shortcuts:
            action = QAction(self)
            action.setShortcut(QKeySequence(key))
            action.triggered.connect(handler)
            self.addAction(action)
    
    def new_chat(self):
        self.web_view.setUrl(QUrl("https://claude.ai/"))
    
    def reload_page(self):
        self.web_view.reload()
    
    def toggle_sidebar(self):
        self.sidebar.setVisible(not self.sidebar.isVisible())
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_settings(self):
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            for key, value in new_settings.items():
                self.settings.setValue(key, value)
            self.apply_theme()
    
    def apply_theme(self):
        font_size_setting = self.settings.value("font_size", "Medium")
        font_sizes = {"Small": 9, "Medium": 10, "Large": 12}
        font_size = font_sizes.get(font_size_setting, 10)
        
        app = QApplication.instance()
        font = app.font()
        font.setPointSize(font_size)
        app.setFont(font)
    
    def force_quit(self):
        for popup in self.popup_windows:
            if popup and not popup.isHidden():
                popup.close()
        
        self.settings.setValue("geometry", self.saveGeometry())
        QApplication.instance().quit()
        sys.exit(0)
    
    def closeEvent(self, event):
        if self.settings.value("minimize_to_tray", True, type=bool) and self.tray_icon:
            event.ignore()
            self.hide()
        else:
            self.force_quit()
            event.accept()


def main():
    # CRITICAL: Disable FedCM to force traditional OAuth popups
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-features=FedCm,FedCmIdpSignin'
    
    app = QApplication(sys.argv)
    app.setApplicationName("Claude Desktop")
    app.setOrganizationName("ClaudeDesktop")
    app.setStyle("Breeze")
    app.setQuitOnLastWindowClosed(False)
    
    window = ClaudeDesktopApp()
    
    settings = QSettings("ClaudeDesktop", "ClaudeLinux")
    if settings.contains("geometry"):
        window.restoreGeometry(settings.value("geometry"))
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
