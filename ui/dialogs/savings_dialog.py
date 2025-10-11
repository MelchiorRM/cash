from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QDateEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS, DATE_FORMAT
from core.database import DatabaseManager
from core.utils import validate_amount, get_today
from datetime import datetime


class SavingsDialog(QDialog):
    """Dialog for adding/editing savings goals"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal, goal=None):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.goal = goal
        self.is_edit = goal is not None
        
        self.init_ui()
        self.apply_styles()
        
        if self.is_edit:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Goal" if self.is_edit else "Create Savings Goal")
        self.setGeometry(100, 100, 450, 350)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Savings Goal" if not self.is_edit else "Edit Goal")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Goal name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Goal Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Summer Vacation")
        name_layout.addWidget(self.name_input, 1)
        layout.addLayout(name_layout)
        
        # Target amount
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Target Amount (NT$):"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("0.00")
        target_layout.addWidget(self.target_input, 1)
        layout.addLayout(target_layout)
        
        # Current amount (read-only for new goals)
        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current Amount (NT$):"))
        self.current_input = QLineEdit()
        self.current_input.setPlaceholderText("0.00")
        if not self.is_edit:
            self.current_input.setText("0.00")
            self.current_input.setReadOnly(True)
        current_layout.addWidget(self.current_input, 1)
        layout.addLayout(current_layout)
        
        # Deadline
        deadline_layout = QHBoxLayout()
        deadline_layout.addWidget(QLabel("Deadline:"))
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setDate(QDate.currentDate().addMonths(3))
        self.deadline_edit.setCalendarPopup(True)
        deadline_layout.addWidget(self.deadline_edit, 1)
        layout.addLayout(deadline_layout)
        
        # Info text
        info_label = QLabel(
            "💡 Set a realistic target amount and deadline.\n"
            "You can add money to your goal anytime."
        )
        info_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10px;")
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save")
        save_btn.setStyleSheet(self.get_button_style())
        save_btn.clicked.connect(self.save_goal)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(self.get_button_style(COLORS['secondary']))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def populate_fields(self):
        """Populate fields with goal data for editing"""
        self.name_input.setText(self.goal['name'])
        self.target_input.setText(str(self.goal['target_amount']))
        self.current_input.setText(str(self.goal['current_amount']))
        self.deadline_edit.setDate(QDate.fromString(self.goal['deadline'], DATE_FORMAT))
    
    def save_goal(self):
        """Save goal to database"""
        # Validate inputs
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a goal name")
            return
        
        if not self.target_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a target amount")
            return
        
        valid, target_amount = validate_amount(self.target_input.text())
        if not valid:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid target amount")
            return
        
        if self.is_edit:
            if not self.current_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter current amount")
                return
            
            valid, current_amount = validate_amount(self.current_input.text())
            if not valid:
                QMessageBox.warning(self, "Validation Error", "Please enter a valid current amount")
                return
        else:
            current_amount = 0.0
        
        try:
            name = self.name_input.text()
            deadline = self.deadline_edit.date().toString(DATE_FORMAT)
            
            if self.is_edit:
                self.db.update_savings_goal_amount(self.goal['id'], current_amount)
                # Note: In a full implementation, you'd also update name and deadline
            else:
                self.db.add_savings_goal(name, target_amount, deadline)
            
            self.data_changed.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save goal: {str(e)}")
    
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
            QLineEdit, QDateEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus, QDateEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QCalendarWidget {{
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