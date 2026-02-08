import customtkinter as ctk


class UserGuideFrame(ctk.CTkFrame):
    """User guide and documentation page"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create user guide widgets"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="📖 User Guide & Documentation",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main scrollable container
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Welcome section with hero card
        welcome_card = ctk.CTkFrame(main, fg_color="#1e3a2f", corner_radius=15, border_width=2, border_color="#00ff88")
        welcome_card.pack(fill="x", pady=10)
        
        welcome_content = ctk.CTkFrame(welcome_card, fg_color="transparent")
        welcome_content.pack(fill="x", padx=25, pady=20)
        
        ctk.CTkLabel(
            welcome_content,
            text="👋 Welcome to Shine Art Studio POS",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00ff88"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            welcome_content,
            text="Your complete photography studio management solution",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        ).pack(anchor="w", pady=(5, 15))
        
        features_frame = ctk.CTkFrame(welcome_content, fg_color="transparent")
        features_frame.pack(fill="x")
        
        features = [
            ("👥", "Customer Management"),
            ("💰", "Billing & Invoices"),
            ("📅", "Booking System"),
            ("🖼", "Frame Inventory"),
            ("📊", "Advanced Reports"),
            ("💵", "Expense Tracking"),
            ("📜", "Bill History"),
            ("⚙️", "Easy Settings"),
        ]
        
        for i, (icon, text) in enumerate(features):
            feat = ctk.CTkFrame(features_frame, fg_color="#0d0d1a", corner_radius=8)
            feat.pack(side="left", padx=(0, 10), pady=5)
            ctk.CTkLabel(feat, text=f"  {icon} {text}  ", font=ctk.CTkFont(size=12)).pack(padx=10, pady=8)
        
        # Quick Start Guide
        self.create_guide_section(
            main,
            "🚀",
            "Quick Start Guide",
            "#8C00FF",
            [
                ("Step 1: Login", "Enter your username and password. Default admin: admin / admin123"),
                ("Step 2: Navigate", "Use the sidebar to access different sections of the app"),
                ("Step 3: Add Data", "Start by adding customers, services, and photo frames"),
                ("Step 4: Create Invoices", "Go to Billing to create invoices for customers"),
                ("Step 5: Track Business", "Check Dashboard for overview and reports"),
            ]
        )
        
        # Billing Guide
        self.create_guide_section(
            main,
            "💰",
            "Billing & Invoices",
            "#ffd93d",
            [
                ("Search Customer", "Type 5+ digits of phone number to auto-search customers"),
                ("Guest Customer", "Click 'Guest' for walk-in customers without registration"),
                ("Add Items", "Browse Services and Frames tabs, click 'Add to Cart'"),
                ("Manage Cart", "Use +/- buttons for quantity, trash icon to remove"),
                ("Apply Discount", "Enter discount amount before generating invoice"),
                ("Generate Invoice", "Click button to create and print invoice PDF"),
                ("Payment Types", "Full payment or partial with advance amount"),
                ("Quick Print", "Invoices auto-print after generation"),
            ]
        )
        
        # Customer Management
        self.create_guide_section(
            main,
            "👥",
            "Customer Management",
            "#00ff88",
            [
                ("Add Customer", "Go to Customers → Fill form → Click Add"),
                ("Edit Customer", "Select from table → Edit details → Click Update"),
                ("Search", "Use search bar to find by name or phone number"),
                ("Quick Add", "In Billing, click 'New Customer' for quick add"),
            ]
        )
        
        # Services Management
        self.create_guide_section(
            main,
            "📋",
            "Services Management",
            "#ff6b6b",
            [
                ("Add Service", "Go to Services → Enter name & price → Click Add"),
                ("Edit Service", "Select from list → Update details → Save"),
                ("Delete Service", "Select service → Click Delete button"),
                ("Categories", "Organize services by type (Photography, Editing, etc.)"),
            ]
        )
        
        # Photo Frames
        self.create_guide_section(
            main,
            "🖼",
            "Photo Frames Inventory",
            "#9b59b6",
            [
                ("Add Frame", "Go to Photo Frames → Enter details → Add"),
                ("Track Stock", "Stock automatically decreases when frames are sold"),
                ("Low Stock Alert", "Dashboard shows warning for low stock items"),
                ("Restock", "Update quantity when new frames arrive"),
            ]
        )
        
        # Bookings
        self.create_guide_section(
            main,
            "📅",
            "Booking Management",
            "#e67e22",
            [
                ("Create Booking", "Go to Bookings → Select customer & category → Enter details"),
                ("Advance Payment", "Collect advance amount during booking creation"),
                ("Settlement Invoice", "Create final invoice when customer completes payment"),
                ("View Schedule", "Table view shows all bookings with payment status"),
                ("Track Payments", "See advance paid, balance due, and settlement status"),
                ("Reprint Booking Invoice", "Reprint advance payment receipts anytime"),
            ]
        )
        
        # Bill History
        self.create_guide_section(
            main,
            "📜",
            "Bill History",
            "#3498db",
            [
                ("View All Bills", "Go to Bill History to see all past bills"),
                ("Search", "Find bills by number, customer name, or phone"),
                ("Date Filter", "Filter bills by date range for specific periods"),
                ("Guest Filter", "Toggle 'Include Guest' to show/hide guest customer bills"),
                ("Reprint Bills", "Select bill → Click Reprint to generate PDF"),
                ("Payment Details", "View payment method, discount, and amount paid"),
                ("Export Data", "Filter and export bills for accounting purposes"),
            ]
        )
        
        # Invoice History
        self.create_guide_section(
            main,
            "📄",
            "Invoice History",
            "#16a085",
            [
                ("View Invoices", "Go to Invoices to see all advance and settlement invoices"),
                ("Search", "Find invoices by number, customer, or date"),
                ("Invoice Types", "Normal invoices, booking advances, and settlements"),
                ("Reprint", "Select invoice → Click Reprint to generate PDF"),
                ("Balance Due", "Track invoices with pending payments"),
            ]
        )
        
        # Expenses Management
        self.create_guide_section(
            main,
            "💵",
            "Expense Management",
            "#c0392b",
            [
                ("Add Expense", "Go to Expenses → Enter details → Click Add"),
                ("Categories", "Categorize expenses: Rent, Utilities, Supplies, etc."),
                ("Track Spending", "View all expenses with date and category"),
                ("Monthly Report", "Dashboard shows monthly expense summary"),
                ("Edit/Delete", "Update or remove expense entries as needed"),
            ]
        )
        
        # Categories Management
        self.create_guide_section(
            main,
            "📂",
            "Category Management",
            "#8e44ad",
            [
                ("Service Categories", "Organize services by type (Wedding, Portrait, etc.)"),
                ("Frame Categories", "Group frames by size or material"),
                ("Expense Categories", "Create custom expense categories"),
                ("Easy Organization", "Categories help in reporting and analytics"),
            ]
        )
        
        # Reports & Analytics
        self.create_guide_section(
            main,
            "📊",
            "Reports & Analytics",
            "#2980b9",
            [
                ("Dashboard Overview", "Real-time stats: revenue, expenses, profit"),
                ("Executive Report", "Comprehensive business report with charts and trends"),
                ("Industrial Report", "Detailed operational report for management"),
                ("Financial Report", "Income, expenses, and profit analysis"),
                ("Staff Report", "Individual staff performance tracking"),
                ("Expense Report", "Detailed expense breakdown by category"),
                ("Export Reports", "Generate PDF reports for accounting"),
            ]
        )
        
        # Admin Features
        if self.auth_manager.is_admin():
            self.create_guide_section(
                main,
                "👤",
                "User Management (Admin Only)",
                "#e74c3c",
                [
                    ("Add User", "Go to Users → Fill form → Set role → Add"),
                    ("Edit User", "Select user → Update details → Save"),
                    ("Reset Password", "Select user → Enter new password → Update"),
                    ("Roles", "Admin: Full access | Staff: Limited access"),
                    ("Disable Account", "Set status to Disabled instead of deleting"),
                ]
            )
            
            self.create_guide_section(
                main,
                "🔐",
                "Permissions (Admin Only)",
                "#d35400",
                [
                    ("Role Management", "Set permissions for Admin and Staff roles"),
                    ("Feature Access", "Control who can access billing, expenses, reports"),
                    ("Delete Permissions", "Restrict deletion of customers, services, etc."),
                    ("Custom Permissions", "Fine-tune access for each feature"),
                    ("Security", "Protect sensitive data with role-based access"),
                ]
            )
            
            self.create_guide_section(
                main,
                "⚙️",
                "Settings (Admin Only)",
                "#95a5a6",
                [
                    ("Studio Info", "Update studio name and contact details"),
                    ("Invoice Settings", "Configure header, footer, and terms"),
                    ("Appearance", "Switch between Dark, Light, or System theme"),
                    ("Backup", "Create database backup for safety"),
                    ("Restore", "Recover from backup if needed"),
                    ("Profile Settings", "Update your profile and password"),
                ]
            )
        
        # Tips Section
        tips_card = ctk.CTkFrame(main, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        tips_card.pack(fill="x", pady=10)
        
        tips_header = ctk.CTkFrame(tips_card, fg_color="#0d0d1a", corner_radius=10)
        tips_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            tips_header,
            text="💡 Pro Tips & Best Practices",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffd93d"
        ).pack(anchor="w", padx=15, pady=12)
        
        tips_content = ctk.CTkFrame(tips_card, fg_color="transparent")
        tips_content.pack(fill="x", padx=25, pady=(0, 20))
        
        tips = [
            "🔄 Create regular backups (weekly recommended)",
            "📊 Check Dashboard daily for business overview and trends",
            "📱 Keep customer phone numbers accurate for easy search",
            "🖼 Monitor frame stock to avoid running out",
            "📅 Use advance payment system for bookings to secure orders",
            "💾 Store backups in a safe external location",
            "🔐 Change default admin password after first login",
            "📝 Use guest filter in Bill History to analyze walk-in sales",
            "💵 Track expenses regularly for accurate profit calculation",
            "📈 Review Executive Reports monthly for business insights",
            "⚡ Settlement invoices automatically link to original bookings",
            "🎨 Use categories to organize services and frames efficiently",
        ]
        
        for tip in tips:
            tip_row = ctk.CTkFrame(tips_content, fg_color="#0d0d1a", corner_radius=8)
            tip_row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                tip_row,
                text=tip,
                font=ctk.CTkFont(size=13),
                text_color="#cccccc",
                anchor="w"
            ).pack(anchor="w", padx=15, pady=10)
        
        # Footer
        footer = ctk.CTkFrame(main, fg_color="transparent")
        footer.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            footer,
            text="Need more help? Visit the Support page or contact the developer.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()
    
    def create_guide_section(self, parent, icon, title, color, items):
        """Create a guide section with items"""
        section = ctk.CTkFrame(parent, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        section.pack(fill="x", pady=10)
        
        # Header
        header = ctk.CTkFrame(section, fg_color="#0d0d1a", corner_radius=10)
        header.pack(fill="x", padx=15, pady=15)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="x", padx=15, pady=12)
        
        # Icon badge
        icon_badge = ctk.CTkFrame(header_content, fg_color=color, width=40, height=40, corner_radius=20)
        icon_badge.pack(side="left", padx=(0, 15))
        icon_badge.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_badge,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color="white" if color not in ["#ffd93d", "#95a5a6"] else "#1a1a2e"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            header_content,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color
        ).pack(side="left")
        
        # Content
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        for item_title, item_desc in items:
            item_frame = ctk.CTkFrame(content, fg_color="#0d0d1a", corner_radius=8)
            item_frame.pack(fill="x", pady=3)
            
            item_content = ctk.CTkFrame(item_frame, fg_color="transparent")
            item_content.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                item_content,
                text=f"▸ {item_title}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=color,
                anchor="w"
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                item_content,
                text=item_desc,
                font=ctk.CTkFont(size=12),
                text_color="#aaaaaa",
                anchor="w",
                wraplength=800
            ).pack(anchor="w", pady=(2, 0))
