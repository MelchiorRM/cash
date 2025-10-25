from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QGridLayout, QProgressBar, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from config import COLORS, EXPENSE_CATEGORIES
from core.database import DatabaseManager
from core.utils import format_currency, get_current_month_year


class BudgetWidget(QWidget):
    """Widget for managing budgets"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        
        self.init_ui()
        self.data_changed.connect(self.refresh)
    
    def init_ui(self):
        """Initialize budget widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header with add button
        header_layout = QHBoxLayout()
        title = QLabel("Monthly Budgets")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        add_btn = QPushButton("➕ Add Budget")
        add_btn.setStyleSheet(self.get_button_style())
        add_btn.clicked.connect(self.open_add_dialog)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Scrollable budget list
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
        """Open dialog to add budget"""
        from ui.dialogs.budget_dialog import BudgetDialog
        dialog = BudgetDialog(self.db, self.data_changed)
        dialog.exec_()
        self.refresh()
    
    def open_edit_dialog(self, budget_id: int, category: str, limit_amount: float):
        """Open dialog to edit budget"""
        from ui.dialogs.budget_dialog import BudgetDialog
        budget = {'id': budget_id, 'category': category, 'limit_amount': limit_amount}
        dialog = BudgetDialog(self.db, self.data_changed, budget)
        dialog.exec_()
        self.refresh()
    
    def delete_budget(self, budget_id: int):
        """Delete a budget"""
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Delete Budget", 
                                     "Are you sure you want to delete this budget?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete_budget(budget_id)
            self.data_changed.emit()
            self.refresh()
    
    def refresh(self):
        """Refresh budget list"""
        # Clear existing items
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget is not None:
                widget.deleteLater()
        
        year, month = get_current_month_year()
        budget_status = self.db.get_budget_status(year, month)
        
        if not budget_status:
            no_budget_label = QLabel("No budgets set. Create one to get started!")
            no_budget_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
            self.scroll_layout.addWidget(no_budget_label)
            self.scroll_layout.addStretch()
            return
        
        for budget in budget_status:
            card = self.create_budget_card(budget)
            self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()
    
    def create_budget_card(self, budget: dict) -> QFrame:
        """Create a budget card widget"""
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
        
        # Header: Category and percentage
        header_layout = QHBoxLayout()
        
        category_label = QLabel(budget['category'])
        category_label.setFont(QFont("Arial", 12, QFont.Bold))
        category_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        spent = budget['spent']
        limit = budget['limit_amount']
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        percentage_label = QLabel(f"{percentage:.0f}%")
        percentage_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        if percentage >= 100:
            percentage_label.setStyleSheet(f"color: {COLORS['danger']};")
        elif percentage >= 80:
            percentage_label.setStyleSheet(f"color: {COLORS['warning']};")
        else:
            percentage_label.setStyleSheet(f"color: {COLORS['success']};")
        
        header_layout.addWidget(category_label)
        header_layout.addStretch()
        header_layout.addWidget(percentage_label)
        layout.addLayout(header_layout)
        
        # Progress bar - NO TEXT INSIDE
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(min(int(percentage), 100))
        progress.setFixedHeight(10)
        progress.setTextVisible(False)  # HIDE TEXT INSIDE BAR
        
        if percentage >= 100:
            color = COLORS['danger']
        elif percentage >= 80:
            color = COLORS['warning']
        else:
            color = COLORS['success']
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['dark_bg']};
                border: none;
                border-radius: 5px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)
        layout.addWidget(progress)
        
        # Amount details
        amount_layout = QHBoxLayout()
        amount_label = QLabel(f"{format_currency(spent)} / {format_currency(limit)}")
        amount_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        amount_label.setFont(QFont("Arial", 10))
        
        remaining = limit - spent
        if remaining >= 0:
            remaining_label = QLabel(f"Remaining: {format_currency(remaining)}")
            remaining_label.setStyleSheet(f"color: {COLORS['success']};")
        else:
            remaining_label = QLabel(f"Over by: {format_currency(abs(remaining))}")
            remaining_label.setStyleSheet(f"color: {COLORS['danger']};")
        remaining_label.setFont(QFont("Arial", 10))
        
        amount_layout.addWidget(amount_label)
        amount_layout.addStretch()
        amount_layout.addWidget(remaining_label)
        layout.addLayout(amount_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet(self.get_small_button_style())
        edit_btn.clicked.connect(lambda: self.open_edit_dialog(
            budget['id'], budget['category'], budget['limit_amount']
        ))
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setStyleSheet(self.get_small_button_style(COLORS['danger']))
        delete_btn.clicked.connect(lambda: self.delete_budget(budget['id']))
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        card.setLayout(layout)
        return card
    
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