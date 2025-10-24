import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List
import json
from pathlib import Path

from config import (EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT, 
                   SMTP_SERVER, SMTP_PORT, COLORS)
from core.database import DatabaseManager
from core.utils import format_currency, get_current_month_year


class NotificationManager:
    """Handles email notifications for the finance tracker"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.last_notification_file = Path("last_notification.json")
    
    def should_send_daily_reminder(self) -> bool:
        """Check if we should send today's reminder"""
        today = datetime.now().date().isoformat()
        
        # Check last notification date
        if self.last_notification_file.exists():
            with open(self.last_notification_file, 'r') as f:
                data = json.load(f)
                last_date = data.get('last_daily_reminder')
                if last_date == today:
                    return False  # Already sent today
        
        return True
    
    def mark_notification_sent(self, notification_type: str):
        """Mark that a notification was sent"""
        today = datetime.now().date().isoformat()
        
        data = {}
        if self.last_notification_file.exists():
            with open(self.last_notification_file, 'r') as f:
                data = json.load(f)
        
        data[notification_type] = today
        
        with open(self.last_notification_file, 'w') as f:
            json.dump(data, f)
    
    def send_daily_reminder(self) -> bool:
        """Send daily reminder to log expenses"""
        if not self.should_send_daily_reminder():
            print("Daily reminder already sent today")
            return False
        
        subject = "💰 Daily Expense Reminder - Cash Tracker"
        
        # Get today's summary
        year, month = get_current_month_year()
        monthly_summary = self.db.get_monthly_summary(year, month)
        
        # Get today's transactions
        today = datetime.now().strftime("%Y-%m-%d")
        today_transactions = self.db.get_all_transactions(
            start_date=today, 
            end_date=today
        )
        
        body = self._create_daily_reminder_email(
            monthly_summary, 
            today_transactions
        )
        
        success = self._send_email(subject, body)
        
        if success:
            self.mark_notification_sent('last_daily_reminder')
            print(f"Daily reminder sent successfully at {datetime.now()}")
        
        return success
    
    def send_budget_alert(self, category: str, spent: float, limit: float) -> bool:
        """Send email alert when budget is exceeded"""
        percentage = (spent / limit * 100) if limit > 0 else 0
        
        if percentage >= 100:
            subject = f"🔴 Budget EXCEEDED: {category}"
            emoji = "🔴"
            status = "EXCEEDED"
        elif percentage >= 80:
            subject = f"⚠️ Budget Warning: {category}"
            emoji = "⚠️"
            status = "WARNING"
        else:
            return False  # No alert needed
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f1f5f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; padding: 20px;">
                <h2 style="color: #ef4444;">{emoji} Budget Alert: {status}</h2>
                
                <p>Your <strong>{category}</strong> budget needs attention:</p>
                
                <table style="width: 100%; margin: 20px 0;">
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #334155;">Budget Limit:</td>
                        <td style="padding: 10px; border-bottom: 1px solid #334155; text-align: right;">{format_currency(limit)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border-bottom: 1px solid #334155;">Amount Spent:</td>
                        <td style="padding: 10px; border-bottom: 1px solid #334155; text-align: right; color: #ef4444;">{format_currency(spent)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; font-weight: bold;">Percentage Used:</td>
                        <td style="padding: 10px; text-align: right; font-weight: bold; color: #ef4444;">{percentage:.1f}%</td>
                    </tr>
                </table>
                
                <p style="color: #f59e0b; font-weight: bold;">
                    {'You have exceeded your budget!' if percentage >= 100 else 'Please monitor your spending carefully.'}
                </p>
                
                <p style="color: #94a3b8; font-size: 12px; margin-top: 30px;">
                    This is an automated alert from Cash Finance Tracker.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(subject, body, html=True)
    
    def _create_daily_reminder_email(self, monthly_summary: dict, 
                                    today_transactions: List[dict]) -> str:
        """Create HTML email body for daily reminder"""
        today_date = datetime.now().strftime("%B %d, %Y")
        
        # Count today's transactions
        today_count = len(today_transactions)
        today_total = sum(t['amount'] for t in today_transactions if t['type'] == 'Expense')
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f1f5f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #1e293b; border-radius: 8px; padding: 20px;">
                <h2 style="color: #6366f1;">💰 Daily Expense Reminder</h2>
                <p style="color: #cbd5e1;">Good day! Time to log your expenses for <strong>{today_date}</strong></p>
                
                <div style="background-color: #0f172a; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <h3 style="color: #10b981; margin-top: 0;">Today's Activity</h3>
                    <p>✅ Transactions logged: <strong>{today_count}</strong></p>
                    <p>💸 Total spent today: <strong>{format_currency(today_total)}</strong></p>
                </div>
                
                <div style="background-color: #0f172a; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <h3 style="color: #6366f1; margin-top: 0;">This Month's Summary</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td style="padding: 8px; color: #10b981;">Income:</td>
                            <td style="padding: 8px; text-align: right; color: #10b981;">{format_currency(monthly_summary['income'])}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; color: #ef4444;">Expenses:</td>
                            <td style="padding: 8px; text-align: right; color: #ef4444;">{format_currency(monthly_summary['expense'])}</td>
                        </tr>
                        <tr style="border-top: 1px solid #334155;">
                            <td style="padding: 8px; font-weight: bold;">Balance:</td>
                            <td style="padding: 8px; text-align: right; font-weight: bold;">{format_currency(monthly_summary['balance'])}</td>
                        </tr>
                    </table>
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #1e40af; border-radius: 8px;">
                    <p style="margin: 0; text-align: center; font-weight: bold;">
                        📱 Open Cash Tracker to log your expenses!
                    </p>
                </div>
                
                <p style="color: #94a3b8; font-size: 12px; margin-top: 30px;">
                    This is your daily reminder from Cash Finance Tracker.<br>
                    You're receiving this because you enabled daily notifications.
                </p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _send_email(self, subject: str, body: str, html: bool = True) -> bool:
        """Send an email"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECIPIENT
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def check_and_send_budget_alerts(self):
        """Check all budgets and send alerts if needed"""
        year, month = get_current_month_year()
        budget_status = self.db.get_budget_status(year, month)
        
        alerts_sent = 0
        for budget in budget_status:
            category = budget['category']
            spent = budget['spent']
            limit = budget['limit_amount']
            percentage = (spent / limit * 100) if limit > 0 else 0
            
            # Only send alert once per day per budget
            alert_key = f"budget_alert_{category}_{datetime.now().date().isoformat()}"
            
            if percentage >= 80:
                if self.send_budget_alert(category, spent, limit):
                    alerts_sent += 1
        
        return alerts_sent


# Helper function to run as a scheduled task
def send_scheduled_notifications():
    """Main function to be called by scheduler"""
    db = DatabaseManager()
    notifier = NotificationManager(db)
    
    # Send daily reminder
    notifier.send_daily_reminder()
    
    # Check and send budget alerts
    notifier.check_and_send_budget_alerts()


if __name__ == "__main__":
    # Test the notification system
    send_scheduled_notifications()