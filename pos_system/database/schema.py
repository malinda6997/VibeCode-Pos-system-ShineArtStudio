import sqlite3
import os
from datetime import datetime

class DatabaseSchema:
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """Create all database tables"""
        self.connect()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('Admin', 'Staff')),
                full_name TEXT NOT NULL,
                profile_picture TEXT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Add profile_picture column if not exists (for existing databases)
        try:
            self.cursor.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT DEFAULT NULL')
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Customers table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                mobile_number TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Services table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Photo frames table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS photo_frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                frame_name TEXT NOT NULL,
                size TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Invoices table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                discount REAL DEFAULT 0,
                total_amount REAL NOT NULL,
                paid_amount REAL NOT NULL,
                balance_amount REAL NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        # Invoice items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                item_type TEXT NOT NULL CHECK(item_type IN ('Service', 'Frame')),
                item_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit_price REAL NOT NULL,
                total_price REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id)
            )
        ''')
        
        # Bookings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                mobile_number TEXT NOT NULL,
                photoshoot_category TEXT NOT NULL,
                full_amount REAL NOT NULL,
                advance_payment REAL NOT NULL,
                balance_amount REAL NOT NULL,
                booking_date DATE NOT NULL,
                location TEXT,
                description TEXT,
                status TEXT DEFAULT 'Pending' CHECK(status IN ('Pending', 'Completed', 'Cancelled')),
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
        self.close()
        
    def initialize_default_data(self):
        """Insert default data for testing"""
        self.connect()
        
        # Check if default admin exists
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if self.cursor.fetchone()[0] == 0:
            # Import here to avoid circular dependency
            from auth.auth_manager import AuthManager
            auth_manager = AuthManager(self.db_path)
            
            # Create default admin
            admin_hash = auth_manager.hash_password('admin123')
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_hash, 'Admin', 'System Administrator'))
            
            # Create default staff
            staff_hash = auth_manager.hash_password('staff123')
            self.cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            ''', ('staff', staff_hash, 'Staff', 'Staff User'))
        
        # Add some default services
        self.cursor.execute("SELECT COUNT(*) FROM services")
        if self.cursor.fetchone()[0] == 0:
            default_services = [
                ('ID Photo', 500.00),
                ('Passport Photo', 800.00),
                ('Studio Portrait', 3500.00),
                ('Wedding Photography', 75000.00),
                ('Event Photography', 25000.00),
                ('Product Photography', 15000.00)
            ]
            self.cursor.executemany('''
                INSERT INTO services (service_name, price)
                VALUES (?, ?)
            ''', default_services)
        
        # Add some default photo frames
        self.cursor.execute("SELECT COUNT(*) FROM photo_frames")
        if self.cursor.fetchone()[0] == 0:
            default_frames = [
                ('Wooden Frame', '4x6', 1200.00, 50),
                ('Wooden Frame', '5x7', 1800.00, 40),
                ('Wooden Frame', '8x10', 2500.00, 30),
                ('Metal Frame', '4x6', 1500.00, 35),
                ('Metal Frame', '5x7', 2200.00, 25),
                ('Metal Frame', '8x10', 3000.00, 20),
                ('Acrylic Frame', '4x6', 2000.00, 15),
                ('Acrylic Frame', '5x7', 2800.00, 15),
                ('Acrylic Frame', '8x10', 3800.00, 10)
            ]
            self.cursor.executemany('''
                INSERT INTO photo_frames (frame_name, size, price, quantity)
                VALUES (?, ?, ?, ?)
            ''', default_frames)
        
        self.conn.commit()
        self.close()
        
    def reset_database(self):
        """Drop all tables and recreate (use with caution)"""
        self.connect()
        
        tables = ['invoice_items', 'invoices', 'bookings', 'photo_frames', 
                  'services', 'customers', 'users']
        
        for table in tables:
            self.cursor.execute(f'DROP TABLE IF EXISTS {table}')
        
        self.conn.commit()
        self.close()
        
        self.create_tables()
        self.initialize_default_data()


def initialize_database(db_path='pos_database.db'):
    """Main function to initialize the database"""
    db = DatabaseSchema(db_path)
    db.create_tables()
    db.initialize_default_data()
    print(f"Database initialized successfully at: {os.path.abspath(db_path)}")
    return db_path


if __name__ == "__main__":
    initialize_database()
