#!/usr/bin/env python3
"""
Personal Finance Tracker
A beautiful and functional desktop application for managing personal finances

Usage:
    python main.py

Setup:
    1. Create virtual environment: python -m venv venv
    2. Activate it: source venv/bin/activate (or venv\Scripts\activate on Windows)
    3. Install dependencies: pip install -r requirements.txt
    4. Generate sample data (optional): python data/sample_data.py
    5. Run the app: python main.py
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.window.main_window import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()