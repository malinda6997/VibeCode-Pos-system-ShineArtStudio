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
            text="📖 User Guide",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main scrollable container
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Welcome section
        self.create_guide_section(
            main,
            "👋 Welcome to Shine Art Studio POS",
            """
Welcome to the Shine Art Studio Point of Sale System! This comprehensive guide will help you understand and use all features of the application effectively.

The POS system is designed to help photography studios manage their daily operations including:
• Customer management
• Service and product pricing
• Photo frame inventory
• Booking management
• Invoice generation and printing
• Sales reports and analytics
            """
        )
        
        # Getting Started
        self.create_guide_section(
            main,
            "🚀 Getting Started",
            """
1. LOGIN
   • Enter your username and password on the login screen
   • Default admin credentials: admin / admin123
   • Contact your administrator if you forget your password

2. NAVIGATION
   • Use the sidebar on the left to navigate between different sections
   • The sidebar shows your current active page highlighted in cyan
   • Admin-only sections appear only for administrator accounts
            """
        )
        
        # Billing Guide
        self.create_guide_section(
            main,
            "💰 Billing & Invoices",
            """
CREATING A NEW INVOICE:
1. Go to "Billing" from the sidebar
2. Search and select a customer (or add a new one)
3. Browse Services and Photo Frames tabs
4. Click "Add to Cart" for items you want to include
5. Adjust quantities in the cart if needed
6. Enter discount or advance payment if applicable
7. Click "Generate Invoice"
8. The invoice PDF will be generated and can be printed

CART MANAGEMENT:
• Use +/- buttons to adjust item quantities
• Click the trash icon to remove items
• The total is automatically calculated

PAYMENT OPTIONS:
• Full Payment: Customer pays the total amount
• Partial Payment: Enter advance amount for balance due later
            """
        )
        
        # Customer Management
        self.create_guide_section(
            main,
            "👥 Customer Management",
            """
ADDING NEW CUSTOMERS:
1. Navigate to "Customers" from sidebar
2. Fill in customer details:
   • Full Name (required)
   • Phone Number (required)
   • Email (optional)
   • Address (optional)
3. Click "Add Customer"

EDITING CUSTOMERS:
1. Select a customer from the list
2. Edit the details in the form
3. Click "Update Customer"

SEARCHING CUSTOMERS:
• Use the search bar to find customers by name or phone
• Results update as you type
            """
        )
        
        # Services Management
        self.create_guide_section(
            main,
            "📋 Services Management",
            """
ADDING NEW SERVICES:
1. Go to "Services" from sidebar
2. Enter service details:
   • Service Name
   • Description
   • Price
3. Click "Add Service"

EDITING/DELETING:
• Select a service from the list to edit
• Use Update or Delete buttons as needed
• Prices can be updated at any time
            """
        )
        
        # Photo Frames
        self.create_guide_section(
            main,
            "🖼️ Photo Frames Inventory",
            """
MANAGING FRAME INVENTORY:
1. Navigate to "Photo Frames"
2. Add new frame types with:
   • Frame name/size (e.g., "8x10 Wood Frame")
   • Stock quantity
   • Price per unit
3. Stock levels are automatically updated when frames are sold

LOW STOCK ALERTS:
• Frames with stock below threshold show warning
• Check Dashboard for quick low stock overview
• Restock before running out!
            """
        )
        
        # Bookings
        self.create_guide_section(
            main,
            "📅 Booking Management",
            """
CREATING A BOOKING:
1. Go to "Bookings" from sidebar
2. Select a customer
3. Choose booking date and time
4. Select service type (e.g., Wedding, Portrait)
5. Add notes about the booking
6. Click "Save Booking"

MANAGING BOOKINGS:
• Pending bookings show in the list
• Click to select and view details
• Update status when session is complete
• Filter by date to find specific bookings
            """
        )
        
        # Invoice History
        self.create_guide_section(
            main,
            "📄 Invoice History",
            """
VIEWING PAST INVOICES:
1. Navigate to "Invoices" from sidebar
2. Browse the list of all generated invoices
3. Use search to find specific invoices
4. Filter by date range

REPRINTING INVOICES:
• Select any invoice from the list
• Click "Reprint Invoice"
• A new PDF copy will be generated

CHECKING BALANCES:
• Invoices with pending balance are highlighted
• Process additional payments when received
            """
        )
        
        # Admin Features
        if self.auth_manager.is_admin():
            self.create_guide_section(
                main,
                "👤 User Management (Admin Only)",
                """
ADDING NEW USERS:
1. Go to "Users" from sidebar
2. Fill in user details:
   • Full Name
   • Username
   • Password (min 6 characters)
   • Role (Admin or Staff)
3. Click "Add User"

MANAGING USERS:
• Edit user details by selecting from list
• Reset passwords when users forget
• Disable accounts instead of deleting
• Admins have full access, Staff have limited access
                """
            )
            
            self.create_guide_section(
                main,
                "⚙️ Settings (Admin Only)",
                """
STUDIO SETTINGS:
• Update studio name and contact information
• Configure invoice header and footer text
• Set currency and tax rates

APPEARANCE:
• Switch between Dark, Light, or System theme
• Configure low stock alert threshold

BACKUP & RESTORE:
• Regular backups are recommended
• Click "Backup Database" to save a copy
• Use "Restore Database" to recover from backup
• Always backup before major changes!
                """
            )
        
        # Keyboard Shortcuts
        self.create_guide_section(
            main,
            "⌨️ Tips & Best Practices",
            """
DAILY WORKFLOW:
1. Start by checking the Dashboard for overview
2. Review pending bookings for the day
3. Process any outstanding invoices
4. Check low stock items and reorder
5. Backup data at end of day

DATA SAFETY:
• Create regular backups (weekly recommended)
• Store backups in a safe location
• Test restore procedure occasionally

PERFORMANCE TIPS:
• Close unused browser windows
• Restart application if it becomes slow
• Report any issues to support
            """
        )
    
    def create_guide_section(self, parent, title: str, content: str):
        """Create a guide section"""
        section = ctk.CTkFrame(parent, fg_color="#1e1e3f", corner_radius=15)
        section.pack(fill="x", pady=10)
        
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        )
        title_label.pack(anchor="w", padx=25, pady=(20, 10))
        
        content_label = ctk.CTkLabel(
            section,
            text=content.strip(),
            font=ctk.CTkFont(size=13),
            text_color="#cccccc",
            justify="left",
            anchor="w",
            wraplength=900
        )
        content_label.pack(anchor="w", padx=25, pady=(0, 20))
