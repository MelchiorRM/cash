import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Dict, Optional
from config import COLORS, CHART_STYLE
from core.utils import format_currency, get_month_name


class ChartsManager:
    """Manages all chart creation and rendering"""
    
    def __init__(self):
        sns.set_style(CHART_STYLE)
        # Better default settings for dark theme
        plt.rcParams['figure.facecolor'] = COLORS['dark_bg']
        plt.rcParams['axes.facecolor'] = COLORS['card_bg']
        plt.rcParams['text.color'] = COLORS['text_primary']
        plt.rcParams['axes.labelcolor'] = COLORS['text_secondary']
        plt.rcParams['xtick.color'] = COLORS['text_secondary']
        plt.rcParams['ytick.color'] = COLORS['text_secondary']
        plt.rcParams['axes.edgecolor'] = COLORS['border']
        plt.rcParams['grid.color'] = COLORS['border']
        plt.rcParams['grid.alpha'] = 0.3
    
    def create_expense_pie_chart(self, expenses_data: List[dict]) -> Figure:
        """Create pie chart for expenses by category"""
        fig = Figure(figsize=(6, 4.5), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not expenses_data:
            ax.text(0.5, 0.5, 'No expense data available', 
                   ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        categories = [item['category'] for item in expenses_data]
        amounts = [item['total'] for item in expenses_data]
        
        # Better color palette
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                 COLORS['warning'], COLORS['danger'], COLORS['info'],
                 '#a78bfa', '#f472b6', '#fb923c', '#34d399']
        colors = colors[:len(categories)]
        
        # Create pie chart with better styling
        wedges, texts, autotexts = ax.pie(
            amounts, labels=categories, autopct='%1.1f%%',
            colors=colors, startangle=90,
            textprops={'color': COLORS['text_primary'], 'fontsize': 9},
            pctdistance=0.85
        )
        
        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(8)
        
        # Style labels
        for text in texts:
            text.set_fontsize(9)
        
        ax.set_title('Expenses by Category', color=COLORS['text_primary'],
                    fontsize=12, fontweight='bold', pad=15)
        
        fig.tight_layout(pad=1.5)
        return fig
    
    def create_spending_trend_chart(self, daily_data: List[dict]) -> Figure:
        """Create line chart for spending trends over time"""
        fig = Figure(figsize=(6, 4.5), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not daily_data:
            ax.text(0.5, 0.5, 'No spending data available', 
                   ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        dates = [item['date'] for item in daily_data]
        amounts = [item['total'] for item in daily_data]
        
        # Process data with pandas
        df = pd.DataFrame({'date': dates, 'amount': amounts})
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate moving average for smoother line
        if len(df) >= 7:
            df['ma7'] = df['amount'].rolling(window=7, min_periods=1).mean()
        else:
            df['ma7'] = df['amount']
        
        # Plot daily spending
        ax.plot(df['date'], df['amount'], marker='o', linestyle='-', 
               linewidth=2, markersize=4, color=COLORS['primary'],
               label='Daily Spending', alpha=0.6)
        
        # Plot moving average
        ax.plot(df['date'], df['ma7'], linestyle='--', linewidth=2.5,
               color=COLORS['secondary'], label='7-Day Average', alpha=0.9)
        
        # Fill area under curve
        ax.fill_between(df['date'], df['amount'], alpha=0.15, color=COLORS['primary'])
        
        ax.set_title('Daily Spending Trends', color=COLORS['text_primary'],
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Date', color=COLORS['text_secondary'], fontsize=9)
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'], fontsize=9)
        ax.legend(loc='upper left', framealpha=0.9, fontsize=8)
        ax.grid(True, alpha=0.2, linestyle='--')
        ax.tick_params(axis='both', labelsize=8)
        
        # Rotate x-axis labels for better readability
        fig.autofmt_xdate(rotation=45)
        
        fig.tight_layout(pad=1.5)
        return fig
    
    def create_budget_comparison_chart(self, budget_status: List[dict]) -> Figure:
        """Create bar chart comparing budget vs actual spending"""
        fig = Figure(figsize=(8, 5), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not budget_status:
            ax.text(0.5, 0.5, 'No budgets configured', 
                   ha='center', va='center',
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
        
        # Create bars
        bars1 = ax.bar([i - width/2 for i in x], limits, width, 
                       label='Budget Limit', color=COLORS['success'], 
                       alpha=0.7, edgecolor=COLORS['border'], linewidth=1)
        bars2 = ax.bar([i + width/2 for i in x], spent, width, 
                       label='Actual Spent', color=COLORS['primary'], 
                       alpha=0.8, edgecolor=COLORS['border'], linewidth=1)
        
        # Color bars based on budget status
        for i, (limit, amount) in enumerate(zip(limits, spent)):
            if amount >= limit:
                bars2[i].set_color(COLORS['danger'])
                bars2[i].set_alpha(0.8)
            elif amount >= limit * 0.8:
                bars2[i].set_color(COLORS['warning'])
                bars2[i].set_alpha(0.8)
        
        ax.set_title('Budget vs Actual Spending', color=COLORS['text_primary'],
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Category', color=COLORS['text_secondary'], fontsize=9)
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'], fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.2, axis='y', linestyle='--')
        ax.tick_params(axis='both', labelsize=8)
        
        fig.tight_layout(pad=1.5)
        return fig
    
    def create_income_vs_expense_chart(self, monthly_data: List[dict]) -> Figure:
        """Create grouped bar chart for income vs expense over months"""
        fig = Figure(figsize=(8, 5), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not monthly_data:
            ax.text(0.5, 0.5, 'No data available', 
                   ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        months = [f"{item['month']}" for item in monthly_data]
        income = [item['income'] for item in monthly_data]
        expenses = [item['expense'] for item in monthly_data]
        
        x = range(len(months))
        width = 0.35
        
        bars1 = ax.bar([i - width/2 for i in x], income, width, 
                       label='Income', color=COLORS['success'], 
                       alpha=0.8, edgecolor=COLORS['border'], linewidth=1)
        bars2 = ax.bar([i + width/2 for i in x], expenses, width, 
                       label='Expenses', color=COLORS['danger'], 
                       alpha=0.8, edgecolor=COLORS['border'], linewidth=1)
        
        ax.set_title('Income vs Expenses', color=COLORS['text_primary'],
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Month', color=COLORS['text_secondary'], fontsize=9)
        ax.set_ylabel('Amount (NT$)', color=COLORS['text_secondary'], fontsize=9)
        ax.set_xticks(x)
        ax.set_xticklabels(months, rotation=45, ha='right', fontsize=8)
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.2, axis='y', linestyle='--')
        ax.tick_params(axis='both', labelsize=8)
        
        fig.tight_layout(pad=1.5)
        return fig
    
    def create_savings_progress_chart(self, goals_data: List[dict]) -> Figure:
        """Create horizontal bar chart for savings goals progress"""
        num_goals = len(goals_data) if goals_data else 1
        fig_height = max(3, 2 + num_goals * 0.6)
        
        fig = Figure(figsize=(8, fig_height), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not goals_data:
            ax.text(0.5, 0.5, 'No savings goals set', 
                   ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=12)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        names = [item['name'] for item in goals_data]
        current = [item['current_amount'] for item in goals_data]
        target = [item['target_amount'] for item in goals_data]
        
        y = range(len(names))
        
        # Background bars (targets)
        ax.barh(y, target, color=COLORS['border'], alpha=0.3, 
                edgecolor=COLORS['border'], linewidth=1)
        
        # Progress bars with color coding
        colors = [COLORS['success'] if c >= t else COLORS['primary'] 
                 for c, t in zip(current, target)]
        bars = ax.barh(y, current, color=colors, alpha=0.85,
                       edgecolor=COLORS['border'], linewidth=1)
        
        # Add percentage labels
        for i, (c, t) in enumerate(zip(current, target)):
            percentage = min((c / t * 100) if t > 0 else 0, 100)
            # Position label at the end of the bar
            label_x = c + (max(target) * 0.02)
            ax.text(label_x, i, f'{percentage:.0f}%', va='center',
                   color=COLORS['text_primary'], fontweight='bold', fontsize=9)
        
        ax.set_title('Savings Goals Progress', color=COLORS['text_primary'],
                    fontsize=12, fontweight='bold', pad=15)
        ax.set_xlabel('Amount (NT$)', color=COLORS['text_secondary'], fontsize=9)
        ax.set_yticks(y)
        ax.set_yticklabels(names, fontsize=9)
        ax.grid(True, alpha=0.2, axis='x', linestyle='--')
        ax.tick_params(axis='both', labelsize=8)
        
        fig.tight_layout(pad=1.5)
        return fig