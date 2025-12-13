import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image
import os
import random


class ModernToast(ctk.CTkFrame):
    """Modern toast notification that appears and auto-dismisses"""
    
    def __init__(self, parent, message: str, toast_type: str = "info", duration: int = 2500):
        # Get the root window
        self.root = parent.winfo_toplevel()
        super().__init__(self.root, corner_radius=12)
        
        self.duration = duration
        
        # Colors based on type
        colors = {
            "success": {"bg": "#1e3a2f", "accent": "#00ff88", "icon": "✓"},
            "error": {"bg": "#3a1e1e", "accent": "#ff6b6b", "icon": "✕"},
            "warning": {"bg": "#3a2e1e", "accent": "#ffd93d", "icon": "⚠"},
            "info": {"bg": "#1e2a3a", "accent": "#00d4ff", "icon": "ℹ"},
        }
        
        style = colors.get(toast_type, colors["info"])
        
        self.configure(fg_color=style["bg"], border_width=1, border_color=style["accent"])
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=15, pady=12)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=style["icon"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=style["accent"],
            width=25
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Message
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="white"
        )
        msg_label.pack(side="left")
        
        # Position at top center
        self.place(relx=0.5, y=-60, anchor="n")
        
        # Animate in
        self.animate_in()
    
    def animate_in(self):
        """Slide in animation"""
        self.update_idletasks()
        self._animate_to_y(15, self.start_dismiss_timer)
    
    def _animate_to_y(self, target_y: int, callback=None):
        """Animate to target Y position"""
        current_y = self.winfo_y()
        if current_y < target_y:
            new_y = min(current_y + 8, target_y)
            self.place(relx=0.5, y=new_y, anchor="n")
            if new_y < target_y:
                self.after(10, lambda: self._animate_to_y(target_y, callback))
            elif callback:
                callback()
        elif callback:
            callback()
    
    def start_dismiss_timer(self):
        """Start timer to dismiss toast"""
        self.after(self.duration, self.animate_out)
    
    def animate_out(self):
        """Slide out animation"""
        self._animate_out_y()
    
    def _animate_out_y(self):
        """Animate out"""
        current_y = self.winfo_y()
        if current_y > -60:
            self.place(relx=0.5, y=current_y - 8, anchor="n")
            self.after(10, self._animate_out_y)
        else:
            self.destroy()


class ModernConfirmDialog(ctk.CTkToplevel):
    """Modern confirmation dialog"""
    
    def __init__(self, parent, title: str, message: str, confirm_text: str = "Yes", 
                 cancel_text: str = "No", icon: str = "?", accent_color: str = "#00d4ff"):
        super().__init__(parent)
        
        self.result = False
        
        # Window setup
        self.title("")
        self.geometry("400x220")
        self.resizable(False, False)
        self.configure(fg_color="#1a1a2e")
        
        # Center on parent
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        
        self.update_idletasks()
        x = parent.winfo_toplevel().winfo_x() + (parent.winfo_toplevel().winfo_width() // 2) - 200
        y = parent.winfo_toplevel().winfo_y() + (parent.winfo_toplevel().winfo_height() // 2) - 110
        self.geometry(f"400x220+{x}+{y}")
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Main container with border
        main = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15, border_width=2, border_color="#333355")
        main.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Icon
        icon_label = ctk.CTkLabel(
            main,
            text=icon,
            font=ctk.CTkFont(size=40),
            text_color=accent_color
        )
        icon_label.pack(pady=(25, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            main,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 5))
        
        # Message
        msg_label = ctk.CTkLabel(
            main,
            text=message,
            font=ctk.CTkFont(size=13),
            text_color="#aaaaaa"
        )
        msg_label.pack(pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=cancel_text,
            width=120,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            command=self.on_cancel
        )
        cancel_btn.pack(side="left", padx=10)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=confirm_text,
            width=120,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=accent_color,
            text_color="#1a1a2e",
            hover_color=accent_color,
            command=self.on_confirm
        )
        confirm_btn.pack(side="left", padx=10)
        
        # Keyboard bindings
        self.bind("<Return>", lambda e: self.on_confirm())
        self.bind("<Escape>", lambda e: self.on_cancel())
        
        # Focus
        confirm_btn.focus_set()
    
    def on_confirm(self):
        self.result = True
        self.destroy()
    
    def on_cancel(self):
        self.result = False
        self.destroy()
    
    def get_result(self) -> bool:
        self.wait_window()
        return self.result


