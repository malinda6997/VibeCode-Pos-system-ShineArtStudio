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
        self.is_guest_customer = False  # Track if guest customer mode
        self.guest_customer_name = ""  # Guest customer name
        self.cart_items = []
        self.categories_map = {}  # name -> id mapping
        self.categories_data = {}  # name -> full category data including service_cost
        self.services_map = {}  # name -> service data
        self.category_service_cost = 0  # Track category service cost
        self.selected_category_name = None  # Track selected category
        self.create_widgets()
        self.load_categories()
    
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
        customer_label.pack(pady=(10, 10))
        
        # Guest Customer Toggle
        guest_toggle_container = ctk.CTkFrame(customer_frame, fg_color="transparent")
        guest_toggle_container.pack(fill="x", padx=15, pady=(0, 10))
        
        self.guest_switch_var = ctk.StringVar(value="off")
        self.guest_switch = ctk.CTkSwitch(
            guest_toggle_container,
            text="Guest Customer (Walk-in)",
            variable=self.guest_switch_var,
            onvalue="on",
            offvalue="off",
            command=self.toggle_guest_customer,
            progress_color="#00d4ff",
            button_color="#00ff88",
            button_hover_color="#00cc6a"
        )
        self.guest_switch.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            guest_toggle_container,
            text="💡 No registration needed",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        ).pack(side="left", padx=10)
        
        # Mobile search (for registered customers)
        self.search_container = ctk.CTkFrame(customer_frame, fg_color="transparent")
        self.search_container.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(self.search_container, text="Mobile Number:").pack(side="left", padx=5)
        self.mobile_search = ctk.CTkEntry(self.search_container, width=150, height=30)
        self.mobile_search.pack(side="left", padx=5)
        self.mobile_search.bind("<KeyRelease>", self.on_mobile_search_change)
        
        ctk.CTkButton(
            self.search_container,
            text="Search",
            command=self.search_customer,
            width=80,
            height=30
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.search_container,
            text="➕ Add New Customer",
            command=self.add_new_customer,
            width=150,
            height=30,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        # Guest customer name entry (hidden by default)
        self.guest_name_container = ctk.CTkFrame(customer_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.guest_name_container, text="Customer Name:").pack(side="left", padx=5)
        self.guest_name_entry = ctk.CTkEntry(self.guest_name_container, width=250, height=30, placeholder_text="Enter guest customer name")
        self.guest_name_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(
            self.guest_name_container,
            text="✓ Confirm",
            command=self.confirm_guest_customer,
            width=100,
            height=30,
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00cc6a",
            font=ctk.CTkFont(size=12, weight="bold")
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
            text="🔍 Search customer by mobile number or add a new one",
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
            command=self.on_item_type_change
        )
        self.item_type.pack(side="left", padx=10)
        self.item_type.set("Service")
        
        # Category selector (for services)
        category_container = ctk.CTkFrame(items_frame, fg_color="transparent")
        category_container.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(category_container, text="Category:").pack(side="left", padx=5)
        self.category_combo = ctk.CTkComboBox(
            category_container,
            width=180,
            height=30,
            values=["Select Category"],
            command=self.on_category_change,
            state="readonly"
        )
        self.category_combo.pack(side="left", padx=5)
        self.category_combo.set("Select Category")
        
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
        
        # Category Service Cost Display (read-only)
        service_cost_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        service_cost_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(service_cost_frame, text="Category Service:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.service_cost_label = ctk.CTkLabel(
            service_cost_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=13),
            text_color="#ffd93d"
        )
        self.service_cost_label.pack(side="right")
        
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
        
        # Advance Payment (optional)
        advance_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        advance_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(advance_frame, text="Advance Payment:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.advance_entry = ctk.CTkEntry(advance_frame, width=120, height=35)
        self.advance_entry.insert(0, "0")
        self.advance_entry.pack(side="right")
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Paid amount
        paid_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        paid_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(paid_frame, text="Paid Amount:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.paid_entry = ctk.CTkEntry(paid_frame, width=120, height=35)
        self.paid_entry.pack(side="right")
        self.paid_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())
        
        # Remaining Balance
        balance_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        balance_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(
            balance_frame,
            text="Remaining Balance:",
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
    
    def load_categories(self):
        """Load categories for dropdown"""
        categories = self.db_manager.get_all_categories()
        self.categories_map = {cat['category_name']: cat['id'] for cat in categories}
        self.categories_data = {cat['category_name']: cat for cat in categories}
        category_names = ["Select Category"] + list(self.categories_map.keys())
        self.category_combo.configure(values=category_names)
        # Load initial items
        self.on_item_type_change("Service")
    
    def on_item_type_change(self, item_type):
        """Handle item type change"""
        if item_type == "Service":
            # Show category selector and reset
            self.category_combo.set("Select Category")
            self.item_combo.configure(values=["Select Category First"])
            self.item_combo.set("Select Category First")
            self.services_map = {}
            self.category_service_cost = 0
            self.selected_category_name = None
        else:
            # Load frames directly - no category service cost for frames
            self.category_service_cost = 0
            self.selected_category_name = None
            self.load_frames()
        self.calculate_totals()
    
    def on_category_change(self, selected_category):
        """Load services when category changes and check service cost"""
        if selected_category == "Select Category":
            self.item_combo.configure(values=["Select Category First"])
            self.item_combo.set("Select Category First")
            self.services_map = {}
            self.category_service_cost = 0
            self.selected_category_name = None
            self.calculate_totals()
            return
        
        category_id = self.categories_map.get(selected_category)
        category_data = self.categories_data.get(selected_category)
        
        # Get category service cost if available
        if category_data and category_data.get('service_cost') is not None:
            self.category_service_cost = float(category_data['service_cost'])
            self.selected_category_name = selected_category
        else:
            self.category_service_cost = 0
            self.selected_category_name = None
        
        if category_id:
            services = self.db_manager.get_services_by_category(category_id)
            self.services_map = {s['service_name']: s for s in services}
            service_names = list(self.services_map.keys())
            if service_names:
                self.item_combo.configure(values=service_names)
                self.item_combo.set(service_names[0])
            else:
                self.item_combo.configure(values=["No Services in Category"])
                self.item_combo.set("No Services in Category")
        else:
            self.item_combo.configure(values=["No Services"])
            self.item_combo.set("No Services")
            self.services_map = {}
        
        self.calculate_totals()
    
    def load_frames(self):
        """Load photo frames"""
        items = self.db_manager.get_all_photo_frames()
        self.items_data = {f"{item['frame_name']} - {item['size']}": item for item in items}
        frame_names = list(self.items_data.keys())
        if frame_names:
            self.item_combo.configure(values=frame_names)
            self.item_combo.set(frame_names[0])
        else:
            self.item_combo.configure(values=["No Frames"])
            self.item_combo.set("No Frames")
    
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
        self.is_guest_customer = False
        self.guest_customer_name = ""
        self.customer_card.pack_forget()
        self.no_customer_label.pack(pady=10)
        self.mobile_search.delete(0, "end")
        self.guest_name_entry.delete(0, "end")
    
    def toggle_guest_customer(self):
        """Toggle between guest and registered customer mode"""
        if self.guest_switch_var.get() == "on":
            # Switch to guest customer mode
            self.is_guest_customer = True
            self.search_container.pack_forget()
            self.guest_name_container.pack(fill="x", padx=15, pady=5)
            self.clear_selected_customer_display()
            self.hide_suggestions()
            # Update label
            self.no_customer_label.configure(text="🎫 Enter guest customer name above")
        else:
            # Switch back to registered customer mode
            self.is_guest_customer = False
            self.guest_customer_name = ""
            self.guest_name_container.pack_forget()
            self.search_container.pack(fill="x", padx=15, pady=5)
            self.clear_selected_customer_display()
            # Restore label
            self.no_customer_label.configure(text="🔍 Search customer by mobile number or add a new one")
    
    def clear_selected_customer_display(self):
        """Clear customer card display without resetting guest mode"""
        self.selected_customer = None
        self.customer_card.pack_forget()
        self.no_customer_label.pack(pady=10)
        self.mobile_search.delete(0, "end")
        self.guest_name_entry.delete(0, "end")
    
    def confirm_guest_customer(self):
        """Confirm guest customer name"""
        name = self.guest_name_entry.get().strip()
        if not name:
            MessageDialog.show_error("Error", "Please enter guest customer name")
            return
        
        self.guest_customer_name = name
        # Show in customer card with guest indicator
        self.customer_name_label.configure(text=f"🎫 {name}")
        self.customer_mobile_label.configure(text="Guest Customer (Walk-in)")
        self.no_customer_label.pack_forget()
        self.customer_card.pack(fill="x", padx=15, pady=10)
    
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
        """Add new customer dialog with proper size and scrolling"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Customer")
        dialog.geometry("500x420")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 210
        dialog.geometry(f"500x420+{x}+{y}")
        
        # Main scrollable frame with matching background
        main_scroll = ctk.CTkScrollableFrame(
            dialog, 
            fg_color="#1a1a2e",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Content frame inside scroll
        content_frame = ctk.CTkFrame(main_scroll, fg_color="#1e1e3f", corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(
            content_frame,
            text="➕ Add New Customer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=(25, 30))
        
        # Form frame
        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=35)
        
        # Customer Name
        ctk.CTkLabel(
            form_frame,
            text="Customer Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        name_entry = ctk.CTkEntry(
            form_frame, 
            height=45,
            font=ctk.CTkFont(size=13),
            placeholder_text="Enter customer full name",
            corner_radius=8
        )
        name_entry.pack(fill="x", pady=(0, 20))
        
        # Mobile Number
        ctk.CTkLabel(
            form_frame,
            text="Mobile Number:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        mobile_entry = ctk.CTkEntry(
            form_frame, 
            height=45,
            font=ctk.CTkFont(size=13),
            placeholder_text="Enter 10-digit mobile number",
            corner_radius=8
        )
        mobile_entry.pack(fill="x", pady=(0, 25))
        
        def save_customer():
            name = name_entry.get().strip()
            mobile = mobile_entry.get().strip()
            
            if not name:
                MessageDialog.show_error("Error", "Please enter customer name")
                return
            
            if not mobile:
                MessageDialog.show_error("Error", "Please enter mobile number")
                return
            
            if not self.validate_mobile(mobile):
                MessageDialog.show_error("Error", "Mobile number must be 10 digits")
                return
            
            # Check if exists
            existing = self.db_manager.get_customer_by_mobile(mobile)
            if existing:
                MessageDialog.show_error("Error", "Customer with this mobile already exists")
                return
            
            customer_id = self.db_manager.add_customer(name, mobile)
            if customer_id:
                MessageDialog.show_success("Success", "Customer added successfully")
                dialog.destroy()
                # Auto-select the new customer
                self.mobile_search.delete(0, 'end')
                self.mobile_search.insert(0, mobile)
                self.search_customer()
            else:
                MessageDialog.show_error("Error", "Failed to add customer")
        
        # Button frame
        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 30))
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            width=130,
            height=45,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="➕ Add Customer",
            command=save_customer,
            width=160,
            height=45,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)
        
        # Focus on name entry
        name_entry.focus()
    
    def load_items(self, value=None):
        """Load items based on type - Now handled by on_item_type_change and on_category_change"""
        pass  # Keep for compatibility but functionality moved to new methods
    
    def add_to_cart(self):
        """Add item to cart"""
        item_type = self.item_type.get()
        selected_key = self.item_combo.get()
        
        if not selected_key or selected_key in ["Select Category First", "No Services in Category", "No Services", "No Frames"]:
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
        
        if item_type == "Service":
            if selected_key not in self.services_map:
                MessageDialog.show_error("Error", "Please select a valid service")
                return
            item = self.services_map[selected_key]
            cart_item = {
                'type': 'Service',
                'id': item['id'],
                'name': item['service_name'],
                'quantity': qty,
                'unit_price': item['price'],
                'total': item['price'] * qty
            }
        else:
            if not hasattr(self, 'items_data') or selected_key not in self.items_data:
                MessageDialog.show_error("Error", "Please select a valid frame")
                return
            item = self.items_data[selected_key]
            # Check stock for frames
            if item['quantity'] < qty:
                MessageDialog.show_error("Error", f"Insufficient stock. Available: {item['quantity']}")
                return
            cart_item = {
                'type': 'Frame',
                'id': item['id'],
                'name': selected_key,
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
        """Calculate totals including category service cost"""
        subtotal = sum(item['total'] for item in self.cart_items)
        
        discount_str = self.discount_entry.get().strip()
        discount = float(discount_str) if discount_str and self.validate_number(discount_str, True) else 0
        
        # Add category service cost if applicable
        service_cost = self.category_service_cost
        
        total = subtotal + service_cost - discount
        
        self.subtotal_label.configure(text=f"LKR {subtotal:.2f}")
        self.service_cost_label.configure(text=f"LKR {service_cost:.2f}")
        self.total_label.configure(text=f"LKR {total:.2f}")
        
        self.calculate_balance()
    
    def calculate_balance(self):
        """Calculate remaining balance based on advance and paid amount"""
        total_str = self.total_label.cget("text").replace("LKR ", "").replace(",", "")
        total = float(total_str) if total_str else 0
        
        advance_str = self.advance_entry.get().strip()
        advance = float(advance_str) if advance_str and self.validate_number(advance_str, True) else 0
        
        paid_str = self.paid_entry.get().strip()
        paid = float(paid_str) if paid_str and self.validate_number(paid_str, True) else 0
        
        # Total paid = advance + paid amount
        total_paid = advance + paid
        
        # Remaining balance (never negative)
        remaining = max(0, total - total_paid)
        
        self.balance_label.configure(text=f"LKR {remaining:.2f}")
        
        # Update color based on balance
        if remaining > 0:
            self.balance_label.configure(text_color="#ff6b6b")  # Red for pending
        else:
            self.balance_label.configure(text_color="#00ff88")  # Green for fully paid
    
    def generate_invoice(self):
        """Generate and save invoice"""
        # Check for customer (either registered or guest)
        if self.is_guest_customer:
            if not self.guest_customer_name:
                MessageDialog.show_error("Error", "Please enter guest customer name")
                return
        else:
            if not self.selected_customer:
                MessageDialog.show_error("Error", "Please select a customer")
                return
        
        if not self.cart_items:
            MessageDialog.show_error("Error", "Please add items to cart")
            return
        
        paid_str = self.paid_entry.get().strip()
        advance_str = self.advance_entry.get().strip()
        
        # Validate paid amount (can be 0 if advance covers total)
        if paid_str and not self.validate_number(paid_str, True):
            MessageDialog.show_error("Error", "Please enter valid paid amount")
            return
        
        if advance_str and not self.validate_number(advance_str, True):
            MessageDialog.show_error("Error", "Please enter valid advance amount")
            return
        
        # Calculate totals
        subtotal = sum(item['total'] for item in self.cart_items)
        discount = float(self.discount_entry.get() or 0)
        service_cost = self.category_service_cost
        total = subtotal + service_cost - discount
        advance = float(advance_str) if advance_str else 0
        paid = float(paid_str) if paid_str else 0
        total_paid = advance + paid
        
        # Remaining balance (never negative)
        balance = max(0, total - total_paid)
        
        # Generate invoice number
        invoice_number = self.db_manager.generate_invoice_number()
        
        # Determine customer_id and guest_name
        if self.is_guest_customer:
            customer_id = None
            guest_name = self.guest_customer_name
        else:
            customer_id = self.selected_customer['id']
            guest_name = None
        
        # Create invoice with category service cost and advance payment
        invoice_id = self.db_manager.create_invoice(
            invoice_number,
            customer_id,
            subtotal,
            discount,
            total,
            total_paid,
            balance,
            self.auth_manager.get_user_id(),
            service_cost,
            advance,
            guest_name
        )
        
        if not invoice_id:
            MessageDialog.show_error("Error", "Failed to create invoice")
            return
        
        # Add invoice items and update stock
        for item in self.cart_items:
            buying_price = 0
            if item['type'] == 'Frame':
                # Get buying price for frame profit tracking
                frame_data = self.db_manager.get_photo_frame_by_id(item['id'])
                if frame_data:
                    buying_price = frame_data.get('buying_price', 0) or 0
            
            self.db_manager.add_invoice_item(
                invoice_id,
                item['type'],
                item['id'],
                item['name'],
                item['quantity'],
                item['unit_price'],
                item['total'],
                buying_price * item['quantity']  # Total buying cost
            )
            
            # Update frame stock
            if item['type'] == 'Frame':
                self.db_manager.update_frame_quantity(item['id'], -item['quantity'])
        
        # Add category service cost as a separate line item if applicable
        if service_cost > 0 and self.selected_category_name:
            self.db_manager.add_invoice_item(
                invoice_id,
                'CategoryService',
                0,
                f"Category Service - {self.selected_category_name}",
                1,
                service_cost,
                service_cost,
                0
            )
        
        # Generate PDF
        invoice_data = self.db_manager.get_invoice_by_id(invoice_id)
        items_data = self.db_manager.get_invoice_items(invoice_id)
        
        # Prepare customer data for PDF (works for both guest and registered)
        if self.is_guest_customer:
            customer_data = {
                'full_name': self.guest_customer_name,
                'mobile_number': 'Guest Customer'
            }
        else:
            customer_data = self.selected_customer
        
        try:
            pdf_path = self.invoice_generator.generate_invoice(
                invoice_data,
                items_data,
                customer_data
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
        self.is_guest_customer = False
        self.guest_customer_name = ""
        self.cart_items = []
        self.category_service_cost = 0
        self.selected_category_name = None
        self.mobile_search.delete(0, 'end')
        self.guest_name_entry.delete(0, 'end')
        # Reset guest switch
        self.guest_switch_var.set("off")
        self.guest_name_container.pack_forget()
        self.search_container.pack(fill="x", padx=15, pady=5)
        self.clear_selected_customer()
        self.no_customer_label.configure(text="🔍 Search customer by mobile number or add a new one")
        self.discount_entry.delete(0, 'end')
        self.discount_entry.insert(0, "0")
        self.advance_entry.delete(0, 'end')
        self.advance_entry.insert(0, "0")
        self.paid_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')
        self.quantity_entry.insert(0, "1")
        # Reset category and item selection
        self.item_type.set("Service")
        self.category_combo.set("Select Category")
        self.item_combo.configure(values=["Select Category First"])
        self.item_combo.set("Select Category First")
        self.services_map = {}
        self.refresh_cart()
        self.calculate_totals()
