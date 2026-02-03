import customtkinter as ctk
from typing import Callable, Dict, List, Tuple
from PIL import Image, ImageDraw, ImageOps
import os


class Sidebar(ctk.CTkFrame):
    """Modern collapsible sidebar navigation component with emoji icons and scrollable content"""
    
    EXPANDED_WIDTH = 250
    COLLAPSED_WIDTH = 70
    
    def __init__(self, parent, auth_manager, on_navigate: Callable):
        super().__init__(parent, fg_color="#0d0d1a", width=self.EXPANDED_WIDTH, corner_radius=0)
        self.pack_propagate(False)
        
        self.auth_manager = auth_manager
        self.on_navigate = on_navigate
        self.active_tab = "dashboard"
        self.buttons: Dict[str, ctk.CTkButton] = {}
        self.button_data: Dict[str, Tuple[str, str]] = {}  # Store icon and text for each button
        self.user_avatar = None
        self.is_collapsed = False
        
        # Store references to collapsible elements
        self.collapsible_labels: List[ctk.CTkLabel] = []
        self.collapsible_frames: List[ctk.CTkFrame] = []
        self.logo_label = None
        self.logo_img_label = None
        self.sidebar_logo_image = None
        self.sidebar_logo_image_small = None
        self.user_frame = None
        self.user_info_frame = None
        
        self.create_sidebar()
    
    def create_sidebar(self):
        """Create sidebar layout with scrollable navigation"""
        
        # Toggle button at top
        toggle_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        toggle_frame.pack(fill="x", pady=(10, 0))
        toggle_frame.pack_propagate(False)
        
        self.toggle_btn = ctk.CTkButton(
            toggle_frame,
            text="☰",
            font=ctk.CTkFont(size=20),
            fg_color="transparent",
            hover_color="#1a1a2e",
            width=40,
            height=40,
            corner_radius=20,
            command=self.toggle_sidebar
        )
        self.toggle_btn.pack(side="left", padx=10)
        
        # Logo section (fixed at top)
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent", height=70)
        self.logo_frame.pack(fill="x", pady=(5, 10))
        self.logo_frame.pack_propagate(False)
        
        # Load and display studio logo image
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logos", "studio-logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Calculate proportional width for text-based logo (expanded)
                orig_width, orig_height = logo_img.size
                target_height = 50
                aspect_ratio = orig_width / orig_height
                target_width = int(target_height * aspect_ratio)
                target_width = max(min(target_width, 220), 160)
                self.sidebar_logo_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(target_width, target_height))
                
                # Small logo for collapsed state
                small_height = 35
                small_width = int(small_height * aspect_ratio)
                small_width = min(small_width, 50)
                self.sidebar_logo_image_small = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(small_width, small_height))
                
                self.logo_img_label = ctk.CTkLabel(self.logo_frame, image=self.sidebar_logo_image, text="")
                self.logo_img_label.pack(pady=(10, 5))
        except Exception as e:
            print(f"Could not load sidebar logo: {e}")
            # Fallback text only if logo fails to load
            self.logo_label = ctk.CTkLabel(
                self.logo_frame,
                text="✨ Shine Art Studio",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#8C00FF"
            )
            self.logo_label.pack(pady=(10, 5))
            self.collapsible_labels.append(self.logo_label)
        
        # Separator
        sep = ctk.CTkFrame(self, fg_color="#1a1a2e", height=2)
        sep.pack(fill="x", padx=20, pady=10)
        
        # Scrollable navigation container
        self.nav_scroll = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#1a1a2e",
            scrollbar_button_hover_color="#8C00FF"
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
            ("bills", "🧾", "Bills History", "can_access_invoices"),
        ]
        
        # Admin only items
        admin_items = [
            ("users", "👤", "Users", "can_access_users"),
            ("permissions", "🔐", "Permissions", "can_access_permissions"),
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
            self.admin_sep = ctk.CTkFrame(self.nav_scroll, fg_color="#1a1a2e", height=1)
            self.admin_sep.pack(fill="x", padx=10, pady=10)
            
            self.admin_label = ctk.CTkLabel(
                self.nav_scroll,
                text="ADMIN",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#666666"
            )
            self.admin_label.pack(anchor="w", padx=15, pady=(5, 5))
            self.collapsible_labels.append(self.admin_label)
            
            for tab_id, icon, text, perm_key in admin_items:
                if self.auth_manager.has_permission(perm_key):
                    self.create_nav_button(self.nav_scroll, tab_id, icon, text)
        
        # Separator before bottom items
        bottom_sep = ctk.CTkFrame(self.nav_scroll, fg_color="#1a1a2e", height=1)
        bottom_sep.pack(fill="x", padx=10, pady=10)
        
        # Bottom section items (filter by permissions)
        for tab_id, icon, text, perm_key in bottom_items:
            if self.auth_manager.has_permission(perm_key):
                self.create_nav_button(self.nav_scroll, tab_id, icon, text)
        
        # User info at very bottom (fixed)
        self.user_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=12)
        self.user_frame.pack(fill="x", padx=12, pady=(10, 15))
        
        user = self.auth_manager.get_current_user()
        if user:
            # User info layout
            self.user_content = ctk.CTkFrame(self.user_frame, fg_color="transparent")
            self.user_content.pack(fill="x", padx=12, pady=12)
            
            # User info (name + role)
            self.user_info_frame = ctk.CTkFrame(self.user_content, fg_color="transparent")
            self.user_info_frame.pack(side="left", fill="x", expand=True)
            
            self.user_name_label = ctk.CTkLabel(
                self.user_info_frame,
                text=user['full_name'],
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="white",
                anchor="w"
            )
            self.user_name_label.pack(anchor="w")
            self.collapsible_labels.append(self.user_name_label)
            
            # Role badge with styling
            role_color = "#8C00FF" if user['role'] == 'Admin' else "#00ff88"
            self.user_role_label = ctk.CTkLabel(
                self.user_info_frame,
                text=f"● {user['role']}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=role_color,
                anchor="w"
            )
            self.user_role_label.pack(anchor="w")
            self.collapsible_labels.append(self.user_role_label)
            
            # Recent login info (Admin only)
            if user['role'] == 'Admin':
                last_login = user.get('last_login')
                if last_login:
                    login_text = f"Recent: {last_login[:16]}" if len(last_login) > 16 else f"Recent: {last_login}"
                else:
                    login_text = "First login"
                self.last_login_label = ctk.CTkLabel(
                    self.user_info_frame,
                    text=login_text,
                    font=ctk.CTkFont(size=9),
                    text_color="#666666",
                    anchor="w"
                )
                self.last_login_label.pack(anchor="w")
                self.collapsible_labels.append(self.last_login_label)
            else:
                self.last_login_label = None
            
            # User icon for collapsed state
            self.user_icon_label = ctk.CTkLabel(
                self.user_content,
                text="👤",
                font=ctk.CTkFont(size=24),
                text_color="#8C00FF"
            )
            # Hidden by default in expanded state
        
        # Set dashboard as active
        self.set_active("dashboard")
    
    def toggle_sidebar(self):
        """Toggle between expanded and collapsed states"""
        if self.is_collapsed:
            self.expand_sidebar()
        else:
            self.collapse_sidebar()
    
    def collapse_sidebar(self):
        """Collapse sidebar to show only icons - optimized for performance"""
        self.is_collapsed = True
        
        # Update toggle button
        self.toggle_btn.configure(text="▶")
        
        # Hide ALL text - show only icons in buttons
        for tab_id, btn in self.buttons.items():
            icon, text = self.button_data[tab_id]
            btn.configure(text=icon, anchor="center", width=50)
        
        # Completely hide all collapsible labels
        for label in self.collapsible_labels:
            label.pack_forget()
        
        # Hide admin label if exists
        if hasattr(self, 'admin_label'):
            self.admin_label.pack_forget()
        
        # Hide logo completely
        if self.logo_img_label:
            self.logo_img_label.pack_forget()
        if self.logo_label:
            self.logo_label.pack_forget()
        
        # Minimize logo frame
        self.logo_frame.configure(height=10)
        
        # Hide user info completely, show only icon
        if self.user_info_frame:
            self.user_info_frame.pack_forget()
            self.user_name_label.pack_forget()
            self.user_role_label.pack_forget()
            if self.last_login_label:
                self.last_login_label.pack_forget()
            self.user_icon_label.pack(side="left", padx=5)
        
        # Update user frame padding
        if self.user_frame:
            self.user_frame.pack_configure(padx=8)
            self.user_content.pack_configure(padx=8, pady=8)
        
        # Apply width change
        self._animate_width(self.EXPANDED_WIDTH, self.COLLAPSED_WIDTH)
        
        # Force update to ensure all changes are applied
        self.update_idletasks()
    
    def expand_sidebar(self):
        """Expand sidebar to show full content - optimized for performance"""
        self.is_collapsed = False
        
        # Apply width change first
        self._animate_width(self.COLLAPSED_WIDTH, self.EXPANDED_WIDTH)
        
        # Update toggle button
        self.toggle_btn.configure(text="☰")
        
        # Restore full text in buttons
        for tab_id, btn in self.buttons.items():
            icon, text = self.button_data[tab_id]
            btn.configure(text=f"{icon}  {text}", anchor="w", width=0)
        
        # Restore admin label if exists
        if hasattr(self, 'admin_label') and self.admin_label in self.collapsible_labels:
            self.admin_label.pack(anchor="w", padx=15, pady=(5, 5))
        
        # Restore logo
        if self.logo_img_label and self.sidebar_logo_image:
            self.logo_img_label.configure(image=self.sidebar_logo_image)
            self.logo_img_label.pack(pady=(10, 5))
        elif self.logo_label:
            self.logo_label.pack(pady=(10, 5))
        
        # Restore logo frame height
        self.logo_frame.configure(height=70)
        
        # Restore user info
        if self.user_info_frame:
            self.user_icon_label.pack_forget()
            self.user_info_frame.pack(side="left", fill="x", expand=True)
            self.user_name_label.pack(anchor="w")
            self.user_role_label.pack(anchor="w")
            if self.last_login_label:
                self.last_login_label.pack(anchor="w")
        
        # Update user frame padding
        if self.user_frame:
            self.user_frame.pack_configure(padx=12)
            self.user_content.pack_configure(padx=12, pady=12)
        
        # Force update
        self.update_idletasks()
    
    def _animate_width(self, start_width: int, end_width: int, steps: int = 10):
        """Set sidebar width instantly for smooth performance"""
        # Instant width change - no animation lag
        self.configure(width=end_width)
        self.update_idletasks()
    
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
                    background = Image.new('RGB', img.size, (26, 26, 46))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Object-fit: cover - crop from center to make square
                width, height = img.size
                min_dim = min(width, height)
                
                left = (width - min_dim) // 2
                top = (height - min_dim) // 2
                right = left + min_dim
                bottom = top + min_dim
                
                img = img.crop((left, top, right, bottom))
                img = img.resize(size, Image.Resampling.LANCZOS)
                
                # Create perfect circular mask with anti-aliasing
                mask_size = (size[0] * 4, size[1] * 4)
                mask = Image.new('L', mask_size, 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size[0] - 1, mask_size[1] - 1), fill=255)
                mask = mask.resize(size, Image.Resampling.LANCZOS)
                
                output = Image.new('RGBA', size, (0, 0, 0, 0))
                img_rgba = img.convert('RGBA')
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
            hover_color="#1a1a2e",
            anchor="w",
            height=42,
            corner_radius=20,
            command=lambda t=tab_id: self.navigate(t)
        )
        btn.pack(fill="x", pady=2, padx=5)
        self.buttons[tab_id] = btn
        self.button_data[tab_id] = (icon, text)
    
    def navigate(self, tab_id: str):
        """Handle navigation"""
        self.set_active(tab_id)
        self.on_navigate(tab_id)
    
    def set_active(self, tab_id: str):
        """Set active tab styling"""
        self.active_tab = tab_id
        
        for tid, btn in self.buttons.items():
            if tid == tab_id:
                btn.configure(fg_color="#8C00FF", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="white")
