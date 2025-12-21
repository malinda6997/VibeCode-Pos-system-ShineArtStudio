import customtkinter as ctk
from tkinter import ttk
from database import DatabaseManager
from auth import AuthManager
from ui.components import LoginWindow, Toast, MessageDialog
from ui.sidebar import Sidebar
from PIL import Image
import os

# Import all frames
from ui.customer_frame import CustomerManagementFrame
from ui.service_frame import ServiceManagementFrame
from ui.frame_frame import FrameManagementFrame
from ui.billing_frame import BillingFrame
from ui.booking_frame import BookingManagementFrame
from ui.invoice_history_frame import InvoiceHistoryFrame
from ui.dashboard_frame import DashboardFrame
from ui.users_frame import UsersManagementFrame
from ui.settings_frame import SettingsFrame
from ui.support_frame import SupportFrame
from ui.user_guide_frame import UserGuideFrame
from ui.profile_frame import ProfileFrame
from ui.category_frame import CategoryManagementFrame
from ui.permissions_frame import PermissionsFrame
from ui.staff_reports_frame import StaffReportsFrame
from services.user_service import UserService


class MainApplication(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure ttk styles for tables with larger font
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
            background="#1e1e3f",
            foreground="white",
            fieldbackground="#1e1e3f",
            font=("Segoe UI", 12),
            rowheight=32
        )
        style.configure("Treeview.Heading",
            background="#252545",
            foreground="white",
            font=("Segoe UI", 12, "bold")
        )
        style.map("Treeview",
            background=[("selected", "#00d4ff")],
            foreground=[("selected", "#1a1a2e")]
        )
        
        # Hide main window initially
        self.withdraw()
        
        # Window setup
        self.title("Shine Art Studio - POS System")
        self.geometry("1500x850")
        self.minsize(1200, 700)
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager()
        self.user_service = UserService()
        
        # Current user
        self.current_user = None
        
        # Create main container
        self.main_container = None
        self.content_frame = None
        self.sidebar = None
        self.profile_image_label = None
        
        # Show login
        self.show_login()
    
    def show_login(self):
        """Show login window"""
        login_window = LoginWindow(self, self.auth_manager, self.on_login_success)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.deiconify()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - 750
        y = (self.winfo_screenheight() // 2) - 425
        self.geometry(f"1500x850+{x}+{y}")
        
        self.create_main_interface()
    
    def load_profile_image(self, user_id: int, size: tuple = (40, 40)):
        """Load user profile image with circular mask or return default"""
        try:
            profile_path = self.user_service.get_profile_picture(user_id)
            if profile_path and os.path.exists(profile_path):
                img = Image.open(profile_path)
                # Make it square first
                img = img.resize(size, Image.Resampling.LANCZOS)
                # Create circular mask
                mask = Image.new('L', size, 0)
                from PIL import ImageDraw
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size[0], size[1]), fill=255)
                # Apply mask to create circular image
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                img = img.convert('RGBA')
                output.paste(img, (0, 0), mask)
                return ctk.CTkImage(light_image=output, dark_image=output, size=size)
        except Exception as e:
            print(f"Error loading profile image: {e}")
        return None
    
    def create_main_interface(self):
        """Create main application interface with modern sidebar"""
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="#0d0d1a")
        self.main_container.pack(fill="both", expand=True)
        
        # Create sidebar with navigation
        self.sidebar = Sidebar(self.main_container, self.auth_manager, self.navigate_to)
        self.sidebar.pack(fill="y", side="left")
        
        # Right side container (top bar + content)
        right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        right_container.pack(fill="both", expand=True, side="right")
        
        # Top bar
        top_bar = ctk.CTkFrame(right_container, height=60, fg_color="#1a1a2e")
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        
        # Logo/Title container
        logo_title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        logo_title_frame.pack(side="left", padx=20, pady=10)
        
        # Logo
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo001.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(40, 40))
                logo_label = ctk.CTkLabel(logo_title_frame, image=logo_photo, text="")
                logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Title
        title_label = ctk.CTkLabel(
            logo_title_frame,
            text="Shine Art Studio",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        # Right side of top bar - Logout only
        right_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        right_frame.pack(side="right", padx=20)
        
        # Logout button
        logout_btn = ctk.CTkButton(
            right_frame,
            text="🚪 Logout",
            command=self.logout,
            width=100,
            height=35,
            fg_color="#ff4757",
            hover_color="#ff3344",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        logout_btn.pack(side="right", padx=5)
        
        # Content area
        self.content_frame = ctk.CTkFrame(right_container, fg_color="#0d0d1a")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Show default view (Dashboard)
        self.navigate_to("dashboard")
        
        # Set parent for MessageDialog toasts
        MessageDialog.set_parent(self.content_frame)
    
    def update_profile_display(self):
        """Update profile picture - called when profile is updated"""
        # Sidebar avatar will be updated on next login
        pass
    
    def navigate_to(self, page: str):
        """Navigate to a specific page"""
        # Permission mapping for each page
        permission_map = {
            "dashboard": "can_access_dashboard",
            "billing": "can_access_billing",
            "customers": "can_access_customers",
            "categories": "can_access_categories",
            "services": "can_access_services",
            "frames": "can_access_frames",
            "bookings": "can_access_bookings",
            "invoices": "can_access_invoices",
            "users": "can_access_users",
            "permissions": "can_access_permissions",
            "staff_reports": "can_access_staff_reports",
            "settings": "can_access_settings",
            "profile": "can_access_profile",
            "support": "can_access_support",
            "guide": "can_access_user_guide",
        }
        
        # Check permission before navigating
        required_permission = permission_map.get(page)
        if required_permission and not self.auth_manager.has_permission(required_permission):
            Toast.show_toast(self, "Access Denied", "You don't have permission to access this feature.", "error")
            return
        
        self.clear_content()
        
        # Update sidebar active state
        if self.sidebar:
            self.sidebar.set_active(page)
        
        frame_classes = {
            "dashboard": DashboardFrame,
            "billing": BillingFrame,
            "customers": CustomerManagementFrame,
            "categories": CategoryManagementFrame,
            "services": ServiceManagementFrame,
            "frames": FrameManagementFrame,
            "bookings": BookingManagementFrame,
            "invoices": InvoiceHistoryFrame,
            "users": UsersManagementFrame,
            "permissions": PermissionsFrame,
            "staff_reports": StaffReportsFrame,
            "settings": SettingsFrame,
            "profile": ProfileFrame,
            "support": SupportFrame,
            "guide": UserGuideFrame,
        }
        
        frame_class = frame_classes.get(page)
        if frame_class:
            # Pass main_app reference to ProfileFrame and DashboardFrame
            if page in ["profile", "dashboard"]:
                frame = frame_class(self.content_frame, self.auth_manager, self.db_manager, self)
            else:
                frame = frame_class(self.content_frame, self.auth_manager, self.db_manager)
            frame.pack(fill="both", expand=True)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout and return to login screen"""
        # Show confirmation dialog
        if Toast.confirm(self, "Logout", "Are you sure you want to logout?", 
                        "Yes, Logout", "Cancel", "🚪", "#ff4757"):
            self.auth_manager.logout()
            self.current_user = None
            
            # Clear main container
            if self.main_container:
                self.main_container.destroy()
                self.main_container = None
            
            # Show login
            self.show_login()


def main():
    """Main entry point"""
    # Initialize database
    from database import initialize_database
    initialize_database()
    
    # Start application
    app = MainApplication()
    app.mainloop()


if __name__ == "__main__":
    main()
