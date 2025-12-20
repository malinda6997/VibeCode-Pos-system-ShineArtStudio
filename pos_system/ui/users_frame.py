import customtkinter as ctk
from tkinter import ttk
from services.user_service import UserService
from ui.components import Toast


class UsersManagementFrame(ctk.CTkFrame):
    """User management interface (Admin only)"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.user_service = UserService()
        self.selected_user_id = None
        self.editing_mode = False
        
        # Admin check
        if not self.auth_manager.is_admin():
            self.show_access_denied()
            return
        
        self.create_widgets()
        self.load_users()
    
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
            text="Only administrators can manage users.",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        ).pack()
    
    def create_widgets(self):
        """Create user management widgets"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="👤 User Management",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Left panel - Form (scrollable)
        left = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15, width=400)
        left.pack(side="left", fill="y", padx=(0, 15), pady=0)
        left.pack_propagate(False)
        
        # Scrollable container for form
        left_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        left_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        form_title = ctk.CTkLabel(
            left_scroll,
            text="User Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.pack(pady=(15, 10))
        
        # Form fields container
        form = ctk.CTkFrame(left_scroll, fg_color="transparent")
        form.pack(fill="x", padx=20)
        
        # Full Name
        ctk.CTkLabel(form, text="Full Name:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.fullname_entry = ctk.CTkEntry(form, height=38, font=ctk.CTkFont(size=13))
        self.fullname_entry.pack(fill="x", pady=(0, 5))
        
        # Username
        ctk.CTkLabel(form, text="Username:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.username_entry = ctk.CTkEntry(form, height=38, font=ctk.CTkFont(size=13))
        self.username_entry.pack(fill="x", pady=(0, 5))
        
        # Password
        ctk.CTkLabel(form, text="Password:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.password_entry = ctk.CTkEntry(form, height=38, font=ctk.CTkFont(size=13), show="●")
        self.password_entry.pack(fill="x", pady=(0, 5))
        
        # Confirm Password
        ctk.CTkLabel(form, text="Confirm Password:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.confirm_password_entry = ctk.CTkEntry(form, height=38, font=ctk.CTkFont(size=13), show="●")
        self.confirm_password_entry.pack(fill="x", pady=(0, 5))
        
        # Role
        ctk.CTkLabel(form, text="Role:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.role_combo = ctk.CTkComboBox(
            form, 
            values=["Admin", "Staff"],
            height=38,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.role_combo.pack(fill="x", pady=(0, 5))
        self.role_combo.set("Staff")
        
        # Status
        ctk.CTkLabel(form, text="Status:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(5, 3))
        self.status_combo = ctk.CTkComboBox(
            form,
            values=["Active", "Disabled"],
            height=38,
            font=ctk.CTkFont(size=13),
            state="readonly"
        )
        self.status_combo.pack(fill="x", pady=(0, 10))
        self.status_combo.set("Active")
        
        # Buttons
        btn_frame = ctk.CTkFrame(left_scroll, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Add User",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            command=lambda: self.add_user()
        )
        self.add_btn.pack(fill="x", pady=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update User",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ffd93d",
            text_color="#1a1a2e",
            hover_color="#e6c235",
            command=self.update_user,
            state="disabled"
        )
        self.update_btn.pack(fill="x", pady=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete User",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            command=self.delete_user,
            state="disabled"
        )
        self.delete_btn.pack(fill="x", pady=5)
        
        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Clear Form",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            command=self.clear_form
        )
        self.clear_btn.pack(fill="x", pady=5)
        
        # Right panel - Users list
        right = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        right.pack(side="right", fill="both", expand=True)
        
        list_title = ctk.CTkLabel(
            right,
            text="All Users",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.pack(pady=(20, 15))
        
        # Users table
        table_frame = ctk.CTkFrame(right, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        columns = ("ID", "Full Name", "Username", "Role", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Full Name", text="Full Name")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Role", text="Role")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Full Name", width=180)
        self.tree.column("Username", width=120)
        self.tree.column("Role", width=80, anchor="center")
        self.tree.column("Status", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_user(self):
        """Add new user"""
        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_password_entry.get()
        role = self.role_combo.get()
        
        if not fullname:
            Toast.error(self, "Please enter full name")
            return
        
        if not username:
            Toast.error(self, "Please enter username")
            return
        
        if len(username) < 3:
            Toast.error(self, "Username must be at least 3 characters")
            return
            
        if not password:
            Toast.error(self, "Please enter password")
            return
        
        if len(password) < 6:
            Toast.error(self, "Password must be at least 6 characters")
            return
        
        if password != confirm:
            Toast.error(self, "Passwords do not match")
            return
        
        if self.user_service.username_exists(username):
            Toast.error(self, "Username already exists")
            return
        
        user_id = self.user_service.create_user(username, password, role, fullname)
        
        if user_id:
            Toast.success(self, "User created successfully!")
            self.clear_form()
            self.load_users()
        else:
            Toast.error(self, "Failed to create user")
    
    def update_user(self):
        """Update selected user"""
        if not self.selected_user_id:
            Toast.error(self, "Please select a user to update")
            return
        
        fullname = self.fullname_entry.get().strip()
        username = self.username_entry.get().strip()
        role = self.role_combo.get()
        status = 1 if self.status_combo.get() == "Active" else 0
        
        if not fullname:
            Toast.error(self, "Please enter full name")
            return
        
        if not username:
            Toast.error(self, "Please enter username")
            return
        
        if len(username) < 3:
            Toast.error(self, "Username must be at least 3 characters")
            return
        
        if self.user_service.username_exists(username, self.selected_user_id):
            Toast.error(self, "Username already exists")
            return
        
        # Update user details
        success = self.user_service.update_user(
            self.selected_user_id, username, role, fullname, status
        )
        
        # Update password if provided
        password = self.password_entry.get()
        if password:
            confirm = self.confirm_password_entry.get()
            if len(password) < 6:
                Toast.error(self, "Password must be at least 6 characters")
                return
            if password != confirm:
                Toast.error(self, "Passwords do not match")
                return
            self.user_service.update_password(self.selected_user_id, password)
        
        if success:
            Toast.success(self, "User updated successfully!")
            self.clear_form()
            self.load_users()
        else:
            Toast.error(self, "Failed to update user")
    
    def delete_user(self):
        """Delete selected user"""
        if not self.selected_user_id:
            return
        
        # Prevent deleting yourself
        current_user = self.auth_manager.get_current_user()
        if current_user and current_user['id'] == self.selected_user_id:
            Toast.error(self, "You cannot delete your own account")
            return
        
        if not Toast.confirm(self, "Delete User", "Are you sure you want to delete this user?", 
                            "Delete", "Cancel", "🗑️", "#ff6b6b"):
            return
        
        success = self.user_service.delete_user(self.selected_user_id)
        
        if success:
            Toast.success(self, "User deleted successfully")
            self.clear_form()
            self.load_users()
        else:
            Toast.error(self, "Failed to delete user")
    
    def clear_form(self):
        """Clear all form fields"""
        self.fullname_entry.delete(0, "end")
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.confirm_password_entry.delete(0, "end")
        self.role_combo.set("Staff")
        self.status_combo.set("Active")
        self.selected_user_id = None
        self.editing_mode = False
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
    
    def load_users(self):
        """Load all users into table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = self.user_service.get_all_users()
        
        for user in users:
            status = "Active" if user['is_active'] else "Disabled"
            self.tree.insert("", "end", values=(
                user['id'],
                user['full_name'],
                user['username'],
                user['role'],
                status
            ))
    
    def on_select(self, event):
        """Handle user selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_user_id = values[0]
        
        # Load user details
        user = self.user_service.get_user_by_id(self.selected_user_id)
        if user:
            self.fullname_entry.delete(0, "end")
            self.fullname_entry.insert(0, user['full_name'])
            
            self.username_entry.delete(0, "end")
            self.username_entry.insert(0, user['username'])
            
            self.password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
            
            self.role_combo.set(user['role'])
            self.status_combo.set("Active" if user['is_active'] else "Disabled")
            
            self.editing_mode = True
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
