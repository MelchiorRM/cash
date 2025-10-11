import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTabWidget, QLabel, QFrame, QScrollArea,
                             QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor
from datetime import datetime

from config import (APP_NAME, APP_VERSION, WINDOW_WIDTH, WINDOW_HEIGHT, 
                   MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT, COLORS)
from core.database import DatabaseManager
from core.utils import get_today, get_current_month_year, format_currency, calculate_budget_alerts
from ui.charts.charts_manager import ChartsManager


class MainWindow(QMainWindow):
    """Main application window"""
    
    data_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Initialize managers
        self.db = DatabaseManager()
        self.charts_manager = ChartsManager()
        
        # Setup UI
        self.init_ui()
        self.apply_styles()
        
        # Connect signals
        self.data_changed.connect(self.refresh_all)
        
        # Auto-refresh timer (every 5 seconds)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.start(5000)
    
    def init_ui(self):
        """Initialize user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main content with tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(self.get_tab_stylesheet())
        
        from ui.widgets.dashboard_widget import DashboardWidget
        from ui.widgets.transaction_widget import TransactionWidget
        from ui.widgets.budget_widget import BudgetWidget
        from ui.widgets.savings_widget import SavingsWidget
        from ui.charts.charts_w import ChartsWidget
        
        self.dashboard_widget = DashboardWidget(self.db, self.data_changed)
        self.transaction_widget = TransactionWidget(self.db, self.data_changed)
        self.budget_widget = BudgetWidget(self.db, self.data_changed)
        self.savings_widget = SavingsWidget(self.db, self.data_changed)
        self.charts_widget = ChartsWidget(self.db)
        
        tabs.addTab(self.dashboard_widget, "📊 Dashboard")
        tabs.addTab(self.transaction_widget, "💸 Transactions")
        tabs.addTab(self.budget_widget, "💰 Budgets")
        tabs.addTab(self.savings_widget, "🎯 Savings")
        tabs.addTab(self.charts_widget, "📈 Charts")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def create_header(self) -> QWidget:
        """Create top header with app title and controls"""
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        header.setFixedHeight(60)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # App title
        title = QLabel(f"{APP_NAME}")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Version
        version = QLabel(f"v{APP_VERSION}")
        version.setFont(QFont("Arial", 9))
        version.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(version)
        
        layout.addStretch()
        
        # Quick add button
        quick_add_btn = QPushButton("➕ Quick Add")
        quick_add_btn.setStyleSheet(self.get_button_stylesheet())
        quick_add_btn.setFixedHeight(40)
        quick_add_btn.clicked.connect(self.open_quick_add)
        layout.addWidget(quick_add_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setStyleSheet(self.get_button_stylesheet())
        settings_btn.setFixedHeight(40)
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)
        
        header.setLayout(layout)
        return header
    
    def refresh_all(self):
        """Refresh all widgets with latest data"""
        self.dashboard_widget.refresh()
        if hasattr(self, 'transaction_widget'):
            self.transaction_widget.refresh()
        if hasattr(self, 'budget_widget'):
            self.budget_widget.refresh()
        if hasattr(self, 'savings_widget'):
            self.savings_widget.refresh()
    
    def open_quick_add(self):
        """Open quick add transaction dialog"""
        from ui.dialogs.quick_add_dialog import QuickAddDialog
        dialog = QuickAddDialog(self.db, self.data_changed)
        dialog.exec_()
    
    def open_settings(self):
        """Open settings dialog"""
        from ui.dialogs.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def get_button_stylesheet(self) -> str:
        """Get stylesheet for buttons"""
        return f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {COLORS['primary']};
                opacity: 0.8;
            }}
        """
    
    def get_tab_stylesheet(self) -> str:
        """Get stylesheet for tabs"""
        return f"""
            QTabWidget::pane {{
                border: none;
            }}
            QTabBar::tab {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_secondary']};
                padding: 10px 20px;
                border: none;
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary']};
                border-bottom: 2px solid {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
            }}
        """
    
    def apply_styles(self):
        """Apply global stylesheet"""
        stylesheet = f"""
            QMainWindow {{
                background-color: {COLORS['dark_bg']};
            }}
            QWidget {{
                background-color: {COLORS['dark_bg']};
                color: {COLORS['text_primary']};
            }}
            QFrame {{
                background-color: {COLORS['dark_bg']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QPushButton {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['secondary']};
            }}
            QTableWidget {{
                background-color: {COLORS['card_bg']};
                alternate-background-color: {COLORS['dark_bg']};
                gridline-color: {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: {COLORS['text_primary']};
                padding: 5px;
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
        """
        self.setStyleSheet(stylesheet)
    
    def closeEvent(self, event):
        """Handle application close"""
        self.refresh_timer.stop()
        event.accept()


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    main()