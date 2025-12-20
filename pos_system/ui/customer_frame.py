import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class CustomerManagementFrame(BaseFrame):
    """Customer management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_customer_id = None
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
        input_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
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
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Customer",
            command=self.add_customer,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Customer",
            command=self.update_customer,
            width=130,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Customer",
            command=self.delete_customer,
            width=130,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff4757",
            hover_color="#ff3344",
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            width=120,
            height=35,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        )
        clear_btn.pack(side="left", padx=5)
        
        # Search section
        search_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
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
        table_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
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
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
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
    
    def update_customer(self):
        """Update customer - Both admin and staff can edit"""
        if not self.selected_customer_id:
            MessageDialog.show_error("Error", "Please select a customer to update")
            return
        
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
        
        # Check if mobile exists for other customer
        existing = self.db_manager.get_customer_by_mobile(mobile)
        if existing and existing['id'] != self.selected_customer_id:
            MessageDialog.show_error("Error", "Another customer with this mobile number already exists")
            return
        
        success = self.db_manager.update_customer(self.selected_customer_id, name, mobile)
        
        if success:
            MessageDialog.show_success("Success", "Customer updated successfully")
            self.clear_form()
            self.load_customers()
        else:
            MessageDialog.show_error("Error", "Failed to update customer")
    
    def delete_customer(self):
        """Delete customer - Admin only"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can delete customers")
            return
        
        if not self.selected_customer_id:
            MessageDialog.show_error("Error", "Please select a customer to delete")
            return
        
        # Get customer info for confirmation
        customer = self.db_manager.get_customer_by_id(self.selected_customer_id)
        if not customer:
            MessageDialog.show_error("Error", "Customer not found")
            return
        
        if not MessageDialog.show_confirm("Confirm Delete", f"Are you sure you want to delete customer '{customer['full_name']}'?\n\nThis action cannot be undone."):
            return
        
        success = self.db_manager.delete_customer(self.selected_customer_id)
        
        if success:
            MessageDialog.show_success("Success", "Customer deleted successfully")
            self.clear_form()
            self.load_customers()
        else:
            MessageDialog.show_error("Error", "Failed to delete customer. Customer may have associated invoices.")
    
    def clear_form(self):
        """Clear input fields"""
        self.name_entry.delete(0, 'end')
        self.mobile_entry.delete(0, 'end')
        self.selected_customer_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")
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
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_customer_id = values[0]
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, values[1])
        self.mobile_entry.delete(0, 'end')
        self.mobile_entry.insert(0, values[2])
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")  # Both admin and staff can update
        # Only admin can delete
        if self.is_admin():
            self.delete_btn.configure(state="normal")
        else:
            self.delete_btn.configure(state="disabled")
