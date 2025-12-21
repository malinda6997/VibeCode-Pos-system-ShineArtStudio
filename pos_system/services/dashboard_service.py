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
                SELECT COALESCE(SUM(balance_amount), 0) 
                FROM invoices 
                WHERE balance_amount > 0
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
    
    # ==================== Photo Frame Profit Tracking (Admin Only) ====================
    
    def get_frame_profit_stats(self) -> Dict[str, Any]:
        """Get photo frame profit statistics - Admin only"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total frames sold from invoice items
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(quantity), 0) as total_sold,
                    COALESCE(SUM(total_price), 0) as total_selling,
                    COALESCE(SUM(buying_price), 0) as total_buying
                FROM invoice_items 
                WHERE item_type = 'Frame'
            ''')
            result = cursor.fetchone()
            
            total_sold = result[0] or 0
            total_selling = float(result[1] or 0)
            total_buying = float(result[2] or 0)
            net_profit = total_selling - total_buying
            
            conn.close()
            
            return {
                'total_frames_sold': total_sold,
                'total_buying_cost': total_buying,
                'total_selling_amount': total_selling,
                'net_profit': net_profit
            }
        except sqlite3.Error as e:
            print(f"Error getting frame profit stats: {e}")
            return {
                'total_frames_sold': 0,
                'total_buying_cost': 0,
                'total_selling_amount': 0,
                'net_profit': 0
            }
    
    def get_today_frame_profit(self) -> Dict[str, Any]:
        """Get today's photo frame profit - Admin only"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(ii.quantity), 0) as total_sold,
                    COALESCE(SUM(ii.total_price), 0) as total_selling,
                    COALESCE(SUM(ii.buying_price), 0) as total_buying
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE ii.item_type = 'Frame' AND DATE(i.created_at) = ?
            ''', (today,))
            result = cursor.fetchone()
            
            total_sold = result[0] or 0
            total_selling = float(result[1] or 0)
            total_buying = float(result[2] or 0)
            net_profit = total_selling - total_buying
            
            conn.close()
            
            return {
                'total_frames_sold': total_sold,
                'total_buying_cost': total_buying,
                'total_selling_amount': total_selling,
                'net_profit': net_profit
            }
        except sqlite3.Error as e:
            print(f"Error getting today's frame profit: {e}")
            return {
                'total_frames_sold': 0,
                'total_buying_cost': 0,
                'total_selling_amount': 0,
                'net_profit': 0
            }
    
    def get_monthly_frame_profit(self) -> Dict[str, Any]:
        """Get monthly photo frame profit - Admin only"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(ii.quantity), 0) as total_sold,
                    COALESCE(SUM(ii.total_price), 0) as total_selling,
                    COALESCE(SUM(ii.buying_price), 0) as total_buying
                FROM invoice_items ii
                JOIN invoices i ON ii.invoice_id = i.id
                WHERE ii.item_type = 'Frame' AND DATE(i.created_at) >= ?
            ''', (first_day,))
            result = cursor.fetchone()
            
            total_sold = result[0] or 0
            total_selling = float(result[1] or 0)
            total_buying = float(result[2] or 0)
            net_profit = total_selling - total_buying
            
            conn.close()
            
            return {
                'total_frames_sold': total_sold,
                'total_buying_cost': total_buying,
                'total_selling_amount': total_selling,
                'net_profit': net_profit
            }
        except sqlite3.Error as e:
            print(f"Error getting monthly frame profit: {e}")
            return {
                'total_frames_sold': 0,
                'total_buying_cost': 0,
                'total_selling_amount': 0,
                'net_profit': 0
            }
    
    # ==================== Staff Dashboard Widgets ====================
    
    def get_upcoming_bookings(self, limit: int = 5) -> list:
        """Get upcoming bookings for staff dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            today = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT b.id, b.event_date, b.event_time, b.event_location, 
                       b.event_type, b.status, c.full_name as customer_name
                FROM bookings b
                JOIN customers c ON b.customer_id = c.id
                WHERE b.event_date >= ? AND b.status IN ('Pending', 'Confirmed')
                ORDER BY b.event_date ASC, b.event_time ASC
                LIMIT ?
            ''', (today, limit))
            
            bookings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return bookings
        except sqlite3.Error as e:
            print(f"Error getting upcoming bookings: {e}")
            return []
    
    def get_recent_customers(self, limit: int = 5) -> list:
        """Get recently added customers for staff dashboard"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, full_name, mobile_number, created_at
                FROM customers
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            customers = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return customers
        except sqlite3.Error as e:
            print(f"Error getting recent customers: {e}")
            return []
    
    def get_frame_stock_summary(self, limit: int = 5) -> list:
        """Get frame stock summary for staff dashboard (no prices)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get frames sorted by stock level (lowest first for alerts)
            cursor.execute('''
                SELECT id, frame_name, size, quantity
                FROM photo_frames
                ORDER BY quantity ASC
                LIMIT ?
            ''', (limit,))
            
            frames = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return frames
        except sqlite3.Error as e:
            print(f"Error getting frame stock: {e}")
            return []
    
    def get_staff_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics for staff users (no financial data)"""
        return {
            'today_invoices': self.get_today_invoices(),
            'total_invoices': self.get_total_invoices(),
            'total_customers': self.get_total_customers(),
            'pending_bookings': self.get_pending_bookings(),
            'low_stock_frames': self.get_low_stock_frames(),
            'upcoming_bookings': self.get_upcoming_bookings(),
            'recent_customers': self.get_recent_customers(),
            'frame_stock': self.get_frame_stock_summary(),
        }
    
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
    
    def get_admin_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics including admin-only frame profit data"""
        stats = self.get_dashboard_stats()
        stats['frame_profit'] = self.get_frame_profit_stats()
        stats['today_frame_profit'] = self.get_today_frame_profit()
        stats['monthly_frame_profit'] = self.get_monthly_frame_profit()
        return stats
