import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image
import os


class ModernToast(ctk.CTkToplevel):
    """Modern toast notification that appears and auto-dismisses"""
    
    def __init__(self, parent, message: str, toast_type: str = "info", duration: int = 700):
        # Get the root window
        self.root = parent.winfo_toplevel()
        super().__init__(self.root)
        
        self.duration = duration
        
        # Remove window decorations
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(fg_color="#0d0d1a")
        
        # Colors based on type
        colors = {
            "success": {"bg": "#1e2f1e", "accent": "#8C00FF", "icon": "✓"},
            "error": {"bg": "#3a1e1e", "accent": "#ff6b6b", "icon": "✕"},
            "warning": {"bg": "#3a2e1e", "accent": "#ffd93d", "icon": "⚠"},
            "info": {"bg": "#1e1e2f", "accent": "#8C00FF", "icon": "ℹ"},
        }
        
        style = colors.get(toast_type, colors["info"])
        
        # Main frame with styling
        main_frame = ctk.CTkFrame(self, fg_color=style["bg"], corner_radius=12, 
                                   border_width=2, border_color=style["accent"])
        main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Content
        content = ctk.CTkFrame(main_frame, fg_color="transparent")
        content.pack(padx=25, pady=18)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content,
            text=style["icon"],
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=style["accent"],
            width=35
        )
        icon_label.pack(side="left", padx=(0, 15))
        
        # Message
        msg_label = ctk.CTkLabel(
            content,
            text=message,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        )
        msg_label.pack(side="left")
        
        # Position toast at top center of root window
        self.update_idletasks()
        
        toast_width = self.winfo_reqwidth()
        root_x = self.root.winfo_x()
        root_width = self.root.winfo_width()
        root_y = self.root.winfo_y()
        
        x = root_x + (root_width // 2) - (toast_width // 2)
        self.target_y = root_y + 30
        self.current_y = root_y - 100
        
        self.geometry(f"+{x}+{self.current_y}")
        
        # Start animation
        self.after(10, self.animate_in)
    
    def animate_in(self):
        """Slide in animation"""
        try:
            if self.current_y < self.target_y:
                self.current_y += 20
                x = self.winfo_x()
                self.geometry(f"+{x}+{self.current_y}")
                self.after(5, self.animate_in)
            else:
                self.after(self.duration, self.animate_out)
        except:
            pass
    
    def animate_out(self):
        """Slide out animation"""
        try:
            if self.current_y > self.root.winfo_y() - 100:
                self.current_y -= 20
                x = self.winfo_x()
                self.geometry(f"+{x}+{self.current_y}")
                self.after(5, self.animate_out)
            else:
                self.destroy()
        except:
            pass


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
        self._close_dialog()
    
    def on_cancel(self):
        self.result = False
        self._close_dialog()
    
    def _close_dialog(self):
        """Properly close dialog and release grab"""
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
    
    def get_result(self) -> bool:
        self.wait_window()
        return self.result


class Toast:
    """Static class to show toast notifications"""
    
    @staticmethod
    def success(parent, message: str, duration: int = 700):
        """Show success toast"""
        ModernToast(parent, message, "success", duration)
    
    @staticmethod
    def error(parent, message: str, duration: int = 700):
        """Show error toast"""
        ModernToast(parent, message, "error", duration)
    
    @staticmethod
    def warning(parent, message: str, duration: int = 700):
        """Show warning toast"""
        ModernToast(parent, message, "warning", duration)
    
    @staticmethod
    def info(parent, message: str, duration: int = 700):
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
        
        self.parent = parent
        self.auth_manager = auth_manager
        self.on_success = on_success
        
        self.title("Shine Art Studio - Login")
        
        # Set window icon
        self._set_window_icon()
        
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
        
        # Handle window close event (X button or Alt+F4)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
    
    def _set_window_icon(self):
        """Set the login window icon"""
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logos", "App logo.jpg")
            if os.path.exists(icon_path):
                from PIL import ImageTk
                icon_image = Image.open(icon_path)
                # Create multiple sizes for better display
                icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                icon_photos = []
                for size in icon_sizes:
                    resized = icon_image.resize(size, Image.Resampling.LANCZOS)
                    icon_photos.append(ImageTk.PhotoImage(resized))
                self._icon_photos = icon_photos  # Keep reference to prevent garbage collection
                self.iconphoto(True, *icon_photos)
        except Exception as e:
            print(f"Could not load login window icon: {e}")
        
    def create_widgets(self):
        """Create login form widgets"""
        
        # Set window background
        self.configure(fg_color="#060606")
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="#060606")
        main_container.pack(fill="both", expand=True)
        
        # Left side - Image panel
        left_panel = ctk.CTkFrame(main_container, fg_color="#060606", corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)
        
        # Display login image
        self.display_image = None
        try:
            assets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "login_images")
            image_path = os.path.join(assets_path, "loginimage01.jpg")
            
            if os.path.exists(image_path):
                login_img = Image.open(image_path)
                
                # Calculate image size to fill left panel while maintaining aspect ratio
                window_height = int(self.winfo_screenheight() * 0.8)
                target_height = window_height
                aspect_ratio = login_img.width / login_img.height
                target_width = int(target_height * aspect_ratio)
                
                self.display_image = ctk.CTkImage(
                    light_image=login_img,
                    dark_image=login_img,
                    size=(target_width, target_height)
                )
                
                img_label = ctk.CTkLabel(left_panel, image=self.display_image, text="", fg_color="#060606")
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
        right_panel = ctk.CTkFrame(main_container, fg_color="#060606", width=520, corner_radius=0)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        
        # Form container
        form_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        form_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo - Match dashboard sidebar proportions
        self.logo_image = None
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logos", "studio-logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Use same sizing logic as sidebar dashboard
                orig_width, orig_height = logo_img.size
                target_height = 50
                aspect_ratio = orig_width / orig_height
                target_width = int(target_height * aspect_ratio)
                # Constrain width to fit login panel (max 220px like sidebar)
                target_width = max(min(target_width, 220), 160)
                self.logo_image = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(target_width, target_height))
                logo_label = ctk.CTkLabel(form_container, image=self.logo_image, text="")
                logo_label.pack(pady=(0, 30))
        except Exception as e:
            print(f"Could not load logo: {e}")
        
        # Welcoming subtitle message
        subtitle_label = ctk.CTkLabel(
            form_container,
            text="Welcome! Please login to your account",
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
            corner_radius=20
        )
        self.username_entry.pack(pady=(0, 25))
        
        # Password field with visibility toggle
        password_container = ctk.CTkFrame(form_container, fg_color="transparent")
        password_container.pack(pady=(0, 35))
        
        password_label = ctk.CTkLabel(
            password_container,
            text="Password",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cccccc",
            anchor="w"
        )
        password_label.pack(pady=(0, 10), anchor="w", padx=5)
        
        # Password entry and toggle button container
        password_input_frame = ctk.CTkFrame(password_container, fg_color="transparent")
        password_input_frame.pack()
        
        self.password_entry = ctk.CTkEntry(
            password_input_frame,
            placeholder_text="Enter your password",
            show="●",
            height=48,
            width=360,
            font=ctk.CTkFont(size=15),
            border_width=2,
            corner_radius=20
        )
        self.password_entry.pack(side="left", padx=(0, 10))
        
        # Password visibility toggle
        self.password_visible = False
        self.toggle_password_btn = ctk.CTkButton(
            password_input_frame,
            text="👁",
            command=self.toggle_password_visibility,
            width=50,
            height=48,
            font=ctk.CTkFont(size=18),
            fg_color="#2b2b2b",
            hover_color="#3d3d3d",
            corner_radius=20
        )
        self.toggle_password_btn.pack(side="left")
        
        # Login button with enhanced styling
        login_btn = ctk.CTkButton(
            form_container,
            text="LOGIN",
            command=self.handle_login,
            height=52,
            width=420,
            font=ctk.CTkFont(size=17, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=25,
            border_width=0
        )
        login_btn.pack(pady=(0, 20))
        
        # Footer
        footer_label = ctk.CTkLabel(
            right_panel,
            text="Developed by Malinda Prabath\n© 2025 Photography Studio Management System. All rights reserved.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            justify="center"
        )
        footer_label.pack(side="bottom", pady=25)
        
        # Keyboard bindings
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # Set focus
        self.after(100, lambda: self.username_entry.focus())
    
    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_visible:
            self.password_entry.configure(show="●")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.password_visible = True
    
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
            # Release grab before destroying to prevent input freeze
            try:
                self.grab_release()
            except:
                pass
            self.destroy()
            self.on_success(user)
        else:
            Toast.error(self, "Invalid username or password")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
    
    def on_close(self):
        """Handle window close event - exit entire application"""
        try:
            self.grab_release()
        except:
            pass
        self.destroy()
        self.parent.destroy()


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
    
    def restore_focus(self, widget=None):
        """Restore focus to widget or main window after dialog/popup closes"""
        try:
            self.winfo_toplevel().focus_force()
            if widget:
                widget.focus_set()
        except:
            pass
    
    def ensure_inputs_enabled(self, *widgets):
        """Ensure input widgets are in normal state and editable"""
        for widget in widgets:
            try:
                if hasattr(widget, 'configure'):
                    widget.configure(state="normal")
            except:
                pass
    
    def create_modern_table(self, parent, columns, column_widths=None, height=15):
        """Create a modern styled treeview table with enhanced visuals"""
        from tkinter import ttk
        
        # Create container frame with rounded corners effect
        table_container = ctk.CTkFrame(parent, fg_color="#0d0d1a", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Inner frame for table
        inner_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Create Treeview
        tree = ttk.Treeview(inner_frame, columns=columns, show="headings", height=height)
        
        # Configure columns
        default_width = 120
        for i, col in enumerate(columns):
            tree.heading(col, text=col)
            width = column_widths.get(col, default_width) if column_widths else default_width
            anchor = "center" if col in ["ID", "Status", "Qty", "Role"] else "w"
            if "Price" in col or "Amount" in col or "Total" in col or "LKR" in col or "Profit" in col:
                anchor = "e"
            tree.column(col, width=width, anchor=anchor)
        
        # Configure row tags for alternating colors
        tree.tag_configure('oddrow', background='#1e1e3f', foreground='#e0e0e0')
        tree.tag_configure('evenrow', background='#252545', foreground='#e0e0e0')
        tree.tag_configure('selected', background='#00d4ff', foreground='#1a1a2e')
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(inner_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree, table_container
    
    def insert_table_row(self, tree, values, index=None):
        """Insert a row with alternating colors"""
        if index is None:
            index = len(tree.get_children())
        tag = 'evenrow' if index % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=values, tags=(tag,))
    
    def refresh_table_tags(self, tree):
        """Refresh alternating row colors after modifications"""
        for i, item in enumerate(tree.get_children()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.item(item, tags=(tag,))
