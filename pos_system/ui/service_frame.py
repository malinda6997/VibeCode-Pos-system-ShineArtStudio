import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class ServiceManagementFrame(BaseFrame):
    """Service management interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_service_id = None
        self.create_widgets()
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
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Service name
        name_label = ctk.CTkLabel(input_frame, text="Service Name:", font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.name_entry.grid(row=0, column=1, padx=15, pady=10)
        
        # Price
        price_label = ctk.CTkLabel(input_frame, text="Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        price_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.price_entry = ctk.CTkEntry(input_frame, width=250, height=35)
        self.price_entry.grid(row=1, column=1, padx=15, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
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
            fg_color="orange",
            hover_color="darkorange",
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
        
        # Check admin permissions
        if not self.is_admin():
            self.delete_btn.configure(state="disabled")
        
        # Table section
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview
        columns = ("ID", "Service Name", "Price", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Service Name", text="Service Name")
        self.tree.heading("Price", text="Price (LKR)")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Service Name", width=300)
        self.tree.column("Price", width=150, anchor="e")
        self.tree.column("Created At", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_service(self):
        """Add new service"""
        name = self.name_entry.get().strip()
        price = self.price_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter service name")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        service_id = self.db_manager.add_service(name, float(price))
        
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
        
        if not name:
            MessageDialog.show_error("Error", "Please enter service name")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        success = self.db_manager.update_service(self.selected_service_id, name, float(price))
        
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
        self.selected_service_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled" if not self.is_admin() else "normal")
        self.name_entry.focus()
    
    def load_services(self):
        """Load all services"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        services = self.db_manager.get_all_services()
        
        for service in services:
            self.tree.insert("", "end", values=(
                service['id'],
                service['service_name'],
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
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, values[1])
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, values[2])
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")
        if self.is_admin():
            self.delete_btn.configure(state="normal")
