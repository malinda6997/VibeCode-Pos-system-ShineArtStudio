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
        
        # Set application window icon
        self._set_window_icon()
        
        # Configure ttk styles for modern tables
        style = ttk.Style()
        style.theme_use("clam")
        
        # Modern table styling with gradient-like effect
        style.configure("Treeview",
            background="#1a1a2e",
            foreground="#e0e0e0",
            fieldbackground="#1a1a2e",
            font=("Segoe UI", 12),
            rowheight=45,
            borderwidth=0
        )
        
        # Modern header styling with accent color
        style.configure("Treeview.Heading",
            background="#252545",
            foreground="#00d4ff",
            font=("Segoe UI", 12, "bold"),
            borderwidth=0,
            relief="flat",
            padding=(10, 8)
        )
        
        # Selection and hover effects
        style.map("Treeview",
            background=[
                ("selected", "#00d4ff"),
                ("!selected", "#1a1a2e")
            ],
            foreground=[
                ("selected", "#1a1a2e"),
                ("!selected", "#e0e0e0")
            ]
        )
        
        # Header hover effect
        style.map("Treeview.Heading",
            background=[
                ("active", "#3d3d7a"),
                ("!active", "#252545")
            ],
            foreground=[
                ("active", "#00ff88"),
                ("!active", "#00d4ff")
            ]
        )
        
        # Modern scrollbar styling
        style.configure("Vertical.TScrollbar",
            background="#2d2d5a",
            troughcolor="#1a1a2e",
            borderwidth=0,
            arrowsize=0,
            width=12
        )
        
        style.map("Vertical.TScrollbar",
            background=[
                ("active", "#00d4ff"),
                ("!active", "#3d3d7a")
            ]
        )
        
        # Configure alternating row colors using tags (applied in frames)
        style.configure("oddrow.Treeview", background="#1e1e3f")
        style.configure("evenrow.Treeview", background="#252545")
        
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
    
    def _set_window_icon(self):
        """Set the application window icon"""
        try:
            # Use the uploaded appLogo.ico directly
            ico_path = os.path.join(os.path.dirname(__file__), "assets", "logos", "appLogo.ico")
            
            if os.path.exists(ico_path):
                # Set the window icon using iconbitmap for Windows taskbar
                self.iconbitmap(ico_path)
                
                # Also load as image for iconphoto
                from PIL import ImageTk
                icon_image = Image.open(ico_path)
                
                # Convert to RGBA if needed
                if icon_image.mode != 'RGBA':
                    icon_image = icon_image.convert('RGBA')
                
                # Also set iconphoto for other platforms/contexts
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                icon_photos = []
                for size in icon_sizes:
                    resized = icon_image.resize(size, Image.Resampling.LANCZOS)
                    icon_photos.append(ImageTk.PhotoImage(resized))
                self._icon_photos = icon_photos  # Keep reference to prevent garbage collection
                self.iconphoto(True, *icon_photos)
        except Exception as e:
            print(f"Could not load application icon: {e}")
    
    def show_login(self):
        """Show login window"""
        login_window = LoginWindow(self, self.auth_manager, self.on_login_success)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        self.deiconify()
        
        # Re-set window icon to ensure consistency
        self._set_window_icon()
        
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
        
        # Top bar left spacer (logo is in sidebar, no duplicate here)
        left_spacer = ctk.CTkFrame(top_bar, fg_color="transparent")
        left_spacer.pack(side="left", padx=20, pady=10)
        
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
        """Logout with option to login again or exit application"""
        # Create custom dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Logout")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"400x200+{x}+{y}")
        
        result = {"action": None}
        
        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
        
        def login_again():
            result["action"] = "login"
            close_dialog()
        
        def exit_app():
            result["action"] = "exit"
            close_dialog()
        
        def cancel():
            result["action"] = "cancel"
            close_dialog()
        
        dialog.protocol("WM_DELETE_WINDOW", cancel)
        
        # Icon and message
        ctk.CTkLabel(
            dialog,
            text="🚪",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog,
            text="Do you want to login again?",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="Yes, Login Again",
            command=login_again,
            width=120,
            height=40,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="No, Exit App",
            command=exit_app,
            width=120,
            height=40,
            fg_color="#ff4757",
            hover_color="#ff3344",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=cancel,
            width=80,
            height=40,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        ).pack(side="left", padx=5)
        
        # Wait for dialog
        dialog.wait_window()
        
        if result["action"] == "login":
            # Logout and show login screen
            self.auth_manager.logout()
            self.current_user = None
            
            if self.main_container:
                self.main_container.destroy()
                self.main_container = None
            
            self.content_frame = None
            self.sidebar = None
            self.withdraw()
            self.show_login()
            
        elif result["action"] == "exit":
            # Exit application
            self.auth_manager.logout()
            self.destroy()


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
