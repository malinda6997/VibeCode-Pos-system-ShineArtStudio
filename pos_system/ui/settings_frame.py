import customtkinter as ctk
from tkinter import filedialog
from services.settings_service import SettingsService
from ui.components import Toast, MessageDialog


class SettingsFrame(ctk.CTkFrame):
    """Settings page for admin configuration - Admin only"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.settings_service = SettingsService()
        
        # Admin check
        if not self.auth_manager.is_admin():
            self.show_access_denied()
            return
        
        self.create_widgets()
        self.load_settings()
    
    def show_access_denied(self):
        """Show access denied message for non-admin users"""
        access_frame = ctk.CTkFrame(self, fg_color="transparent")
        access_frame.pack(expand=True)
        
        ctk.CTkLabel(
            access_frame,
            text="🚫",
            font=ctk.CTkFont(size=60)
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            access_frame,
            text="Access Denied",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ff6b6b"
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            access_frame,
            text="Only administrators can access settings.",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        ).pack()
    
    def create_widgets(self):
        """Create settings widgets"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main scrollable frame
        main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Studio Information Section
        studio_section = self.create_section(main_scroll, "Studio Information")
        
        # Studio Name
        self.studio_name_entry = self.create_setting_field(
            studio_section, "Studio Name:", "Shine Art Photography Studio"
        )
        
        # Contact Number
        self.contact_entry = self.create_setting_field(
            studio_section, "Contact Number:", ""
        )
        
        # Email
        self.email_entry = self.create_setting_field(
            studio_section, "Email Address:", ""
        )
        
        # Address
        ctk.CTkLabel(
            studio_section,
            text="Address:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        self.address_text = ctk.CTkTextbox(studio_section, height=80, font=ctk.CTkFont(size=13))
        self.address_text.pack(fill="x", pady=(0, 10))
        
        # Invoice Settings Section
        invoice_section = self.create_section(main_scroll, "Invoice Settings")
        
        # Currency
        ctk.CTkLabel(
            invoice_section,
            text="Currency:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.currency_combo = ctk.CTkComboBox(
            invoice_section,
            values=["LKR", "USD", "EUR", "GBP", "INR"],
            height=40,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.currency_combo.pack(fill="x", pady=(0, 10))
        self.currency_combo.set("LKR")
        
        # Invoice Footer
        ctk.CTkLabel(
            invoice_section,
            text="Invoice Footer Text:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        self.footer_text = ctk.CTkTextbox(invoice_section, height=80, font=ctk.CTkFont(size=13))
        self.footer_text.pack(fill="x", pady=(0, 10))
        
        # Tax Settings
        tax_frame = ctk.CTkFrame(invoice_section, fg_color="transparent")
        tax_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            tax_frame,
            text="Tax Rate (%):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")
        
        self.tax_entry = ctk.CTkEntry(tax_frame, width=100, height=40, font=ctk.CTkFont(size=13))
        self.tax_entry.pack(side="left", padx=15)
        self.tax_entry.insert(0, "0")
        
        # Appearance Section
        appearance_section = self.create_section(main_scroll, "Appearance")
        
        # Theme
        ctk.CTkLabel(
            appearance_section,
            text="Theme Mode:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.theme_combo = ctk.CTkComboBox(
            appearance_section,
            values=["Dark", "Light", "System"],
            height=40,
            font=ctk.CTkFont(size=13),
            state="readonly",
            command=self.change_theme
        )
        self.theme_combo.pack(fill="x", pady=(0, 10))
        self.theme_combo.set("Dark")
        
        # Low Stock Threshold
        ctk.CTkLabel(
            appearance_section,
            text="Low Stock Alert Threshold:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        self.low_stock_entry = ctk.CTkEntry(appearance_section, height=40, font=ctk.CTkFont(size=13))
        self.low_stock_entry.pack(fill="x", pady=(0, 10))
        self.low_stock_entry.insert(0, "5")
        
        # Backup Section
        backup_section = self.create_section(main_scroll, "Backup & Data")
        
        backup_btn_frame = ctk.CTkFrame(backup_section, fg_color="transparent")
        backup_btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            backup_btn_frame,
            text="📁 Backup Database",
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            command=self.backup_database,
            width=200
        ).pack(side="left", padx=(0, 15))
        
        ctk.CTkButton(
            backup_btn_frame,
            text="📥 Restore Database",
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ffd93d",
            text_color="#1a1a2e",
            hover_color="#e6c235",
            command=self.restore_database,
            width=200
        ).pack(side="left")
        
        # Save Button
        save_frame = ctk.CTkFrame(self, fg_color="transparent")
        save_frame.pack(fill="x", padx=30, pady=20)
        
        ctk.CTkButton(
            save_frame,
            text="💾 Save Settings",
            height=50,
            width=200,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00cc6a",
            command=self.save_settings
        ).pack(side="right")
        
        ctk.CTkButton(
            save_frame,
            text="🔄 Reset to Default",
            height=50,
            width=200,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            command=self.reset_settings
        ).pack(side="right", padx=15)
    
    def create_section(self, parent, title: str) -> ctk.CTkFrame:
        """Create a settings section"""
        section = ctk.CTkFrame(parent, fg_color="#1e1e3f", corner_radius=15)
        section.pack(fill="x", pady=10)
        
        section_title = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        section_title.pack(anchor="w", padx=25, pady=(20, 10))
        
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=25, pady=(0, 20))
        
        return content
    
    def create_setting_field(self, parent, label: str, default: str = "") -> ctk.CTkEntry:
        """Create a setting input field"""
        ctk.CTkLabel(
            parent,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        entry = ctk.CTkEntry(parent, height=40, font=ctk.CTkFont(size=13))
        entry.pack(fill="x", pady=(0, 10))
        if default:
            entry.insert(0, default)
        
        return entry
    
    def load_settings(self):
        """Load current settings"""
        all_settings = self.settings_service.get_all_settings()
        
        # Helper to get setting value
        def get_val(key, default=""):
            if key in all_settings:
                return all_settings[key].get('setting_value', default) if isinstance(all_settings[key], dict) else all_settings[key]
            return default
        
        self.studio_name_entry.delete(0, "end")
        self.studio_name_entry.insert(0, get_val("studio_name", "Shine Art Photography Studio"))
        
        self.contact_entry.delete(0, "end")
        self.contact_entry.insert(0, get_val("contact_number", ""))
        
        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, get_val("email", ""))
        
        self.address_text.delete("1.0", "end")
        self.address_text.insert("1.0", get_val("address", ""))
        
        self.currency_combo.set(get_val("currency", "LKR"))
        
        self.footer_text.delete("1.0", "end")
        self.footer_text.insert("1.0", get_val("invoice_footer", "Thank you for your business!"))
        
        self.tax_entry.delete(0, "end")
        self.tax_entry.insert(0, get_val("tax_rate", "0"))
        
        self.theme_combo.set(get_val("theme_mode", "Dark"))
        
        self.low_stock_entry.delete(0, "end")
        self.low_stock_entry.insert(0, get_val("low_stock_threshold", "5"))
    
    def save_settings(self):
        """Save all settings"""
        settings = {
            "studio_name": self.studio_name_entry.get().strip(),
            "contact_number": self.contact_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "address": self.address_text.get("1.0", "end-1c").strip(),
            "currency": self.currency_combo.get(),
            "invoice_footer": self.footer_text.get("1.0", "end-1c").strip(),
            "tax_rate": self.tax_entry.get().strip(),
            "theme_mode": self.theme_combo.get(),
            "low_stock_threshold": self.low_stock_entry.get().strip()
        }
        
        self.settings_service.update_multiple_settings(settings)
        Toast.success(self, "Settings saved successfully!")
    
    def reset_settings(self):
        """Reset to default settings"""
        if Toast.confirm(self, "Reset Settings", "Reset all settings to default values?",
                        "Reset", "Cancel", "🔄", "#ffd93d"):
            self.settings_service.reset_to_defaults()
            self.load_settings()
            Toast.success(self, "Settings reset to defaults")
    
    def change_theme(self, theme: str):
        """Change application theme"""
        ctk.set_appearance_mode(theme.lower())
    
    def backup_database(self):
        """Backup database file"""
        import shutil
        from datetime import datetime
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("SQLite Database", "*.db")],
            initialfilename=f"pos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        
        if filepath:
            try:
                import os
                db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pos_database.db")
                shutil.copy2(db_path, filepath)
                Toast.success(self, "Database backed up successfully!")
            except Exception as e:
                Toast.error(self, f"Backup failed: {e}")
    
    def restore_database(self):
        """Restore database from backup"""
        filepath = filedialog.askopenfilename(
            filetypes=[("SQLite Database", "*.db")]
        )
        
        if filepath:
            if Toast.confirm(self, "Restore Database", "This will replace all current data. Continue?",
                           "Restore", "Cancel", "⚠️", "#ff6b6b"):
                try:
                    import shutil
                    import os
                    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pos_database.db")
                    shutil.copy2(filepath, db_path)
                    Toast.success(self, "Database restored! Please restart the app.")
                except Exception as e:
                    Toast.error(self, f"Restore failed: {e}")
