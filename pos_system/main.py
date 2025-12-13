import customtkinter as ctk
from database import DatabaseManager
from auth import AuthManager
from ui.components import LoginWindow
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


class MainApplication(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Hide main window initially
        self.withdraw()
        
        # Window setup
        self.title("Shine Art Studio - POS System")
        self.geometry("1500x850")
        self.minsize(1200, 700)
        
        # Initialize managers
        self.db_manager = DatabaseManager()
        self.auth_manager = AuthManager()
        
        # Current user
        self.current_user = None
        
        # Create main container
        self.main_container = None
        self.content_frame = None
        self.sidebar = None
        
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
        
        # Right side of top bar
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
    
    def navigate_to(self, page: str):
        """Navigate to a specific page"""
        self.clear_content()
        
        frame_classes = {
            "dashboard": DashboardFrame,
            "billing": BillingFrame,
            "customers": CustomerManagementFrame,
            "services": ServiceManagementFrame,
            "frames": FrameManagementFrame,
            "bookings": BookingManagementFrame,
            "invoices": InvoiceHistoryFrame,
            "users": UsersManagementFrame,
            "settings": SettingsFrame,
            "profile": ProfileFrame,
            "support": SupportFrame,
            "guide": UserGuideFrame,
        }
        
        frame_class = frame_classes.get(page)
        if frame_class:
            frame = frame_class(self.content_frame, self.auth_manager, self.db_manager)
            frame.pack(fill="both", expand=True)
    
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout and return to login screen"""
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
