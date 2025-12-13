import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services import InvoiceGenerator


class BillingFrame(BaseFrame):
    """Billing and invoice generation interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.invoice_generator = InvoiceGenerator()
        self.selected_customer = None
        self.cart_items = []
        self.create_widgets()
    
    def create_widgets(self):
        """Create billing widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Billing & Invoice",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Customer and items
        left_panel = ctk.CTkFrame(main_container, fg_color="#1e1e3f", corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Customer section
        customer_frame = ctk.CTkFrame(left_panel, fg_color="#252545", corner_radius=10)
        customer_frame.pack(fill="x", padx=15, pady=15)
        
        customer_label = ctk.CTkLabel(
            customer_frame,
            text="Customer Information",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        customer_label.pack(pady=(10, 15))
        
        # Mobile search
        search_container = ctk.CTkFrame(customer_frame, fg_color="transparent")
        search_container.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(search_container, text="Mobile Number:").pack(side="left", padx=5)
        self.mobile_search = ctk.CTkEntry(search_container, width=150, height=30)
        self.mobile_search.pack(side="left", padx=5)
        self.mobile_search.bind("<KeyRelease>", self.on_mobile_search_change)
        
        ctk.CTkButton(
            search_container,
            text="Search",
            command=self.search_customer,
            width=80,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            search_container,
            text="New Customer",
            command=self.add_new_customer,
            width=120,
            height=30,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        ).pack(side="left", padx=5)
        
        # Customer suggestions dropdown (hidden by default)
        self.suggestions_frame = ctk.CTkFrame(customer_frame, fg_color="#2d2d5a", corner_radius=8)
        self.suggestion_buttons = []
        
        # Customer details display card (hidden by default)
        self.customer_card = ctk.CTkFrame(customer_frame, fg_color="#1e3a2f", corner_radius=10, border_width=2, border_color="#00ff88")
        
        # Card content
        card_content = ctk.CTkFrame(self.customer_card, fg_color="transparent")
        card_content.pack(fill="x", padx=15, pady=12)
        
        # Left side - Icon
        icon_frame = ctk.CTkFrame(card_content, fg_color="#00ff88", width=50, height=50, corner_radius=25)
        icon_frame.pack(side="left", padx=(0, 15))
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame,
            text="👤",
            font=ctk.CTkFont(size=24),
            text_color="#1a1a2e"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Right side - Customer details
        details_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        details_frame.pack(side="left", fill="x", expand=True)
        
        self.customer_name_label = ctk.CTkLabel(
            details_frame,
            text="",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white",
            anchor="w"
        )
        self.customer_name_label.pack(fill="x")
        
        self.customer_mobile_label = ctk.CTkLabel(
            details_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#00ff88",
            anchor="w"
        )
        self.customer_mobile_label.pack(fill="x")
        
        # Clear button
        self.clear_customer_btn = ctk.CTkButton(
            card_content,
            text="✕",
            width=30,
            height=30,
            fg_color="#ff6b6b",
            hover_color="#e55555",
            corner_radius=15,
            command=self.clear_selected_customer
        )
        self.clear_customer_btn.pack(side="right", padx=(10, 0))
        
        # No customer selected label
        self.no_customer_label = ctk.CTkLabel(
            customer_frame,
            text="🔍 Search customer by mobile number",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.no_customer_label.pack(pady=10)
        
        # Add items section
        items_frame = ctk.CTkFrame(left_panel, fg_color="#252545", corner_radius=10)
        items_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        items_label = ctk.CTkLabel(
            items_frame,
            text="Add Items",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        items_label.pack(pady=(10, 15))
        
        # Item type selector
        type_container = ctk.CTkFrame(items_frame, fg_color="transparent")
        type_container.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(type_container, text="Item Type:").pack(side="left", padx=5)
        self.item_type = ctk.CTkSegmentedButton(
            type_container,
            values=["Service", "Frame"],
            command=self.load_items
        )
        self.item_type.pack(side="left", padx=10)
        self.item_type.set("Service")
        
        # Item selector
        item_container = ctk.CTkFrame(items_frame, fg_color="transparent")
        item_container.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(item_container, text="Select Item:").pack(side="left", padx=5)
        self.item_combo = ctk.CTkComboBox(
            item_container,
            width=200,
            height=30,
            state="readonly"
        )
        self.item_combo.pack(side="left", padx=5)
        
        ctk.CTkLabel(item_container, text="Qty:").pack(side="left", padx=5)
        self.quantity_entry = ctk.CTkEntry(item_container, width=60, height=30)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            item_container,
            text="Add to Cart",
            command=self.add_to_cart,
            width=100,
            height=30
        ).pack(side="left", padx=5)
        
        # Cart table
        cart_frame = ctk.CTkFrame(left_panel, fg_color="#252545", corner_radius=10)
        cart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        cart_label = ctk.CTkLabel(
            cart_frame,
            text="Cart Items",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        cart_label.pack(pady=(10, 10))
        
        # Cart treeview
        columns = ("Item", "Type", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(cart_frame, columns=columns, show="headings", height=8)
        
        self.cart_tree.heading("Item", text="Item Name")
        self.cart_tree.heading("Type", text="Type")
        self.cart_tree.heading("Qty", text="Qty")
        self.cart_tree.heading("Price", text="Unit Price")
        self.cart_tree.heading("Total", text="Total")
        
        self.cart_tree.column("Item", width=180)
        self.cart_tree.column("Type", width=80, anchor="center")
        self.cart_tree.column("Qty", width=50, anchor="center")
        self.cart_tree.column("Price", width=90, anchor="e")
        self.cart_tree.column("Total", width=90, anchor="e")
        
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Remove button
        ctk.CTkButton(
            cart_frame,
            text="Remove Selected",
            command=self.remove_from_cart,
            width=150,
            height=30,
            fg_color="#ff4757",
            hover_color="#ff3344"
        ).pack(pady=(0, 10))
        
        # Right panel - Payment
        right_panel = ctk.CTkFrame(main_container, width=350, fg_color="#1e1e3f", corner_radius=15)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        payment_label = ctk.CTkLabel(
            right_panel,
            text="Payment Details",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        payment_label.pack(pady=(20, 20))
        
        # Subtotal
        subtotal_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        subtotal_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(subtotal_frame, text="Subtotal:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.subtotal_label = ctk.CTkLabel(
            subtotal_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.subtotal_label.pack(side="right")
        
        # Discount
        discount_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        discount_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(discount_frame, text="Discount:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.discount_entry = ctk.CTkEntry(discount_frame, width=100, height=30)
        self.discount_entry.insert(0, "0")
        self.discount_entry.pack(side="right")
        self.discount_entry.bind("<KeyRelease>", lambda e: self.calculate_totals())
        
        # Total
        total_frame = ctk.CTkFrame(right_panel)
        total_frame.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            total_frame,
            text="Total Amount:",
            font=ctk.CTkFont(size=15, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#00ff00"
        )
        self.total_label.pack(side="right", padx=10, pady=10)
        
        # Paid amount
        paid_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        paid_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(paid_frame, text="Paid Amount:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.paid_entry = ctk.CTkEntry(paid_frame, width=120, height=35)
        self.paid_entry.pack(side="right")
        self.paid_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Balance
        balance_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        balance_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(
            balance_frame,
            text="Balance:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left")
        self.balance_label = ctk.CTkLabel(
            balance_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="yellow"
        )
        self.balance_label.pack(side="right")
        
        # Generate invoice button
        ctk.CTkButton(
            right_panel,
            text="Generate Invoice",
            command=self.generate_invoice,
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e"
        ).pack(pady=30)
        
        # Clear all button
        ctk.CTkButton(
            right_panel,
            text="Clear All",
            command=self.clear_all,
            width=200,
            height=35,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        ).pack(pady=10)
        
        # Load initial items
        self.load_items()
    
    def search_customer(self):
        """Search customer by mobile"""
        self.hide_suggestions()
        mobile = self.mobile_search.get().strip()
        
        if not mobile:
            MessageDialog.show_error("Error", "Please enter mobile number")
            return
        
        customer = self.db_manager.get_customer_by_mobile(mobile)
        
        if customer:
            self.show_customer_card(customer)
        else:
            MessageDialog.show_error("Not Found", "Customer not found")
            self.selected_customer = None
    
    def show_customer_card(self, customer):
        """Display selected customer in a nice card"""
        self.selected_customer = customer
        self.customer_name_label.configure(text=customer['full_name'])
        self.customer_mobile_label.configure(text=f"📱 {customer['mobile_number']}")
        self.no_customer_label.pack_forget()
        self.customer_card.pack(fill="x", padx=15, pady=10)
    
    def clear_selected_customer(self):
        """Clear selected customer"""
        self.selected_customer = None
        self.customer_card.pack_forget()
        self.no_customer_label.pack(pady=10)
        self.mobile_search.delete(0, "end")
    
    def on_mobile_search_change(self, event=None):
        """Auto-search when typing 5+ digits"""
        mobile = self.mobile_search.get().strip()
        
        # Only search if 5 or more digits entered
        if len(mobile) >= 5:
            customers = self.db_manager.search_customers(mobile)
            
            if customers:
                self.show_suggestions(customers)
            else:
                self.hide_suggestions()
        else:
            self.hide_suggestions()
    
    def show_suggestions(self, customers):
        """Show customer suggestions dropdown"""
        # Clear existing buttons
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons = []
        
        # Show frame
        self.suggestions_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        # Add customer buttons (max 5)
        for customer in customers[:5]:
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=f"📱 {customer['mobile_number']}  -  {customer['full_name']}",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#3d3d6a",
                anchor="w",
                height=35,
                command=lambda c=customer: self.select_suggestion(c)
            )
            btn.pack(fill="x", padx=5, pady=2)
            self.suggestion_buttons.append(btn)
    
    def hide_suggestions(self):
        """Hide suggestions dropdown"""
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons = []
        self.suggestions_frame.pack_forget()
    
    def select_suggestion(self, customer):
        """Select a customer from suggestions"""
        self.hide_suggestions()
        self.mobile_search.delete(0, "end")
        self.mobile_search.insert(0, customer['mobile_number'])
        self.show_customer_card(customer)

    def add_new_customer(self):
        """Add new customer dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Customer")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 200
        y = (dialog.winfo_screenheight() // 2) - 125
        dialog.geometry(f"400x250+{x}+{y}")
        
        ctk.CTkLabel(
            dialog,
            text="Add New Customer",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(dialog, text="Full Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog, width=300, height=35)
        name_entry.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Mobile Number:").pack(pady=5)
        mobile_entry = ctk.CTkEntry(dialog, width=300, height=35)
        mobile_entry.pack(pady=5)
        
        def save_customer():
            name = name_entry.get().strip()
            mobile = mobile_entry.get().strip()
            
            if not name or not mobile:
                MessageDialog.show_error("Error", "Please fill all fields")
                return
            
            if not self.validate_mobile(mobile):
                MessageDialog.show_error("Error", "Mobile must be 10 digits")
                return
            
            customer_id = self.db_manager.add_customer(name, mobile)
            if customer_id:
                MessageDialog.show_success("Success", "Customer added")
                self.mobile_search.delete(0, 'end')
                self.mobile_search.insert(0, mobile)
                dialog.destroy()
                self.search_customer()
            else:
                MessageDialog.show_error("Error", "Failed to add customer")
        
        ctk.CTkButton(
            dialog,
            text="Save Customer",
            command=save_customer,
            width=200,
            height=40
        ).pack(pady=20)
    
    def load_items(self, value=None):
        """Load items based on type"""
        item_type = self.item_type.get()
        
        if item_type == "Service":
            items = self.db_manager.get_all_services()
            self.items_data = {f"{item['service_name']}": item for item in items}
        else:
            items = self.db_manager.get_all_photo_frames()
            self.items_data = {f"{item['frame_name']} - {item['size']}": item for item in items}
        
        self.item_combo.configure(values=list(self.items_data.keys()))
        if self.items_data:
            self.item_combo.set(list(self.items_data.keys())[0])
    
    def add_to_cart(self):
        """Add item to cart"""
        if not self.item_combo.get():
            MessageDialog.show_error("Error", "Please select an item")
            return
        
        qty_str = self.quantity_entry.get().strip()
        if not qty_str or not self.validate_number(qty_str):
            MessageDialog.show_error("Error", "Please enter valid quantity")
            return
        
        qty = int(qty_str)
        if qty <= 0:
            MessageDialog.show_error("Error", "Quantity must be greater than 0")
            return
        
        selected_key = self.item_combo.get()
        item = self.items_data[selected_key]
        item_type = self.item_type.get()
        
        # Check stock for frames
        if item_type == "Frame" and item['quantity'] < qty:
            MessageDialog.show_error("Error", f"Insufficient stock. Available: {item['quantity']}")
            return
        
        # Add to cart
        cart_item = {
            'type': item_type,
            'id': item['id'],
            'name': selected_key if item_type == "Frame" else item['service_name'],
            'quantity': qty,
            'unit_price': item['price'],
            'total': item['price'] * qty
        }
        
        self.cart_items.append(cart_item)
        self.refresh_cart()
        self.calculate_totals()
        
        # Reset quantity
        self.quantity_entry.delete(0, 'end')
        self.quantity_entry.insert(0, "1")
    
    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select an item to remove")
            return
        
        index = self.cart_tree.index(selection[0])
        self.cart_items.pop(index)
        self.refresh_cart()
        self.calculate_totals()
    
    def refresh_cart(self):
        """Refresh cart display"""
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        for item in self.cart_items:
            self.cart_tree.insert("", "end", values=(
                item['name'],
                item['type'],
                item['quantity'],
                f"{item['unit_price']:.2f}",
                f"{item['total']:.2f}"
            ))
    
    def calculate_totals(self):
        """Calculate totals"""
        subtotal = sum(item['total'] for item in self.cart_items)
        
        discount_str = self.discount_entry.get().strip()
        discount = float(discount_str) if discount_str and self.validate_number(discount_str, True) else 0
        
        total = subtotal - discount
        
        self.subtotal_label.configure(text=f"LKR {subtotal:.2f}")
        self.total_label.configure(text=f"LKR {total:.2f}")
        
        self.calculate_balance()
    
    def calculate_balance(self):
        """Calculate balance"""
        total_str = self.total_label.cget("text").replace("LKR ", "")
        total = float(total_str) if total_str else 0
        
        paid_str = self.paid_entry.get().strip()
        paid = float(paid_str) if paid_str and self.validate_number(paid_str, True) else 0
        
        balance = paid - total
        
        self.balance_label.configure(text=f"LKR {balance:.2f}")
    
    def generate_invoice(self):
        """Generate and save invoice"""
        if not self.selected_customer:
            MessageDialog.show_error("Error", "Please select a customer")
            return
        
        if not self.cart_items:
            MessageDialog.show_error("Error", "Please add items to cart")
            return
        
        paid_str = self.paid_entry.get().strip()
        if not paid_str or not self.validate_number(paid_str, True):
            MessageDialog.show_error("Error", "Please enter paid amount")
            return
        
        # Calculate totals
        subtotal = sum(item['total'] for item in self.cart_items)
        discount = float(self.discount_entry.get() or 0)
        total = subtotal - discount
        paid = float(paid_str)
        balance = paid - total
        
        # Generate invoice number
        invoice_number = self.db_manager.generate_invoice_number()
        
        # Create invoice
        invoice_id = self.db_manager.create_invoice(
            invoice_number,
            self.selected_customer['id'],
            subtotal,
            discount,
            total,
            paid,
            balance,
            self.auth_manager.get_user_id()
        )
        
        if not invoice_id:
            MessageDialog.show_error("Error", "Failed to create invoice")
            return
        
        # Add invoice items and update stock
        for item in self.cart_items:
            self.db_manager.add_invoice_item(
                invoice_id,
                item['type'],
                item['id'],
                item['name'],
                item['quantity'],
                item['unit_price'],
                item['total']
            )
            
            # Update frame stock
            if item['type'] == 'Frame':
                self.db_manager.update_frame_quantity(item['id'], -item['quantity'])
        
        # Generate PDF
        invoice_data = self.db_manager.get_invoice_by_id(invoice_id)
        items_data = self.db_manager.get_invoice_items(invoice_id)
        
        try:
            pdf_path = self.invoice_generator.generate_invoice(
                invoice_data,
                items_data,
                self.selected_customer
            )
            
            MessageDialog.show_success("Success", f"Invoice {invoice_number} generated successfully!")
            
            # Open PDF
            self.invoice_generator.open_invoice(pdf_path)
            
            # Clear all
            self.clear_all()
            
        except Exception as e:
            MessageDialog.show_error("Error", f"Failed to generate PDF: {str(e)}")
    
    def clear_all(self):
        """Clear all fields"""
        self.selected_customer = None
        self.cart_items = []
        self.mobile_search.delete(0, 'end')
        self.customer_info.configure(text="No customer selected", text_color="gray")
        self.discount_entry.delete(0, 'end')
        self.discount_entry.insert(0, "0")
        self.paid_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')
        self.quantity_entry.insert(0, "1")
        self.refresh_cart()
        self.calculate_totals()
