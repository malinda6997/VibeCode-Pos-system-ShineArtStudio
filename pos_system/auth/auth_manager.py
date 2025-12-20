import hashlib
import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime


class AuthManager:
    """Handle user authentication and password management"""
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        self.current_user = None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return self.hash_password(password) == password_hash
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user and return user info if successful"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM users 
                WHERE username = ? AND is_active = 1
            ''', (username,))
            
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user['password_hash']):
                self.current_user = dict(user)
                
                # Update last_login timestamp
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
                cursor.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (current_time, user['id']))
                conn.commit()
                
                # Store last_login in current_user
                self.current_user['last_login'] = current_time
                
                # Load user permissions
                self._load_user_permissions(cursor, user['id'], user['role'])
                
                conn.close()
                return self.current_user
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            print(f"Authentication error: {e}")
            return None
    
    def _load_user_permissions(self, cursor, user_id: int, role: str):
        """Load user permissions into current_user dict"""
        # Admin has all permissions
        if role == 'Admin':
            self.current_user['permissions'] = {
                'can_access_dashboard': True,
                'can_access_billing': True,
                'can_access_customers': True,
                'can_access_categories': True,
                'can_access_services': True,
                'can_access_frames': True,
                'can_access_bookings': True,
                'can_access_invoices': True,
                'can_access_support': True,
                'can_access_user_guide': True,
                'can_access_users': True,
                'can_access_settings': True,
                'can_access_permissions': True,
                'can_access_profile': True
            }
        else:
            # Load staff permissions from database
            cursor.execute('''
                SELECT * FROM user_permissions WHERE user_id = ?
            ''', (user_id,))
            perm_row = cursor.fetchone()
            
            if perm_row:
                perm_dict = dict(perm_row)
                self.current_user['permissions'] = {
                    'can_access_dashboard': bool(perm_dict.get('can_access_dashboard', 1)),
                    'can_access_billing': bool(perm_dict.get('can_access_billing', 1)),
                    'can_access_customers': bool(perm_dict.get('can_access_customers', 1)),
                    'can_access_categories': bool(perm_dict.get('can_access_categories', 1)),
                    'can_access_services': bool(perm_dict.get('can_access_services', 1)),
                    'can_access_frames': bool(perm_dict.get('can_access_frames', 1)),
                    'can_access_bookings': bool(perm_dict.get('can_access_bookings', 1)),
                    'can_access_invoices': bool(perm_dict.get('can_access_invoices', 1)),
                    'can_access_support': bool(perm_dict.get('can_access_support', 1)),
                    'can_access_user_guide': bool(perm_dict.get('can_access_user_guide', 1)),
                    'can_access_users': False,
                    'can_access_settings': False,
                    'can_access_permissions': False,
                    'can_access_profile': True
                }
            else:
                # Default permissions for staff (all enabled except admin features)
                self.current_user['permissions'] = {
                    'can_access_dashboard': True,
                    'can_access_billing': True,
                    'can_access_customers': True,
                    'can_access_categories': True,
                    'can_access_services': True,
                    'can_access_frames': True,
                    'can_access_bookings': True,
                    'can_access_invoices': True,
                    'can_access_support': True,
                    'can_access_user_guide': True,
                    'can_access_users': False,
                    'can_access_settings': False,
                    'can_access_permissions': False,
                    'can_access_profile': True
                }
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if current user has a specific permission"""
        if not self.current_user:
            return False
        permissions = self.current_user.get('permissions', {})
        return permissions.get(permission_name, False)
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Check if a user is currently authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return self.current_user
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user and self.current_user['role'] == 'Admin'
    
    def is_staff(self) -> bool:
        """Check if current user is staff"""
        return self.current_user and self.current_user['role'] == 'Staff'
    
    def get_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return self.current_user['id'] if self.current_user else None
    
    def get_user_role(self) -> Optional[str]:
        """Get current user role"""
        return self.current_user['role'] if self.current_user else None
    
    def get_user_name(self) -> Optional[str]:
        """Get current user full name"""
        return self.current_user['full_name'] if self.current_user else None
    
    def change_password(self, user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            new_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?
                WHERE id = ?
            ''', (new_hash, user_id))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Password change error: {e}")
            return False
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str) -> Optional[int]:
        """Create a new user (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, role, full_name))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return user_id
            
        except sqlite3.Error as e:
            print(f"User creation error: {e}")
            return None
    
    def get_all_users(self) -> list:
        """Get all users (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, username, role, full_name, is_active FROM users')
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return users
            
        except sqlite3.Error as e:
            print(f"Error fetching users: {e}")
            return []
    
    def toggle_user_status(self, user_id: int) -> bool:
        """Activate or deactivate a user (admin only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
                WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Error toggling user status: {e}")
            return False
