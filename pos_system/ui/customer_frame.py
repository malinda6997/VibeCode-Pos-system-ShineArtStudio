import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class CustomerManagementFrame(BaseFrame):
    """Customer management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.create_widgets()
        self.load_customers()
    
    def create_widgets(self):
        """Create customer management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Customer Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Full name
        name_label = ctk.CTkLabel(input_frame, text="Full Name:", font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.name_entry.grid(row=0, column=1, padx=15, pady=10)
        
        # Mobile number
        mobile_label = ctk.CTkLabel(input_frame, text="Mobile Number:", font=ctk.CTkFont(size=13, weight="bold"))
        mobile_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.mobile_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.mobile_entry.grid(row=1, column=1, padx=15, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Customer",
            command=self.add_customer,
            width=150,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        add_btn.pack(side="left", padx=10)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            width=150,
            height=35,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=10)
        
        # Search section
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_label = ctk.CTkLabel(search_frame, text="Search:", font=ctk.CTkFont(size=13, weight="bold"))
        search_label.pack(side="left", padx=15, pady=10)
        
        self.search_entry = ctk.CTkEntry(search_frame, width=300, height=35)
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_customers())
        
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.load_customers,
            width=120,
            height=35
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Table section
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview
        columns = ("ID", "Full Name", "Mobile Number", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Full Name", text="Full Name")
        self.tree.heading("Mobile Number", text="Mobile Number")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Full Name", width=250)
        self.tree.column("Mobile Number", width=150)
        self.tree.column("Created At", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def add_customer(self):
        """Add new customer"""
        name = self.name_entry.get().strip()
        mobile = self.mobile_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter customer name")
            return
        
        if not mobile:
            MessageDialog.show_error("Error", "Please enter mobile number")
            return
        
        if not self.validate_mobile(mobile):
            MessageDialog.show_error("Error", "Mobile number must be 10 digits")
            return
        
        # Check if mobile already exists
        existing = self.db_manager.get_customer_by_mobile(mobile)
        if existing:
            MessageDialog.show_error("Error", "Customer with this mobile number already exists")
            return
        
        customer_id = self.db_manager.add_customer(name, mobile)
        
        if customer_id:
            MessageDialog.show_success("Success", "Customer added successfully")
            self.clear_form()
            self.load_customers()
        else:
            MessageDialog.show_error("Error", "Failed to add customer")
    
    def clear_form(self):
        """Clear input fields"""
        self.name_entry.delete(0, 'end')
        self.mobile_entry.delete(0, 'end')
        self.name_entry.focus()
    
    def load_customers(self):
        """Load all customers"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        customers = self.db_manager.get_all_customers()
        
        for customer in customers:
            self.tree.insert("", "end", values=(
                customer['id'],
                customer['full_name'],
                customer['mobile_number'],
                customer['created_at']
            ))
    
    def search_customers(self):
        """Search customers"""
        search_term = self.search_entry.get().strip()
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_customers()
            return
        
        customers = self.db_manager.search_customers(search_term)
        
        for customer in customers:
            self.tree.insert("", "end", values=(
                customer['id'],
                customer['full_name'],
                customer['mobile_number'],
                customer['created_at']
            ))
