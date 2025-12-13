import sqlite3
from typing import Dict, Any, Optional


class SettingsService:
    """Manage application settings stored in database"""
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        self._ensure_settings_table()
        self._initialize_default_settings()
    
    def _ensure_settings_table(self):
        """Create settings table if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT,
                setting_type TEXT DEFAULT 'string',
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def _initialize_default_settings(self):
        """Initialize default settings if not exist"""
        defaults = {
            'studio_name': ('Shine Art Studio', 'string', 'Studio display name'),
            'contact_number': ('0771234567', 'string', 'Studio contact number'),
            'address': ('123 Main Street, Colombo', 'string', 'Studio address'),
            'email': ('info@shineartstudio.com', 'string', 'Studio email'),
            'invoice_footer': ('Thank you for your business!', 'string', 'Invoice footer message'),
            'invoice_prefix': ('INV', 'string', 'Invoice number prefix'),
            'currency': ('LKR', 'string', 'Currency code'),
            'theme_mode': ('dark', 'string', 'Application theme mode'),
            'app_version': ('1.0.0', 'string', 'Application version'),
        }
        
        for key, (value, stype, desc) in defaults.items():
            if not self.get_setting(key):
                self.set_setting(key, value, stype, desc)
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT setting_value FROM settings WHERE setting_key = ?', (key,))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error getting setting: {e}")
            return None
    
    def set_setting(self, key: str, value: str, setting_type: str = 'string', 
                   description: str = '') -> bool:
        """Set or update a setting"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (setting_key, setting_value, setting_type, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(setting_key) DO UPDATE SET 
                    setting_value = excluded.setting_value,
                    updated_at = CURRENT_TIMESTAMP
            ''', (key, value, setting_type, description))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error setting: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM settings ORDER BY setting_key')
            rows = cursor.fetchall()
            conn.close()
            return {row['setting_key']: dict(row) for row in rows}
        except sqlite3.Error as e:
            print(f"Error getting all settings: {e}")
            return {}
    
    def update_multiple_settings(self, settings: Dict[str, str]) -> bool:
        """Update multiple settings at once"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for key, value in settings.items():
                cursor.execute('''
                    INSERT INTO settings (setting_key, setting_value, setting_type, description)
                    VALUES (?, ?, 'string', '')
                    ON CONFLICT(setting_key) DO UPDATE SET 
                        setting_value = excluded.setting_value,
                        updated_at = CURRENT_TIMESTAMP
                ''', (key, value))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Error updating settings: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values"""
        defaults = {
            'studio_name': 'Shine Art Studio',
            'contact_number': '0771234567',
            'address': '123 Main Street, Colombo',
            'email': 'info@shineartstudio.com',
            'invoice_footer': 'Thank you for your business!',
            'invoice_prefix': 'INV',
            'currency': 'LKR',
            'theme_mode': 'Dark',
            'tax_rate': '0',
            'low_stock_threshold': '5',
        }
        return self.update_multiple_settings(defaults)