class Toast:
    """Static class to show toast notifications"""
    
    @staticmethod
    def success(parent, message: str, duration: int = 2500):
        """Show success toast"""
        ModernToast(parent, message, "success", duration)
    
    @staticmethod
    def error(parent, message: str, duration: int = 3000):
        """Show error toast"""
        ModernToast(parent, message, "error", duration)
    
    @staticmethod
    def warning(parent, message: str, duration: int = 3000):
        """Show warning toast"""
        ModernToast(parent, message, "warning", duration)
    
    @staticmethod
    def info(parent, message: str, duration: int = 2500):
        """Show info toast"""
        ModernToast(parent, message, "info", duration)
    
    @staticmethod
    def confirm(parent, title: str, message: str, confirm_text: str = "Yes", 
                cancel_text: str = "No", icon: str = "?", accent_color: str = "#00d4ff") -> bool:
        """Show confirmation dialog and return result"""
        dialog = ModernConfirmDialog(parent, title, message, confirm_text, cancel_text, icon, accent_color)
        return dialog.get_result()


class LoginWindow(ctk.CTkToplevel):
    """Login window for user authentication"""
    
    def __init__(self, parent, auth_manager, on_success: Callable):
        super().__init__(parent)
        
        self.auth_manager = auth_manager
        self.on_success = on_success
        
        self.title("Shine Art Studio - Login")
        
        # Set window size
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.75)
        window_height = int(screen_height * 0.8)
        
        # Center window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Prevent resize
        self.resizable(False, False)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create login form widgets"""
        
        # Set window background
        self.configure(fg_color="#1a1a2e")
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#1a1a2e")
        main_container.pack(fill="both", expand=True)
        
        # Left side - Image panel
        left_panel = ctk.CTkFrame(main_container, fg_color="#1a1a2e", corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)
        
        # Random image selection
        self.display_image = None
        try:
            assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
            image_files = ["Image1.jpg", "image2.jpg", "image3.jpg"]
            available_images = [os.path.join(assets_path, img) for img in image_files if os.path.exists(os.path.join(assets_path, img))]
            
            if available_images:
                selected_image_path = random.choice(available_images)
                login_img = Image.open(selected_image_path)
                
                # Calculate image size
                window_height = int(self.winfo_screenheight() * 0.8)
                target_height = window_height - 100
                aspect_ratio = login_img.width / login_img.height
                target_width = int(target_height * aspect_ratio)
                
                self.display_image = ctk.CTkImage(
                    light_image=login_img,
                    dark_image=login_img,
                    size=(target_width, target_height)
                )
                
                img_label = ctk.CTkLabel(left_panel, image=self.display_image, text="")
                img_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print(f"Could not load login image: {e}")
            fallback = ctk.CTkLabel(
                left_panel,
                text="Shine Art Studio",
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color="white"
            )
            fallback.place(relx=0.5, rely=0.5, anchor="center")
        
        # Right side - Login form panel
        right_panel = ctk.CTkFrame(main_container, fg_color="#1a1a2e", width=520, corner_radius=0)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Form container
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        self.logo_image = None
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo001.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(110, 110))
                logo_label = ctk.CTkLabel(form_container, image=self.logo_image, text="")
                logo_label.pack(pady=(0, 25))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Title with hierarchy
        title_label = ctk.CTkLabel(
            form_container,
            text="Shine Art Studio",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(pady=(0, 8))
        
        subtitle_label = ctk.CTkLabel(
            form_container,
            text="Photography POS System",
            font=ctk.CTkFont(size=15),
            text_color="#888888"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Username field
        username_label = ctk.CTkLabel(
            form_container,
            text="Username",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cccccc",
            anchor="w"
        )
        username_label.pack(pady=(0, 10), anchor="w", padx=5)
        
        self.username_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your username",
            height=48,
            width=420,
            font=ctk.CTkFont(size=15),
            border_width=2,
            corner_radius=8
        )
        self.username_entry.pack(pady=(0, 25))
        
        # Password field
        password_label = ctk.CTkLabel(
            form_container,
            text="Password",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cccccc",
            anchor="w"
        )
        password_label.pack(pady=(0, 10), anchor="w", padx=5)
        
        self.password_entry = ctk.CTkEntry(
            form_container,
            placeholder_text="Enter your password",
            show="●",
            height=48,
            width=420,
            font=ctk.CTkFont(size=15),
            border_width=2,
            corner_radius=8
        )
        self.password_entry.pack(pady=(0, 35))
        
        # Login button with enhanced styling
        login_btn = ctk.CTkButton(
            form_container,
            text="LOGIN",
            command=self.handle_login,
            height=52,
            width=420,
            font=ctk.CTkFont(size=17, weight="bold"),
            fg_color="#1f538d",
            hover_color="#163d6b",
            corner_radius=8,
            border_width=0
        )
        login_btn.pack(pady=(0, 20))
        
        # Footer
        footer_label = ctk.CTkLabel(
            right_panel,
            text="Developed by Malinda Prabath\n© 2025 Photography Studio Management System. All rights reserved.",
            font=ctk.CTkFont(size=11),
            text_color="#555555",
            justify="center"
        )
        footer_label.pack(side="bottom", pady=25)
        
        # Keyboard bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Set focus
        self.after(100, lambda: self.username_entry.focus())
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            Toast.error(self, "Please enter your username")
            self.username_entry.focus()
            return
        
        if not password:
            Toast.error(self, "Please enter your password")
            self.password_entry.focus()
            return
        
        user = self.auth_manager.authenticate(username, password)
        
        if user:
            # No popup - just login directly
            self.destroy()
            self.on_success(user)
        else:
            Toast.error(self, "Invalid username or password")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()


class MessageDialog:
    """Utility class for showing messages - now uses modern Toast"""
    
    _parent = None
    
    @staticmethod
    def set_parent(parent):
        """Set the parent widget for toasts"""
        MessageDialog._parent = parent
    
    @staticmethod
    def show_error(title: str, message: str):
        """Show error toast"""
        if MessageDialog._parent:
            Toast.error(MessageDialog._parent, message)
    
    @staticmethod
    def show_success(title: str, message: str):
        """Show success toast"""
        if MessageDialog._parent:
            Toast.success(MessageDialog._parent, message)
    
    @staticmethod
    def show_warning(title: str, message: str):
        """Show warning toast"""
        if MessageDialog._parent:
            Toast.warning(MessageDialog._parent, message)
    
    @staticmethod
    def show_confirm(title: str, message: str) -> bool:
        """Show confirmation dialog"""
        if MessageDialog._parent:
            return Toast.confirm(MessageDialog._parent, title, message)
        return False


class BaseFrame(ctk.CTkFrame):
    """Base frame with common functionality"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        
    def validate_number(self, value: str, allow_decimal: bool = False) -> bool:
        """Validate if value is a number"""
        if not value:
            return False
        try:
            if allow_decimal:
                float(value)
            else:
                int(value)
            return True
        except ValueError:
            return False
    
    def validate_mobile(self, mobile: str) -> bool:
        """Validate mobile number (10 digits)"""
        return mobile.isdigit() and len(mobile) == 10
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.auth_manager.is_admin()
