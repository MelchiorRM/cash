import os
from pathlib import Path

APP_NAME="Cash"
APP_VERSION="1.0.0"

#Paths
BASE_DIR=Path(__file__).parent
#DB_PATH=BASE_DIR / "cash.db"
DB_PATH=BASE_DIR / "sample"/"sample_data.db" # For testing
ASSETS_PATH=BASE_DIR / "assets"

DB_TIMEOUT=30

WINDOW_WIDTH=1400
WINDOW_HEIGHT=900
MIN_WINDOW_WIDTH=1000
MIN_WINDOW_HEIGHT=700
THEME="dark"

DEFAULT_CURRENCY="NTD"
CURRENCY_SYMBOL="NT$"
DECIMAL_PLACES=2

DATE_FORMAT="%Y-%m-%d"
DISPLAY_FORMAT="%b %d, %Y"

EXPENSE_CATEGORIES=["Food", "Transportation", "Bills", "Entertainment", "Healthcare", "Education", "Other"]
INCOME_CATEGORIES=["Scholarship", "Other"]

EMAIL_SENDER="melchiorremilien@gmail.com"
EMAIL_PASSWORD="Mancity0"
EMAIL_RECIPIENT="melchiorrem001@gmail.com"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587

CHART_FIGURE_SIZE=(10, 6)
CHART_STYLE="whitegrid"
CHART_REFRESH_INTERVAL=1000

COLORS = {
    "primary": "#6366f1",
    "secondary": "#8b5cf6",
    "success": "#10b981",
    "danger": "#ef4444",
    "warning": "#f59e0b",
    "info": "#3b82f6",
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "dark_bg": "#0f172a",
    "card_bg": "#1e293b",
    "border": "#334155",
}

DEFAULT_CHART_RANGE=90