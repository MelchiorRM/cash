from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QProgressBar, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from config import COLORS
from core.database import DatabaseManager
from core.utils import format_currency, calculate_days_until_deadline, format_display_date


class SavingsWidget(QWidget):
    """Widget for managing savings goals"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        
        self.init_ui()
        self.data_changed.connect(self.refresh)
    
    def init_ui(self):
        """Initialize savings widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with add button
        header_layout = QHBoxLayout()
        title = QLabel("Savings Goals")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Add Goal")
        add_btn.setStyleSheet(self.get_button_style())
        add_btn.clicked.connect(self.open_add_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Scrollable goals list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(15)
        
        scroll_widget.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['dark_bg']};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {COLORS['card_bg']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['border']};
                border-radius: 6px;
            }}
        """)
        
        layout.addWidget(scroll)
        self.setLayout(layout)
        self.refresh()
    
    def open_add_dialog(self):
        """Open dialog to add savings goal"""
        from ui.dialogs.savings_dialog import SavingsDialog
        dialog = SavingsDialog(self.db, self.data_changed)
        dialog.exec_()
        self.refresh()
    
    def open_edit_dialog(self, goal):
        """Open dialog to edit savings goal"""
        from ui.dialogs.savings_dialog import SavingsDialog
        dialog = SavingsDialog(self.db, self.data_changed, goal)
        dialog.exec_()
        self.refresh()
    
    def delete_goal(self, goal_id: int):
        """Delete a savings goal"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Delete Goal", 
                                     "Are you sure you want to delete this goal?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_savings_goal(goal_id)
            self.data_changed.emit()
            self.refresh()
    
    def refresh(self):
        """Refresh goals list"""
        # Clear existing items
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget is not None:
                widget.deleteLater()
        
        goals = self.db.get_all_savings_goals()
        
        if not goals:
            no_goals_label = QLabel("No savings goals yet. Create one to get started!")
            no_goals_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            self.scroll_layout.addWidget(no_goals_label)
            self.scroll_layout.addStretch()
            return
        
        for goal in goals:
            card = self.create_goal_card(goal)
            self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()
    
    def create_goal_card(self, goal: dict) -> QFrame:
        """Create a savings goal card widget"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Header: Goal name and status
        header_layout = QHBoxLayout()
        
        name_label = QLabel(goal['name'])
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        # Status badge
        current = goal['current_amount']
        target = goal['target_amount']
        percentage = min((current / target * 100) if target > 0 else 0, 100)
        
        if current >= target:
            status_label = QLabel("✓ Completed")
            status_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
        else:
            status_label = QLabel(f"{percentage:.0f}% Complete")
            status_label.setStyleSheet(f"color: {COLORS['primary']}; font-weight: bold;")
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(status_label)
        layout.addLayout(header_layout)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(int(percentage))
        progress.setFixedHeight(8)
        
        color = COLORS['success'] if current >= target else COLORS['primary']
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['dark_bg']};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        layout.addWidget(progress)
        
        # Amount and deadline
        amount_layout = QHBoxLayout()
        amount_label = QLabel(f"{format_currency(current)} / {format_currency(target)}")
        amount_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        amount_label.setFont(QFont("Arial", 10))
        
        deadline_label = QLabel(f"Due: {format_display_date(goal['deadline'])}")
        deadline_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        deadline_label.setFont(QFont("Arial", 10))
        
        amount_layout.addWidget(amount_label)
        amount_layout.addStretch()
        amount_layout.addWidget(deadline_label)
        layout.addLayout(amount_layout)
        
        # Remaining and days left
        remaining = target - current
        days_left = calculate_days_until_deadline(goal['deadline'])
        
        remaining_layout = QHBoxLayout()
        
        if remaining > 0:
            remaining_label = QLabel(f"Need: {format_currency(remaining)}")
            remaining_label.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            remaining_label = QLabel("Goal achieved! 🎉")
            remaining_label.setStyleSheet(f"color: {COLORS['success']};")
        
        days_label = QLabel(f"{days_left} days left")
        days_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 9px;")
        
        remaining_layout.addWidget(remaining_label)
        remaining_layout.addStretch()
        remaining_layout.addWidget(days_label)
        layout.addLayout(remaining_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_money_btn = QPushButton("➕ Add Money")
        add_money_btn.setStyleSheet(self.get_small_button_style())
        add_money_btn.clicked.connect(lambda: self.add_money_to_goal(goal))
        button_layout.addWidget(add_money_btn)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet(self.get_small_button_style())
        edit_btn.clicked.connect(lambda: self.open_edit_dialog(goal))
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet(self.get_small_button_style(COLORS['danger']))
        delete_btn.clicked.connect(lambda: self.delete_goal(goal['id']))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        card.setLayout(layout)
        return card
    
    def add_money_to_goal(self, goal: dict):
        """Open dialog to add money to goal"""
        from ui.dialogs.add_money_dialog import AddMoneyDialog
        dialog = AddMoneyDialog(self.db, self.data_changed, goal)
        dialog.exec_()
        self.refresh()
    
    def get_button_style(self, color: str = None) -> str:
        """Get button stylesheet"""
        if color is None:
            color = COLORS['primary']
        return f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """
    
    def get_small_button_style(self, color: str = None) -> str:
        """Get small button stylesheet"""
        if color is None:
            color = COLORS['primary']
        return f"""
            QPushButton {{
                background-color: {color};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
        """