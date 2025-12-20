import customtkinter as ctk
from tkinter import filedialog
from services.user_service import UserService
from ui.components import Toast
from PIL import Image
import os


class ProfileFrame(ctk.CTkFrame):
    """User profile and password change page with centered card-style layout"""
    
    def __init__(self, parent, auth_manager, db_manager, main_app=None):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.user_service = UserService()
        self.main_app = main_app
        self.profile_image = None
        
        self.create_widgets()
        self.load_profile()
    
    def create_widgets(self):
        """Create profile widgets with centered card layout"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🔒 My Profile",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Centered container
        center_container = ctk.CTkFrame(self, fg_color="transparent")
        center_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Scrollable main container - centered and constrained width
        main_scroll = ctk.CTkScrollableFrame(
            center_container, 
            fg_color="transparent",
            width=600
        )
        main_scroll.pack(expand=True)
        
        # Profile Card - Centered
        profile_card = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=20, width=550)
        profile_card.pack(pady=15, padx=25)
        profile_card.pack_propagate(False)
        profile_card.configure(height=350)
        
        # Avatar section - centered
        avatar_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        avatar_frame.pack(fill="x", pady=(30, 20))
        
        # Profile picture container - centered
        avatar_inner = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        avatar_inner.pack()
        
        self.avatar_container = ctk.CTkFrame(avatar_inner, fg_color="#252545", width=120, height=120, corner_radius=60)
        self.avatar_container.pack()
        self.avatar_container.pack_propagate(False)
        
        # Large avatar icon/image
        self.avatar_label = ctk.CTkLabel(
            self.avatar_container,
            text="👤",
            font=ctk.CTkFont(size=50)
        )
        self.avatar_label.pack(expand=True)
        
        # Button container - centered
        btn_container = ctk.CTkFrame(avatar_frame, fg_color="transparent")
        btn_container.pack(pady=(15, 0))
        
        # Upload button
        upload_btn = ctk.CTkButton(
            btn_container,
            text="📷 Upload Photo",
            height=35,
            width=130,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            corner_radius=8,
            command=self.upload_profile_picture
        )
        upload_btn.pack(side="left", padx=5)
        
        # Remove photo button
        remove_btn = ctk.CTkButton(
            btn_container,
            text="🗑️ Remove",
            height=35,
            width=100,
            font=ctk.CTkFont(size=12),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            corner_radius=8,
            command=self.remove_profile_picture
        )
        remove_btn.pack(side="left", padx=5)
        
        # Name and role - centered
        self.name_label = ctk.CTkLabel(
            profile_card,
            text="User Name",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.name_label.pack(pady=(10, 5))
        
        self.role_label = ctk.CTkLabel(
            profile_card,
            text="Role",
            font=ctk.CTkFont(size=14),
            text_color="#00d4ff"
        )
        self.role_label.pack()
        
        # Profile details card
        details_card = ctk.CTkFrame(profile_card, fg_color="#252545", corner_radius=12)
        details_card.pack(fill="x", padx=30, pady=(20, 30))
        
        self.username_detail = self.create_detail_row(details_card, "Username:", "")
        self.role_detail = self.create_detail_row(details_card, "Role:", "")
        self.status_detail = self.create_detail_row(details_card, "Status:", "Active")
        
        # Change Password Card - Centered
        password_card = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=20, width=550)
        password_card.pack(pady=15, padx=25)
        password_card.pack_propagate(False)
        password_card.configure(height=380)
        
        ctk.CTkLabel(
            password_card,
            text="🔑 Change Password",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(25, 20))
        
        password_form = ctk.CTkFrame(password_card, fg_color="transparent")
        password_form.pack(fill="x", padx=40)
        
        # Current Password
        ctk.CTkLabel(
            password_form,
            text="Current Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.current_password = ctk.CTkEntry(
            password_form,
            height=42,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Enter current password",
            corner_radius=8
        )
        self.current_password.pack(fill="x", pady=(0, 12))
        
        # New Password
        ctk.CTkLabel(
            password_form,
            text="New Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.new_password = ctk.CTkEntry(
            password_form,
            height=42,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Min 6 characters",
            corner_radius=8
        )
        self.new_password.pack(fill="x", pady=(0, 12))
        
        # Confirm New Password
        ctk.CTkLabel(
            password_form,
            text="Confirm New Password:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.confirm_password = ctk.CTkEntry(
            password_form,
            height=42,
            font=ctk.CTkFont(size=13),
            show="●",
            placeholder_text="Confirm new password",
            corner_radius=8
        )
        self.confirm_password.pack(fill="x", pady=(0, 15))
        
        # Change Password Button - centered
        ctk.CTkButton(
            password_card,
            text="🔄 Update Password",
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            corner_radius=10,
            command=self.change_password
        ).pack(pady=(0, 25))
        
        # Account Info Card - Centered
        info_card = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=20, width=550)
        info_card.pack(pady=15, padx=25)
        info_card.pack_propagate(False)
        info_card.configure(height=200)
        
        ctk.CTkLabel(
            info_card,
            text="📊 Account Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(25, 15))
        
        info_text = ctk.CTkLabel(
            info_card,
            text="""• Your account is used to access the POS system
