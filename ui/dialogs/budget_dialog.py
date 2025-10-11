from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QComboBox, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS, EXPENSE_CATEGORIES
from core.database import DatabaseManager
from core.utils import validate_amount


class BudgetDialog(QDialog):
    """Dialog for adding/editing budgets"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal, budget=None):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.budget = budget
        self.is_edit = budget is not None
        
        self.init_ui()
        self.apply_styles()
        
        if self.is_edit:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Budget" if self.is_edit else "Add Budget")
        self.setGeometry(100, 100, 450, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Set Budget" if not self.is_edit else "Edit Budget")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(EXPENSE_CATEGORIES)
        self.category_combo.setEnabled(not self.is_edit)
        category_layout.addWidget(self.category_combo, 1)
        layout.addLayout(category_layout)
        
        # Limit amount
        limit_layout = QHBoxLayout()
        limit_layout.addWidget(QLabel("Monthly Limit (NT$):"))
        self.limit_input = QLineEdit()
        self.limit_input.setPlaceholderText("0.00")
        limit_layout.addWidget(self.limit_input, 1)
        layout.addLayout(limit_layout)
        
        # Info text
        info_label = QLabel(
            "💡 Set a realistic monthly limit for this category.\n"
            "You'll receive alerts at 80% and 100% usage."
        )
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px;")
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(self.get_button_style())
        save_btn.clicked.connect(self.save_budget)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.get_button_style(COLORS['secondary']))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with budget data for editing"""
        self.category_combo.setCurrentText(self.budget['category'])
        self.limit_input.setText(str(self.budget['limit_amount']))
    
    def save_budget(self):
        """Save budget to database"""
        # Validate inputs
        if not self.limit_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a limit amount")
            return
        
        valid, amount = validate_amount(self.limit_input.text())
        if not valid:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount")
            return
        
        try:
            category = self.category_combo.currentText()
            self.db.add_budget(category, amount)
            
            self.data_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save budget: {str(e)}")
    
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
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """