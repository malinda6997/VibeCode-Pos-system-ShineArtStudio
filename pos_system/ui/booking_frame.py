import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from ui.components import BaseFrame, MessageDialog, Toast
from datetime import datetime
from services.invoice_generator import InvoiceGenerator


class BookingManagementFrame(BaseFrame):
    """Booking and photoshoot management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_booking_id = None
        self.categories_map = {}  # name -> id mapping
        self.services_map = {}  # name -> service data
        self.invoice_generator = InvoiceGenerator()
        self.current_filter = "Pending"  # Default filter to Pending
        self.create_widgets()
        self.load_categories()
        self.load_bookings()
    
    def create_widgets(self):
        """Create booking management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Booking / Photoshoot Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Form (Scrollable)
        left_panel = ctk.CTkFrame(container, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15, width=450)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Scrollable form container
        form_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="#0d0d1a", corner_radius=10)
        form_scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Form title
        ctk.CTkLabel(
            form_scroll,
            text="📝 Booking Details",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 15))
        
        # Customer name
        ctk.CTkLabel(
            form_scroll,
            text="Customer Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13), corner_radius=15, border_width=1)
        self.name_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Mobile number
        ctk.CTkLabel(
            form_scroll,
            text="Mobile Number:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.mobile_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13), corner_radius=15, border_width=1)
        self.mobile_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Category selection - LOCKED TO "Booking" (Read-only)
        ctk.CTkLabel(
            form_scroll,
            text="Category:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        # Static read-only entry showing "Booking"
        self.category_entry = ctk.CTkEntry(
            form_scroll,
            height=38,
            font=ctk.CTkFont(size=13, weight="bold"),
            state="readonly",
            fg_color="#1a1a2e",
            text_color="#8C00FF",
            corner_radius=15
        )
        self.category_entry.pack(fill="x", padx=15, pady=(0, 10))
        # Set default value to "Booking"
        self.category_entry.configure(state="normal")
        self.category_entry.insert(0, "Booking")
        self.category_entry.configure(state="readonly")
        
        # Service selection (all services available)
        ctk.CTkLabel(
            form_scroll,
            text="Service:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.service_combo = ctk.CTkComboBox(
            form_scroll,
            height=38,
            font=ctk.CTkFont(size=13),
            values=["Loading..."],
            state="readonly",
            command=self.on_service_change,
            corner_radius=15
        )
        self.service_combo.pack(fill="x", padx=15, pady=(0, 10))
        self.service_combo.set("Select Service")
        
        # Full amount
        ctk.CTkLabel(
            form_scroll,
            text="Full Amount (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.full_amount_entry = ctk.CTkEntry(
            form_scroll, 
            height=38, 
            font=ctk.CTkFont(size=13),
            state="readonly",
            fg_color="#1a1a2e",
            text_color="#8C00FF",
            corner_radius=15
        )
        self.full_amount_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Advance payment
        ctk.CTkLabel(
            form_scroll,
            text="Advance Payment (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.advance_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13), corner_radius=15, border_width=1)
        self.advance_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Balance display
        balance_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        balance_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            balance_frame,
            text="Balance Amount:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")
        
        self.balance_label = ctk.CTkLabel(
            balance_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8C00FF"
        )
        self.balance_label.pack(side="right")
        
        # Booking date
        ctk.CTkLabel(
            form_scroll,
            text="Booking Date:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        date_container = ctk.CTkFrame(form_scroll, fg_color="transparent")
        date_container.pack(fill="x", padx=15, pady=(0, 10))
        
        self.date_entry = DateEntry(
            date_container,
            width=25,
            background='#2d2d5a',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.pack(anchor="w")
        
        # Location
        ctk.CTkLabel(
            form_scroll,
            text="Location:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.location_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13), corner_radius=15, border_width=1)
        self.location_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Description
        ctk.CTkLabel(
            form_scroll,
            text="Description:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.description_text = ctk.CTkTextbox(form_scroll, height=70, font=ctk.CTkFont(size=13))
        self.description_text.pack(fill="x", padx=15, pady=(0, 10))
        
        # Status
        ctk.CTkLabel(
            form_scroll,
            text="Status:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.status_combo = ctk.CTkComboBox(
            form_scroll,
            height=38,
            font=ctk.CTkFont(size=13),
            values=["Pending", "Completed", "Cancelled"],
            corner_radius=15
        )
        self.status_combo.pack(fill="x", padx=15, pady=(0, 15))
        self.status_combo.set("Pending")
        
        # Buttons - Row 1
        btn_frame1 = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_frame1.pack(fill="x", padx=15, pady=(10, 5))
        
        self.add_btn = ctk.CTkButton(
            btn_frame1,
            text="➕ Add Booking",
            command=self.add_booking,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        )
        self.add_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.update_btn = ctk.CTkButton(
            btn_frame1,
            text="✏️ Update",
            command=self.update_booking,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            state="disabled"
        )
        self.update_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Buttons - Row 2
        btn_frame2 = ctk.CTkFrame(form_scroll, fg_color="transparent")
        btn_frame2.pack(fill="x", padx=15, pady=(5, 20))
        
        self.delete_btn = ctk.CTkButton(
            btn_frame2,
            text="🗑️ Delete",
            command=self.delete_booking,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#ff4757",
            hover_color="#ff3344",
            corner_radius=20,
            state="disabled"
        )
        self.delete_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            btn_frame2,
            text="🔄 Clear Form",
            command=self.clear_form,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        )
        clear_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Right panel - Table
        right_panel = ctk.CTkFrame(container, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Search and Filters - SIMPLIFIED LAYOUT (No Status Filters)
        search_frame = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=10)
        search_frame.pack(fill="x", padx=15, pady=15)
        
        # Search controls
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(search_container, text="🔍 Search:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(search_container, width=250, height=35, corner_radius=20, border_width=1)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_bookings())
        
        ctk.CTkButton(
            search_container,
            text="Refresh",
            command=self.load_bookings,
            width=100,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=5)
        
        # Info label showing filter status
        ctk.CTkLabel(
            search_container,
            text="📑 Showing: Active Bookings Only",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(side="right", padx=10)
        
        # Table header
        table_header = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=10, height=45)
        table_header.pack(fill="x", padx=15, pady=(0, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="📅 Booking Records",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#8C00FF"
        ).pack(side="left", padx=15, pady=10)
        
        self.record_count_label = ctk.CTkLabel(
            table_header,
            text="0 records",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.record_count_label.pack(side="right", padx=15, pady=10)
        
        # Table
        table_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a2e", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Updated column structure (NO Status column): Customer, Mobile, Service, Full Amount, Advance, Date
        columns = ("Customer", "Mobile", "Service", "FullAmount", "Advance", "Date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("Customer", text="👤 Customer Name")
        self.tree.heading("Mobile", text="📱 Mobile Number")
        self.tree.heading("Service", text="🛠️ Service")
        self.tree.heading("FullAmount", text="💰 Full Amount (LKR)")
        self.tree.heading("Advance", text="💵 Advance Amount (LKR)")
        self.tree.heading("Date", text="📅 Date")
        
        self.tree.column("Customer", width=140)
        self.tree.column("Mobile", width=120, anchor="center")
        self.tree.column("Service", width=160)
        self.tree.column("FullAmount", width=150, anchor="e")
        self.tree.column("Advance", width=150, anchor="e")
        self.tree.column("Date", width=120, anchor="center")
        
        # Configure row tags (with updated colors)
        self.tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        self.tree.tag_configure('pending', background='#3a2e1e', foreground='#ffa500')
        self.tree.tag_configure('completed', background='#1e3a2f', foreground='#8C00FF')
        self.tree.tag_configure('cancelled', background='#3a1e1e', foreground='#ff6b6b')
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        # Double-click to open settlement dialog for pending bookings
        self.tree.bind("<Double-Button-1>", self.on_booking_double_click)
    
    def load_categories(self):
        """Load ONLY services from the 'Booking' category"""
        booking_services = []
        categories = self.db_manager.get_all_categories()
        
        # Find the Booking category
        booking_category = None
        for cat in categories:
            # Check for category named 'Booking' (case-insensitive)
            if cat['category_name'].lower() == 'booking':
                booking_category = cat
                break
        
        if booking_category:
            services = self.db_manager.get_services_by_category(booking_category['id'])
            for service in services:
                # Create display name without 'Booking - ' prefix
                # Just use the service name directly
                display_name = service['service_name']
                
                booking_services.append({
                    'display_name': display_name,
                    'service_data': service,
                    'category_name': booking_category['category_name'],
                    'full_name': f"{booking_category['category_name']} - {service['service_name']}"  # Keep full name for database
                })
        
        # Update service combo with booking services only
        if booking_services:
            service_names = [s['display_name'] for s in booking_services]
            self.service_combo.configure(values=service_names)
            self.service_combo.set("Select Service")
            # Store service map for lookups
            self.services_map = {s['display_name']: s for s in booking_services}
        else:
            self.service_combo.configure(values=["No Booking Services Available"])
            self.service_combo.set("No Booking Services Available")
    
    def format_service_name(self, service_name):
        """Format service name: remove 'Booking - ' prefix and 'Photoshoot'/'Photography' suffix"""
        if not service_name:
            return service_name
        
        # Remove 'Booking - ' prefix
        if service_name.startswith('Booking - '):
            service_name = service_name[10:]  # len('Booking - ') = 10
        
        # Remove 'Photoshoot' or 'Photography' suffix (case-insensitive)
        service_name = service_name.strip()
        if service_name.lower().endswith(' photoshoot'):
            service_name = service_name[:-11].strip()  # len(' photoshoot') = 11
        elif service_name.lower().endswith(' photography'):
            service_name = service_name[:-12].strip()  # len(' photography') = 12
        
        return service_name
    
    def on_service_change(self, selected_service):
        """Auto-fill amount when service is selected"""
        if selected_service in ["Select Service", "Loading...", "No Booking Services Available"]:
            # Clear the amount
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, "end")
            self.full_amount_entry.configure(state="readonly")
            self.calculate_balance()
            return
        
        # Get service details and auto-fill price
        service_info = self.services_map.get(selected_service)
        if service_info and 'service_data' in service_info:
            service_data = service_info['service_data']
            if 'price' in service_data:
                price = service_data['price']
                self.full_amount_entry.configure(state="normal")
                self.full_amount_entry.delete(0, "end")
                self.full_amount_entry.insert(0, f"{float(price):.2f}")
                self.full_amount_entry.configure(state="readonly")
                self.calculate_balance()
    
    def calculate_balance(self):
        """Calculate remaining balance with real-time color coding"""
        full = self.full_amount_entry.get().strip()
        advance = self.advance_entry.get().strip()
        
        if full and self.validate_number(full, True) and advance and self.validate_number(advance, True):
            balance = float(full) - float(advance)
            self.balance_label.configure(text=f"LKR {balance:.2f}")
            # Color coding: red if balance remaining, purple if fully paid
            if balance > 0:
                self.balance_label.configure(text_color="#ff6b6b")  # Red
            else:
                self.balance_label.configure(text_color="#8C00FF")  # Purple
        else:
            self.balance_label.configure(text="LKR 0.00")
            self.balance_label.configure(text_color="#8C00FF")
    
    def add_booking(self):
        """Add new booking"""
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        service = self.service_combo.get()  # Now includes category
        full_amount = self.full_amount_entry.get().strip()
        advance = self.advance_entry.get().strip()
        date = self.date_entry.get_date().strftime('%Y-%m-%d')
        location = self.location_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter customer name")
            return
        
        if not mobile or not self.validate_mobile(mobile):
            MessageDialog.show_error("Error", "Please enter valid mobile number (10 digits)")
            return
        
        if service in ["Select Service", "Loading...", "No Booking Services Available"]:
            MessageDialog.show_error("Error", "Please select a service")
            return
        
        if not full_amount or not self.validate_number(full_amount, True):
            MessageDialog.show_error("Error", "Please enter valid full amount")
            return
        
        if not advance or not self.validate_number(advance, True):
            MessageDialog.show_error("Error", "Please enter valid advance payment")
            return
        
        # Get the full service name for database (includes 'Booking - ' prefix)
        service_info = self.services_map.get(service)
        if service_info and 'full_name' in service_info:
            photoshoot_category = service_info['full_name']  # Use full name with category
        else:
            # Fallback: add 'Booking - ' prefix if not found
            photoshoot_category = f"Booking - {service}"
        
        booking_id = self.db_manager.create_booking(
            name, mobile, photoshoot_category,
            float(full_amount), float(advance),
            date, location, description,
            self.auth_manager.get_user_id()
        )
        
        if booking_id:
            # Store booking data for invoice generation
            booking_data = {
                'id': booking_id,
                'customer_name': name,
                'mobile_number': mobile,
                'photoshoot_category': photoshoot_category,
                'full_amount': full_amount,
                'advance_payment': advance,
                'booking_date': date,
                'location': location,
                'description': description,
                'status': 'Pending'
            }
            
            # Show success message, refresh table, and show invoice popup
            MessageDialog.show_success("Success", "Booking added successfully!")
            self.clear_form()
            self.load_bookings()  # Refresh table immediately
            # Set focus back to search entry to prevent input lock
            self.after(100, lambda: self.search_entry.focus_set())
            self.show_booking_invoice_popup(booking_data)
        else:
            MessageDialog.show_error("Error", "Failed to add booking")
    
    def show_booking_invoice_popup(self, booking_data):
        """Show popup to generate invoice after successful booking"""
        # Create custom popup dialog
        popup = ctk.CTkToplevel(self)
        popup.title("Booking Successful")
        popup.geometry("600x580")
        popup.resizable(False, False)
        popup.configure(fg_color="#1a1a2e")
        
        # Make modal
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        
        # Center on screen
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 300
        y = (popup.winfo_screenheight() // 2) - 290
        popup.geometry(f"600x580+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkFrame(popup, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Success icon and message
        ctk.CTkLabel(
            main_frame,
            text="✅",
            font=ctk.CTkFont(size=50)
        ).pack(pady=(25, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Booking Created Successfully!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(0, 15))
        
        # Booking summary
        summary_frame = ctk.CTkFrame(main_frame, fg_color="#0d0d1a", corner_radius=10)
        summary_frame.pack(fill="x", padx=25, pady=10)
        
        # Parse category and service
        photoshoot_cat = booking_data['photoshoot_category']
        if ' - ' in photoshoot_cat:
            parts = photoshoot_cat.split(' - ', 1)
            category = parts[0]
            service = parts[1] if len(parts) > 1 else ''
        else:
            category = photoshoot_cat
            service = ''
        
        summary_text = f"""
👤 Customer: {booking_data['customer_name']}
📱 Mobile: {booking_data['mobile_number']}
📁 Category: {category}
🛠️ Service: {service}
📅 Date: {booking_data['booking_date']}
💰 Amount: LKR {float(booking_data['full_amount']):,.2f}
💵 Advance: LKR {float(booking_data['advance_payment']):,.2f}
        """
        
        ctk.CTkLabel(
            summary_frame,
            text=summary_text.strip(),
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        ).pack(padx=15, pady=15, anchor="w")
        
        # Question
        ctk.CTkLabel(
            main_frame,
            text="Would you like to generate a receipt?",
            font=ctk.CTkFont(size=14),
            text_color="#aaaaaa"
        ).pack(pady=(15, 20))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        # Store filepath for later use
        self.generated_invoice_path = None
        
        def generate_invoice():
            """Generate and show invoice"""
            try:
                # Get current user's name
                current_user = self.auth_manager.get_current_user()
                created_by_name = current_user.get('full_name', 'Staff') if current_user else 'Staff'
                user_id = self.auth_manager.get_user_id()
                
                # Generate the invoice PDF
                filepath = self.invoice_generator.generate_booking_invoice(booking_data, created_by_name)
                self.generated_invoice_path = filepath
                
                # Extract invoice number from filename (Booking_BK-YYYYMMDDHHMMSS.pdf)
                import os
                filename = os.path.basename(filepath)
                invoice_number = filename.replace('Booking_', '').replace('.pdf', '')
                
                # Save invoice to database
                full_amount = float(booking_data['full_amount'])
                advance_payment = float(booking_data['advance_payment'])
                balance = full_amount - advance_payment
                
                invoice_id = self.db_manager.create_invoice(
                    invoice_number=invoice_number,
                    customer_id=None,  # Guest booking
                    subtotal=full_amount,
                    discount=0,
                    total_amount=full_amount,
                    paid_amount=advance_payment,
                    balance_amount=balance,
                    created_by=user_id,
                    category_service_cost=0,
                    advance_payment=advance_payment,
                    guest_name=booking_data['customer_name'],
                    booking_id=booking_data.get('id')
                )
                
                # Add invoice item (the service)
                if invoice_id:
                    self.db_manager.add_invoice_item(
                        invoice_id=invoice_id,
                        item_type='BookingService',
                        item_id=booking_data.get('id', 0),
                        item_name=booking_data['photoshoot_category'],
                        quantity=1,
                        unit_price=full_amount,
                        total_price=full_amount,
                        buying_price=0
                    )
                
                # Show invoice preview popup
                popup.destroy()
                self.show_invoice_preview_popup(filepath, booking_data)
                
            except Exception as e:
                Toast.error(self, f"Error generating invoice: {str(e)}")
        
        def close_popup():
            """Close without generating invoice"""
            popup.destroy()
            Toast.success(self, "Booking saved successfully!")
        
        # Generate Invoice button
        ctk.CTkButton(
            btn_frame,
            text="📄 Generate Receipt",
            command=generate_invoice,
            width=180,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)
        
        # Cancel button
        ctk.CTkButton(
            btn_frame,
            text="✕ Close",
            command=close_popup,
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)
        
        # Handle window close
        popup.protocol("WM_DELETE_WINDOW", close_popup)
    
    def show_invoice_preview_popup(self, filepath, booking_data):
        """Show invoice preview with print option"""
        # Create preview popup
        preview = ctk.CTkToplevel(self)
        preview.title("Booking Receipt")
        preview.geometry("650x600")
        preview.resizable(False, False)
        preview.configure(fg_color="#1a1a2e")
        
        # Make modal
        preview.transient(self.winfo_toplevel())
        preview.grab_set()
        
        # Center on screen
        preview.update_idletasks()
        x = (preview.winfo_screenwidth() // 2) - 325
        y = (preview.winfo_screenheight() // 2) - 300
        preview.geometry(f"650x600+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkFrame(preview, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        ctk.CTkLabel(
            main_frame,
            text="📄",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            main_frame,
            text="Receipt Generated Successfully!",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(0, 15))
        
        # Info frame
        info_frame = ctk.CTkFrame(main_frame, fg_color="#0d0d1a", corner_radius=10)
        info_frame.pack(fill="x", padx=25, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"📋 Customer: {booking_data['customer_name']}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(padx=15, pady=(15, 5), anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"📅 Booking Date: {booking_data['booking_date']}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(padx=15, pady=5, anchor="w")
        
        full_amt = float(booking_data['full_amount'])
        advance = float(booking_data['advance_payment'])
        balance = full_amt - advance
        
        ctk.CTkLabel(
            info_frame,
            text=f"💰 Total Amount: LKR {full_amt:,.2f}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(padx=15, pady=5, anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"💵 Advance Paid: LKR {advance:,.2f}",
            font=ctk.CTkFont(size=13),
            anchor="w"
        ).pack(padx=15, pady=5, anchor="w")
        
        balance_color = "#ff6b6b" if balance > 0 else "#00ff88"
        ctk.CTkLabel(
            info_frame,
            text=f"⏳ Balance Due: LKR {balance:,.2f}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=balance_color,
            anchor="w"
        ).pack(padx=15, pady=(5, 15), anchor="w")
        
        # File info
        import os
        filename = os.path.basename(filepath)
        ctk.CTkLabel(
            main_frame,
            text=f"📁 File: {filename}",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(pady=10)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def open_invoice():
            """Open invoice in PDF viewer"""
            self.invoice_generator.open_invoice(filepath)
        
        def print_invoice():
            """Print the invoice"""
            try:
                self.invoice_generator.print_invoice(filepath)
                Toast.success(self, "Receipt sent to printer!")
            except Exception as e:
                Toast.error(self, f"Print error: {str(e)}")
        
        def close_preview():
            """Close preview"""
            preview.destroy()
            Toast.success(self, "Booking completed successfully!")
        
        # View PDF button
        ctk.CTkButton(
            btn_frame,
            text="👁️ View PDF",
            command=open_invoice,
            width=130,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Print button
        ctk.CTkButton(
            btn_frame,
            text="🖨️ Print",
            command=print_invoice,
            width=130,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Close button
        ctk.CTkButton(
            btn_frame,
            text="✓ Done",
            command=close_preview,
            width=100,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Handle window close
        preview.protocol("WM_DELETE_WINDOW", close_preview)
    
    def show_settlement_preview_popup(self, filepath, cash_entry):
        """Show settlement receipt preview with Download/Print options"""
        # Create preview popup
        preview = ctk.CTkToplevel(self)
        preview.title("Settlement Receipt")
        preview.geometry("650x600")
        preview.resizable(False, False)
        preview.configure(fg_color="#1a1a2e")
        
        # Make modal
        preview.transient(self.winfo_toplevel())
        preview.grab_set()
        
        # Center on screen
        preview.update_idletasks()
        x = (preview.winfo_screenwidth() // 2) - 325
        y = (preview.winfo_screenheight() // 2) - 300
        preview.geometry(f"650x600+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkFrame(preview, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        ctk.CTkLabel(
            main_frame,
            text="✅",
            font=ctk.CTkFont(size=40)
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            main_frame,
            text="Settlement Completed!",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            main_frame,
            text="Balance Fully Paid • Booking Completed",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        ).pack(pady=(0, 20))
        
        # Info frame
        info_frame = ctk.CTkFrame(main_frame, fg_color="#0d0d1a", corner_radius=10)
        info_frame.pack(fill="x", padx=25, pady=10)
        
        # File info
        import os
        filename = os.path.basename(filepath)
        ctk.CTkLabel(
            info_frame,
            text=f"📄 Settlement Receipt",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            info_frame,
            text=f"File: {filename}",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(pady=(0, 15))
        
        # Separator
        sep = ctk.CTkFrame(main_frame, height=2, fg_color="#333333")
        sep.pack(fill="x", padx=40, pady=20)
        
        # Instructions
        ctk.CTkLabel(
            main_frame,
            text="What would you like to do next?",
            font=ctk.CTkFont(size=13),
            text_color="#cccccc"
        ).pack(pady=(10, 20))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def download_receipt():
            """Open receipt for download/save"""
            self.invoice_generator.open_bill(filepath)
            Toast.success(self, "Receipt opened!")
        
        def print_receipt():
            """Send receipt to printer"""
            try:
                self.invoice_generator.print_invoice(filepath)
                Toast.success(self, "Receipt sent to printer!")
            except Exception as e:
                Toast.error(self, f"Print error: {str(e)}")
        
        def close_and_reset():
            """Close preview and reset input"""
            cash_entry.delete(0, 'end')  # Reset cash input
            preview.destroy()
            Toast.success(self, "Settlement process completed!")
        
        # Download button
        ctk.CTkButton(
            btn_frame,
            text="💾 Download",
            command=download_receipt,
            width=140,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Print button
        ctk.CTkButton(
            btn_frame,
            text="🖨️ Print Now",
            command=print_receipt,
            width=140,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Close button
        ctk.CTkButton(
            btn_frame,
            text="✓ Done",
            command=close_and_reset,
            width=120,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00dd77",
            corner_radius=20
        ).pack(side="left", padx=8)
        
        # Handle window close
        preview.protocol("WM_DELETE_WINDOW", close_and_reset)
    
    def update_booking(self):
        """Update selected booking"""
        if not self.selected_booking_id:
            MessageDialog.show_error("Error", "Please select a booking to update")
            return
        
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        service = self.service_combo.get()  # Already contains category
        full_amount = self.full_amount_entry.get().strip()
        advance = self.advance_entry.get().strip()
        date = self.date_entry.get_date().strftime('%Y-%m-%d')
        location = self.location_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        status = self.status_combo.get()
        
        if not name or not mobile:
            MessageDialog.show_error("Error", "Please fill required fields")
            return
        
        if not self.validate_mobile(mobile):
            MessageDialog.show_error("Error", "Mobile must be 10 digits")
            return
        
        if service in ["Select Service", "Loading...", "No Booking Services Available"]:
            MessageDialog.show_error("Error", "Please select a service")
            return
        
        if not full_amount or not advance:
            MessageDialog.show_error("Error", "Please enter amounts")
            return
        
        if not self.validate_number(full_amount, True) or not self.validate_number(advance, True):
            MessageDialog.show_error("Error", "Please enter valid amounts")
            return
        
        # Get the full service name for database (includes 'Booking - ' prefix)
        service_info = self.services_map.get(service)
        if service_info and 'full_name' in service_info:
            photoshoot_category = service_info['full_name']  # Use full name with category
        else:
            # Fallback: add 'Booking - ' prefix if not found
            photoshoot_category = f"Booking - {service}"
        
        success = self.db_manager.update_booking(
            self.selected_booking_id, name, mobile, photoshoot_category,
            float(full_amount), float(advance),
            date, location, description, status
        )
        
        if success:
            MessageDialog.show_success("Success", "Booking updated successfully")
            self.clear_form()
            self.load_bookings()
            # Set focus back to search entry to prevent input lock
            self.after(100, lambda: self.search_entry.focus_set())
        else:
            MessageDialog.show_error("Error", "Failed to update booking")
    
    def delete_booking(self):
        """Delete selected booking"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can delete bookings")
            return
        
        if not self.selected_booking_id:
            MessageDialog.show_error("Error", "Please select a booking to delete")
            return
        
        if not MessageDialog.show_confirm("Confirm", "Are you sure you want to delete this booking?"):
            return
        
        success = self.db_manager.delete_booking(self.selected_booking_id)
        
        if success:
            MessageDialog.show_success("Success", "Booking deleted successfully")
            self.clear_form()
            self.load_bookings()
            # Set focus back to search entry to prevent input lock
            self.after(100, lambda: self.search_entry.focus_set())
        else:
            MessageDialog.show_error("Error", "Failed to delete booking")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, 'end')
        self.mobile_entry.delete(0, 'end')
        # Category is locked to "Booking" - no need to reset
        self.service_combo.set("Select Service")
        # Clear read-only full_amount_entry
        self.full_amount_entry.configure(state="normal")
        self.full_amount_entry.delete(0, 'end')
        self.full_amount_entry.configure(state="readonly")
        self.advance_entry.delete(0, 'end')
        self.location_entry.delete(0, 'end')
        self.description_text.delete("1.0", "end")
        self.status_combo.set("Pending")
        self.balance_label.configure(text="LKR 0.00")
        self.balance_label.configure(text_color="#8C00FF")
        self.selected_booking_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
        # Reload services in case new ones were added
        self.load_categories()
    
    def load_bookings(self):
        """Load bookings based on current filter (default: Pending only)"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all bookings and filter by current status
        all_bookings = self.db_manager.get_all_bookings()
        
        # Filter bookings based on current_filter
        if self.current_filter != "All":
            bookings = [b for b in all_bookings if b['status'] == self.current_filter]
        else:
            bookings = all_bookings
        
        for i, booking in enumerate(bookings):
            status = booking['status']
            if status == 'Completed':
                tag = 'completed'
            elif status == 'Cancelled':
                tag = 'cancelled'
            elif status == 'Pending':
                tag = 'pending'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Format service name: strip prefixes/suffixes
            service_display = self.format_service_name(booking['photoshoot_category'])
            
            # New column structure (NO Status): Customer, Mobile, Service, Full Amount, Advance, Date
            self.tree.insert("", "end", values=(
                booking['customer_name'],
                booking['mobile_number'],
                service_display,
                f"{booking['full_amount']:.2f}",
                f"{booking['advance_payment']:.2f}",
                booking['booking_date']
            ), tags=(tag,), iid=str(booking['id']))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bookings)} records")
    
    def search_bookings(self):
        """Search bookings (respects current filter)"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_bookings()
            return
        
        all_bookings = self.db_manager.search_bookings(search_term)
        
        # Apply current filter to search results
        if self.current_filter != "All":
            bookings = [b for b in all_bookings if b['status'] == self.current_filter]
        else:
            bookings = all_bookings
        
        for i, booking in enumerate(bookings):
            status = booking['status']
            if status == 'Completed':
                tag = 'completed'
            elif status == 'Cancelled':
                tag = 'cancelled'
            elif status == 'Pending':
                tag = 'pending'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Format service name: strip prefixes/suffixes
            service_display = self.format_service_name(booking['photoshoot_category'])
            
            # New column structure (NO Status): Customer, Mobile, Service, Full Amount, Advance, Date
            self.tree.insert("", "end", values=(
                booking['customer_name'],
                booking['mobile_number'],
                service_display,
                f"{booking['full_amount']:.2f}",
                f"{booking['advance_payment']:.2f}",
                booking['booking_date']
            ), tags=(tag,), iid=str(booking['id']))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bookings)} records")
    
    def filter_by_status(self, status):
        """Filter bookings by status"""
        self.current_filter = status
        self.filter_status.set(status)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all bookings
        all_bookings = self.db_manager.get_all_bookings()
        
        # Filter by status
        if status != "All":
            bookings = [b for b in all_bookings if b['status'] == status]
        else:
            bookings = all_bookings
        
        for i, booking in enumerate(bookings):
            booking_status = booking['status']
            if booking_status == 'Completed':
                tag = 'completed'
            elif booking_status == 'Cancelled':
                tag = 'cancelled'
            elif booking_status == 'Pending':
                tag = 'pending'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Format service name: strip prefixes/suffixes
            service_display = self.format_service_name(booking['photoshoot_category'])
            
            # New column structure (NO Status): Customer, Mobile, Service, Full Amount, Advance, Date
            self.tree.insert("", "end", values=(
                booking['customer_name'],
                booking['mobile_number'],
                service_display,
                f"{booking['full_amount']:.2f}",
                f"{booking['advance_payment']:.2f}",
                booking['booking_date']
            ), tags=(tag,), iid=str(booking['id']))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bookings)} records")
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get booking ID from iid (item ID) instead of values since we removed ID column
        self.selected_booking_id = int(selection[0])
        
        # Load full booking details
        booking = self.db_manager.get_booking_by_id(self.selected_booking_id)
        
        if booking:
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, booking['customer_name'])
            
            self.mobile_entry.delete(0, 'end')
            self.mobile_entry.insert(0, booking['mobile_number'])
            
            # Service field shows full photoshoot_category (already contains category)
            photoshoot_cat = booking['photoshoot_category']
            
            # Set service directly if it exists in the services map
            if photoshoot_cat in self.services_map:
                self.service_combo.set(photoshoot_cat)
            else:
                # Service might not be in map, still display it
                self.service_combo.set(photoshoot_cat)
            
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, 'end')
            self.full_amount_entry.insert(0, str(booking['full_amount']))
            self.full_amount_entry.configure(state="readonly")
            
            self.advance_entry.delete(0, 'end')
            self.advance_entry.insert(0, str(booking['advance_payment']))
            
            self.date_entry.set_date(datetime.strptime(booking['booking_date'], '%Y-%m-%d'))
            
            self.location_entry.delete(0, 'end')
            self.location_entry.insert(0, booking['location'] or '')
            
            self.description_text.delete("1.0", "end")
            self.description_text.insert("1.0", booking['description'] or '')
            
            self.status_combo.set(booking['status'])
            
            self.calculate_balance()
            
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="normal")
            if self.is_admin():
                self.delete_btn.configure(state="normal")
    
    def on_booking_double_click(self, event):
        """Handle double-click on booking - open settlement dialog for pending bookings"""
        selection = self.tree.selection()
        if not selection:
            return
        
        booking_id = int(selection[0])
        booking = self.db_manager.get_booking_by_id(booking_id)
        
        if not booking:
            return
        
        # Only open settlement for pending bookings with balance due
        if booking['status'].lower() == 'pending':
            balance_due = float(booking['full_amount']) - float(booking['advance_payment'])
            if balance_due > 0:
                self.show_settlement_dialog(booking)
            else:
                MessageDialog.show_info("No Balance", "This booking has no remaining balance to settle.")
        elif booking['status'].lower() == 'completed':
            MessageDialog.show_info("Already Completed", "This booking has already been completed.")
        elif booking['status'].lower() == 'cancelled':
            MessageDialog.show_info("Cancelled", "This booking has been cancelled.")
    
    def show_settlement_dialog(self, booking):
        """Show settlement dialog for pending booking with balance"""
        # Create modal dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Balance Settlement")
        dialog.geometry("700x800")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#1a1a2e")
        
        # Make modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (800 // 2)
        dialog.geometry(f"700x800+{x}+{y}")
        
        def close_dialog():
            dialog.grab_release()
            dialog.destroy()
            # Restore focus to prevent input lock
            self.after(100, lambda: self.search_entry.focus_set())
        
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        ctk.CTkLabel(
            scroll_frame,
            text="💵 Balance Settlement",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(0, 20))
        
        # Original booking info section
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Original Booking Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(15, 10))
        
        # Booking info grid
        info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        info_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        full_amount = float(booking['full_amount'])
        advance_paid = float(booking['advance_payment'])
        balance_due = full_amount - advance_paid
        
        # Format service name
        service_display = self.format_service_name(booking['photoshoot_category'])
        
        info_data = [
            ("Customer Name:", booking['customer_name']),
            ("Mobile Number:", booking['mobile_number']),
            ("Service:", service_display),
            ("Booking Date:", booking['booking_date']),
            ("Location:", booking['location'] or 'N/A'),
        ]
        
        for idx, (label, value) in enumerate(info_data):
            ctk.CTkLabel(
                info_grid,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            ).grid(row=idx, column=0, sticky="w", pady=5, padx=(0, 10))
            
            ctk.CTkLabel(
                info_grid,
                text=str(value),
                font=ctk.CTkFont(size=12),
                anchor="w"
            ).grid(row=idx, column=1, sticky="w", pady=5)
        
        # Financial summary section
        financial_frame = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=10)
        financial_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        ctk.CTkLabel(
            financial_frame,
            text="Financial Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(15, 10))
        
        # Financial grid
        financial_grid = ctk.CTkFrame(financial_frame, fg_color="transparent")
        financial_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        financial_items = [
            ("Full Amount:", f"Rs. {full_amount:,.2f}", "#ffffff"),
            ("Advance Paid:", f"Rs. {advance_paid:,.2f}", "#00ff88"),
            ("Balance Due:", f"Rs. {balance_due:,.2f}", "#ff4757"),
        ]
        
        for idx, (label, value, color) in enumerate(financial_items):
            ctk.CTkLabel(
                financial_grid,
                text=label,
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            ).grid(row=idx, column=0, sticky="w", pady=8, padx=(0, 20))
            
            ctk.CTkLabel(
                financial_grid,
                text=value,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color,
                anchor="e"
            ).grid(row=idx, column=1, sticky="e", pady=8)
        
        financial_grid.columnconfigure(1, weight=1)
        
        # Payment input section
        payment_frame = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=10)
        payment_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        ctk.CTkLabel(
            payment_frame,
            text="Final Payment",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(15, 10))
        
        payment_grid = ctk.CTkFrame(payment_frame, fg_color="transparent")
        payment_grid.pack(fill="x", padx=20, pady=(0, 15))
        
        # Cash received input
        ctk.CTkLabel(
            payment_grid,
            text="Cash Received:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=10, padx=(0, 10))
        
        cash_entry = ctk.CTkEntry(
            payment_grid,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14),
            corner_radius=10,
            border_width=2,
            border_color="#8C00FF"
        )
        cash_entry.grid(row=0, column=1, sticky="ew", pady=10)
        cash_entry.insert(0, f"{balance_due:.2f}")
        cash_entry.focus()
        
        # Change display
        change_label = ctk.CTkLabel(
            payment_grid,
            text="Change: Rs. 0.00",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff88"
        )
        change_label.grid(row=1, column=0, columnspan=2, pady=10)
        
        payment_grid.columnconfigure(1, weight=1)
        
        def calculate_change(*args):
            try:
                cash_received = float(cash_entry.get() or 0)
                change = cash_received - balance_due
                if change >= 0:
                    change_label.configure(text=f"Change: Rs. {change:,.2f}", text_color="#00ff88")
                else:
                    change_label.configure(text=f"Insufficient: Rs. {abs(change):,.2f}", text_color="#ff4757")
            except:
                change_label.configure(text="Change: Rs. 0.00", text_color="#00ff88")
        
        cash_entry.bind("<KeyRelease>", calculate_change)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def process_settlement():
            try:
                cash_received = float(cash_entry.get() or 0)
            except:
                MessageDialog.show_error("Error", "Please enter a valid cash amount")
                return
            
            if cash_received < balance_due:
                MessageDialog.show_error("Error", f"Cash received (Rs. {cash_received:,.2f}) is less than balance due (Rs. {balance_due:,.2f})")
                return
            
            # Update booking status to Completed
            success = self.db_manager.update_booking(
                booking['id'],
                booking['customer_name'],
                booking['mobile_number'],
                booking['photoshoot_category'],
                full_amount,
                full_amount,  # Set advance to full amount (fully paid)
                booking['booking_date'],
                booking['location'],
                booking['description'],
                'Completed'
            )
            
            if not success:
                MessageDialog.show_error("Error", "Failed to update booking status")
                return
            
            # Generate settlement invoice
            settlement_data = {
                'booking_id': booking['id'],
                'customer_name': booking['customer_name'],
                'mobile_number': booking['mobile_number'],
                'photoshoot_category': booking['photoshoot_category'],
                'original_booking_date': booking['booking_date'],
                'settlement_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'full_amount': full_amount,
                'original_advance': advance_paid,
                'final_payment': balance_due,
                'cash_received': cash_received,
                'change_given': cash_received - balance_due,
                'location': booking['location'],
                'description': booking['description'],
                'created_by_name': self.auth_manager.get_username()
            }
            
            pdf_path = self.invoice_generator.generate_booking_settlement_invoice(settlement_data)
            
            # Show settlement preview popup
            self.show_settlement_preview_popup(pdf_path, cash_entry)
            
            close_dialog()
            self.load_bookings()  # Refresh to show updated status
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=close_dialog,
            width=150,
            height=45,
            fg_color="#555555",
            hover_color="#444444",
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="✔ Process Settlement",
            command=process_settlement,
            width=220,
            height=45,
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00dd77",
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
