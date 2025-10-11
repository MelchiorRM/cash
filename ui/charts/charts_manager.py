import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Dict, Optional
from config import COLORS, CHART_FIGURE_SIZE, CHART_STYLE, DEFAULT_CHART_RANGE
from core.utils import format_currency, get_month_name


class ChartsManager:
    """Manages all chart creation and rendering"""
    
    def __init__(self):
        sns.set_style(CHART_STYLE)
        plt.rcParams['figure.facecolor'] = COLORS['dark_bg']
        plt.rcParams['axes.facecolor'] = COLORS['card_bg']
        plt.rcParams['text.color'] = COLORS['text_primary']
        plt.rcParams['axes.labelcolor'] = COLORS['text_secondary']
        plt.rcParams['xtick.color'] = COLORS['text_secondary']
        plt.rcParams['ytick.color'] = COLORS['text_secondary']
    
    def create_expense_pie_chart(self, expenses_data: List[dict]) -> Figure:
        """Create pie chart for expenses by category"""
        fig = Figure(figsize=CHART_FIGURE_SIZE, facecolor=COLORS['dark_bg'])
        ax = fig.add_subplot(111)
        
        if not expenses_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        categories = [item['category'] for item in expenses_data]
        amounts = [item['total'] for item in expenses_data]
        
        #COLOR PALETTE
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                 COLORS['warning'], COLORS['danger'], COLORS['info'],
                 '#a78bfa', '#f472b6']
        colors = colors[:len(categories)]
        
        wedges, texts, autotexts = ax.pie(
            amounts, labels=categories, autopct='%1.1f%%',
            colors=colors, startangle=90,
            textprops={'color': COLORS['text_primary'], 'fontsize': 10}
        )
        
        # Styling for text
        for autotext in autotexts:
            autotext.set_color(COLORS['dark_bg'])
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Expenses by Category', color=COLORS['text_primary'],
                    fontsize=14, fontweight='bold', pad=20)
        
        fig.tight_layout()
        return fig
    
    def create_spending_trend_chart(self, daily_data: List[dict]) -> Figure:
        """Create line chart for spending trends over time"""
        fig = Figure(figsize=CHART_FIGURE_SIZE, facecolor=COLORS['dark_bg'])
        ax = fig.add_subplot(111)
        
        if not daily_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        dates = [item['date'] for item in daily_data]
        amounts = [item['total'] for item in daily_data]
        
        # Calculate moving average for smoother line
        df = pd.DataFrame({'date': dates, 'amount': amounts})
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['ma7'] = df['amount'].rolling(window=7, min_periods=1).mean()
        
        ax.plot(df['date'], df['amount'], marker='o', linestyle='-', 
               linewidth=2, markersize=6, color=COLORS['primary'],
               label='Daily Spending', alpha=0.7)
        ax.plot(df['date'], df['ma7'], linestyle='--', linewidth=2,
               color=COLORS['secondary'], label='7-Day Moving Avg', alpha=0.8)
        
        ax.fill_between(df['date'], df['amount'], alpha=0.2, color=COLORS['primary'])
        
        ax.set_title('Spending Trends', color=COLORS['text_primary'],
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Date', color=COLORS['text_secondary'])
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'])
        ax.legend(loc='upper left', framealpha=0.9)
        ax.grid(True, alpha=0.2)
        fig.autofmt_xdate(rotation=45)
        
        fig.tight_layout()
        return fig
    
    def create_budget_comparison_chart(self, budget_status: List[dict]) -> Figure:
        """Create bar chart comparing budget vs actual spending"""
        fig = Figure(figsize=CHART_FIGURE_SIZE, facecolor=COLORS['dark_bg'])
        ax = fig.add_subplot(111)
        
        if not budget_status:
            ax.text(0.5, 0.5, 'No budgets set', ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        categories = [item['category'] for item in budget_status]
        limits = [item['limit_amount'] for item in budget_status]
        spent = [item['spent'] for item in budget_status]
        
        x = range(len(categories))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], limits, width, label='Budget',
                       color=COLORS['success'], alpha=0.8)
        bars2 = ax.bar([i + width/2 for i in x], spent, width, label='Spent',
                       color=COLORS['primary'], alpha=0.8)
        
        #BARS COLOR
        for i, (limit, amount) in enumerate(zip(limits, spent)):
            if amount >= limit:
                bars2[i].set_color(COLORS['danger'])
            elif amount >= limit * 0.8:
                bars2[i].set_color(COLORS['warning'])
        
        ax.set_title('Budget vs Actual Spending', color=COLORS['text_primary'],
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Category', color=COLORS['text_secondary'])
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'])
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.2, axis='y')
        
        fig.tight_layout()
        return fig
    
    def create_income_vs_expense_chart(self, monthly_data: List[dict]) -> Figure:
        """Create stacked bar chart for income vs expense over months"""
        fig = Figure(figsize=CHART_FIGURE_SIZE, facecolor=COLORS['dark_bg'])
        ax = fig.add_subplot(111)
        
        if not monthly_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        months = [f"{item['month']}" for item in monthly_data]
        income = [item['income'] for item in monthly_data]
        expenses = [item['expense'] for item in monthly_data]
        
        x = range(len(months))
        width = 0.6
        
        bars1 = ax.bar(x, income, width, label='Income',
                       color=COLORS['success'], alpha=0.8)
        bars2 = ax.bar(x, expenses, width, bottom=income, label='Expenses',
                       color=COLORS['danger'], alpha=0.8)
        
        ax.set_title('Income vs Expenses', color=COLORS['text_primary'],
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Month', color=COLORS['text_secondary'])
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'])
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.2, axis='y')
        
        fig.tight_layout()
        return fig
    
    def create_savings_progress_chart(self, goals_data: List[dict]) -> Figure:
        """Create horizontal bar chart for savings goals progress"""
        fig = Figure(figsize=(10, 4 + len(goals_data) * 0.5), facecolor=COLORS['dark_bg'])
        ax = fig.add_subplot(111)
        
        if not goals_data:
            ax.text(0.5, 0.5, 'No savings goals', ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        names = [item['name'] for item in goals_data]
        current = [item['current_amount'] for item in goals_data]
        target = [item['target_amount'] for item in goals_data]
        
        y = range(len(names))
        
        ax.barh(y, target, color=COLORS['card_bg'], alpha=0.5)
        
        colors = [COLORS['success'] if c >= t else COLORS['primary'] 
                 for c, t in zip(current, target)]
        ax.barh(y, current, color=colors, alpha=0.8)
        
        for i, (c, t) in enumerate(zip(current, target)):
            percentage = min((c / t * 100) if t > 0 else 0, 100)
            ax.text(c + 50, i, f'{percentage:.0f}%', va='center',
                   color=COLORS['text_primary'], fontweight='bold')
        
        ax.set_title('Savings Goals Progress', color=COLORS['text_primary'],
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Amount (NT$)', color=COLORS['text_secondary'])
        ax.set_yticks(y)
        ax.set_yticklabels(names)
        ax.grid(True, alpha=0.2, axis='x')
        
        fig.tight_layout()
        return fig