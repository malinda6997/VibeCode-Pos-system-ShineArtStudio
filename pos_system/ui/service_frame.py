import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class ServiceManagementFrame(BaseFrame):
    """Service management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_service_id = None
        self.categories_map = {}  # name -> id mapping
        self.create_widgets()
        self.load_categories()
        self.load_services()
    
    def create_widgets(self):
        """Create service management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Service Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Service name
        name_label = ctk.CTkLabel(input_frame, text="Service Name:", font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.name_entry.grid(row=0, column=1, padx=15, pady=10)
        
        # Category dropdown
        category_label = ctk.CTkLabel(input_frame, text="Category:", font=ctk.CTkFont(size=13, weight="bold"))
        category_label.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        
        self.category_combo = ctk.CTkComboBox(
            input_frame, 
            width=200, 
            height=35,
            values=["Select Category"],
            state="readonly"
        )
        self.category_combo.grid(row=0, column=3, padx=15, pady=10)
        self.category_combo.set("Select Category")
        
        # Price
        price_label = ctk.CTkLabel(input_frame, text="Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        price_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.price_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.price_entry.grid(row=1, column=1, padx=15, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Service",
            command=self.add_service,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Service",
            command=self.update_service,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Service",
            command=self.delete_service,
            width=120,
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
        
        # Check admin permissions
        if not self.is_admin():
            self.delete_btn.configure(state="disabled")
        
        # Table section
        table_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview
        columns = ("ID", "Service Name", "Category", "Price", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Service Name", text="Service Name")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Price", text="Price (LKR)")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Service Name", width=250)
        self.tree.column("Category", width=150)
        self.tree.column("Price", width=120, anchor="e")
        self.tree.column("Created At", width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def load_categories(self):
        """Load categories for dropdown"""
        categories = self.db_manager.get_all_categories()
        self.categories_map = {cat['category_name']: cat['id'] for cat in categories}
        category_names = ["Select Category"] + list(self.categories_map.keys())
        self.category_combo.configure(values=category_names)
    
    def add_service(self):
        """Add new service"""
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        category_name = self.category_combo.get()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter service name")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        if category_name == "Select Category":
            MessageDialog.show_error("Error", "Please select a category")
            return
        
        category_id = self.categories_map.get(category_name)
        
        service_id = self.db_manager.add_service(name, float(price), category_id)
        
        if service_id:
            MessageDialog.show_success("Success", "Service added successfully")
            self.clear_form()
            self.load_services()
        else:
            MessageDialog.show_error("Error", "Failed to add service")
    
    def update_service(self):
        """Update selected service"""
        if not self.selected_service_id:
            MessageDialog.show_error("Error", "Please select a service to update")
            return
        
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        category_name = self.category_combo.get()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter service name")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        if category_name == "Select Category":
            MessageDialog.show_error("Error", "Please select a category")
            return
        
        category_id = self.categories_map.get(category_name)
        
        success = self.db_manager.update_service(self.selected_service_id, name, float(price), category_id)
        
        if success:
            MessageDialog.show_success("Success", "Service updated successfully")
            self.clear_form()
            self.load_services()
        else:
            MessageDialog.show_error("Error", "Failed to update service")
    
    def delete_service(self):
        """Delete selected service"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can delete services")
            return
        
        if not self.selected_service_id:
            MessageDialog.show_error("Error", "Please select a service to delete")
            return
        
        if not MessageDialog.show_confirm("Confirm", "Are you sure you want to delete this service?"):
            return
        
        success = self.db_manager.delete_service(self.selected_service_id)
        
        if success:
            MessageDialog.show_success("Success", "Service deleted successfully")
            self.clear_form()
            self.load_services()
        else:
            MessageDialog.show_error("Error", "Failed to delete service")
    
    def clear_form(self):
        """Clear input fields"""
        self.name_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.category_combo.set("Select Category")
        self.selected_service_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled" if not self.is_admin() else "normal")
        self.name_entry.focus()
        # Reload categories in case new ones were added
        self.load_categories()
    
    def load_services(self):
        """Load all services"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        services = self.db_manager.get_all_services()
        
        for service in services:
            category_name = service.get('category_name', 'N/A') or 'N/A'
            self.tree.insert("", "end", values=(
                service['id'],
                service['service_name'],
                category_name,
                f"{service['price']:.2f}",
                service['created_at']
            ))
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_service_id = values[0]
        
        # Get full service data
        service = self.db_manager.get_service_by_id(self.selected_service_id)
        
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, service['service_name'])
        
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, str(service['price']))
        
        # Set category
        category_name = service.get('category_name')
        if category_name and category_name in self.categories_map:
            self.category_combo.set(category_name)
        else:
            self.category_combo.set("Select Category")
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")
        if self.is_admin():
            self.delete_btn.configure(state="normal")
