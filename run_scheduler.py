"""
Background scheduler for sending automatic email notifications.
Run this separately from the main GUI application.
"""

import schedule
import time
from datetime import datetime
from core.notifications import send_scheduled_notifications
from core.database import DatabaseManager


def job():
    """Job to run daily"""
    print(f"\n{'='*50}")
    print(f"Running scheduled notification check at {datetime.now()}")
    print(f"{'='*50}\n")
    
    try:
        send_scheduled_notifications()
        print("✅ Notifications checked successfully")
    except Exception as e:
        print(f"❌ Error running notifications: {e}")


def main():
    """Main scheduler loop"""
    print("="*50)
    print("Cash Tracker - Notification Scheduler Started")
    print("="*50)
    print(f"Current time: {datetime.now()}")
    print("\nScheduled tasks:")
    print("  • Daily reminder: Every day at 8:00 PM")
    print("  • Budget alerts: Every day at 9:00 AM and 6:00 PM")
    print("\nPress Ctrl+C to stop the scheduler\n")
    print("="*50)
    
    # Schedule daily reminder at 8:00 PM
    schedule.every().day.at("20:00").do(job)
    
    # Schedule budget checks at 9:00 AM and 6:00 PM
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("18:00").do(job)
    
    # Run immediately on startup (for testing)
    print("\n🔍 Running initial check...")
    job()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler stopped by user")
        print("="*50)


if __name__ == "__main__":
    main()