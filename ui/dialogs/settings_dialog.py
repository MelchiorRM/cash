from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTabWidget, QWidget, QListWidget, QListWidgetItem, QLineEdit,
                             QMessageBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import COLORS, EXPENSE_CATEGORIES, INCOME_CATEGORIES
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
        
        # Expense categories
        expense_label = QLabel("Expense Categories")
        expense_label.setFont(QFont("Arial", 11, QFont.Bold))
        expense_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(expense_label)
        
        expense_layout = QHBoxLayout()
        self.expense_list = QListWidget()
        self.expense_list.setStyleSheet(self.get_list_style())
        for cat in EXPENSE_CATEGORIES:
            self.expense_list.addItem(cat)
        expense_layout.addWidget(self.expense_list, 1)
        
        expense_button_layout = QVBoxLayout()
        add_expense_btn = QPushButton("➕ Add")
        add_expense_btn.setStyleSheet(self.get_small_button_style())
        add_expense_btn.clicked.connect(lambda: self.add_category("Expense"))
        expense_button_layout.addWidget(add_expense_btn)
        
        remove_expense_btn = QPushButton("🗑️ Remove")
        remove_expense_btn.setStyleSheet(self.get_small_button_style(COLORS['danger']))
        remove_expense_btn.clicked.connect(lambda: self.remove_category("Expense", self.expense_list))
        expense_button_layout.addWidget(remove_expense_btn)
        expense_button_layout.addStretch()
        
        expense_layout.addLayout(expense_button_layout)
        layout.addLayout(expense_layout)
        
        layout.addSpacing(20)
        
        # Income categories
        income_label = QLabel("Income Categories")
        income_label.setFont(QFont("Arial", 11, QFont.Bold))
        income_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(income_label)
        
        income_layout = QHBoxLayout()
        self.income_list = QListWidget()
        self.income_list.setStyleSheet(self.get_list_style())
        for cat in INCOME_CATEGORIES:
            self.income_list.addItem(cat)
        income_layout.addWidget(self.income_list, 1)
        
        income_button_layout = QVBoxLayout()
        add_income_btn = QPushButton("➕ Add")
        add_income_btn.setStyleSheet(self.get_small_button_style())
        add_income_btn.clicked.connect(lambda: self.add_category("Income"))
        income_button_layout.addWidget(add_income_btn)
        
        remove_income_btn = QPushButton("🗑️ Remove")
        remove_income_btn.setStyleSheet(self.get_small_button_style(COLORS['danger']))
        remove_income_btn.clicked.connect(lambda: self.remove_category("Income", self.income_list))
        income_button_layout.addWidget(remove_income_btn)
        income_button_layout.addStretch()
        
        income_layout.addLayout(income_button_layout)
        layout.addLayout(income_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_about_tab(self) -> QWidget:
        """Create about tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        from config import APP_NAME, APP_VERSION
        
        about_text = QLabel(
            f"<b>{APP_NAME}</b><br>"
            f"Version: {APP_VERSION}<br><br>"
            f"A beautiful personal finance tracker built with PyQt5.<br><br>"
            f"<b>Features:</b><br>"
            f"• Transaction management<br>"
            f"• Budget tracking<br>"
            f"• Savings goals<br>"
            f"• Financial charts and analytics<br><br>"
            f"<b>Currency:</b> Taiwan NTD (NT$)<br>"
            f"<b>Theme:</b> Dark Mode<br><br>"
            f"All data is stored locally in SQLite database."
        )
        about_text.setStyleSheet(f"color: {COLORS['text_secondary']}; line-height: 1.6;")
        about_text.setWordWrap(True)
        layout.addWidget(about_text)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def add_category(self, category_type: str):
        """Add a new category"""
        text, ok = self.get_text_input(f"Add {category_type} Category", "Category Name:")
        if ok and text:
            text = text.strip()
            if category_type == "Expense":
                if text in EXPENSE_CATEGORIES:
                    self.show_message("Category already exists.", "Error")
                    return
                EXPENSE_CATEGORIES.append(text)
                self.expense_list.addItem(text)
            else:
                if text in INCOME_CATEGORIES:
                    self.show_message("Category already exists.", "Error")
                    return
                INCOME_CATEGORIES.append(text)
                self.income_list.addItem(text)
            self.db.update_categories(EXPENSE_CATEGORIES, INCOME_CATEGORIES)
            self.show_message("Category added successfully.", "Success")

    def remove_category(self, category_type: str, list_widget: QListWidget):
        """Remove selected category"""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            self.show_message("Please select a category to remove.", "Error")
            return
        for item in selected_items:
            category = item.text()
            if category_type == "Expense":
                EXPENSE_CATEGORIES.remove(category)
            else:
                INCOME_CATEGORIES.remove(category)
            list_widget.takeItem(list_widget.row(item))
        self.db.update_categories(EXPENSE_CATEGORIES, INCOME_CATEGORIES)
        self.show_message("Category removed successfully.", "Success")