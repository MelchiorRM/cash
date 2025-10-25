from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTabWidget, QWidget, QListWidget, QListWidgetItem, QLineEdit,
                             QMessageBox, QScrollArea, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import COLORS, EXPENSE_CATEGORIES, INCOME_CATEGORIES, APP_NAME, APP_VERSION
from core.database import DatabaseManager


class SettingsDialog(QDialog):
    """Settings dialog for application configuration"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize settings dialog"""
        self.setWindowTitle("Settings")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Settings")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(self.get_tab_style())
        
        # Categories tab
        categories_tab = self.create_categories_tab()
        tabs.addTab(categories_tab, "📁 Categories")
        
        # About tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ️ About")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("✓ Close")
        close_btn.setStyleSheet(self.get_button_style())
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_categories_tab(self) -> QWidget:
        """Create categories management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        info_label = QLabel("ℹ️ Note: Category management is view-only in this version.\nDefault categories are defined in config.py")
        info_label.setStyleSheet(f"color: {COLORS['warning']}; padding: 10px; background-color: {COLORS['card_bg']}; border-radius: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Expense categories
        expense_label = QLabel("Expense Categories")
        expense_label.setFont(QFont("Arial", 11, QFont.Bold))
        expense_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(expense_label)
        
        self.expense_list = QListWidget()
        self.expense_list.setStyleSheet(self.get_list_style())
        for cat in EXPENSE_CATEGORIES:
            self.expense_list.addItem(cat)
        self.expense_list.setMaximumHeight(150)
        layout.addWidget(self.expense_list)
        
        layout.addSpacing(20)
        
        # Income categories
        income_label = QLabel("Income Categories")
        income_label.setFont(QFont("Arial", 11, QFont.Bold))
        income_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(income_label)
        
        self.income_list = QListWidget()
        self.income_list.setStyleSheet(self.get_list_style())
        for cat in INCOME_CATEGORIES:
            self.income_list.addItem(cat)
        self.income_list.setMaximumHeight(100)
        layout.addWidget(self.income_list)
        
        layout.addStretch()
        
        # Instructions
        instructions = QLabel(
            "💡 To modify categories:\n"
            "1. Open config.py in a text editor\n"
            "2. Edit EXPENSE_CATEGORIES or INCOME_CATEGORIES lists\n"
            "3. Restart the application"
        )
        instructions.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px; padding: 10px;")
        layout.addWidget(instructions)
        
        widget.setLayout(layout)
        return widget
    
    def create_about_tab(self) -> QWidget:
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        about_text = QLabel(
            f"<h2>{APP_NAME}</h2>"
            f"<p><b>Version:</b> {APP_VERSION}</p><br>"
            f"<p>A beautiful personal finance tracker built with PyQt5.</p><br>"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Transaction management with filtering</li>"
            f"<li>Budget tracking with alerts</li>"
            f"<li>Savings goals with progress tracking</li>"
            f"<li>Interactive expense pie chart</li>"
            f"<li>Monthly financial summaries</li>"
            f"</ul><br>"
            f"<p><b>Configuration:</b></p>"
            f"<ul>"
            f"<li>Currency: Taiwan NTD (NT$)</li>"
            f"<li>Theme: Dark Mode</li>"
            f"<li>Database: SQLite (Local)</li>"
            f"</ul><br>"
            f"<p style='color: {COLORS['text_secondary']}; font-size: 10px;'>"
            f"All data is stored locally in SQLite database.<br>"
            f"Your financial information never leaves your computer."
            f"</p>"
        )
        about_text.setStyleSheet(f"color: {COLORS['text_primary']};")
        about_text.setWordWrap(True)
        about_text.setTextFormat(Qt.RichText)
        layout.addWidget(about_text)
        
        layout.addStretch()
        
        # System info
        import sys
        import platform
        system_info = QLabel(
            f"<p style='color: {COLORS['text_secondary']}; font-size: 9px;'>"
            f"<b>System Information:</b><br>"
            f"Python: {sys.version.split()[0]}<br>"
            f"Platform: {platform.system()} {platform.release()}<br>"
            f"Database: {self.db.db_path}"
            f"</p>"
        )
        system_info.setWordWrap(True)
        system_info.setTextFormat(Qt.RichText)
        layout.addWidget(system_info)
        
        widget.setLayout(layout)
        return widget
    
    def apply_styles(self):
        """Apply stylesheet"""
        stylesheet = f"""
            QDialog {{
                background-color: {COLORS['dark_bg']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QListWidget {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['border']};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def get_button_style(self, color=None) -> str:
        """Get button stylesheet"""
        if color is None:
            color = COLORS['primary']
        return f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """
    
    def get_tab_style(self) -> str:
        """Get tab stylesheet"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['dark_bg']};
            }}
            QTabBar::tab {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_secondary']};
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
        """
    
    def get_list_style(self) -> str:
        """Get list widget stylesheet"""
        return f"""
            QListWidget {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['border']};
            }}
        """  