• All your actions are logged for security
• Keep your password secure and don't share it
• Contact administrator if you need to reset your password
• Log out when leaving the workstation""",
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa",
            justify="left"
        )
        info_text.pack(padx=40, pady=(0, 25))
    
    def create_detail_row(self, parent, label: str, value: str) -> ctk.CTkLabel:
        """Create a detail row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
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
            
            # Load profile picture
            self.load_profile_picture(user['id'])
    
    def load_profile_picture(self, user_id: int):
        """Load and display profile picture"""
        try:
            profile_path = self.user_service.get_profile_picture(user_id)
            if profile_path and os.path.exists(profile_path):
                img = Image.open(profile_path)
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                self.profile_image = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                self.avatar_label.configure(image=self.profile_image, text="")
            else:
                self.avatar_label.configure(image=None, text="👤", font=ctk.CTkFont(size=50))
        except Exception as e:
            print(f"Error loading profile picture: {e}")
            self.avatar_label.configure(image=None, text="👤", font=ctk.CTkFont(size=50))
    
    def upload_profile_picture(self):
        """Upload new profile picture"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Profile Picture",
            filetypes=filetypes
        )
        
        if filepath:
            try:
                user = self.auth_manager.get_current_user()
                if not user:
                    return
                
                # Create profile_pictures directory if not exists
                profiles_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "profile_pictures")
                os.makedirs(profiles_dir, exist_ok=True)
                
                # Generate unique filename
                ext = os.path.splitext(filepath)[1]
                new_filename = f"user_{user['id']}{ext}"
                new_path = os.path.join(profiles_dir, new_filename)
                
                # Copy and resize image
                img = Image.open(filepath)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                img.save(new_path)
                
                # Update database
                if self.user_service.update_profile_picture(user['id'], new_path):
                    self.load_profile_picture(user['id'])
                    
                    # Update top bar display
                    if self.main_app:
                        self.main_app.update_profile_display()
                    
                    Toast.success(self, "Profile picture updated successfully!")
                else:
                    Toast.error(self, "Failed to update profile picture")
                    
            except Exception as e:
                Toast.error(self, f"Failed to upload image: {e}")
    
    def remove_profile_picture(self):
        """Remove profile picture"""
        user = self.auth_manager.get_current_user()
        if not user:
            return
        
        def do_remove():
            # Get current picture path
            current_path = self.user_service.get_profile_picture(user['id'])
            
            # Delete file if exists
            if current_path and os.path.exists(current_path):
                try:
                    os.remove(current_path)
                except:
                    pass
            
            # Clear from database
            if self.user_service.update_profile_picture(user['id'], None):
                self.avatar_label.configure(image=None, text="👤", font=ctk.CTkFont(size=50))
                self.profile_image = None
                
                # Update top bar display
                if self.main_app:
                    self.main_app.update_profile_display()
                
                Toast.success(self, "Profile picture removed")
        
        Toast.confirm(self, "Remove Picture", "Remove your profile picture?", 
                     "Yes, Remove", "Cancel", "🗑️", "#e74c3c", do_remove)
    
    def change_password(self):
        """Handle password change"""
        current = self.current_password.get()
        new = self.new_password.get()
        confirm = self.confirm_password.get()
        
        if not current or not new or not confirm:
            Toast.error(self, "Please fill in all password fields")
            return
        
        if new != confirm:
            Toast.error(self, "New passwords do not match")
            return
        
        if len(new) < 6:
            Toast.error(self, "Password must be at least 6 characters")
            return
        
        # Verify current password
        user = self.auth_manager.get_current_user()
        # Re-authenticate to verify current password
        verified = self.auth_manager.authenticate(user['username'], current)
        if not verified:
            Toast.error(self, "Current password is incorrect")
            # Restore user session since authenticate clears it on failure
            self.auth_manager.current_user = user
            return
        
        # Update password
        success = self.user_service.update_password(user['id'], new)
        
        if success:
            Toast.success(self, "Password updated successfully!")
            self.current_password.delete(0, "end")
            self.new_password.delete(0, "end")
            self.confirm_password.delete(0, "end")
        else:
            Toast.error(self, "Failed to update password")
