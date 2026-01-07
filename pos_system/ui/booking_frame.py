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
        left_panel = ctk.CTkFrame(container, fg_color="#1e1e3f", corner_radius=15, width=450)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Scrollable form container
        form_scroll = ctk.CTkScrollableFrame(left_panel, fg_color="#252545", corner_radius=10)
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
        
        self.name_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
        self.name_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Mobile number
        ctk.CTkLabel(
            form_scroll,
            text="Mobile Number:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.mobile_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
        self.mobile_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Category selection
        ctk.CTkLabel(
            form_scroll,
            text="Category:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.category_combo = ctk.CTkComboBox(
            form_scroll,
            height=38,
            font=ctk.CTkFont(size=13),
            values=["Select Category"],
            command=self.on_category_change,
            state="readonly"
        )
        self.category_combo.pack(fill="x", padx=15, pady=(0, 10))
        self.category_combo.set("Select Category")
        
        # Service selection (filtered by category)
        ctk.CTkLabel(
            form_scroll,
            text="Service:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.service_combo = ctk.CTkComboBox(
            form_scroll,
            height=38,
            font=ctk.CTkFont(size=13),
            values=["Select Category First"],
            state="readonly",
            command=self.on_service_change
        )
        self.service_combo.pack(fill="x", padx=15, pady=(0, 10))
        self.service_combo.set("Select Category First")
        
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
            fg_color="#2d2d5a",
            text_color="#00ff88"
        )
        self.full_amount_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Advance payment
        ctk.CTkLabel(
            form_scroll,
            text="Advance Payment (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.advance_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
        self.advance_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
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
            text_color="#ffd93d"
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
        
        self.location_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
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
            values=["Pending", "Completed", "Cancelled"]
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
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        )
        self.add_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.update_btn = ctk.CTkButton(
            btn_frame1,
            text="✏️ Update",
            command=self.update_booking,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
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
            state="disabled"
        )
        self.delete_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        clear_btn = ctk.CTkButton(
            btn_frame2,
            text="🔄 Clear Form",
            command=self.clear_form,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        )
        clear_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Right panel - Table
        right_panel = ctk.CTkFrame(container, fg_color="#1e1e3f", corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Search
        search_frame = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=10)
        search_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
        self.search_entry = ctk.CTkEntry(search_frame, width=200, height=35)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_bookings())
        
        ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.load_bookings,
            width=100,
            height=35
        ).pack(side="left", padx=5)
        
        # Table header
        table_header = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=10, height=45)
        table_header.pack(fill="x", padx=15, pady=(0, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="📅 Booking Records",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff"
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
        
        columns = ("ID", "Customer", "Mobile", "Category", "Service", "Amount", "Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ID", text="🔢 ID")
        self.tree.heading("Customer", text="👤 Customer")
        self.tree.heading("Mobile", text="📱 Mobile")
        self.tree.heading("Category", text="📁 Category")
        self.tree.heading("Service", text="🛠️ Service")
        self.tree.heading("Amount", text="💰 Amount")
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Status", text="📊 Status")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Customer", width=100)
        self.tree.column("Mobile", width=90, anchor="center")
        self.tree.column("Category", width=100)
        self.tree.column("Service", width=100)
        self.tree.column("Amount", width=80, anchor="e")
        self.tree.column("Date", width=90, anchor="center")
        self.tree.column("Status", width=80, anchor="center")
        
        # Configure row tags
        self.tree.tag_configure('oddrow', background='#1e1e3f', foreground='#e0e0e0')
        self.tree.tag_configure('evenrow', background='#252545', foreground='#e0e0e0')
        self.tree.tag_configure('pending', background='#3a2e1e', foreground='#ffd93d')
        self.tree.tag_configure('completed', background='#1e3a2f', foreground='#00ff88')
        self.tree.tag_configure('cancelled', background='#3a1e1e', foreground='#ff6b6b')
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_categories(self):
        """Load categories for dropdown"""
        categories = self.db_manager.get_all_categories()
        self.categories_map = {cat['category_name']: cat['id'] for cat in categories}
        category_names = ["Select Category"] + list(self.categories_map.keys())
        self.category_combo.configure(values=category_names)
    
    def on_category_change(self, selected_category):
        """Load services when category changes"""
        if selected_category == "Select Category":
            self.service_combo.configure(values=["Select Category First"])
            self.service_combo.set("Select Category First")
            self.services_map = {}
            # Clear the amount
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, "end")
            self.full_amount_entry.configure(state="readonly")
            self.calculate_balance()
            return
        
        category_id = self.categories_map.get(selected_category)
        if category_id:
            services = self.db_manager.get_services_by_category(category_id)
            self.services_map = {s['service_name']: s for s in services}
            service_names = ["Select Service"] + list(self.services_map.keys())
            self.service_combo.configure(values=service_names)
            self.service_combo.set("Select Service")
            # Clear the amount when category changes
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, "end")
            self.full_amount_entry.configure(state="readonly")
            self.calculate_balance()
        else:
            self.service_combo.configure(values=["No Services"])
            self.service_combo.set("No Services")
            self.services_map = {}
    
    def on_service_change(self, selected_service):
        """Auto-fill amount when service is selected"""
        if selected_service in ["Select Service", "Select Category First", "No Services"]:
            # Clear the amount
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, "end")
            self.full_amount_entry.configure(state="readonly")
            self.calculate_balance()
            return
        
        # Get service details and auto-fill price
        service_data = self.services_map.get(selected_service)
        if service_data and 'price' in service_data:
            price = service_data['price']
            self.full_amount_entry.configure(state="normal")
            self.full_amount_entry.delete(0, "end")
            self.full_amount_entry.insert(0, f"{float(price):.2f}")
            self.full_amount_entry.configure(state="readonly")
            self.calculate_balance()
    
    def calculate_balance(self):
        """Calculate and display balance"""
        full = self.full_amount_entry.get().strip()
        advance = self.advance_entry.get().strip()
        
        if full and self.validate_number(full, True) and advance and self.validate_number(advance, True):
            balance = float(full) - float(advance)
            self.balance_label.configure(text=f"LKR {balance:.2f}")
        else:
            self.balance_label.configure(text="LKR 0.00")
    
    def add_booking(self):
        """Add new booking"""
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        category = self.category_combo.get()
        service = self.service_combo.get()
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
        
        if category == "Select Category":
            MessageDialog.show_error("Error", "Please select a category")
            return
        
        if service in ["Select Service", "Select Category First", "No Services"]:
            MessageDialog.show_error("Error", "Please select a service")
            return
        
        if not full_amount or not self.validate_number(full_amount, True):
            MessageDialog.show_error("Error", "Please enter valid full amount")
            return
        
        if not advance or not self.validate_number(advance, True):
            MessageDialog.show_error("Error", "Please enter valid advance payment")
            return
        
        # Combine category and service for photoshoot_category field
        photoshoot_category = f"{category} - {service}"
        
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
            
            # Show success message and invoice popup
            self.clear_form()
            self.load_bookings()
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
        main_frame = ctk.CTkFrame(popup, fg_color="#1e1e3f", corner_radius=15)
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
        summary_frame = ctk.CTkFrame(main_frame, fg_color="#252545", corner_radius=10)
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
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        ).pack(side="left", padx=10)
        
        # Cancel button
        ctk.CTkButton(
            btn_frame,
            text="✕ Close",
            command=close_popup,
            width=120,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
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
        main_frame = ctk.CTkFrame(preview, fg_color="#1e1e3f", corner_radius=15)
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
        info_frame = ctk.CTkFrame(main_frame, fg_color="#252545", corner_radius=10)
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
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        ).pack(side="left", padx=8)
        
        # Print button
        ctk.CTkButton(
            btn_frame,
            text="🖨️ Print",
            command=print_invoice,
            width=130,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00cc6a"
        ).pack(side="left", padx=8)
        
        # Close button
        ctk.CTkButton(
            btn_frame,
            text="✓ Done",
            command=close_preview,
            width=100,
            height=45,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        ).pack(side="left", padx=8)
        
        # Handle window close
        preview.protocol("WM_DELETE_WINDOW", close_preview)
    
    def update_booking(self):
        """Update selected booking"""
        if not self.selected_booking_id:
            MessageDialog.show_error("Error", "Please select a booking to update")
            return
        
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        category = self.category_combo.get()
        service = self.service_combo.get()
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
        
        if category == "Select Category":
            MessageDialog.show_error("Error", "Please select a category")
            return
        
        if service in ["Select Service", "Select Category First", "No Services"]:
            MessageDialog.show_error("Error", "Please select a service")
            return
        
        if not full_amount or not advance:
            MessageDialog.show_error("Error", "Please enter amounts")
            return
        
        # Combine category and service for photoshoot_category field
        photoshoot_category = f"{category} - {service}"
        
        success = self.db_manager.update_booking(
            self.selected_booking_id, name, mobile, photoshoot_category,
            float(full_amount), float(advance),
            date, location, description, status
        )
        
        if success:
            MessageDialog.show_success("Success", "Booking updated successfully")
            self.clear_form()
            self.load_bookings()
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
        else:
            MessageDialog.show_error("Error", "Failed to delete booking")
    
    def clear_form(self):
        """Clear form fields"""
        self.name_entry.delete(0, 'end')
        self.mobile_entry.delete(0, 'end')
        self.category_combo.set("Select Category")
        self.service_combo.configure(values=["Select Category First"])
        self.service_combo.set("Select Category First")
        self.services_map = {}
        # Clear read-only full_amount_entry
        self.full_amount_entry.configure(state="normal")
        self.full_amount_entry.delete(0, 'end')
        self.full_amount_entry.configure(state="readonly")
        self.advance_entry.delete(0, 'end')
        self.location_entry.delete(0, 'end')
        self.description_text.delete("1.0", "end")
        self.status_combo.set("Pending")
        self.balance_label.configure(text="LKR 0.00")
        self.selected_booking_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
        # Reload categories in case new ones were added
        self.load_categories()
    
    def load_bookings(self):
        """Load all bookings"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        bookings = self.db_manager.get_all_bookings()
        
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
            
            # Split photoshoot_category into category and service
            photoshoot_cat = booking['photoshoot_category']
            if ' - ' in photoshoot_cat:
                parts = photoshoot_cat.split(' - ', 1)
                category = parts[0]
                service = parts[1] if len(parts) > 1 else ''
            else:
                category = photoshoot_cat
                service = ''
            
            self.tree.insert("", "end", values=(
                booking['id'],
                booking['customer_name'],
                booking['mobile_number'],
                category,
                service,
                f"{booking['full_amount']:.2f}",
                booking['booking_date'],
                booking['status']
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bookings)} records")
    
    def search_bookings(self):
        """Search bookings"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_bookings()
            return
        
        bookings = self.db_manager.search_bookings(search_term)
        
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
            
            # Split photoshoot_category into category and service
            photoshoot_cat = booking['photoshoot_category']
            if ' - ' in photoshoot_cat:
                parts = photoshoot_cat.split(' - ', 1)
                category = parts[0]
                service = parts[1] if len(parts) > 1 else ''
            else:
                category = photoshoot_cat
                service = ''
            
            self.tree.insert("", "end", values=(
                booking['id'],
                booking['customer_name'],
                booking['mobile_number'],
                category,
                service,
                f"{booking['full_amount']:.2f}",
                booking['booking_date'],
                booking['status']
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bookings)} records")
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_booking_id = values[0]
        
        # Load full booking details
        booking = self.db_manager.get_booking_by_id(self.selected_booking_id)
        
        if booking:
            self.name_entry.delete(0, 'end')
            self.name_entry.insert(0, booking['customer_name'])
            
            self.mobile_entry.delete(0, 'end')
            self.mobile_entry.insert(0, booking['mobile_number'])
            
            # Split photoshoot_category into category and service
            photoshoot_cat = booking['photoshoot_category']
            if ' - ' in photoshoot_cat:
                parts = photoshoot_cat.split(' - ', 1)
                category_name = parts[0]
                service_name = parts[1] if len(parts) > 1 else ''
            else:
                category_name = photoshoot_cat
                service_name = ''
            
            # Set category and trigger service load
            if category_name in self.categories_map:
                self.category_combo.set(category_name)
                self.on_category_change(category_name)
                # Set service if available
                if service_name and service_name in self.services_map:
                    self.service_combo.set(service_name)
                else:
                    self.service_combo.set("Select Service")
            else:
                self.category_combo.set("Select Category")
                self.service_combo.configure(values=["Select Category First"])
                self.service_combo.set("Select Category First")
            
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
