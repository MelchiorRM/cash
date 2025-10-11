from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox, QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS, DATE_FORMAT, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from core.database import DatabaseManager
from core.utils import get_today, validate_amount
from datetime import datetime


class QuickAddDialog(QDialog):
    """Quick add dialog for fast transaction entry"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize quick add dialog"""
        self.setWindowTitle("Quick Add Transaction")
        self.setGeometry(100, 100, 400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Quick Add Transaction")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Type selection (Expense/Income tabs style)
        type_layout = QHBoxLayout()
        self.expense_btn = QPushButton("Expense")
        self.expense_btn.setFixedHeight(40)
        self.expense_btn.setStyleSheet(self.get_active_button_style())
        self.expense_btn.clicked.connect(self.select_expense)
        
        self.income_btn = QPushButton("Income")
        self.income_btn.setFixedHeight(40)
        self.income_btn.setStyleSheet(self.get_inactive_button_style())
        self.income_btn.clicked.connect(self.select_income)
        
        type_layout.addWidget(self.expense_btn)
        type_layout.addWidget(self.income_btn)
        layout.addLayout(type_layout)
        
        self.current_type = "Expense"
        
        # Category
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(EXPENSE_CATEGORIES)
        cat_layout.addWidget(self.category_combo, 1)
        layout.addLayout(cat_layout)
        
        # Amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount (NT$):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_input, 1)
        layout.addLayout(amount_layout)
        
        # Description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Note (optional):"))
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Add a note...")
        desc_layout.addWidget(self.description_input, 1)
        layout.addLayout(desc_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_btn = QPushButton("➕ Add & Close")
        add_btn.setStyleSheet(self.get_button_style())
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self.add_and_close)
        button_layout.addWidget(add_btn)
        
        add_another_btn = QPushButton("➕ Add & New")
        add_another_btn.setStyleSheet(self.get_button_style(COLORS['secondary']))
        add_another_btn.setFixedHeight(40)
        add_another_btn.clicked.connect(self.add_and_new)
        button_layout.addWidget(add_another_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.amount_input.setFocus()
    
    def select_expense(self):
        """Switch to expense mode"""
        self.current_type = "Expense"
        self.expense_btn.setStyleSheet(self.get_active_button_style())
        self.income_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.category_combo.clear()
        self.category_combo.addItems(EXPENSE_CATEGORIES)
    
    def select_income(self):
        """Switch to income mode"""
        self.current_type = "Income"
        self.income_btn.setStyleSheet(self.get_active_button_style())
        self.expense_btn.setStyleSheet(self.get_inactive_button_style())
        
        self.category_combo.clear()
        self.category_combo.addItems(INCOME_CATEGORIES)
    
    def add_and_close(self):
        """Add transaction and close dialog"""
        if self.save_transaction():
            self.accept()
    
    def add_and_new(self):
        """Add transaction and reset for new entry"""
        if self.save_transaction():
            self.clear_fields()
    
    def save_transaction(self) -> bool:
        """Save transaction and return success status"""
        # Validate
        if not self.amount_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an amount")
            return False
        
        valid, amount = validate_amount(self.amount_input.text())
        if not valid:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount")
            return False
        
        try:
            date_str = get_today()
            category = self.category_combo.currentText()
            description = self.description_input.text()
            
            self.db.add_transaction(date_str, self.current_type, category, amount, description)
            self.data_changed.emit()
            
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save transaction: {str(e)}")
            return False
    
    def clear_fields(self):
        """Clear input fields"""
        self.amount_input.clear()
        self.description_input.clear()
        self.amount_input.setFocus()
    
    def apply_styles(self):
        """Apply stylesheet"""
        stylesheet = f"""
            QDialog {{
                background-color: {COLORS['dark_bg']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
                font-weight: bold;
            }}
            QLineEdit, QComboBox {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['primary']};
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
                font-size: 12px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """
    
    def get_active_button_style(self) -> str:
        """Get active button style"""
        return f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
        """
    
    def get_inactive_button_style(self) -> str:
        """Get inactive button style"""
        return f"""
            QPushButton {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """