import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import List, Dict, Optional
from config import COLORS, CHART_STYLE
from core.utils import format_currency, get_month_name


class ChartsManager:
    """Manages chart creation and rendering - PIE CHART ONLY"""
    
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
        """Create interactive pie chart for expenses by category with hover tooltips"""
        fig = Figure(figsize=(7, 5.5), facecolor=COLORS['dark_bg'], dpi=100)
        ax = fig.add_subplot(111)
        
        if not expenses_data:
            ax.text(0.5, 0.5, 'No expense data available', 
                   ha='center', va='center',
                   color=COLORS['text_secondary'], fontsize=14)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
        
        categories = [item['category'] for item in expenses_data]
        amounts = [item['total'] for item in expenses_data]
        
        # Calculate total for percentages
        total = sum(amounts)
        
        # Better color palette
        colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'],
                 COLORS['warning'], COLORS['danger'], COLORS['info'],
                 '#a78bfa', '#f472b6', '#fb923c', '#34d399']
        colors = colors[:len(categories)]
        
        # Create pie chart WITHOUT labels (they'll appear on hover)
        wedges, texts, autotexts = ax.pie(
            amounts, 
            autopct='%1.1f%%',
            colors=colors, 
            startangle=90,
            textprops={'color': 'white', 'fontsize': 10, 'weight': 'bold'},
            pctdistance=0.85
        )
        
        # Style percentage text inside wedges
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Add legend on the side instead of labels
        legend_labels = [f'{cat}: {format_currency(amt)}' for cat, amt in zip(categories, amounts)]
        ax.legend(wedges, legend_labels, 
                 loc='center left',
                 bbox_to_anchor=(1, 0, 0.5, 1),
                 fontsize=9,
                 frameon=True,
                 facecolor=COLORS['card_bg'],
                 edgecolor=COLORS['border'])
        
        ax.set_title('Expenses by Category', 
                    color=COLORS['text_primary'],
                    fontsize=14, 
                    fontweight='bold', 
                    pad=20)
        
        # Create hover annotation (initially invisible)
        annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                           bbox=dict(boxstyle="round", fc=COLORS['card_bg'], 
                                   ec=COLORS['primary'], lw=2),
                           arrowprops=dict(arrowstyle="->", color=COLORS['primary']),
                           fontsize=11, color=COLORS['text_primary'],
                           weight='bold')
        annot.set_visible(False)
        
        # Mouse hover event handler
        def hover(event):
            if event.inaxes == ax:
                for i, wedge in enumerate(wedges):
                    if wedge.contains(event)[0]:
                        # Show tooltip
                        category = categories[i]
                        amount = amounts[i]
                        percentage = (amount / total * 100) if total > 0 else 0
                        
                        text = f"{category}\n{format_currency(amount)}\n{percentage:.1f}%"
                        annot.set_text(text)
                        annot.xy = (event.xdata, event.ydata)
                        annot.set_visible(True)
                        
                        # Highlight the wedge
                        wedge.set_edgecolor('white')
                        wedge.set_linewidth(3)
                        
                        fig.canvas.draw_idle()
                        return
                
                # Mouse not over any wedge
                annot.set_visible(False)
                for wedge in wedges:
                    wedge.set_edgecolor(COLORS['border'])
                    wedge.set_linewidth(1)
                fig.canvas.draw_idle()
        
        # Connect the hover event
        fig.canvas.mpl_connect("motion_notify_event", hover)
        
        fig.tight_layout(pad=1.5)
        return fig