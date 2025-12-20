import customtkinter as ctk
from PIL import Image
import os
from typing import Callable, Dict, Optional


class Sidebar(ctk.CTkFrame):
    """Modern sidebar navigation component with PNG icons"""
    
    def __init__(self, parent, auth_manager, on_navigate: Callable):
        super().__init__(parent, fg_color="#1a1a2e", width=250, corner_radius=0)
        self.pack_propagate(False)
        
        self.auth_manager = auth_manager
        self.on_navigate = on_navigate
        self.active_tab = "dashboard"
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.icons: Dict[str, ctk.CTkImage] = {}
        self.active_icons: Dict[str, ctk.CTkImage] = {}
        
        self.icons_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        
        # Preload all icons
        self.preload_icons()
        self.create_sidebar()
    
    def preload_icons(self):
        """Preload all navigation icons"""
        icon_names = [
            "dashboard", "billing", "customers", "services", "frames", 
            "bookings", "invoices", "categories", "users", "settings",
            "profile", "support", "guide"
        ]
        for name in icon_names:
            icon = self.load_icon(name)
            if icon:
                self.icons[name] = icon
            # Load active (dark) version for highlighted state
            active_icon = self.load_icon(name, for_active=True)
            if active_icon:
                self.active_icons[name] = active_icon
    
    def load_icon(self, name: str, size: tuple = (20, 20), for_active: bool = False) -> Optional[ctk.CTkImage]:
        """Load icon from assets folder"""
        try:
            icon_path = os.path.join(self.icons_path, f"{name}.png")
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                # Convert to RGBA if not already
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"Error loading icon {name}: {e}")
        return None
    
    def create_sidebar(self):
        """Create sidebar layout"""
        
        # Logo section
        logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", pady=(20, 10))
        logo_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="✨ Shine Art",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00d4ff"
        )
        logo_label.pack(pady=10)
        
        studio_label = ctk.CTkLabel(
            logo_frame,
            text="Photography Studio",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        studio_label.pack()
        
        # Separator
        sep = ctk.CTkFrame(self, fg_color="#333355", height=2)
        sep.pack(fill="x", padx=20, pady=15)
        
        # Navigation items with icon names matching PNG files
        nav_items = [
            ("dashboard", "dashboard", "Dashboard"),
            ("billing", "billing", "Billing"),
            ("customers", "customers", "Customers"),
            ("categories", "categories", "Categories"),
            ("services", "services", "Services"),
            ("frames", "frames", "Photo Frames"),
            ("bookings", "bookings", "Bookings"),
            ("invoices", "invoices", "Invoices"),
        ]
        
        # Admin only items
        admin_items = [
            ("users", "users", "Users"),
            ("settings", "settings", "Settings"),
        ]
        
        # All users items
        bottom_items = [
            ("profile", "profile", "My Profile"),
            ("support", "support", "Support"),
            ("guide", "guide", "User Guide"),
        ]
        
        # Main navigation
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10)
        
        for tab_id, icon_name, text in nav_items:
            self.create_nav_button(nav_frame, tab_id, icon_name, text)
        
        # Admin section - only show for admin users
        if self.auth_manager.is_admin():
            admin_sep = ctk.CTkFrame(nav_frame, fg_color="#333355", height=1)
            admin_sep.pack(fill="x", padx=10, pady=10)
            
            admin_label = ctk.CTkLabel(
                nav_frame,
                text="ADMIN",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#666666"
            )
            admin_label.pack(anchor="w", padx=15, pady=(5, 5))
            
            for tab_id, icon_name, text in admin_items:
                self.create_nav_button(nav_frame, tab_id, icon_name, text)
        
        # Bottom section
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=10)
        
        bottom_sep = ctk.CTkFrame(bottom_frame, fg_color="#333355", height=1)
        bottom_sep.pack(fill="x", padx=10, pady=10)
        
        for tab_id, icon_name, text in bottom_items:
            self.create_nav_button(bottom_frame, tab_id, icon_name, text)
        
        # User info at bottom
        user_frame = ctk.CTkFrame(self, fg_color="#252545", corner_radius=10)
        user_frame.pack(fill="x", padx=15, pady=(0, 20))
        
        user = self.auth_manager.get_current_user()
        if user:
            user_name = ctk.CTkLabel(
                user_frame,
                text=user['full_name'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white"
            )
            user_name.pack(pady=(10, 2))
            
            user_role = ctk.CTkLabel(
                user_frame,
                text=user['role'],
                font=ctk.CTkFont(size=10),
                text_color="#00d4ff"
            )
            user_role.pack(pady=(0, 10))
        
        # Set dashboard as active
        self.set_active("dashboard")
    
    def create_nav_button(self, parent, tab_id: str, icon_name: str, text: str):
        """Create navigation button with PNG icon"""
        
        # Get icon if available
        icon = self.icons.get(icon_name)
        
        btn = ctk.CTkButton(
            parent,
            text=f"   {text}",
            image=icon,
            compound="left",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#2d2d5a",
            anchor="w",
            height=40,
            corner_radius=8,
            command=lambda t=tab_id: self.navigate(t)
        )
        btn.pack(fill="x", pady=2, padx=5)
        btn._icon_name = icon_name  # Store icon name for later reference
        self.buttons[tab_id] = btn
    
    def navigate(self, tab_id: str):
        """Handle navigation"""
        self.set_active(tab_id)
        self.on_navigate(tab_id)
    
    def set_active(self, tab_id: str):
        """Set active tab styling"""
        self.active_tab = tab_id
        
        for tid, btn in self.buttons.items():
            icon_name = getattr(btn, '_icon_name', tid)
            if tid == tab_id:
                btn.configure(fg_color="#00d4ff", text_color="#1a1a2e")
                # Use active icon if available
                if icon_name in self.active_icons:
                    btn.configure(image=self.active_icons[icon_name])
            else:
                btn.configure(fg_color="transparent", text_color="white")
                # Use normal icon
                if icon_name in self.icons:
                    btn.configure(image=self.icons[icon_name])
