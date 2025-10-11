from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Represents a financial transaction"""
    id: int
    date: str
    type: str
    category: str
    amount: float
    description: str
    created_at: str
    
    @property
    def display_amount(self) -> str:
        """Return formatted amount with sign"""
        sign = "+" if self.type == "Income" else "-"
        return f"{sign}NT${self.amount:,.2f}"

@dataclass
class Budget:
    """Represents a budget for a category"""
    id: int
    category: str
    limit_amount: float
    created_at: str
    spent: float = 0.0
    
    @property
    def percentage_used(self) -> float:
        """Calculate percentage of budget used"""
        if self.limit_amount == 0:
            return 0
        return min((self.spent / self.limit_amount) * 100, 100)
    
    @property
    def remaining(self) -> float:
        """Calculate remaining budget"""
        return max(self.limit_amount - self.spent, 0)
    
    @property
    def is_warning(self) -> bool:
        """Check if budget is in warning zone (80-99%)"""
        return 80 <= self.percentage_used < 100
    
    @property
    def is_exceeded(self) -> bool:
        """Check if budget is exceeded (100%+)"""
        return self.percentage_used >= 100

@dataclass
class SavingsGoal:
    """Represents a savings goal"""
    id: int
    name: str
    target_amount: float
    current_amount: float
    deadline: str
    created_at: str
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress towards goal (0-100)"""
        if self.target_amount == 0:
            return 0
        return min((self.current_amount / self.target_amount) * 100, 100)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to save"""
        return max(self.target_amount - self.current_amount, 0)
    
    @property
    def is_completed(self) -> bool:
        """Check if goal is completed"""
        return self.current_amount >= self.target_amount
    
    @property
    def days_remaining(self) -> int:
        """Calculate days until deadline"""
        from datetime import datetime
        try:
            deadline_date = datetime.strptime(self.deadline, "%Y-%m-%d").date()
            days = (deadline_date - datetime.now().date()).days
            return max(days, 0)
        except:
            return 0

@dataclass
class MonthlySummary:
    """Monthly financial summary"""
    year: int
    month: int
    total_income: float
    total_expense: float
    balance: float
    
    @property
    def savings_rate(self) -> float:
        """Calculate savings rate as percentage"""
        if self.total_income == 0:
            return 0
        return (self.balance / self.total_income) * 100

@dataclass
class BudgetAlert:
    """Represents a budget alert/warning"""
    category: str
    limit_amount: float
    spent_amount: float
    percentage: float
    alert_type: str
    
    @property
    def message(self) -> str:
        """Generate alert message"""
        if self.alert_type == "warning":
            return f"⚠️ {self.category}: {self.percentage:.0f}% of budget used"
        else:
            return f"🔴 {self.category}: Budget EXCEEDED by NT${self.spent_amount - self.limit_amount:,.2f}"