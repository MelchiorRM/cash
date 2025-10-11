from datetime import datetime, timedelta
from typing import Tuple, List, Optional
from config import DATE_FORMAT, DISPLAY_DATE_FORMAT, CURRENCY_SYMBOL, DECIMAL_PLACES

def format_currency(amount: float, include_symbol: bool = True) -> str:
    """Format amount as currency string"""
    formatted = f"{amount:,.{DECIMAL_PLACES}f}"
    if include_symbol:
        return f"{CURRENCY_SYMBOL}{formatted}"
    return formatted

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object"""
    return datetime.strptime(date_str, DATE_FORMAT)

def get_today() -> str:
    """Get today's date as formatted string"""
    return datetime.now().strftime(DATE_FORMAT)

def get_date_range_for_period(period: str) -> Tuple[str, str]:
    """Get start and end date for a given period"""
    today = datetime.now()
    
    if period == "today":
        start = today.strftime(DATE_FORMAT)
        return start, start
    
    elif period == "this_week":
        start = (today - timedelta(days=today.weekday())).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end
    
    elif period == "this_month":
        start = today.replace(day=1).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end
    
    elif period == "this_year":
        start = today.replace(month=1, day=1).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end
    
    elif period == "last_30_days":
        start = (today - timedelta(days=30)).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end
    
    elif period == "last_90_days":
        start = (today - timedelta(days=90)).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end
    
    else:
        start = (today - timedelta(days=30)).strftime(DATE_FORMAT)
        end = today.strftime(DATE_FORMAT)
        return start, end

def get_current_month_year() -> Tuple[int, int]:
    """Get current year and month"""
    today = datetime.now()
    return today.year, today.month

def format_display_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        date_obj = parse_date(date_str)
        return date_obj.strftime(DISPLAY_DATE_FORMAT)
    except:
        return date_str

def get_month_name(month: int) -> str:
    """Get month name from month number"""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return months[month - 1] if 1 <= month <= 12 else ""

def calculate_budget_alerts(budget_status: List[dict]) -> List[dict]:
    """Generate budget alerts/warnings"""
    alerts = []
    from config import BUDGET_WARNING_THRESHOLD, BUDGET_DANGER_THRESHOLD
    
    for budget in budget_status:
        category = budget['category']
        limit_amount = budget['limit_amount']
        spent = budget['spent']
        
        if limit_amount == 0:
            continue
        
        percentage = (spent / limit_amount) * 100
        
        if percentage >= BUDGET_DANGER_THRESHOLD:
            alerts.append({
                'type': 'exceeded',
                'category': category,
                'percentage': percentage,
                'message': f"🔴 {category}: Budget EXCEEDED ({percentage:.0f}%)"
            })
        elif percentage >= BUDGET_WARNING_THRESHOLD:
            alerts.append({
                'type': 'warning',
                'category': category,
                'percentage': percentage,
                'message': f"⚠️ {category}: {percentage:.0f}% of budget used"
            })
    
    return alerts

def calculate_days_until_deadline(deadline_str: str) -> int:
    """Calculate days remaining until deadline"""
    try:
        deadline = datetime.strptime(deadline_str, DATE_FORMAT).date()
        today = datetime.now().date()
        days = (deadline - today).days
        return max(days, 0)
    except:
        return 0

def get_color_by_percentage(percentage: float) -> str:
    """Get color based on percentage value"""
    from config import COLORS
    
    if percentage >= 100:
        return COLORS['danger']
    elif percentage >= 80:
        return COLORS['warning']
    elif percentage >= 50:
        return COLORS['secondary']
    else:
        return COLORS['success']

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def validate_amount(amount_str: str) -> Tuple[bool, float]:
    """Validate and parse amount string"""
    try:
        amount = float(amount_str)
        return amount > 0, amount
    except:
        return False, 0

def validate_date(date_str: str) -> bool:
    """Validate date format"""
    try:
        datetime.strptime(date_str, DATE_FORMAT)
        return True
    except:
        return False