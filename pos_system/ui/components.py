import customtkinter as ctk
from tkinter import messagebox
from typing import Callable, Optional


class LoginWindow(ctk.CTkToplevel):
    """Login window for user authentication"""
    
    def __init__(self, parent, auth_manager, on_success: Callable):
        super().__init__(parent)
        
        self.auth_manager = auth_manager
        self.on_success = on_success
        
        self.title("Shine Art Studio - Login")
        self.geometry("450x550")
        self.resizable(False, False)
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"450x550+{x}+{y}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create login form widgets"""
        
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Shine Art Studio",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Photography POS System",
            font=ctk.CTkFont(size=16)
        )
        subtitle_label.pack(pady=(0, 40))
        
        # Login form
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="both", expand=True, pady=20)
        
        # Username
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        username_label.pack(pady=(30, 5), padx=30, anchor="w")
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter username",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(pady=(0, 20), padx=30, fill="x")
        
        # Password
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        password_label.pack(pady=(0, 5), padx=30, anchor="w")
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter password",
            show="●",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(pady=(0, 30), padx=30, fill="x")
        
        # Login button
        login_btn = ctk.CTkButton(
            form_frame,
            text="Login",
            command=self.handle_login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        login_btn.pack(pady=(0, 20), padx=30, fill="x")
        
        # Info text
        info_label = ctk.CTkLabel(
            form_frame,
            text="Default credentials:\nAdmin: admin / admin123\nStaff: staff / staff123",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.pack(pady=(10, 20))
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Focus username
        self.username_entry.focus()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        user = self.auth_manager.authenticate(username, password)
        
        if user:
            messagebox.showinfo("Success", f"Welcome, {user['full_name']}!")
            self.destroy()
            self.on_success(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')
            self.username_entry.focus()


class MessageDialog:
    """Utility class for showing messages"""
    
    @staticmethod
    def show_error(title: str, message: str):
        """Show error message"""
        messagebox.showerror(title, message)
    
    @staticmethod
    def show_success(title: str, message: str):
        """Show success message"""
        messagebox.showinfo(title, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """Show warning message"""
        messagebox.showwarning(title, message)
    
    @staticmethod
    def show_confirm(title: str, message: str) -> bool:
        """Show confirmation dialog"""
        return messagebox.askyesno(title, message)


class BaseFrame(ctk.CTkFrame):
    """Base frame with common functionality"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        
    def validate_number(self, value: str, allow_decimal: bool = False) -> bool:
        """Validate if value is a number"""
        if not value:
            return False
        try:
            if allow_decimal:
                float(value)
            else:
                int(value)
            return True
        except ValueError:
            return False
    
    def validate_mobile(self, mobile: str) -> bool:
        """Validate mobile number (10 digits)"""
        return mobile.isdigit() and len(mobile) == 10
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.auth_manager.is_admin()
