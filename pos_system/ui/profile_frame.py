import customtkinter as ctk
from tkinter import filedialog
from services.user_service import UserService
from ui.components import Toast
from PIL import Image
import os


class ProfileFrame(ctk.CTkFrame):
    """User profile and password change page with full-width layout"""
    
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
        """Create profile widgets with full-width layout"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="🔒 My Profile",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Scrollable main container - full width
        main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Profile Card - Full width
        profile_card = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=15)
        profile_card.pack(fill="x", pady=10)
        
        # Avatar section
        avatar_frame = ctk.CTkFrame(profile_card, fg_color="transparent")
        avatar_frame.pack(fill="x", padx=30, pady=30)
        
        # Profile picture container - circular avatar only
        self.avatar_container = ctk.CTkFrame(avatar_frame, fg_color="#252545", width=120, height=120, corner_radius=60)
        self.avatar_container.pack()
        self.avatar_container.pack_propagate(False)
        
        # Large avatar icon/image
        self.avatar_label = ctk.CTkLabel(
            self.avatar_container,
            text="👤",
            font=ctk.CTkFont(size=50)
        )
        self.avatar_label.pack(expand=True)
        
        # Upload button
        upload_btn = ctk.CTkButton(
            avatar_frame,
            text="📷 Upload Photo",
            height=35,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            corner_radius=8,
            command=self.upload_profile_picture
        )
        upload_btn.pack(pady=(15, 5))
        
        # Remove photo button
        remove_btn = ctk.CTkButton(
            avatar_frame,
            text="🗑️ Remove Photo",
            height=30,
            width=150,
            font=ctk.CTkFont(size=11),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            corner_radius=8,
            command=self.remove_profile_picture
        )
        remove_btn.pack(pady=(0, 10))
        
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
        
        # Profile details - full width card section
        details_frame = ctk.CTkFrame(profile_card, fg_color="#252545", corner_radius=10)
        details_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        self.username_detail = self.create_detail_row(details_frame, "Username:", "")
        self.role_detail = self.create_detail_row(details_frame, "Role:", "")
        self.status_detail = self.create_detail_row(details_frame, "Status:", "Active")
        self.last_login_detail = self.create_detail_row(details_frame, "Last Login:", "")
        
        # Change Password Section - Full width
        password_section = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=15)
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
            placeholder_text="Enter current password",
            corner_radius=8
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
            placeholder_text="Enter new password (min 6 characters)",
            corner_radius=8
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
            placeholder_text="Confirm new password",
            corner_radius=8
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
            corner_radius=10,
            command=self.change_password
        ).pack(anchor="w")
        
        # Account Activity Section - Full width
        activity_section = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=15)
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
            text="""• Your account is used to access the POS system
• All your actions are logged for security
• Keep your password secure and don't share it
• Contact administrator if you need to reset your password
• Log out when leaving the workstation""",
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
            
            # Set last login
            last_login = user.get('last_login')
            if last_login:
                self.last_login_detail.configure(text=last_login)
            else:
                self.last_login_detail.configure(text="First login")
            
            # Load profile picture
            self.load_profile_picture(user['id'])
    
    def load_profile_picture(self, user_id: int):
        """Load and display profile picture with circular mask"""
        try:
            profile_path = self.user_service.get_profile_picture(user_id)
            if profile_path and os.path.exists(profile_path):
                img = Image.open(profile_path)
                # Make square crop from center
                min_dim = min(img.size)
                left = (img.width - min_dim) // 2
                top = (img.height - min_dim) // 2
                img = img.crop((left, top, left + min_dim, top + min_dim))
                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                
                # Create circular mask
                from PIL import ImageDraw
                mask = Image.new('L', (100, 100), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 100, 100), fill=255)
                
                # Apply mask
                output = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
                img = img.convert('RGBA')
                output.paste(img, (0, 0), mask)
                
                self.profile_image = ctk.CTkImage(light_image=output, dark_image=output, size=(100, 100))
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
        
        # Show confirmation dialog
        confirmed = Toast.confirm(
            self, 
            "Remove Picture", 
            "Remove your profile picture?", 
            "Yes, Remove", 
            "Cancel", 
            "🗑️", 
            "#e74c3c"
        )
        
        if confirmed:
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
                
                Toast.success(self, "Profile picture removed successfully!")
            else:
                Toast.error(self, "Failed to remove profile picture")
    
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
