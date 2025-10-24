from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                             QScrollArea, QProgressBar, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from config import COLORS, DEFAULT_CHART_RANGE
from core.database import DatabaseManager
from core.utils import (get_current_month_year, format_currency, 
                        get_date_range_for_period, calculate_budget_alerts)
from ui.charts.charts_manager import ChartsManager
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class DashboardWidget(QWidget):
    """Dashboard widget showing financial overview"""
    
    def __init__(self, db: DatabaseManager, data_changed: pyqtSignal):
        super().__init__()
        self.db = db
        self.data_changed = data_changed
        self.charts_manager = ChartsManager()
        
        # Store references to value labels for easy updates
        self.balance_value_label = None
        self.income_value_label = None
        self.expense_value_label = None
        
        self.init_ui()
        self.data_changed.connect(self.refresh)
    
    def init_ui(self):
        """Initialize dashboard UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(20)
        
        # Summary cards
        summary_layout = QHBoxLayout()
        balance_card, self.balance_value_label = self.create_summary_card(
            "Current Balance", "NT$0.00", COLORS['primary']
        )
        income_card, self.income_value_label = self.create_summary_card(
            "Monthly Income", "NT$0.00", COLORS['success']
        )
        expense_card, self.expense_value_label = self.create_summary_card(
            "Monthly Spending", "NT$0.00", COLORS['danger']
        )
        
        summary_layout.addWidget(balance_card)
        summary_layout.addWidget(income_card)
        summary_layout.addWidget(expense_card)
        scroll_layout.addLayout(summary_layout)
        
        # Alerts/Notifications
        self.alerts_frame = QFrame()
        self.alerts_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        self.alerts_layout = QVBoxLayout()
        alerts_title = QLabel("Budget Alerts")
        alerts_title.setFont(QFont("Arial", 12, QFont.Bold))
        alerts_title.setStyleSheet(f"color: {COLORS['text_primary']};")
        self.alerts_layout.addWidget(alerts_title)
        self.alerts_frame.setLayout(self.alerts_layout)
        scroll_layout.addWidget(self.alerts_frame)
        
        # Charts (pie and line)
        charts_layout = QHBoxLayout()
        
        # Pie chart
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
        title = QLabel("Expenses by Category")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        pie_layout.addWidget(title)
        self.pie_canvas = FigureCanvas(self.charts_manager.create_expense_pie_chart([]))
        self.pie_canvas.setMinimumSize(400, 300)
        pie_layout.addWidget(self.pie_canvas)
        pie_frame.setLayout(pie_layout)
        charts_layout.addWidget(pie_frame)
        
        # Line chart
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
        title = QLabel("Spending Trends")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        line_layout.addWidget(title)
        self.line_canvas = FigureCanvas(self.charts_manager.create_spending_trend_chart([]))
        self.line_canvas.setMinimumSize(400, 300)
        line_layout.addWidget(self.line_canvas)
        line_frame.setLayout(line_layout)
        charts_layout.addWidget(line_frame)
        
        scroll_layout.addLayout(charts_layout)
        
        # Budget summary
        budget_frame = QFrame()
        budget_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        budget_layout = QVBoxLayout()
        title = QLabel("Budget Usage Summary")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        budget_layout.addWidget(title)
        
        self.budget_items_layout = QVBoxLayout()
        budget_layout.addLayout(self.budget_items_layout)
        budget_layout.addStretch()
        
        budget_frame.setLayout(budget_layout)
        scroll_layout.addWidget(budget_frame)
        
        # Savings goals
        savings_frame = QFrame()
        savings_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
                padding: 15px;
            }}
        """)
        savings_layout = QVBoxLayout()
        title = QLabel("Active Savings Goals")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        savings_layout.addWidget(title)
        
        self.savings_items_layout = QVBoxLayout()
        savings_layout.addLayout(self.savings_items_layout)
        savings_layout.addStretch()
        
        savings_frame.setLayout(savings_layout)
        scroll_layout.addWidget(savings_frame)
        
        scroll_layout.addStretch()
        scroll_widget.setLayout(scroll_layout)
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
        # Initial data load
        self.refresh()
    
    def create_summary_card(self, title: str, value: str, color: str):
        """Create a summary card widget and return both card and value label"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_bg']};
                border-radius: 8px;
                border-left: 4px solid {color};
                padding: 15px;
            }}
        """)
        card.setFixedHeight(100)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 11))
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card, value_label  # Return both card and value label
    
    def create_budget_item(self, category: str, spent: float, limit: float) -> QFrame:
        """Create a budget item widget"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_bg']};
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Category and percentage
        header_layout = QHBoxLayout()
        category_label = QLabel(category)
        category_label.setFont(QFont("Arial", 10, QFont.Bold))
        category_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        percentage = (spent / limit * 100) if limit > 0 else 0
        percentage_label = QLabel(f"{percentage:.0f}%")
        percentage_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        percentage_label.setFont(QFont("Arial", 9))
        
        header_layout.addWidget(category_label)
        header_layout.addStretch()
        header_layout.addWidget(percentage_label)
        layout.addLayout(header_layout)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(100)
        progress.setValue(min(int(percentage), 100))
        progress.setFixedHeight(6)
        progress.setTextVisible(False)
        
        # Color based on usage
        if percentage >= 100:
            color = COLORS['danger']
        elif percentage >= 80:
            color = COLORS['warning']
        else:
            color = COLORS['success']
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['card_bg']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # Amount details
        amount_layout = QHBoxLayout()
        amount_label = QLabel(f"{format_currency(spent)} / {format_currency(limit)}")
        amount_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        amount_label.setFont(QFont("Arial", 9))
        amount_layout.addWidget(amount_label)
        amount_layout.addStretch()
        layout.addLayout(amount_layout)
        
        item.setLayout(layout)
        return item
    
    def create_savings_goal_item(self, name: str, current: float, target: float, deadline: str) -> QFrame:
        """Create a savings goal item widget"""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['dark_bg']};
                border-radius: 4px;
                padding: 10px;
                margin: 5px 0;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Goal name and deadline
        header_layout = QHBoxLayout()
        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        
        from core.utils import format_display_date
        deadline_label = QLabel(f"Due: {format_display_date(deadline)}")
        deadline_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        deadline_label.setFont(QFont("Arial", 9))
        
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(deadline_label)
        layout.addLayout(header_layout)
        
        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(100)
        percentage = min((current / target * 100) if target > 0 else 0, 100)
        progress.setValue(int(percentage))
        progress.setFixedHeight(6)
        progress.setTextVisible(False)
        
        progress_color = COLORS['success'] if current >= target else COLORS['primary']
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['card_bg']};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {progress_color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)
        
        # Amount details
        amount_layout = QHBoxLayout()
        amount_label = QLabel(f"{format_currency(current)} / {format_currency(target)}")
        amount_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        amount_label.setFont(QFont("Arial", 9))
        
        percentage_label = QLabel(f"{percentage:.0f}%")
        percentage_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        percentage_label.setFont(QFont("Arial", 9, QFont.Bold))
        
        amount_layout.addWidget(amount_label)
        amount_layout.addStretch()
        amount_layout.addWidget(percentage_label)
        layout.addLayout(amount_layout)
        
        item.setLayout(layout)
        return item
    
    def refresh(self):
        """Refresh dashboard data"""
        year, month = get_current_month_year()
        
        # Update summary cards using stored label references
        summary = self.db.get_monthly_summary(year, month)
        self.balance_value_label.setText(format_currency(summary['balance']))
        self.income_value_label.setText(format_currency(summary['income']))
        self.expense_value_label.setText(format_currency(summary['expense']))
        
        # Update charts with better sizing
        start_date, end_date = get_date_range_for_period("last_90_days")
        
        expense_by_category = self.db.get_expenses_by_category(start_date, end_date)
        self.pie_canvas.figure = self.charts_manager.create_expense_pie_chart(expense_by_category)
        self.pie_canvas.draw()
        
        daily_spending = self.db.get_daily_spending(start_date, end_date)
        self.line_canvas.figure = self.charts_manager.create_spending_trend_chart(daily_spending)
        self.line_canvas.draw()
        
        # Update budget summary
        self.update_budget_summary(year, month)
        
        # Update savings goals
        self.update_savings_goals()
        
        # Update alerts
        self.update_alerts(year, month)
    
    def update_budget_summary(self, year: int, month: int):
        """Update budget status display"""
        # Clear existing items
        while self.budget_items_layout.count():
            item = self.budget_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        budget_status = self.db.get_budget_status(year, month)
        
        if not budget_status:
            no_budget_label = QLabel("No budgets set. Go to Budgets tab to create one.")
            no_budget_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            self.budget_items_layout.addWidget(no_budget_label)
            return
        
        for budget in budget_status:
            item = self.create_budget_item(budget['category'], budget['spent'], budget['limit_amount'])
            self.budget_items_layout.addWidget(item)
    
    def update_savings_goals(self):
        """Update savings goals display"""
        # Clear existing items
        while self.savings_items_layout.count():
            item = self.savings_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        goals = self.db.get_all_savings_goals()
        
        if not goals:
            no_goals_label = QLabel("No savings goals. Go to Savings tab to create one.")
            no_goals_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
            self.savings_items_layout.addWidget(no_goals_label)
            return
        
        for goal in goals:
            item = self.create_savings_goal_item(
                goal['name'], goal['current_amount'], 
                goal['target_amount'], goal['deadline']
            )
            self.savings_items_layout.addWidget(item)
    
    def update_alerts(self, year: int, month: int):
        """Update budget alerts and notifications"""
        # Clear existing alerts (keep title)
        while self.alerts_layout.count() > 1:
            item = self.alerts_layout.takeAt(1)
            if item.widget():
                item.widget().deleteLater()
        
        budget_status = self.db.get_budget_status(year, month)
        alerts = calculate_budget_alerts(budget_status)
        
        if not alerts:
            no_alerts_label = QLabel("✓ All budgets are within limits!")
            no_alerts_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
            self.alerts_layout.addWidget(no_alerts_label)
            return
        
        for alert in alerts:
            alert_label = QLabel(alert['message'])
            alert_label.setFont(QFont("Arial", 10))
            if alert['type'] == 'exceeded':
                alert_label.setStyleSheet(f"color: {COLORS['danger']}; font-weight: bold;")
            else:
                alert_label.setStyleSheet(f"color: {COLORS['warning']}; font-weight: bold;")
            self.alerts_layout.addWidget(alert_label)