import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple


class DatabaseManager:
    """Central database manager for all CRUD operations"""
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
    
    def execute_update(self, query: str, params: Tuple = ()) -> bool:
        """Execute INSERT, UPDATE, or DELETE query"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def execute_insert(self, query: str, params: Tuple = ()) -> Optional[int]:
        """Execute INSERT query and return last inserted id"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            last_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return last_id
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    # Customer operations
    def add_customer(self, full_name: str, mobile_number: str) -> Optional[int]:
        """Add a new customer"""
        query = '''
            INSERT INTO customers (full_name, mobile_number)
            VALUES (?, ?)
        '''
        return self.execute_insert(query, (full_name, mobile_number))
    
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
    
    # Service operations
    def add_service(self, service_name: str, price: float) -> Optional[int]:
        """Add a new service"""
        query = 'INSERT INTO services (service_name, price) VALUES (?, ?)'
        return self.execute_insert(query, (service_name, price))
    
    def update_service(self, service_id: int, service_name: str, price: float) -> bool:
        """Update a service"""
        query = '''
            UPDATE services 
            SET service_name = ?, price = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (service_name, price, service_id))
    
    def delete_service(self, service_id: int) -> bool:
        """Delete a service"""
        query = 'DELETE FROM services WHERE id = ?'
        return self.execute_update(query, (service_id,))
    
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services"""
        query = 'SELECT * FROM services ORDER BY service_name'
        return self.execute_query(query)
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        query = 'SELECT * FROM services WHERE id = ?'
        results = self.execute_query(query, (service_id,))
        return results[0] if results else None
    
    # Photo frame operations
    def add_photo_frame(self, frame_name: str, size: str, price: float, quantity: int) -> Optional[int]:
        """Add a new photo frame"""
        query = '''
            INSERT INTO photo_frames (frame_name, size, price, quantity)
            VALUES (?, ?, ?, ?)
        '''
        return self.execute_insert(query, (frame_name, size, price, quantity))
    
    def update_photo_frame(self, frame_id: int, frame_name: str, size: str, 
                          price: float, quantity: int) -> bool:
        """Update a photo frame"""
        query = '''
            UPDATE photo_frames 
            SET frame_name = ?, size = ?, price = ?, quantity = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        return self.execute_update(query, (frame_name, size, price, quantity, frame_id))
    
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
                      balance_amount: float, created_by: int) -> Optional[int]:
        """Create a new invoice"""
        query = '''
            INSERT INTO invoices (invoice_number, customer_id, subtotal, discount,
                                total_amount, paid_amount, balance_amount, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (invoice_number, customer_id, subtotal, 
                                          discount, total_amount, paid_amount, 
                                          balance_amount, created_by))
    
    def add_invoice_item(self, invoice_id: int, item_type: str, item_id: int,
                        item_name: str, quantity: int, unit_price: float,
                        total_price: float) -> Optional[int]:
        """Add an item to an invoice"""
        query = '''
            INSERT INTO invoice_items (invoice_id, item_type, item_id, item_name,
                                      quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        return self.execute_insert(query, (invoice_id, item_type, item_id, item_name,
                                          quantity, unit_price, total_price))
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        """Get invoice with customer details"""
        query = '''
            SELECT i.*, c.full_name, c.mobile_number, u.full_name as created_by_name
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            JOIN users u ON i.created_by = u.id
            WHERE i.id = ?
        '''
        results = self.execute_query(query, (invoice_id,))
        return results[0] if results else None
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice by invoice number"""
        query = '''
            SELECT i.*, c.full_name, c.mobile_number, u.full_name as created_by_name
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
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
        """Get all invoices with customer info"""
        query = '''
            SELECT i.*, c.full_name, c.mobile_number
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def search_invoices(self, search_term: str) -> List[Dict[str, Any]]:
        """Search invoices by invoice number or customer name/mobile"""
        query = '''
            SELECT i.*, c.full_name, c.mobile_number
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE i.invoice_number LIKE ? 
               OR c.full_name LIKE ? 
               OR c.mobile_number LIKE ?
            ORDER BY i.created_at DESC
        '''
        search_pattern = f'%{search_term}%'
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern))
    
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
