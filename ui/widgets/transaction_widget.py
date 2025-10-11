from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QComboBox, 
                             QDateEdit, QLineEdit, QHeaderView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor

from config import COLORS, EXPENSE_CATEGORIES, INCOME_CATEGORIES, DATE_FORMAT
from core.database import DatabaseManager
from core.utils import (format_currency, get_today, get_date_range_for_period, 
                        format_display_date)
from datetime import datetime


class TransactionWidget(QWidget):
    """Widget for managing transactions"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.current_filter = "this_month"
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize transaction widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Period filter
        filter_layout.addWidget(QLabel("Period:"))
        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet(self.get_combo_style())
        self.period_combo.addItems(["Today", "This Week", "This Month", "This Year", "Last 30 Days", "Last 90 Days", "Custom"])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        filter_layout.addWidget(self.period_combo)
        
        # Type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.setStyleSheet(self.get_combo_style())
        self.type_combo.addItems(["All", "Income", "Expense"])
        self.type_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_combo)
        
        # Category filter
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self.get_combo_style())
        self.category_combo.addItem("All")
        self.category_combo.addItems(EXPENSE_CATEGORIES + INCOME_CATEGORIES)
        self.category_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.category_combo)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search description...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        self.search_input.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_input, 1)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(self.get_button_style())
        refresh_btn.clicked.connect(self.refresh)
        filter_layout.addWidget(refresh_btn)
        
        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Transaction")
        add_btn.setStyleSheet(self.get_button_style())
        add_btn.clicked.connect(self.open_add_dialog)
        action_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet(self.get_button_style())
        edit_btn.clicked.connect(self.open_edit_dialog)
        action_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet(self.get_button_style())
        delete_btn.setStyleSheet(self.get_button_style(color=COLORS['danger']))
        delete_btn.clicked.connect(self.delete_transaction)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(5)  # id, date, type, category, amount
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Type", "Category", "Amount"])
        self.table.setStyleSheet(self.get_table_style())
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.setColumnHidden(5, True)  # Hide ID column
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh()
    
    def apply_filters(self):
        """Apply all active filters"""
        transactions = self.db.get_all_transactions()
        
        # Filter by type
        type_filter = self.type_combo.currentText()
        if type_filter != "All":
            transactions = [t for t in transactions if t['type'] == type_filter]
        
        # Filter by category
        category_filter = self.category_combo.currentText()
        if category_filter != "All":
            transactions = [t for t in transactions if t['category'] == category_filter]
        
        # Filter by search text
        search_text = self.search_input.text().lower()
        if search_text:
            transactions = [t for t in transactions if search_text in (t['description'] or '').lower()]
        
        self.populate_table(transactions)
    
    def on_period_changed(self):
        """Handle period selection change"""
        if self.period_combo.currentText() != "Custom":
            self.apply_filters()
    
    def populate_table(self, transactions):
        """Populate table with transactions"""
        self.table.setRowCount(0)
        
        for row, transaction in enumerate(transactions):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(transaction['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(transaction['date']))
            self.table.setItem(row, 2, QTableWidgetItem(transaction['type']))
            self.table.setItem(row, 3, QTableWidgetItem(transaction['category']))
            self.table.setItem(row, 4, QTableWidgetItem(str(transaction['amount'])))
    
    def open_add_dialog(self):
        """Open dialog to add new transaction"""
        from ui.dialogs.transaction_dialog import TransactionDialog
        dialog = TransactionDialog(self.db, self.data_changed)
        dialog.exec_()
        self.refresh()
    
    def open_edit_dialog(self):
        """Open dialog to edit selected transaction"""
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_message("Please select a transaction to edit")
            return
        
        transaction_id = int(self.table.item(current_row, 5).text())
        transactions = self.db.get_all_transactions()
        transaction = next((t for t in transactions if t['id'] == transaction_id), None)
        
        if transaction:
            from ui.dialogs.transaction_dialog import TransactionDialog
            dialog = TransactionDialog(self.db, self.data_changed, transaction)
            dialog.exec_()
            self.refresh()
    
    def delete_transaction(self):
        """Delete selected transaction"""
        current_row = self.table.currentRow()
        if current_row < 0:
            self.show_message("Please select a transaction to delete")
            return
        
        transaction_id = int(self.table.item(current_row, 5).text())
        
        from PyQt5.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, "Delete Transaction", 
                                     "Are you sure you want to delete this transaction?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.db.delete_transaction(transaction_id)
            self.data_changed.emit()
            self.refresh()
    
    def refresh(self):
        """Refresh transaction list"""
        self.apply_filters()
    
    def show_message(self, message: str):
        """Show message dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Information", message)
    
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
    
    def get_combo_style(self) -> str:
        """Get combo box stylesheet"""
        return f"""
            QComboBox {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px;
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
    
    def get_table_style(self) -> str:
        """Get table stylesheet"""
        return f"""
            QTableWidget {{
                background-color: {COLORS['card_bg']};
                alternate-background-color: {COLORS['dark_bg']};
                gridline-color: {COLORS['border']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
        """