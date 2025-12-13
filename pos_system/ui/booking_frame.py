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
        self.create_widgets()
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
        
        # Left panel - Form
        left_panel = ctk.CTkFrame(container, fg_color="#1e1e3f", corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        form_frame = ctk.CTkFrame(left_panel, fg_color="#252545", corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Customer name
        ctk.CTkLabel(
            form_frame,
            text="Customer Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(form_frame, width=250, height=35)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Mobile number
        ctk.CTkLabel(
            form_frame,
            text="Mobile Number:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.mobile_entry = ctk.CTkEntry(form_frame, width=250, height=35)
        self.mobile_entry.grid(row=1, column=1, padx=10, pady=10)
        
        # Photoshoot category
        ctk.CTkLabel(
            form_frame,
            text="Photoshoot Category:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.category_combo = ctk.CTkComboBox(
            form_frame,
            width=250,
            height=35,
            values=[
                "Wedding Photography",
                "Pre-Wedding",
                "Birthday Party",
                "Corporate Event",
                "Product Photography",
                "Portrait Session",
                "Family Photography",
                "Other"
            ]
        )
        self.category_combo.grid(row=2, column=1, padx=10, pady=10)
        self.category_combo.set("Wedding Photography")
        
        # Full amount
        ctk.CTkLabel(
            form_frame,
            text="Full Amount (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.full_amount_entry = ctk.CTkEntry(form_frame, width=250, height=35)
        self.full_amount_entry.grid(row=3, column=1, padx=10, pady=10)
        self.full_amount_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Advance payment
        ctk.CTkLabel(
            form_frame,
            text="Advance Payment (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        
        self.advance_entry = ctk.CTkEntry(form_frame, width=250, height=35)
        self.advance_entry.grid(row=4, column=1, padx=10, pady=10)
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Balance display
        ctk.CTkLabel(
            form_frame,
            text="Balance Amount:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        
        self.balance_label = ctk.CTkLabel(
            form_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="yellow"
        )
        self.balance_label.grid(row=5, column=1, padx=10, pady=10, sticky="w")
        
        # Booking date
        ctk.CTkLabel(
            form_frame,
            text="Booking Date:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=6, column=0, padx=10, pady=10, sticky="w")
        
        self.date_entry = DateEntry(
            form_frame,
            width=30,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.grid(row=6, column=1, padx=10, pady=10, sticky="w")
        
        # Location
        ctk.CTkLabel(
            form_frame,
            text="Location:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=7, column=0, padx=10, pady=10, sticky="w")
        
        self.location_entry = ctk.CTkEntry(form_frame, width=250, height=35)
        self.location_entry.grid(row=7, column=1, padx=10, pady=10)
        
        # Description
        ctk.CTkLabel(
            form_frame,
            text="Description:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=8, column=0, padx=10, pady=10, sticky="nw")
        
        self.description_text = ctk.CTkTextbox(form_frame, width=250, height=80)
        self.description_text.grid(row=8, column=1, padx=10, pady=10)
        
        # Status
        ctk.CTkLabel(
            form_frame,
            text="Status:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=9, column=0, padx=10, pady=10, sticky="w")
        
        self.status_combo = ctk.CTkComboBox(
            form_frame,
            width=250,
            height=35,
            values=["Pending", "Completed", "Cancelled"]
        )
        self.status_combo.grid(row=9, column=1, padx=10, pady=10)
        self.status_combo.set("Pending")
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Booking",
            command=self.add_booking,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Booking",
            command=self.update_booking,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="orange",
            hover_color="darkorange",
            state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Booking",
            command=self.delete_booking,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            width=120,
            height=35,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=5)
        
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
        
        columns = ("ID", "Customer", "Mobile", "Category", "Amount", "Date", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Mobile", text="Mobile")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Customer", width=120)
        self.tree.column("Mobile", width=100)
        self.tree.column("Category", width=120)
        self.tree.column("Amount", width=90, anchor="e")
        self.tree.column("Date", width=90)
        self.tree.column("Status", width=80, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
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
        
        if not full_amount or not self.validate_number(full_amount, True):
            MessageDialog.show_error("Error", "Please enter valid full amount")
            return
        
        if not advance or not self.validate_number(advance, True):
            MessageDialog.show_error("Error", "Please enter valid advance payment")
            return
        
        booking_id = self.db_manager.create_booking(
            name, mobile, category,
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
        
        if not full_amount or not advance:
            MessageDialog.show_error("Error", "Please enter amounts")
            return
        
        success = self.db_manager.update_booking(
            self.selected_booking_id, name, mobile, category,
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
        self.category_combo.set("Wedding Photography")
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
            
            self.tree.insert("", "end", values=(
                booking['id'],
                booking['customer_name'],
                booking['mobile_number'],
                booking['photoshoot_category'],
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
            
            self.tree.insert("", "end", values=(
                booking['id'],
                booking['customer_name'],
                booking['mobile_number'],
                booking['photoshoot_category'],
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
            
            self.category_combo.set(booking['photoshoot_category'])
            
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
