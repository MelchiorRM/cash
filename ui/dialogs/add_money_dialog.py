from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS
from core.database import DatabaseManager
from core.utils import validate_amount, format_currency


class AddMoneyDialog(QDialog):
    """Dialog for adding money to a savings goal"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal, goal: dict):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.goal = goal
        
        self.init_ui()
        self.apply_styles()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Add Money to Goal")
        self.setGeometry(100, 100, 450, 300)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Add Money to Savings Goal")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Goal information
        info_frame = self.create_info_frame()
        layout.addWidget(info_frame)
        
        # Amount input
        amount_layout = QHBoxLayout()
        amount_layout.addWidget(QLabel("Amount to Add (NT$):"))
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("0.00")
        self.amount_input.textChanged.connect(self.update_preview)
        amount_layout.addWidget(self.amount_input, 1)
        layout.addLayout(amount_layout)
        
        # Preview of new amount
        self.preview_label = QLabel("")
        self.preview_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic;")
        layout.addWidget(self.preview_label)
        
        # Progress bar preview
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        layout.addWidget(self.progress_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💰 Add Money")
        save_btn.setStyleSheet(self.get_button_style())
        save_btn.clicked.connect(self.add_money)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.get_button_style(COLORS['secondary']))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        self.amount_input.setFocus()
    
    def create_info_frame(self):
        """Create information frame showing goal details"""
        frame = QLabel()
        frame.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        
        current = self.goal['current_amount']
        target = self.goal['target_amount']
        remaining = target - current
        percentage = (current / target * 100) if target > 0 else 0
        
        info_text = f"""
<b>Goal:</b> {self.goal['name']}<br>
<b>Target:</b> {format_currency(target)}<br>
<b>Current:</b> {format_currency(current)}<br>
<b>Remaining:</b> {format_currency(remaining)}<br>
<b>Progress:</b> {percentage:.1f}%
        """
        
        frame.setText(info_text)
        frame.setWordWrap(True)
        frame.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
                color: {COLORS['text_primary']};
                font-size: 11px;
            }}
        """)
        
        return frame
    
    def update_preview(self):
        """Update preview of new amount and progress"""
        text = self.amount_input.text().strip()
        if not text:
            self.preview_label.setText("")
            self.progress_label.setText("")
            return
        
        valid, amount = validate_amount(text)
        if not valid:
            self.preview_label.setText("⚠️ Invalid amount")
            self.preview_label.setStyleSheet(f"color: {COLORS['danger']}; font-style: italic;")
            self.progress_label.setText("")
            return
        
        current = self.goal['current_amount']
        target = self.goal['target_amount']
        new_amount = current + amount
        new_percentage = (new_amount / target * 100) if target > 0 else 0
        
        # Preview text
        preview_text = f"New total: {format_currency(new_amount)}"
        self.preview_label.setText(preview_text)
        self.preview_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic;")
        
        # Progress text
        if new_amount >= target:
            progress_text = f"✅ Goal will be completed! ({new_percentage:.1f}%)"
            color = COLORS['success']
        else:
            remaining = target - new_amount
            progress_text = f"Progress: {new_percentage:.1f}% (Need {format_currency(remaining)} more)"
            color = COLORS['primary']
        
        self.progress_label.setText(progress_text)
        self.progress_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def add_money(self):
        """Add money to savings goal"""
        # Validate input
        if not self.amount_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter an amount")
            return
        
        valid, amount = validate_amount(self.amount_input.text())
        if not valid:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid amount")
            return
        
        if amount <= 0:
            QMessageBox.warning(self, "Validation Error", "Amount must be greater than zero")
            return
        
        try:
            new_amount = self.goal['current_amount'] + amount
            self.db.update_savings_goal_amount(self.goal['id'], new_amount)
            
            # Check if goal is completed
            if new_amount >= self.goal['target_amount']:
                QMessageBox.information(
                    self, 
                    "Goal Completed! 🎉", 
                    f"Congratulations! You've reached your savings goal for '{self.goal['name']}'!"
                )
            
            self.data_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add money: {str(e)}")
    
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
            QLineEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
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