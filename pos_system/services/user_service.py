import sqlite3
import hashlib
from typing import List, Dict, Any, Optional


class UserService:
    """User management service"""
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, role, full_name, is_active, created_at 
                FROM users ORDER BY id
            ''')
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return users
        except sqlite3.Error as e:
            print(f"Error getting users: {e}")
            return []
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, role, full_name, is_active, created_at, profile_picture 
                FROM users WHERE id = ?
            ''', (user_id,))
            user = cursor.fetchone()
            conn.close()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_profile_picture(self, user_id: int, picture_path: str) -> bool:
        """Update user profile picture"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET profile_picture = ? WHERE id = ?
            ''', (picture_path, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating profile picture: {e}")
            return False
    
    def get_profile_picture(self, user_id: int) -> Optional[str]:
        """Get user profile picture path"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT profile_picture FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error getting profile picture: {e}")
            return None
    
    def create_user(self, username: str, password: str, role: str, 
                   full_name: str) -> Optional[int]:
        """Create new user"""
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
        except sqlite3.IntegrityError:
            print("Username already exists")
            return None
        except sqlite3.Error as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, user_id: int, username: str, role: str, 
                   full_name: str, is_active: int) -> bool:
        """Update user details (without password)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET username = ?, role = ?, full_name = ?, is_active = ?
                WHERE id = ?
            ''', (username, role, full_name, is_active, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating user: {e}")
            return False
    
    def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            password_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE users SET password_hash = ? WHERE id = ?
            ''', (password_hash, user_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating password: {e}")
            return False
    
    def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user's current password"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0] == self.hash_password(password)
            return False
        except sqlite3.Error as e:
            print(f"Error verifying password: {e}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """Delete user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            return False
    
    def toggle_user_status(self, user_id: int) -> bool:
        """Toggle user active status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error toggling status: {e}")
            return False
    
    def username_exists(self, username: str, exclude_id: int = None) -> bool:
        """Check if username exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if exclude_id:
                cursor.execute(
                    'SELECT COUNT(*) FROM users WHERE username = ? AND id != ?',
                    (username, exclude_id)
                )
            else:
                cursor.execute(
                    'SELECT COUNT(*) FROM users WHERE username = ?',
                    (username,)
                )
            count = cursor.fetchone()[0]
            conn.close()
            return count > 0
        except sqlite3.Error:
            return False
