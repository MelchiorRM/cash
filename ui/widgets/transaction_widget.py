from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                             QFrame, QTableWidget, QTableWidgetItem, QComboBox, 
                             QDateEdit, QLineEdit, QHeaderView, QMessageBox)
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
        self.current_transactions = []
        
        self.init_ui()
        self.data_changed.connect(self.refresh)
    
    def init_ui(self):
        """Initialize transaction widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Transactions")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
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
        self.period_combo.addItems(["Today", "This Week", "This Month", "This Year", "Last 30 Days", "Last 90 Days"])
        self.period_combo.setCurrentText("This Month")
        self.period_combo.currentTextChanged.connect(self.apply_filters)
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
        
        filter_layout.addStretch()
        
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
        delete_btn.setStyleSheet(self.get_button_style(color=COLORS['danger']))
        delete_btn.clicked.connect(self.delete_transaction)
        action_layout.addWidget(delete_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # id (hidden), date, type, category, amount, description
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Type", "Category", "Amount", "Description"])
        self.table.setStyleSheet(self.get_table_style())
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Category
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(5, QHeaderView.Stretch)  # Description
        
        self.table.setColumnWidth(0, 50)
        self.table.setColumnHidden(0, True)  # Hide ID column
        
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.refresh()
    
    def apply_filters(self):
        """Apply all active filters"""
        # Get period dates
        period_text = self.period_combo.currentText()
        period_map = {
            "Today": "today",
            "This Week": "this_week",
            "This Month": "this_month",
            "This Year": "this_year",
            "Last 30 Days": "last_30_days",
            "Last 90 Days": "last_90_days"
        }
        period = period_map.get(period_text, "this_month")
        start_date, end_date = get_date_range_for_period(period)
        
        # Get transactions with date filter
        transactions = self.db.get_all_transactions(start_date=start_date, end_date=end_date)
        
        # Filter by type
        type_filter = self.type_combo.currentText()
        if type_filter != "All":
            transactions = [t for t in transactions if t['type'] == type_filter]
        
        # Filter by category
        category_filter = self.category_combo.currentText()
        if category_filter != "All":
            transactions = [t for t in transactions if t['category'] == category_filter]
        
        self.current_transactions = transactions
        self.populate_table(transactions)
    
    def populate_table(self, transactions):
        """Populate table with transactions"""
        self.table.setRowCount(0)
        
        for row, transaction in enumerate(transactions):
            self.table.insertRow(row)
            
            # ID (hidden)
            id_item = QTableWidgetItem(str(transaction['id']))
            self.table.setItem(row, 0, id_item)
            
            # Date
            date_item = QTableWidgetItem(format_display_date(transaction['date']))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, date_item)
            
            # Type with color coding
            type_item = QTableWidgetItem(transaction['type'])
            type_item.setTextAlignment(Qt.AlignCenter)
            if transaction['type'] == 'Income':
                type_item.setForeground(QColor(COLORS['success']))
            else:
                type_item.setForeground(QColor(COLORS['danger']))
            self.table.setItem(row, 2, type_item)
            
            # Category
            category_item = QTableWidgetItem(transaction['category'])
            category_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, category_item)
            
            # Amount with formatting
            amount_str = format_currency(transaction['amount'])
            amount_item = QTableWidgetItem(amount_str)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if transaction['type'] == 'Income':
                amount_item.setForeground(QColor(COLORS['success']))
            else:
                amount_item.setForeground(QColor(COLORS['danger']))
            self.table.setItem(row, 4, amount_item)
            
            # Description
            desc = transaction.get('description', '') or ''
            desc_item = QTableWidgetItem(desc[:50] + '...' if len(desc) > 50 else desc)
            self.table.setItem(row, 5, desc_item)
        
        # Update row heights
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 40)
    
    def open_add_dialog(self):
        """Open dialog to add new transaction"""
        from ui.dialogs.transaction_dialog import TransactionDialog
        dialog = TransactionDialog(self.db, self.data_changed)
        dialog.exec_()
    
    def open_edit_dialog(self):
        """Open dialog to edit selected transaction"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to edit")
            return
        
        transaction_id = int(self.table.item(current_row, 0).text())
        transaction = next((t for t in self.current_transactions if t['id'] == transaction_id), None)
        
        if transaction:
            from ui.dialogs.transaction_dialog import TransactionDialog
            dialog = TransactionDialog(self.db, self.data_changed, transaction)
            dialog.exec_()
    
    def delete_transaction(self):
        """Delete selected transaction"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a transaction to delete")
            return
        
        transaction_id = int(self.table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self, "Delete Transaction", 
            "Are you sure you want to delete this transaction?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.db.delete_transaction(transaction_id)
            self.data_changed.emit()
    
    def refresh(self):
        """Refresh transaction list"""
        self.apply_filters()
    
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
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.7;
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
                min-width: 100px;
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
                color: {COLORS['text_primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                padding: 10px;
                border: none;
                font-weight: bold;
                font-size: 10px;
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
        """