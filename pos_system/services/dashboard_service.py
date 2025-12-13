import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any


class DashboardService:
    """Dashboard statistics service"""
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
    
    def get_today_sales(self) -> float:
        """Get total sales for today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM invoices 
                WHERE DATE(created_at) = ?
            ''', (today,))
            result = cursor.fetchone()[0]
            conn.close()
            return float(result)
        except sqlite3.Error as e:
            print(f"Error getting today sales: {e}")
            return 0.0
    
    def get_total_invoices(self) -> int:
        """Get total number of invoices"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM invoices')
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except sqlite3.Error:
            return 0
    
    def get_today_invoices(self) -> int:
        """Get number of invoices created today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COUNT(*) FROM invoices WHERE DATE(created_at) = ?
            ''', (today,))
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except sqlite3.Error:
            return 0
    
    def get_pending_balances(self) -> float:
        """Get total pending balance amounts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(SUM(ABS(balance_amount)), 0) 
                FROM invoices 
                WHERE balance_amount < 0
            ''')
            result = cursor.fetchone()[0]
            conn.close()
            return float(result)
        except sqlite3.Error:
            return 0.0
    
    def get_total_customers(self) -> int:
        """Get total number of customers"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM customers')
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except sqlite3.Error:
            return 0
    
    def get_pending_bookings(self) -> int:
        """Get number of pending bookings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Pending'")
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except sqlite3.Error:
            return 0
    
    def get_low_stock_frames(self) -> int:
        """Get number of frames with low stock (< 10)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM photo_frames WHERE quantity < 10')
            result = cursor.fetchone()[0]
            conn.close()
            return result
        except sqlite3.Error:
            return 0
    
    def get_weekly_sales(self) -> float:
        """Get total sales for the week"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM invoices 
                WHERE DATE(created_at) >= ?
            ''', (week_ago,))
            result = cursor.fetchone()[0]
            conn.close()
            return float(result)
        except sqlite3.Error:
            return 0.0
    
    def get_monthly_sales(self) -> float:
        """Get total sales for the month"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT COALESCE(SUM(total_amount), 0) 
                FROM invoices 
                WHERE DATE(created_at) >= ?
            ''', (first_day,))
            result = cursor.fetchone()[0]
            conn.close()
            return float(result)
        except sqlite3.Error:
            return 0.0
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get all dashboard statistics"""
        return {
            'today_sales': self.get_today_sales(),
            'today_invoices': self.get_today_invoices(),
            'total_invoices': self.get_total_invoices(),
            'pending_balances': self.get_pending_balances(),
            'total_customers': self.get_total_customers(),
            'pending_bookings': self.get_pending_bookings(),
            'low_stock_frames': self.get_low_stock_frames(),
            'weekly_sales': self.get_weekly_sales(),
            'monthly_sales': self.get_monthly_sales(),
        }
