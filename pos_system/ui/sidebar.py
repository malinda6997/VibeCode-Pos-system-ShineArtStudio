import customtkinter as ctk
from typing import Callable, Dict
from PIL import Image, ImageDraw, ImageOps
import os


class Sidebar(ctk.CTkFrame):
    """Modern sidebar navigation component with emoji icons and scrollable content"""
    
    def __init__(self, parent, auth_manager, on_navigate: Callable):
        super().__init__(parent, fg_color="#1a1a2e", width=250, corner_radius=0)
        self.pack_propagate(False)
        
        self.auth_manager = auth_manager
        self.on_navigate = on_navigate
        self.active_tab = "dashboard"
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.user_avatar = None
        
        self.create_sidebar()
    
    def create_sidebar(self):
        """Create sidebar layout with scrollable navigation"""
        
        # Logo section (fixed at top)
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
        sep.pack(fill="x", padx=20, pady=10)
        
        # Scrollable navigation container
        self.nav_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        self.nav_scroll.pack(fill="both", expand=True, padx=5)
        
        # Navigation items with emoji icons and permission keys
        nav_items = [
            ("dashboard", "📊", "Dashboard", "can_access_dashboard"),
            ("billing", "💳", "Billing", "can_access_billing"),
            ("customers", "👥", "Customers", "can_access_customers"),
            ("categories", "📁", "Categories", "can_access_categories"),
            ("services", "🎨", "Services", "can_access_services"),
            ("frames", "🖼", "Photo Frames", "can_access_frames"),
            ("bookings", "📅", "Bookings", "can_access_bookings"),
            ("invoices", "📄", "Invoices", "can_access_invoices"),
        ]
        
        # Admin only items
        admin_items = [
            ("users", "👤", "Users", "can_access_users"),
            ("permissions", "�", "Permissions", "can_access_permissions"),
            ("staff_reports", "📋", "Staff Reports", "can_access_staff_reports"),
            ("settings", "⚙", "Settings", "can_access_settings"),
        ]
        
        # All users items
        bottom_items = [
            ("profile", "🔒", "My Profile", "can_access_profile"),
            ("support", "💬", "Support", "can_access_support"),
            ("guide", "📖", "User Guide", "can_access_user_guide"),
        ]
        
        # Main navigation buttons (filter by permissions)
        for tab_id, icon, text, perm_key in nav_items:
            if self.auth_manager.has_permission(perm_key):
                self.create_nav_button(self.nav_scroll, tab_id, icon, text)
        
        # Admin section - only show for admin users
        if self.auth_manager.is_admin():
            admin_sep = ctk.CTkFrame(self.nav_scroll, fg_color="#333355", height=1)
            admin_sep.pack(fill="x", padx=10, pady=10)
            
            admin_label = ctk.CTkLabel(
                self.nav_scroll,
                text="ADMIN",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#666666"
            )
            admin_label.pack(anchor="w", padx=15, pady=(5, 5))
            
            for tab_id, icon, text, perm_key in admin_items:
                if self.auth_manager.has_permission(perm_key):
                    self.create_nav_button(self.nav_scroll, tab_id, icon, text)
        
        # Separator before bottom items
        bottom_sep = ctk.CTkFrame(self.nav_scroll, fg_color="#333355", height=1)
        bottom_sep.pack(fill="x", padx=10, pady=10)
        
        # Bottom section items (filter by permissions)
        for tab_id, icon, text, perm_key in bottom_items:
            if self.auth_manager.has_permission(perm_key):
                self.create_nav_button(self.nav_scroll, tab_id, icon, text)
        
        # User info at very bottom (fixed)
        user_frame = ctk.CTkFrame(self, fg_color="#252545", corner_radius=12)
        user_frame.pack(fill="x", padx=12, pady=(10, 15))
        
        user = self.auth_manager.get_current_user()
        if user:
            # User info layout
            user_content = ctk.CTkFrame(user_frame, fg_color="transparent")
            user_content.pack(fill="x", padx=12, pady=12)
            
            # User info (name + role)
            info_frame = ctk.CTkFrame(user_content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)
            
            user_name = ctk.CTkLabel(
                info_frame,
                text=user['full_name'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                anchor="w"
            )
            user_name.pack(anchor="w")
            
            # Role badge with styling
            role_color = "#00d4ff" if user['role'] == 'Admin' else "#00ff88"
            user_role = ctk.CTkLabel(
                info_frame,
                text=f"● {user['role']}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=role_color,
                anchor="w"
            )
            user_role.pack(anchor="w")
            
            # Last login info
            last_login = user.get('last_login')
            if last_login:
                # Format last login to be more compact
                login_text = f"Last: {last_login[:16]}" if len(last_login) > 16 else f"Last: {last_login}"
            else:
                login_text = "First login"
            last_login_label = ctk.CTkLabel(
                info_frame,
                text=login_text,
                font=ctk.CTkFont(size=9),
                text_color="#666666",
                anchor="w"
            )
            last_login_label.pack(anchor="w")
        
        # Set dashboard as active
        self.set_active("dashboard")
    
    def get_user_initials(self, full_name: str) -> str:
        """Get user initials from full name"""
        if not full_name:
            return ""
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1:
            return parts[0][0].upper()
        return ""
    
    def load_user_avatar(self, user_id: int, size: tuple = (40, 40)):
        """Load user profile image with perfect circular mask and object-fit cover"""
        try:
            from services.user_service import UserService
            user_service = UserService()
            profile_path = user_service.get_profile_picture(user_id)
            if profile_path and os.path.exists(profile_path):
                img = Image.open(profile_path)
                
                # Convert to RGB if necessary (handle RGBA, P mode, etc.)
                if img.mode in ('RGBA', 'P', 'LA'):
                    # Create a white background for transparency
                    background = Image.new('RGB', img.size, (26, 26, 46))  # Match sidebar bg
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Object-fit: cover - crop from center to make square
                width, height = img.size
                min_dim = min(width, height)
                
                # Calculate crop box for center crop
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                
                # Crop to square
                img = img.crop((left, top, right, bottom))
                
                # High quality resize using LANCZOS
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Create perfect circular mask with anti-aliasing
                # Use larger size for mask then downscale for smooth edges
                mask_size = (size[0] * 4, size[1] * 4)
                mask = Image.new('L', mask_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size[0] - 1, mask_size[1] - 1), fill=255)
                mask = mask.resize(size, Image.Resampling.LANCZOS)
                
                # Create output with transparency
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                img_rgba = img.convert('RGBA')
                
                # Apply the circular mask
                output.paste(img_rgba, (0, 0))
                output.putalpha(mask)
                
                self.user_avatar = ctk.CTkImage(light_image=output, dark_image=output, size=size)
                return self.user_avatar
        except Exception as e:
            print(f"Error loading sidebar avatar: {e}")
        return None
    
    def create_nav_button(self, parent, tab_id: str, icon: str, text: str):
        """Create navigation button with emoji icon"""
        btn = ctk.CTkButton(
            parent,
            text=f"{icon}  {text}",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#2d2d5a",
            anchor="w",
            height=42,
            corner_radius=8,
            command=lambda t=tab_id: self.navigate(t)
        )
        btn.pack(fill="x", pady=2, padx=5)
        self.buttons[tab_id] = btn
    
    def navigate(self, tab_id: str):
        """Handle navigation"""
        self.set_active(tab_id)
        self.on_navigate(tab_id)
    
    def set_active(self, tab_id: str):
        """Set active tab styling"""
        self.active_tab = tab_id
        
        for tid, btn in self.buttons.items():
            if tid == tab_id:
                btn.configure(fg_color="#00d4ff", text_color="#1a1a2e")
            else:
                btn.configure(fg_color="transparent", text_color="white")
