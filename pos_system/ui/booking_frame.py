import customtkinter as ctk
from tkinter import ttk
from tkcalendar import DateEntry
from ui.components import BaseFrame, MessageDialog
from datetime import datetime


class BookingManagementFrame(BaseFrame):
    """Booking and photoshoot management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_booking_id = None
        self.categories_map = {}  # name -> id mapping
        self.services_map = {}  # name -> service data
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
            state="readonly"
        )
        self.service_combo.pack(fill="x", padx=15, pady=(0, 10))
        self.service_combo.set("Select Category First")
        
        # Full amount
        ctk.CTkLabel(
            form_scroll,
            text="Full Amount (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.full_amount_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
        self.full_amount_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.full_amount_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Advance payment
        ctk.CTkLabel(
            form_scroll,
            text="Advance Payment (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        self.advance_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
        self.advance_entry.pack(fill="x", padx=15, pady=(0, 10))
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        self.advance_entry = ctk.CTkEntry(form_scroll, height=38, font=ctk.CTkFont(size=13))
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
        
        ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=5)
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
        
        # Table
        table_frame = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        columns = ("ID", "Customer", "Mobile", "Category", "Service", "Amount", "Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Mobile", text="Mobile")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Service", text="Service")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Customer", width=100)
        self.tree.column("Mobile", width=90)
        self.tree.column("Category", width=100)
        self.tree.column("Service", width=100)
        self.tree.column("Amount", width=80, anchor="e")
        self.tree.column("Date", width=80)
        self.tree.column("Status", width=70, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
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
            return
        
        category_id = self.categories_map.get(selected_category)
        if category_id:
            services = self.db_manager.get_services_by_category(category_id)
            self.services_map = {s['service_name']: s for s in services}
            service_names = ["Select Service"] + list(self.services_map.keys())
            self.service_combo.configure(values=service_names)
            self.service_combo.set("Select Service")
        else:
            self.service_combo.configure(values=["No Services"])
            self.service_combo.set("No Services")
            self.services_map = {}
    
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
            MessageDialog.show_success("Success", "Booking added successfully")
            self.clear_form()
            self.load_bookings()
        else:
            MessageDialog.show_error("Error", "Failed to add booking")
    
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
        self.full_amount_entry.delete(0, 'end')
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
        
        for booking in bookings:
            tags = ()
            if booking['status'] == 'Completed':
                tags = ('completed',)
            elif booking['status'] == 'Cancelled':
                tags = ('cancelled',)
            
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
            ), tags=tags)
        
        self.tree.tag_configure('completed', background='#006400')
        self.tree.tag_configure('cancelled', background='#8B0000')
    
    def search_bookings(self):
        """Search bookings"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_bookings()
            return
        
        bookings = self.db_manager.search_bookings(search_term)
        
        for booking in bookings:
            tags = ()
            if booking['status'] == 'Completed':
                tags = ('completed',)
            elif booking['status'] == 'Cancelled':
                tags = ('cancelled',)
            
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
            ), tags=tags)
    
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
            
            self.full_amount_entry.delete(0, 'end')
            self.full_amount_entry.insert(0, str(booking['full_amount']))
            
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
