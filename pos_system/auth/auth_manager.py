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
                
                conn.close()
                return self.current_user
            
            conn.close()
            return None
            
        except sqlite3.Error as e:
            print(f"Authentication error: {e}")
            return None
    
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
