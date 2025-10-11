from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, 
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from config import COLORS
from core.database import DatabaseManager
from core.utils import get_date_range_for_period, get_current_month_year
from ui.charts.charts_manager import ChartsManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class ChartsWidget(QWidget):
    """Widget for displaying financial charts"""
    
    def __init__(self, db: DatabaseManager):
        super().__init__()
        self.db = db
        self.charts_manager = ChartsManager()
        
        self.init_ui()
        self.refresh_charts()
    
    def init_ui(self):
        """Initialize charts widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Financial Analysis")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Time Period:"))
        
        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet(self.get_combo_style())
        self.period_combo.addItems([
            "Last 30 Days",
            "Last 90 Days",
            "This Month",
            "This Year"
        ])
        self.period_combo.currentTextChanged.connect(self.refresh_charts)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Charts grid
        charts_grid = QGridLayout()
        charts_grid.setSpacing(15)
        
        # Pie chart frame
        pie_frame = QFrame()
        pie_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 10px;
            }}
        """)
        pie_layout = QVBoxLayout()
        self.pie_canvas = FigureCanvas(self.charts_manager.create_expense_pie_chart([]))
        pie_layout.addWidget(self.pie_canvas)
        pie_frame.setLayout(pie_layout)
        charts_grid.addWidget(pie_frame, 0, 0)
        
        # Line chart frame
        line_frame = QFrame()
        line_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 10px;
            }}
        """)
        line_layout = QVBoxLayout()
        self.line_canvas = FigureCanvas(self.charts_manager.create_spending_trend_chart([]))
        line_layout.addWidget(self.line_canvas)
        line_frame.setLayout(line_layout)
        charts_grid.addWidget(line_frame, 0, 1)
        
        # Budget comparison frame
        budget_frame = QFrame()
        budget_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 10px;
            }}
        """)
        budget_layout = QVBoxLayout()
        year, month = get_current_month_year()
        budget_status = self.db.get_budget_status(year, month)
        self.budget_canvas = FigureCanvas(self.charts_manager.create_budget_comparison_chart(budget_status))
        budget_layout.addWidget(self.budget_canvas)
        budget_frame.setLayout(budget_layout)
        charts_grid.addWidget(budget_frame, 1, 0)
        
        # Savings progress frame
        savings_frame = QFrame()
        savings_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 10px;
            }}
        """)
        savings_layout = QVBoxLayout()
        goals = self.db.get_all_savings_goals()
        self.savings_canvas = FigureCanvas(self.charts_manager.create_savings_progress_chart(goals))
        savings_layout.addWidget(self.savings_canvas)
        savings_frame.setLayout(savings_layout)
        charts_grid.addWidget(savings_frame, 1, 1)
        
        layout.addLayout(charts_grid)
        self.setLayout(layout)
    
    def refresh_charts(self):
        """Refresh all charts with current data"""
        period_text = self.period_combo.currentText()
        
        # Map period text to period key
        period_map = {
            "Last 30 Days": "last_30_days",
            "Last 90 Days": "last_90_days",
            "This Month": "this_month",
            "This Year": "this_year"
        }
        period = period_map.get(period_text, "last_30_days")
        
        start_date, end_date = get_date_range_for_period(period)
        
        # Refresh pie chart
        expense_by_category = self.db.get_expenses_by_category(start_date, end_date)
        self.pie_canvas.figure = self.charts_manager.create_expense_pie_chart(expense_by_category)
        self.pie_canvas.draw()
        
        # Refresh line chart
        daily_spending = self.db.get_daily_spending(start_date, end_date)
        self.line_canvas.figure = self.charts_manager.create_spending_trend_chart(daily_spending)
        self.line_canvas.draw()
        
        # Refresh budget chart
        year, month = get_current_month_year()
        budget_status = self.db.get_budget_status(year, month)
        self.budget_canvas.figure = self.charts_manager.create_budget_comparison_chart(budget_status)
        self.budget_canvas.draw()
        
        # Refresh savings chart
        goals = self.db.get_all_savings_goals()
        self.savings_canvas.figure = self.charts_manager.create_savings_progress_chart(goals)
        self.savings_canvas.draw()
    
    def get_combo_style(self) -> str:
        """Get combo box stylesheet"""
        return f"""
            QComboBox {{
                background-color: {COLORS['card_bg']};
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