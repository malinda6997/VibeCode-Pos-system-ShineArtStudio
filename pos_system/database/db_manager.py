import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import threading


class DatabaseManager:
    """Central database manager for all CRUD operations"""
    
    _lock = threading.Lock()
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection with timeout and WAL mode"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        conn = None
        try:
            with self._lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def execute_update(self, query: str, params: Tuple = ()) -> bool:
        """Execute INSERT, UPDATE, or DELETE query"""
        conn = None
        try:
            with self._lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def execute_insert(self, query: str, params: Tuple = ()) -> Optional[int]:
        """Execute INSERT query and return last inserted id"""
        conn = None
        try:
            with self._lock:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(query, params)
                last_id = cursor.lastrowid
                conn.commit()
                return last_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    # Customer operations
    def add_customer(self, full_name: str, mobile_number: str) -> Optional[int]:
        """Add a new customer"""
        query = '''
            INSERT INTO customers (full_name, mobile_number)
            VALUES (?, ?)
        '''
        return self.execute_insert(query, (full_name, mobile_number))
    
    def update_customer(self, customer_id: int, full_name: str, mobile_number: str) -> bool:
        """Update customer details"""
        query = '''
            UPDATE customers 
            SET full_name = ?, mobile_number = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (full_name, mobile_number, customer_id))
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer"""
        query = 'DELETE FROM customers WHERE id = ?'
        return self.execute_update(query, (customer_id,))
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        query = 'SELECT * FROM customers WHERE id = ?'
        results = self.execute_query(query, (customer_id,))
        return results[0] if results else None
    
    def get_customer_by_mobile(self, mobile_number: str) -> Optional[Dict[str, Any]]:
        """Get customer by mobile number"""
        query = 'SELECT * FROM customers WHERE mobile_number = ?'
        results = self.execute_query(query, (mobile_number,))
        return results[0] if results else None
    
    def get_all_customers(self) -> List[Dict[str, Any]]:
        """Get all customers"""
        query = 'SELECT * FROM customers ORDER BY full_name'
        return self.execute_query(query)
    
    def search_customers(self, search_term: str) -> List[Dict[str, Any]]:
        """Search customers by name or mobile"""
        query = '''
            SELECT * FROM customers 
            WHERE full_name LIKE ? OR mobile_number LIKE ?
            ORDER BY full_name
        '''
        search_pattern = f'%{search_term}%'
        return self.execute_query(query, (search_pattern, search_pattern))
    
    # Category operations
    def add_category(self, category_name: str, service_cost: float = None) -> Optional[int]:
        """Add a new category with optional service cost"""
        query = 'INSERT INTO categories (category_name, service_cost) VALUES (?, ?)'
        return self.execute_insert(query, (category_name, service_cost))
    
    def update_category(self, category_id: int, category_name: str, service_cost: float = None) -> bool:
        """Update a category with optional service cost"""
        query = '''
            UPDATE categories 
            SET category_name = ?, service_cost = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (category_name, service_cost, category_id))
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        query = 'DELETE FROM categories WHERE id = ?'
        return self.execute_update(query, (category_id,))
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        query = 'SELECT * FROM categories ORDER BY category_name'
        return self.execute_query(query)
    
    def get_category_by_id(self, category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID"""
        query = 'SELECT * FROM categories WHERE id = ?'
        results = self.execute_query(query, (category_id,))
        return results[0] if results else None
    
    def get_category_by_name(self, category_name: str) -> Optional[Dict[str, Any]]:
        """Get category by name"""
        query = 'SELECT * FROM categories WHERE category_name = ?'
        results = self.execute_query(query, (category_name,))
        return results[0] if results else None
    
    # Service operations
    def add_service(self, service_name: str, price: float, category_id: int = None) -> Optional[int]:
        """Add a new service"""
        query = 'INSERT INTO services (service_name, price, category_id) VALUES (?, ?, ?)'
        return self.execute_insert(query, (service_name, price, category_id))
    
    def update_service(self, service_id: int, service_name: str, price: float, category_id: int = None) -> bool:
        """Update a service"""
        query = '''
            UPDATE services 
            SET service_name = ?, price = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (service_name, price, category_id, service_id))
    
    def delete_service(self, service_id: int) -> bool:
        """Delete a service"""
        query = 'DELETE FROM services WHERE id = ?'
        return self.execute_update(query, (service_id,))
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services with category info"""
        query = '''
            SELECT s.*, c.category_name 
            FROM services s
            LEFT JOIN categories c ON s.category_id = c.id
            ORDER BY s.service_name
        '''
        return self.execute_query(query)
    
    def get_services_by_category(self, category_id: int) -> List[Dict[str, Any]]:
        """Get services filtered by category"""
        query = '''
            SELECT s.*, c.category_name 
            FROM services s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.category_id = ?
            ORDER BY s.service_name
        '''
        return self.execute_query(query, (category_id,))
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        query = '''
            SELECT s.*, c.category_name 
            FROM services s
            LEFT JOIN categories c ON s.category_id = c.id
            WHERE s.id = ?
        '''
        results = self.execute_query(query, (service_id,))
        return results[0] if results else None
    
    # Photo frame operations
    def add_photo_frame(self, frame_name: str, size: str, price: float, quantity: int,
                        buying_price: float = 0, selling_price: float = 0) -> Optional[int]:
        """Add a new photo frame with buying and selling prices"""
        query = '''
            INSERT INTO photo_frames (frame_name, size, price, quantity, buying_price, selling_price)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (frame_name, size, price, quantity, buying_price, selling_price))
    
    def update_photo_frame(self, frame_id: int, frame_name: str, size: str, 
                          price: float, quantity: int, buying_price: float = 0,
                          selling_price: float = 0) -> bool:
        """Update a photo frame with buying and selling prices"""
        query = '''
            UPDATE photo_frames 
            SET frame_name = ?, size = ?, price = ?, quantity = ?,
                buying_price = ?, selling_price = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (frame_name, size, price, quantity, 
                                          buying_price, selling_price, frame_id))
    
    def delete_photo_frame(self, frame_id: int) -> bool:
        """Delete a photo frame"""
        query = 'DELETE FROM photo_frames WHERE id = ?'
        return self.execute_update(query, (frame_id,))
    
    def get_all_photo_frames(self) -> List[Dict[str, Any]]:
        """Get all photo frames"""
        query = 'SELECT * FROM photo_frames ORDER BY frame_name, size'
        return self.execute_query(query)
    
    def get_photo_frame_by_id(self, frame_id: int) -> Optional[Dict[str, Any]]:
        """Get photo frame by ID"""
        query = 'SELECT * FROM photo_frames WHERE id = ?'
        results = self.execute_query(query, (frame_id,))
        return results[0] if results else None
    
    def update_frame_quantity(self, frame_id: int, quantity_change: int) -> bool:
        """Update frame quantity (positive or negative change)"""
        query = '''
            UPDATE photo_frames 
            SET quantity = quantity + ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (quantity_change, frame_id))
    
    # Invoice operations
    def create_invoice(self, invoice_number: str, customer_id: int, subtotal: float,
                      discount: float, total_amount: float, paid_amount: float,
                      balance_amount: float, created_by: int, 
                      category_service_cost: float = 0, advance_payment: float = 0,
                      guest_name: str = None, booking_id: int = None) -> Optional[int]:
        """Create a new invoice with category service cost and advance payment.
        For guest customers, customer_id is None and guest_name is provided.
        For bookings, booking_id links invoice to booking."""
        query = '''
            INSERT INTO invoices (invoice_number, booking_id, customer_id, guest_name, subtotal, discount,
                                category_service_cost, advance_payment, total_amount, 
                                paid_amount, balance_amount, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (invoice_number, booking_id, customer_id, guest_name, 
                                          subtotal, discount, category_service_cost, advance_payment,
                                          total_amount, paid_amount, balance_amount, created_by))
    
    def add_invoice_item(self, invoice_id: int, item_type: str, item_id: int,
                        item_name: str, quantity: int, unit_price: float,
                        total_price: float, buying_price: float = 0) -> Optional[int]:
        """Add an item to an invoice with optional buying price for frames"""
        query = '''
            INSERT INTO invoice_items (invoice_id, item_type, item_id, item_name,
                                      quantity, unit_price, total_price, buying_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (invoice_id, item_type, item_id, item_name,
                                          quantity, unit_price, total_price, buying_price))
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice with customer details (handles both registered and guest customers)"""
        query = '''
            SELECT i.*, 
                   COALESCE(c.full_name, i.guest_name) as full_name, 
                   c.mobile_number,
                   u.full_name as created_by_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            JOIN users u ON i.created_by = u.id
            WHERE i.id = ?
        '''
        results = self.execute_query(query, (invoice_id,))
        return results[0] if results else None
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice by invoice number (handles both registered and guest customers)"""
        query = '''
            SELECT i.*, 
                   COALESCE(c.full_name, i.guest_name) as full_name, 
                   c.mobile_number,
                   u.full_name as created_by_name
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            JOIN users u ON i.created_by = u.id
            WHERE i.invoice_number = ?
        '''
        results = self.execute_query(query, (invoice_number,))
        return results[0] if results else None
    
    def get_invoice_items(self, invoice_id: int) -> List[Dict[str, Any]]:
        """Get all items for an invoice"""
        query = 'SELECT * FROM invoice_items WHERE invoice_id = ?'
        return self.execute_query(query, (invoice_id,))
    
    def get_all_invoices(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all invoices with customer info (handles both registered and guest customers)"""
        query = '''
            SELECT i.*, 
                   COALESCE(c.full_name, i.guest_name) as full_name, 
                   c.mobile_number
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def search_invoices(self, search_term: str) -> List[Dict[str, Any]]:
        """Search invoices by invoice number or customer name/mobile (handles guest customers)"""
        query = '''
            SELECT i.*, 
                   COALESCE(c.full_name, i.guest_name) as full_name, 
                   c.mobile_number
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.invoice_number LIKE ? 
               OR c.full_name LIKE ? 
               OR c.mobile_number LIKE ?
               OR i.guest_name LIKE ?
            ORDER BY i.created_at DESC
        '''
        search_pattern = f'%{search_term}%'
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
    
    def generate_invoice_number(self) -> str:
        """Generate a unique invoice number"""
        query = 'SELECT MAX(id) as max_id FROM invoices'
        result = self.execute_query(query)
        max_id = result[0]['max_id'] if result and result[0]['max_id'] else 0
        return f"INV{str(max_id + 1).zfill(6)}"
    
    # Booking operations
    def create_booking(self, customer_name: str, mobile_number: str, 
                      photoshoot_category: str, full_amount: float,
                      advance_payment: float, booking_date: str,
                      location: str, description: str, created_by: int) -> Optional[int]:
        """Create a new booking"""
        balance_amount = full_amount - advance_payment
        query = '''
            INSERT INTO bookings (customer_name, mobile_number, photoshoot_category,
                                full_amount, advance_payment, balance_amount,
                                booking_date, location, description, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (customer_name, mobile_number, 
                                          photoshoot_category, full_amount,
                                          advance_payment, balance_amount,
                                          booking_date, location, description, 
                                          created_by))
    
    def update_booking(self, booking_id: int, customer_name: str, mobile_number: str,
                      photoshoot_category: str, full_amount: float,
                      advance_payment: float, booking_date: str,
                      location: str, description: str, status: str) -> bool:
        """Update a booking"""
        balance_amount = full_amount - advance_payment
        query = '''
            UPDATE bookings 
            SET customer_name = ?, mobile_number = ?, photoshoot_category = ?,
                full_amount = ?, advance_payment = ?, balance_amount = ?,
                booking_date = ?, location = ?, description = ?, status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (customer_name, mobile_number,
                                          photoshoot_category, full_amount,
                                          advance_payment, balance_amount,
                                          booking_date, location, description,
                                          status, booking_id))
    
    def delete_booking(self, booking_id: int) -> bool:
        """Delete a booking"""
        query = 'DELETE FROM bookings WHERE id = ?'
        return self.execute_update(query, (booking_id,))
    
    def get_all_bookings(self) -> List[Dict[str, Any]]:
        """Get all bookings"""
        query = '''
            SELECT b.*, u.full_name as created_by_name
            FROM bookings b
            JOIN users u ON b.created_by = u.id
            ORDER BY b.booking_date DESC, b.created_at DESC
        '''
        return self.execute_query(query)
    
    def get_booking_by_id(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """Get booking by ID"""
        query = '''
            SELECT b.*, u.full_name as created_by_name
            FROM bookings b
            JOIN users u ON b.created_by = u.id
            WHERE b.id = ?
        '''
        results = self.execute_query(query, (booking_id,))
        return results[0] if results else None
    
    def search_bookings(self, search_term: str) -> List[Dict[str, Any]]:
        """Search bookings by customer name or mobile"""
        query = '''
            SELECT b.*, u.full_name as created_by_name
            FROM bookings b
            JOIN users u ON b.created_by = u.id
            WHERE b.customer_name LIKE ? OR b.mobile_number LIKE ?
            ORDER BY b.booking_date DESC
        '''
        search_pattern = f'%{search_term}%'
        return self.execute_query(query, (search_pattern, search_pattern))
    
    # ==================== User Permissions Operations ====================
    
    def get_user_permissions(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get permissions for a user"""
        query = 'SELECT * FROM user_permissions WHERE user_id = ?'
        results = self.execute_query(query, (user_id,))
        return results[0] if results else None
    
    def create_default_permissions(self, user_id: int) -> bool:
        """Create default permissions for a new user (all enabled)"""
        query = '''
            INSERT OR IGNORE INTO user_permissions (user_id)
            VALUES (?)
        '''
        return self.execute_update(query, (user_id,))
    
    def update_user_permissions(self, user_id: int, permissions: Dict[str, bool]) -> bool:
        """Update permissions for a user"""
        # First ensure user has a permissions record
        self.create_default_permissions(user_id)
        
        # Build dynamic update query based on provided permissions
        valid_permissions = [
            'can_access_dashboard', 'can_access_billing', 'can_access_customers',
            'can_access_categories', 'can_access_services', 'can_access_frames',
            'can_access_bookings', 'can_access_invoices', 'can_access_support',
            'can_access_user_guide'
        ]
        
        set_clauses = []
        params = []
        for perm in valid_permissions:
            if perm in permissions:
                set_clauses.append(f"{perm} = ?")
                params.append(1 if permissions[perm] else 0)
        
        if not set_clauses:
            return True
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f'''
            UPDATE user_permissions 
            SET {', '.join(set_clauses)}
            WHERE user_id = ?
        '''
        return self.execute_update(query, tuple(params))
    
    def get_all_staff_users(self) -> List[Dict[str, Any]]:
        """Get all staff users for permission management"""
        query = '''
            SELECT id, username, full_name, is_active 
            FROM users 
            WHERE role = 'Staff'
            ORDER BY full_name
        '''
        return self.execute_query(query)
    
    def get_staff_with_permissions(self) -> List[Dict[str, Any]]:
        """Get all staff users with their permissions"""
        query = '''
            SELECT u.id, u.username, u.full_name, u.is_active,
                   COALESCE(p.can_access_dashboard, 1) as can_access_dashboard,
                   COALESCE(p.can_access_billing, 1) as can_access_billing,
                   COALESCE(p.can_access_customers, 1) as can_access_customers,
                   COALESCE(p.can_access_categories, 1) as can_access_categories,
                   COALESCE(p.can_access_services, 1) as can_access_services,
                   COALESCE(p.can_access_frames, 1) as can_access_frames,
                   COALESCE(p.can_access_bookings, 1) as can_access_bookings,
                   COALESCE(p.can_access_invoices, 1) as can_access_invoices,
                   COALESCE(p.can_access_support, 1) as can_access_support,
                   COALESCE(p.can_access_user_guide, 1) as can_access_user_guide
            FROM users u
            LEFT JOIN user_permissions p ON u.id = p.user_id
            WHERE u.role = 'Staff'
            ORDER BY u.full_name
        '''
        return self.execute_query(query)

    # ==================== Staff Daily Reports Operations ====================
    
    def get_all_users_for_reports(self) -> List[Dict[str, Any]]:
        """Get all users (staff and admin) for reporting"""
        query = '''
            SELECT id, username, full_name, role, is_active 
            FROM users 
            ORDER BY role DESC, full_name
        '''
        return self.execute_query(query)
    
    def get_staff_invoices_by_date(self, user_id: int, date: str) -> List[Dict[str, Any]]:
        """Get all invoices created by a staff member on a specific date"""
        query = '''
            SELECT i.*, c.full_name as customer_name, c.mobile_number as customer_mobile
            FROM invoices i
            LEFT JOIN customers c ON i.customer_id = c.id
            WHERE i.created_by = ? AND DATE(i.created_at) = ?
            ORDER BY i.created_at ASC
        '''
        return self.execute_query(query, (user_id, date))
    
    def get_staff_bookings_by_date(self, user_id: int, date: str) -> List[Dict[str, Any]]:
        """Get all bookings created by a staff member on a specific date"""
        query = '''
            SELECT * FROM bookings
            WHERE created_by = ? AND DATE(created_at) = ?
            ORDER BY created_at ASC
        '''
        return self.execute_query(query, (user_id, date))
    
    def get_staff_customers_by_date(self, user_id: int, date: str) -> List[Dict[str, Any]]:
        """Get all customers added on a specific date
        Note: Customers table doesn't have created_by, so we return all customers from that date
        """
        query = '''
            SELECT * FROM customers
            WHERE DATE(created_at) = ?
            ORDER BY created_at ASC
        '''
        return self.execute_query(query, (date,))
    
    def get_staff_daily_summary(self, user_id: int, date: str) -> Dict[str, Any]:
        """Get a summary of staff daily work"""
        invoices = self.get_staff_invoices_by_date(user_id, date)
        bookings = self.get_staff_bookings_by_date(user_id, date)
        
        total_invoice_amount = sum(inv.get('total_amount', 0) for inv in invoices)
        total_paid = sum(inv.get('paid_amount', 0) for inv in invoices)
        total_booking_amount = sum(b.get('full_amount', 0) for b in bookings)
        total_advance = sum(b.get('advance_payment', 0) for b in bookings)
        
        return {
            'invoice_count': len(invoices),
            'total_invoice_amount': total_invoice_amount,
            'total_paid': total_paid,
            'booking_count': len(bookings),
            'total_booking_amount': total_booking_amount,
            'total_advance': total_advance
        }
    
    # Bill operations (thermal receipts for normal sales)
    def create_bill(self, bill_number: str, customer_id: int, subtotal: float,
                   discount: float, total_amount: float, created_by: int,
                   service_charge: float = 0, cash_given: float = 0,
                   guest_name: str = None) -> Optional[int]:
        """Create a new bill (thermal receipt) for normal sales.
        For guest customers, customer_id is None and guest_name is provided."""
        query = '''
            INSERT INTO bills (bill_number, customer_id, guest_name, subtotal, discount,
                             service_charge, total_amount, cash_given, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (bill_number, customer_id, guest_name, subtotal,
                                          discount, service_charge, total_amount, 
                                          cash_given, created_by))
    
    def add_bill_item(self, bill_id: int, item_type: str, item_id: int,
                     item_name: str, quantity: int, unit_price: float,
                     total_price: float, buying_price: float = 0) -> Optional[int]:
        """Add an item to a bill"""
        query = '''
            INSERT INTO bill_items (bill_id, item_type, item_id, item_name,
                                   quantity, unit_price, total_price, buying_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (bill_id, item_type, item_id, item_name,
                                          quantity, unit_price, total_price, buying_price))
    
    def get_bill_by_id(self, bill_id: int) -> Optional[Dict[str, Any]]:
        """Get bill with customer details"""
        query = '''
            SELECT b.*, 
                   COALESCE(c.full_name, b.guest_name) as full_name,
                   c.mobile_number,
                   u.full_name as created_by_name
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.id
            JOIN users u ON b.created_by = u.id
            WHERE b.id = ?
        '''
        results = self.execute_query(query, (bill_id,))
        return results[0] if results else None
    
    def get_bill_items(self, bill_id: int) -> List[Dict[str, Any]]:
        """Get all items for a bill"""
        query = 'SELECT * FROM bill_items WHERE bill_id = ?'
        return self.execute_query(query, (bill_id,))
    
    def generate_bill_number(self) -> str:
        """Generate a unique bill number"""
        query = 'SELECT MAX(id) as max_id FROM bills'
        result = self.execute_query(query)
        max_id = result[0]['max_id'] if result and result[0]['max_id'] else 0
        return f"BILL{str(max_id + 1).zfill(6)}"
    
    def get_all_bills(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all bills with customer info"""
        query = '''
            SELECT b.*, 
                   COALESCE(c.full_name, b.guest_name) as full_name,
                   c.mobile_number
            FROM bills b
            LEFT JOIN customers c ON b.customer_id = c.id
            ORDER BY b.created_at DESC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))

