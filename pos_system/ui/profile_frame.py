import customtkinter as ctk
from tkinter import messagebox
from services.user_service import UserService


class ProfileFrame(ctk.CTkFrame):
    """User profile and password change page"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.user_service = UserService()
        
        self.create_widgets()
        self.load_profile()
    
    def create_widgets(self):
        """Create profile widgets"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🔒 My Profile",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Profile Card
        profile_card = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        profile_card.pack(fill="x", pady=10)
        
        # Avatar section
        avatar_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        avatar_frame.pack(fill="x", padx=30, pady=30)
        
        # Large avatar icon
        avatar_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=80)
        )
        avatar_label.pack()
        
        self.name_label = ctk.CTkLabel(
            avatar_frame,
            text="User Name",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.name_label.pack(pady=(10, 0))
        
        self.role_label = ctk.CTkLabel(
            avatar_frame,
            text="Role",
            font=ctk.CTkFont(size=14),
            text_color="#00d4ff"
        )
        self.role_label.pack()
        
        # Profile details
        details_frame = ctk.CTkFrame(profile_card, fg_color="#252545", corner_radius=10)
        details_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        self.username_detail = self.create_detail_row(details_frame, "Username:", "")
        self.role_detail = self.create_detail_row(details_frame, "Role:", "")
        self.status_detail = self.create_detail_row(details_frame, "Status:", "Active")
        
        # Change Password Section
        password_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        password_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            password_section,
            text="🔑 Change Password",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 15))
        
        password_form = ctk.CTkFrame(password_section, fg_color="transparent")
        password_form.pack(fill="x", padx=30, pady=(0, 30))
        
        # Current Password
        ctk.CTkLabel(
            password_form,
            text="Current Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.current_password = ctk.CTkEntry(
            password_form,
            height=45,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Enter current password"
        )
        self.current_password.pack(fill="x", pady=(0, 15))
        
        # New Password
        ctk.CTkLabel(
            password_form,
            text="New Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.new_password = ctk.CTkEntry(
            password_form,
            height=45,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Enter new password (min 6 characters)"
        )
        self.new_password.pack(fill="x", pady=(0, 15))
        
        # Confirm New Password
        ctk.CTkLabel(
            password_form,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.confirm_password = ctk.CTkEntry(
            password_form,
            height=45,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Confirm new password"
        )
        self.confirm_password.pack(fill="x", pady=(0, 20))
        
        # Password requirements info
        requirements = ctk.CTkLabel(
            password_form,
            text="Password must be at least 6 characters long",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        requirements.pack(anchor="w", pady=(0, 15))
        
        # Change Password Button
        ctk.CTkButton(
            password_form,
            text="🔄 Update Password",
            height=50,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            command=self.change_password
        ).pack(anchor="w")
        
        # Account Activity Section
        activity_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        activity_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            activity_section,
            text="📊 Account Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=30, pady=(20, 15))
        
        activity_content = ctk.CTkFrame(activity_section, fg_color="transparent")
        activity_content.pack(fill="x", padx=30, pady=(0, 30))
        
        info_text = ctk.CTkLabel(
            activity_content,
            text="""
• Your account is used to access the POS system
• All your actions are logged for security
• Keep your password secure and don't share it
• Contact administrator if you need to reset your password
• Log out when leaving the workstation
            """,
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
            justify="left"
        )
        info_text.pack(anchor="w")
    
    def create_detail_row(self, parent, label: str, value: str) -> ctk.CTkLabel:
        """Create a detail row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(size=13),
            text_color="#00d4ff"
        )
        value_label.pack(side="left")
        
        return value_label
    
    def load_profile(self):
        """Load current user profile"""
        user = self.auth_manager.get_current_user()
        
        if user:
            self.name_label.configure(text=user['full_name'])
            self.role_label.configure(text=user['role'])
            self.username_detail.configure(text=user['username'])
            self.role_detail.configure(text=user['role'])
            self.status_detail.configure(text="Active")
    
    def change_password(self):
        """Handle password change"""
        current = self.current_password.get()
        new = self.new_password.get()
        confirm = self.confirm_password.get()
        
        if not current or not new or not confirm:
            messagebox.showerror("Error", "Please fill in all password fields")
            return
        
        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        if len(new) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        # Verify current password
        user = self.auth_manager.get_current_user()
        # Re-authenticate to verify current password
        verified = self.auth_manager.authenticate(user['username'], current)
        if not verified:
            messagebox.showerror("Error", "Current password is incorrect")
            # Restore user session since authenticate clears it on failure
            self.auth_manager.current_user = user
            return
        
        # Update password
        success = self.user_service.update_password(user['id'], new)
        
        if success:
            messagebox.showinfo("Success", "Password updated successfully!")
            self.current_password.delete(0, "end")
            self.new_password.delete(0, "end")
            self.confirm_password.delete(0, "end")
        else:
            messagebox.showerror("Error", "Failed to update password")
