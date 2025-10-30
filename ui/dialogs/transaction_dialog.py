from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QDateEdit, QTextEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS, DATE_FORMAT, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from core.database import DatabaseManager
from core.utils import get_today, validate_amount
from datetime import datetime


class TransactionDialog(QDialog):
    """Dialog for adding/editing transactions"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal, transaction=None):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.transaction = transaction
        self.is_edit = transaction is not None
        
        self.init_ui()
        self.apply_styles()
        
        if self.is_edit:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Transaction" if self.is_edit else "Add Transaction")
        self.setGeometry(100, 100, 500, 450)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Edit Transaction" if self.is_edit else "Add Transaction")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Type selection
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Expense", "Income"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo, 1)
        layout.addLayout(type_layout)
        
        # Date
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addWidget(self.date_edit, 1)
        layout.addLayout(date_layout)
        
        # Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(EXPENSE_CATEGORIES)
        category_layout.addWidget(self.category_combo, 1)
        layout.addLayout(category_layout)
        
        # Amount
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount (NT$):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        amount_layout.addWidget(self.amount_input, 1)
        layout.addLayout(amount_layout)
        
        # Description
        desc_label = QLabel("Description (optional):")
        layout.addWidget(desc_label)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Add notes about this transaction...")
        self.description_input.setFixedHeight(100)
        layout.addWidget(self.description_input)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(self.get_button_style())
        save_btn.clicked.connect(self.save_transaction)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.get_button_style(COLORS['secondary']))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.amount_input.setFocus()
    
    def on_type_changed(self):
        """Update categories when type changes"""
        type_name = self.type_combo.currentText()
        categories = INCOME_CATEGORIES if type_name == "Income" else EXPENSE_CATEGORIES
        
        current = self.category_combo.currentText()
        self.category_combo.clear()
        self.category_combo.addItems(categories)
        
        if current in categories:
            self.category_combo.setCurrentText(current)
    
    def populate_fields(self):
        """Populate fields with transaction data for editing"""
        self.type_combo.setCurrentText(self.transaction['type'])
        self.date_edit.setDate(QDate.fromString(self.transaction['date'], DATE_FORMAT))
        self.category_combo.setCurrentText(self.transaction['category'])
        self.amount_input.setText(str(self.transaction['amount']))
        
        # Handle description - might be None
        description = self.transaction.get('description', '')
        if description:
            self.description_input.setText(description)
    
    def save_transaction(self):
        """Save transaction to database"""
        # Validate inputs
        if not self.amount_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an amount")
            return
        
        valid, amount = validate_amount(self.amount_input.text())
        if not valid:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount (numbers only)")
            return
        
        date_str = self.date_edit.date().toString(DATE_FORMAT)
        type_name = self.type_combo.currentText()
        category = self.category_combo.currentText()
        description = self.description_input.toPlainText().strip()
        
        try:
            if self.is_edit:
                self.db.update_transaction(
                    self.transaction['id'], date_str, type_name, 
                    category, amount, description
                )
                QMessageBox.information(self, "Success", "Transaction updated successfully!")
            else:
                self.db.add_transaction(date_str, type_name, category, amount, description)
                QMessageBox.information(self, "Success", "Transaction added successfully!")
            
            self.data_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save transaction:\n{str(e)}")
            print(f"Database error: {e}")  # Debug info
    
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
            QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                selection-background-color: {COLORS['primary']};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
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
            QCalendarWidget {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['card_bg']};
            }}
            QCalendarWidget QMenu {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
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