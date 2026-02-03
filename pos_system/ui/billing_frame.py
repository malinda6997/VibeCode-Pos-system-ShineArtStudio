import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services import InvoiceGenerator, BillGenerator


class BillingFrame(BaseFrame):
    """Billing and invoice generation interface with popup-based selection"""

    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.invoice_generator = InvoiceGenerator()
        self.bill_generator = BillGenerator()
        self.selected_customer = None
        self.is_guest_customer = False
        self.guest_customer_name = ""
        self.cart_items = []
        self.categories_map = {}
        self.categories_data = {}
        self.services_map = {}
        self.frames_map = {}
        self.category_service_cost = 0
        self.selected_category_name = None
        self.selected_category_id = None
        self.free_service_name = None
        self.payment_type = "full"  # 'full' or 'advance'
        self.booking_reference = None  # For linking to booking
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
        left_panel = ctk.CTkFrame(main_container, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Customer section
        customer_frame = ctk.CTkFrame(left_panel, fg_color="#0d0d1a", corner_radius=10)
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
            progress_color="#8C00FF",
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
            height=30,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            self.search_container,
            text="➕ Add New Customer",
            command=self.add_new_customer,
            width=150,
            height=30,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20,
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

        # Add items section - MODERN DESIGN
        items_frame = ctk.CTkFrame(left_panel, fg_color="#0d0d1a", corner_radius=20, border_width=2, border_color="#444444")
        items_frame.pack(fill="x", padx=15, pady=(0, 15))

        items_label = ctk.CTkLabel(
            items_frame,
            text="Add Items to Cart",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        )
        items_label.pack(pady=(15, 5))

        # Item type selector - MODERN SEGMENTED BUTTON
        type_container = ctk.CTkFrame(items_frame, fg_color="transparent")
        type_container.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            type_container,
            text="Select Item Type:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=5, pady=(0, 5))
        
        self.item_type = ctk.CTkSegmentedButton(
            type_container,
            values=["Services", "Frames"],
            command=self.on_item_type_change,
            selected_color="#8C00FF",
            selected_hover_color="#7300D6",
            unselected_color="#2d2d5a",
            unselected_hover_color="#3d3d7a",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=20,
            border_width=2
        )
        self.item_type.pack(fill="x", padx=5)
        self.item_type.set("Services")  # Default to Services

        # Selected category display - ENHANCED
        self.selected_category_frame = ctk.CTkFrame(items_frame, fg_color="#1e3a2f", corner_radius=10, border_width=2, border_color="#00ff88")
        
        category_info_frame = ctk.CTkFrame(self.selected_category_frame, fg_color="transparent")
        category_info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        self.selected_category_label = ctk.CTkLabel(
            category_info_frame,
            text="No category selected",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00ff88",
            anchor="w"
        )
        self.selected_category_label.pack(anchor="w")
        
        # Service cost display - PROMINENT
        self.category_cost_display = ctk.CTkLabel(
            category_info_frame,
            text="Service Cost: Rs. 0.00",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffd93d",
            anchor="w"
        )
        self.category_cost_display.pack(anchor="w", pady=(3, 0))

        # Free service indicator
        self.free_service_label = ctk.CTkLabel(
            category_info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#ffd93d",
            anchor="w"
        )
        self.free_service_label.pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            self.selected_category_frame,
            text="Change",
            width=70,
            height=28,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            command=self.open_category_popup
        ).pack(side="right", padx=10, pady=8)

        # Popup trigger buttons - MODERN DESIGN
        btn_container = ctk.CTkFrame(items_frame, fg_color="transparent")
        btn_container.pack(fill="x", padx=15, pady=15)

        self.select_category_btn = ctk.CTkButton(
            btn_container,
            text="📁 Select Category",
            width=190,
            height=45,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold"),
            border_width=2,
            border_color="#8C00FF",
            command=self.open_category_popup
        )
        self.select_category_btn.pack(side="left", padx=5)

        self.select_item_btn = ctk.CTkButton(
            btn_container,
            text="🎨 Select Service",
            width=190,
            height=45,
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=20,
            border_width=2,
            border_color="#8C00FF",
            command=self.open_item_popup,
            state="disabled"
        )
        self.select_item_btn.pack(side="left", padx=5)

        # Cart table - FIXED: Store as instance variable to prevent disappearing
        self.cart_frame = ctk.CTkFrame(left_panel, fg_color="#0d0d1a", corner_radius=20, border_width=2, border_color="#444444")
        self.cart_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        cart_label = ctk.CTkLabel(
            self.cart_frame,
            text="🛒 Cart Items",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        )
        cart_label.pack(pady=(15, 10))

        # Cart treeview
        columns = ("Item", "Type", "Qty", "Price", "Total")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings", height=8)

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

        # Bind double-click to remove item
        self.cart_tree.bind("<Double-1>", self.on_cart_item_double_click)

        # Cart action buttons - MODERN DESIGN
        cart_btn_frame = ctk.CTkFrame(self.cart_frame, fg_color="transparent")
        cart_btn_frame.pack(fill="x", padx=10, pady=(0, 15))

        ctk.CTkButton(
            cart_btn_frame,
            text="✏️ Edit Qty",
            command=self.edit_cart_item,
            width=120,
            height=35,
            fg_color="#ffa500",
            hover_color="#cc8400",
            text_color="#1a1a2e",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            cart_btn_frame,
            text="🗑️ Remove",
            command=self.remove_from_cart,
            width=120,
            height=35,
            fg_color="#ff4757",
            hover_color="#ff3344",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            cart_btn_frame,
            text="🗑️ Clear All",
            command=self.clear_cart,
            width=120,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20
        ).pack(side="right", padx=5)

        # Right panel - Payment - MODERNIZED
        right_panel = ctk.CTkFrame(main_container, width=380, fg_color="#060606", border_width=3, border_color="#8C00FF", corner_radius=20)
        right_panel.pack(side="right", fill="y", padx=(10, 0))
        right_panel.pack_propagate(False)

        # Header with icon
        payment_header = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=15)
        payment_header.pack(fill="x", padx=15, pady=(15, 10))
        
        ctk.CTkLabel(
            payment_header,
            text="💳 Payment Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=12)

        # Subtotal - ENHANCED
        subtotal_frame = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=10)
        subtotal_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            subtotal_frame,
            text="Subtotal:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.subtotal_label = ctk.CTkLabel(
            subtotal_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        )
        self.subtotal_label.pack(side="right", padx=15, pady=10)

        # Service Charge - PROMINENT DISPLAY
        service_cost_frame = ctk.CTkFrame(right_panel, fg_color="#2d2d1a", corner_radius=10, border_width=2, border_color="#ffd93d")
        service_cost_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            service_cost_frame,
            text="💰 Service Charge:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=15, pady=10)
        
        self.service_cost_label = ctk.CTkLabel(
            service_cost_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#ffd93d"
        )
        self.service_cost_label.pack(side="right", padx=15, pady=10)

        # Discount - ENHANCED
        discount_frame = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=10)
        discount_frame.pack(fill="x", padx=15, pady=8)
        
        ctk.CTkLabel(
            discount_frame,
            text="Discount:",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=15, pady=10)
        
        self.discount_entry = ctk.CTkEntry(
            discount_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold"),
            border_color="#8C00FF",
            border_width=2
        )
        self.discount_entry.insert(0, "0")
        self.discount_entry.pack(side="right", padx=15, pady=10)
        self.discount_entry.bind("<KeyRelease>", lambda e: self.calculate_totals())

        # Total - HIGH CONTRAST DISPLAY
        total_frame = ctk.CTkFrame(right_panel, fg_color="#1a1a3e", corner_radius=15, border_width=3, border_color="#00ff88")
        total_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            total_frame,
            text="💵 TOTAL AMOUNT:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=15, pady=15)
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00ff88"
        )
        self.total_label.pack(side="right", padx=15, pady=15)

        # Payment Type Selector - CONDITIONAL VISIBILITY
        self.payment_type_frame = ctk.CTkFrame(right_panel, fg_color="#0d0d1a", corner_radius=10, border_width=2, border_color="#444444")
        # Don't pack yet - will be shown conditionally

        ctk.CTkLabel(
            self.payment_type_frame,
            text="Payment Method:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8C00FF"
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.payment_type_var = ctk.StringVar(value="full")

        payment_radio_frame = ctk.CTkFrame(self.payment_type_frame, fg_color="transparent")
        payment_radio_frame.pack(fill="x", padx=15, pady=(5, 15))

        self.full_payment_radio = ctk.CTkRadioButton(
            payment_radio_frame,
            text="💵 Full Payment",
            variable=self.payment_type_var,
            value="full",
            command=self.on_payment_type_change,
            fg_color="#00ff88",
            hover_color="#00cc6a",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.full_payment_radio.pack(side="left", padx=10)

        self.advance_payment_radio = ctk.CTkRadioButton(
            payment_radio_frame,
            text="💳 Advance Payment",
            variable=self.payment_type_var,
            value="advance",
            command=self.on_payment_type_change,
            fg_color="#ffa500",
            hover_color="#cc8400",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.advance_payment_radio.pack(side="left", padx=10)

        # Advance Payment (only for advance payment type and Frames)
        self.advance_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        # Don't pack initially - will be shown only for Frames
        ctk.CTkLabel(self.advance_frame, text="Advance Amount:", font=ctk.CTkFont(size=13)).pack(side="left")
        self.advance_entry = ctk.CTkEntry(self.advance_frame, width=120, height=35, state="disabled")
        self.advance_entry.insert(0, "0")
        self.advance_entry.pack(side="right")
        self.advance_entry.bind("<KeyRelease>", lambda e: self.calculate_balance())

        # Cash Received (for receipt display only)
        paid_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        paid_frame.pack(fill="x", padx=20, pady=10)
        self.paid_label_widget = ctk.CTkLabel(paid_frame, text="Cash Received:", font=ctk.CTkFont(size=13))
        self.paid_label_widget.pack(side="left")
        self.paid_entry = ctk.CTkEntry(paid_frame, width=120, height=35, placeholder_text="For receipt")
        self.paid_entry.pack(side="right")
        # Cash received does not affect calculations, only for receipt printing

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

        # Action buttons container - LARGE AND TOUCH-FRIENDLY
        action_btn_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_btn_frame.pack(fill="x", padx=15, pady=(20, 25))

        # Generate Bill button - PRIMARY ACTION
        ctk.CTkButton(
            action_btn_frame,
            text="💵 Generate Bill",
            command=self.generate_bill,
            width=160,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=25,
            border_width=3,
            border_color="#8C00FF"
        ).pack(side="left", padx=(0, 10))

        # Clear All button - SECONDARY ACTION
        ctk.CTkButton(
            action_btn_frame,
            text="🔄 Clear All",
            command=self.clear_all,
            width=140,
            height=55,
            fg_color="#ff4757",
            hover_color="#ff3344",
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            border_width=3,
            border_color="#ff4757"
        ).pack(side="left")

    def load_categories(self):
        """Load categories data"""
        categories = self.db_manager.get_all_categories()
        self.categories_map = {cat['category_name']: cat['id'] for cat in categories}
        self.categories_data = {cat['category_name']: cat for cat in categories}

    def on_item_type_change(self, item_type):
        """Handle item type change with conditional Payment Type visibility"""
        self.category_service_cost = 0
        self.selected_category_name = None
        self.selected_category_id = None
        self.free_service_name = None
        self.services_map = {}
        self.frames_map = {}
        
        if item_type == "Services":
            # Services selected
            self.select_category_btn.configure(text="📁 Select Category", state="normal")
            self.select_item_btn.configure(text="🎨 Select Service", state="disabled")
            self.selected_category_frame.pack_forget()
            
            # HIDE Payment Type AND Advance Payment for Services
            self.payment_type_frame.pack_forget()
            self.advance_frame.pack_forget()
            
        else:  # Frames
            # Frames selected
            self.select_category_btn.configure(text="📁 Select Category", state="disabled")
            self.select_item_btn.configure(text="🖼️ Select Frame", state="normal")
            self.selected_category_frame.pack_forget()
            self.load_frames()
            
            # SHOW Payment Type AND Advance Payment for Frames
            self.payment_type_frame.pack(fill="x", padx=20, pady=10, before=self.advance_frame)
            self.advance_frame.pack(fill="x", padx=20, pady=10)
        
        self.calculate_totals()

    def open_category_popup(self):
        """Open popup for category selection - OPTIMIZED WIDER DESIGN"""
        popup = ctk.CTkToplevel(self)
        popup.title("Select Category")
        popup.geometry("650x550")  # Wider popup
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.configure(fg_color="#1a1a2e")
        popup.resizable(False, False)

        def close_popup():
            try:
                popup.grab_release()
            except:
                pass
            popup.destroy()
            self.winfo_toplevel().focus_force()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 325  # Centered
        y = (popup.winfo_screenheight() // 2) - 275
        popup.geometry(f"650x550+{x}+{y}")

        # Title
        ctk.CTkLabel(
            popup,
            text="📁 Select Category",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(20, 15))

        # Scrollable category list
        scroll_frame = ctk.CTkScrollableFrame(
            popup,
            fg_color="#060606",
            border_width=2,
            border_color="#444444",
            corner_radius=10,
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        categories = self.db_manager.get_all_categories()
        
        if not categories:
            ctk.CTkLabel(
                scroll_frame,
                text="No categories available",
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            ).pack(pady=50)
        else:
            for cat in categories:
                cat_frame = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=10)
                cat_frame.pack(fill="x", pady=5, padx=5)

                info_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

                ctk.CTkLabel(
                    info_frame,
                    text=cat['category_name'],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white",
                    anchor="w"
                ).pack(anchor="w")

                # Service cost info - PROMINENT DISPLAY
                service_cost = cat.get('service_cost', 0) or 0
                if service_cost > 0:
                    service_cost_frame = ctk.CTkFrame(info_frame, fg_color="#2d2d1a", corner_radius=8)
                    service_cost_frame.pack(anchor="w", pady=(5, 0), fill="x")
                    
                    ctk.CTkLabel(
                        service_cost_frame,
                        text=f"💰 Service Charge: Rs. {service_cost:,.2f}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#ffd93d",
                        anchor="w"
                    ).pack(anchor="w", padx=8, pady=5)

                # Check for free service (price = 0)
                category_id = cat['id']
                services = self.db_manager.get_services_by_category(category_id)
                free_services = [s for s in services if s.get('price', 0) == 0]
                
                if free_services:
                    free_service_name = free_services[0]['service_name']
                    ctk.CTkLabel(
                        info_frame,
                        text=f"🎁 Free Service Included: {free_service_name}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="#00ff88",
                        anchor="w"
                    ).pack(anchor="w")

                def select_cat(c=cat, fs=free_services):
                    self.on_category_selected(c, fs[0]['service_name'] if fs else None)
                    close_popup()

                ctk.CTkButton(
                    cat_frame,
                    text="Select",
                    width=80,
                    height=35,
                    fg_color="#8C00FF",
                    text_color="white",
                    hover_color="#7300D6",
                    corner_radius=20,
                    command=select_cat
                ).pack(side="right", padx=15, pady=12)

        # Cancel button
        ctk.CTkButton(
            popup,
            text="Cancel",
            width=120,
            height=40,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            command=close_popup
        ).pack(pady=15)

    def on_category_selected(self, category, free_service_name=None):
        """Handle category selection with prominent service cost display"""
        self.selected_category_name = category['category_name']
        self.selected_category_id = category['id']
        self.category_service_cost = float(category.get('service_cost', 0) or 0)
        self.free_service_name = free_service_name

        # Load services for this category
        services = self.db_manager.get_services_by_category(self.selected_category_id)
        self.services_map = {s['service_name']: s for s in services}

        # Update UI with prominent service cost
        self.selected_category_label.configure(text=f"📁 {self.selected_category_name}")
        
        # Display service cost prominently
        if self.category_service_cost > 0:
            self.category_cost_display.configure(
                text=f"💰 Service Cost: Rs. {self.category_service_cost:,.2f}",
                text_color="#ffd93d"
            )
        else:
            self.category_cost_display.configure(text="Service Cost: Rs. 0.00", text_color="#888888")
        
        if free_service_name:
            self.free_service_label.configure(text=f"🎁 Free: {free_service_name}")
        else:
            self.free_service_label.configure(text="")

        self.selected_category_frame.pack(fill="x", padx=15, pady=10, before=self.select_category_btn.master)
        self.select_item_btn.configure(state="normal")
        
        # AUTO-FOCUS: Focus on select item button after category selection
        self.after(100, lambda: self.select_item_btn.focus())
        
        self.calculate_totals()

    def open_item_popup(self):
        """Open popup for item selection - OPTIMIZED WITH INLINE QUANTITY"""
        item_type = self.item_type.get()
        
        popup = ctk.CTkToplevel(self)
        popup.title(f"Select {item_type}")
        popup.geometry("750x600")  # Wider popup for better UX
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.configure(fg_color="#1a1a2e")
        popup.resizable(False, False)

        def close_popup():
            try:
                popup.grab_release()
            except:
                pass
            popup.destroy()
            self.winfo_toplevel().focus_force()

        popup.protocol("WM_DELETE_WINDOW", close_popup)

        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - 375  # Centered
        y = (popup.winfo_screenheight() // 2) - 300
        popup.geometry(f"750x600+{x}+{y}")

        # Title
        title_text = "🎨 Select Service" if item_type == "Services" else "🖼️ Select Frame"
        ctk.CTkLabel(
            popup,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(20, 10))

        # Show selected category info for services
        if item_type == "Services" and self.selected_category_name:
            cat_info = ctk.CTkFrame(popup, fg_color="#1e3a2f", corner_radius=10, border_width=2, border_color="#00ff88")
            cat_info.pack(fill="x", padx=20, pady=(0, 10))
            
            ctk.CTkLabel(
                cat_info,
                text=f"📁 Category: {self.selected_category_name}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#00ff88"
            ).pack(side="left", padx=15, pady=10)

            if self.free_service_name:
                ctk.CTkLabel(
                    cat_info,
                    text=f"🎁 Free: {self.free_service_name}",
                    font=ctk.CTkFont(size=12),
                    text_color="#ffd93d"
                ).pack(side="right", padx=15, pady=10)
        
        # Info label for quantity
        info_label = ctk.CTkLabel(
            popup,
            text="👉 Enter quantity next to each item and click 'Add to Cart'",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        info_label.pack(padx=20, pady=(0, 5))

        # Scrollable item list
        scroll_frame = ctk.CTkScrollableFrame(
            popup,
            fg_color="#060606",
            border_width=2,
            border_color="#444444",
            corner_radius=10,
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if item_type == "Services":
            items = list(self.services_map.values())
        else:
            items = list(self.frames_map.values())

        if not items:
            msg = "No services in this category" if item_type == "Services" else "No frames available"
            ctk.CTkLabel(
                scroll_frame,
                text=msg,
                font=ctk.CTkFont(size=14),
                text_color="#888888"
            ).pack(pady=50)
        else:
            for item in items:
                item_frame = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=12, border_width=2, border_color="#444444")
                item_frame.pack(fill="x", pady=8, padx=8)

                # Left side - Item info
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=15)

                if item_type == "Services":
                    name = item['service_name']
                    price = item.get('price', 0)
                    
                    ctk.CTkLabel(
                        info_frame,
                        text=name,
                        font=ctk.CTkFont(size=15, weight="bold"),
                        text_color="white",
                        anchor="w"
                    ).pack(anchor="w")

                    # Price display - highlight free service
                    if price == 0:
                        price_text = "🎁 FREE (Rs. 0.00)"
                        price_color = "#00ff88"
                    else:
                        price_text = f"💵 Unit Price: Rs. {price:,.2f}"
                        price_color = "#ffd93d"

                    ctk.CTkLabel(
                        info_frame,
                        text=price_text,
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=price_color,
                        anchor="w"
                    ).pack(anchor="w", pady=(3, 0))
                else:
                    name = f"{item['frame_name']} - {item['size']}"
                    price = item.get('price', 0)
                    stock = item.get('quantity', 0)

                    ctk.CTkLabel(
                        info_frame,
                        text=item['frame_name'],
                        font=ctk.CTkFont(size=15, weight="bold"),
                        text_color="white",
                        anchor="w"
                    ).pack(anchor="w")

                    ctk.CTkLabel(
                        info_frame,
                        text=f"Size: {item['size']} | Rs. {price:,.2f}",
                        font=ctk.CTkFont(size=13),
                        text_color="#ffd93d",
                        anchor="w"
                    ).pack(anchor="w", pady=(3, 0))

                    stock_color = "#00ff88" if stock > 5 else "#ff6b6b"
                    ctk.CTkLabel(
                        info_frame,
                        text=f"📦 Stock: {stock}",
                        font=ctk.CTkFont(size=12),
                        text_color=stock_color,
                        anchor="w"
                    ).pack(anchor="w", pady=(2, 0))

                # Right side - Quantity + Add button (INLINE)
                action_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                action_frame.pack(side="right", padx=15, pady=15)
                
                # Quantity label
                ctk.CTkLabel(
                    action_frame,
                    text="Qty:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#888888"
                ).pack(pady=(0, 5))
                
                # Quantity input (inline)
                qty_entry = ctk.CTkEntry(
                    action_frame,
                    width=70,
                    height=40,
                    font=ctk.CTkFont(size=15, weight="bold"),
                    border_color="#8C00FF",
                    border_width=2,
                    justify="center"
                )
                qty_entry.insert(0, "1")  # Default to 1
                qty_entry.pack(pady=(0, 8))

                def add_item(i=item, t=item_type, qe=qty_entry):
                    qty_str = qe.get().strip()
                    if not qty_str or not qty_str.isdigit() or int(qty_str) <= 0:
                        MessageDialog.show_error("Error", "Please enter a valid quantity")
                        return
                    qty = int(qty_str)
                    self.add_item_to_cart(i, t, qty)
                    close_popup()
                    # Visual feedback - briefly highlight cart
                    self.cart_frame.configure(border_color="#00ff88")
                    self.after(500, lambda: self.cart_frame.configure(border_color="#444444"))

                ctk.CTkButton(
                    action_frame,
                    text="➕ Add",
                    width=100,
                    height=45,
                    fg_color="#8C00FF",
                    text_color="#ffffff",
                    hover_color="#7300D6",
                    corner_radius=20,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    border_width=2,
                    border_color="#8C00FF",
                    command=add_item
                ).pack()

        # Cancel button
        ctk.CTkButton(
            popup,
            text="Cancel",
            width=120,
            height=40,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            command=close_popup
        ).pack(pady=15)

    def add_item_to_cart(self, item, item_type, qty):
        """Add selected item to cart - handles duplicates by updating qty"""
        if item_type == "Services":
            item_id = item['id']
            item_name = item['service_name']
            unit_price = item.get('price', 0)
            cart_type = 'Service'
        else:
            # Check stock for frames
            if item.get('quantity', 0) < qty:
                MessageDialog.show_error("Error", f"Insufficient stock. Available: {item.get('quantity', 0)}")
                return
            item_id = item['id']
            item_name = f"{item['frame_name']} - {item['size']}"
            unit_price = item.get('price', 0)
            cart_type = 'Frame'

        # Check for existing item in cart (prevent duplicates)
        for existing_item in self.cart_items:
            if existing_item['id'] == item_id and existing_item['type'] == cart_type:
                # Check stock if adding more frames
                if cart_type == 'Frame':
                    new_qty = existing_item['quantity'] + qty
                    if item.get('quantity', 0) < new_qty:
                        MessageDialog.show_error("Error", f"Insufficient stock. Available: {item.get('quantity', 0)}")
                        return
                # Update existing item quantity
                existing_item['quantity'] += qty
                existing_item['total'] = existing_item['unit_price'] * existing_item['quantity']
                self.refresh_cart()
                self.calculate_totals()
                return

        # Add new item to cart
        cart_item = {
            'type': cart_type,
            'id': item_id,
            'name': item_name,
            'quantity': qty,
            'unit_price': unit_price,
            'total': unit_price * qty
        }

        self.cart_items.append(cart_item)
        self.refresh_cart()
        self.calculate_totals()

    def load_frames(self):
        """Load photo frames"""
        items = self.db_manager.get_all_photo_frames()
        self.frames_map = {f"{item['frame_name']} - {item['size']}": item for item in items}

    def toggle_guest_customer(self):
        """Toggle between guest and registered customer mode"""
        if self.guest_switch_var.get() == "on":
            self.is_guest_customer = True
            self.search_container.pack_forget()
            self.guest_name_container.pack(fill="x", padx=15, pady=5)
            self.clear_selected_customer_display()
            self.hide_suggestions()
            self.no_customer_label.configure(text="🎫 Enter guest customer name above")
        else:
            self.is_guest_customer = False
            self.guest_customer_name = ""
            self.guest_name_container.pack_forget()
            self.search_container.pack(fill="x", padx=15, pady=5)
            self.clear_selected_customer_display()
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
        self.customer_name_label.configure(text=f"🎫 {name}")
        self.customer_mobile_label.configure(text="Guest Customer (Walk-in)")
        self.no_customer_label.pack_forget()
        self.customer_card.pack(fill="x", padx=15, pady=10)

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

    def on_mobile_search_change(self, event=None):
        """Auto-search when typing 5+ digits"""
        mobile = self.mobile_search.get().strip()

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
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons = []

        self.suggestions_frame.pack(fill="x", padx=15, pady=(0, 5))

        for customer in customers[:5]:
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=f"📱 {customer['mobile_number']}  -  {customer['full_name']}",
                font=ctk.CTkFont(size=12),
                fg_color="transparent",
                hover_color="#3d3d6a",
                anchor="w",
                height=35,
                corner_radius=20,
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
        dialog.geometry("500x420")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.resizable(False, False)

        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            self.winfo_toplevel().focus_force()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 210
        dialog.geometry(f"500x420+{x}+{y}")

        main_scroll = ctk.CTkScrollableFrame(
            dialog,
            fg_color="#1a1a2e",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        main_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        content_frame = ctk.CTkFrame(main_scroll, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            content_frame,
            text="➕ Add New Customer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(25, 30))

        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=35)

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

            existing = self.db_manager.get_customer_by_mobile(mobile)
            if existing:
                MessageDialog.show_error("Error", "Customer with this mobile already exists")
                return

            customer_id = self.db_manager.add_customer(name, mobile)
            if customer_id:
                MessageDialog.show_success("Success", "Customer added successfully")
                close_dialog()
                self.mobile_search.delete(0, 'end')
                self.mobile_search.insert(0, mobile)
                self.search_customer()
            else:
                MessageDialog.show_error("Error", "Failed to add customer")

        btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        btn_frame.pack(pady=(10, 30))

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=close_dialog,
            width=130,
            height=45,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="➕ Add Customer",
            command=save_customer,
            width=160,
            height=45,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10)

        name_entry.focus()

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

    def edit_cart_item(self):
        """Edit quantity of selected cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select an item to edit")
            return

        index = self.cart_tree.index(selection[0])
        item = self.cart_items[index]

        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Quantity")
        dialog.geometry("350x200")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.resizable(False, False)

        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            self.winfo_toplevel().focus_force()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 175
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f"350x200+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text=f"Edit: {item['name']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=(20, 15))

        qty_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        qty_frame.pack(pady=10)

        ctk.CTkLabel(qty_frame, text="New Quantity:", font=ctk.CTkFont(size=13)).pack(side="left", padx=10)
        qty_entry = ctk.CTkEntry(qty_frame, width=100, height=35)
        qty_entry.insert(0, str(item['quantity']))
        qty_entry.pack(side="left", padx=10)

        def save_qty():
            qty_str = qty_entry.get().strip()
            if not qty_str or not qty_str.isdigit() or int(qty_str) <= 0:
                MessageDialog.show_error("Error", "Please enter a valid quantity (positive integer)")
                return
            new_qty = int(qty_str)

            # Check stock for frames
            if item['type'] == 'Frame':
                frame_data = self.db_manager.get_photo_frame_by_id(item['id'])
                if frame_data and frame_data.get('quantity', 0) < new_qty:
                    MessageDialog.show_error("Error", f"Insufficient stock. Available: {frame_data.get('quantity', 0)}")
                    return

            # Update quantity and total
            item['quantity'] = new_qty
            item['total'] = item['unit_price'] * new_qty
            self.refresh_cart()
            self.calculate_totals()
            close_dialog()

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=close_dialog,
            width=100,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Save",
            command=save_qty,
            width=100,
            height=35,
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)

        qty_entry.focus()
        qty_entry.select_range(0, "end")

    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            return
        self.cart_items = []
        self.refresh_cart()
        self.calculate_totals()

    def on_cart_item_double_click(self, event):
        """Handle double-click on cart item to remove it"""
        selection = self.cart_tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_values = self.cart_tree.item(item_id, 'values')
        if not item_values:
            return

        item_name = item_values[0]

        # Show confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Remove Item")
        dialog.geometry("350x150")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        dialog.resizable(False, False)

        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            self.winfo_toplevel().focus_force()

        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 175
        y = (dialog.winfo_screenheight() // 2) - 75
        dialog.geometry(f"350x150+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text=f"Remove '{item_name}' from cart?",
            font=ctk.CTkFont(size=14),
            wraplength=300
        ).pack(pady=(25, 20))

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        def confirm_remove():
            index = self.cart_tree.index(item_id)
            if 0 <= index < len(self.cart_items):
                self.cart_items.pop(index)
                self.refresh_cart()
                self.calculate_totals()
            close_dialog()

        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=close_dialog,
            width=100,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Remove",
            command=confirm_remove,
            width=100,
            height=35,
            fg_color="#ff4757",
            hover_color="#ff3344",
            corner_radius=20
        ).pack(side="left", padx=10)

    def on_payment_type_change(self):
        """Handle payment type change"""
        self.payment_type = self.payment_type_var.get()

        if self.payment_type == "full":
            # Full payment - disable advance entry and set to 0
            self.advance_entry.configure(state="normal")
            self.advance_entry.delete(0, "end")
            self.advance_entry.insert(0, "0")
            self.advance_entry.configure(state="disabled")
        else:
            # Advance payment - enable advance entry
            self.advance_entry.configure(state="normal")
            self.advance_entry.delete(0, "end")
            self.advance_entry.insert(0, "")
            self.advance_entry.focus()

        self.calculate_balance()

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

        service_cost = 0
        if self.category_service_cost > 0 and any(item['type'] == 'Service' for item in self.cart_items):
            service_cost = self.category_service_cost

        total = max(0, subtotal + service_cost - discount)

        self.subtotal_label.configure(text=f"LKR {subtotal:.2f}")
        self.service_cost_label.configure(text=f"LKR {service_cost:.2f}")
        self.total_label.configure(text=f"LKR {total:.2f}")

        self.calculate_balance()

    def calculate_balance(self):
        """Calculate remaining balance based on payment type"""
        total_str = self.total_label.cget("text").replace("LKR ", "").replace(",", "")
        total = float(total_str) if total_str else 0

        if self.payment_type == "full":
            # Full payment - no balance remaining
            remaining = 0.0
            paid_amount = total
        else:
            # Advance payment - deduct advance from total
            advance_str = self.advance_entry.get().strip()
            advance = 0.0
            if advance_str and self.validate_number(advance_str, True):
                advance = float(advance_str)

            # Validate advance doesn't exceed total
            if advance > total:
                self.advance_entry.delete(0, "end")
                self.advance_entry.insert(0, str(total))
                advance = total

            remaining = max(0, total - advance)
            paid_amount = advance

        self.balance_label.configure(text=f"LKR {remaining:.2f}")

        if remaining > 0:
            self.balance_label.configure(text_color="#ff6b6b")
        else:
            self.balance_label.configure(text_color="#00ff88")

    def generate_bill(self):
        """Generate thermal bill receipt for normal sales (NO booking)"""
        # Validate customer selection
        if self.is_guest_customer:
            if not self.guest_customer_name:
                MessageDialog.show_error("Error", "Please enter guest customer name")
                return
        else:
            if not self.selected_customer:
                MessageDialog.show_error("Error", "Please select a customer")
                return

        # Validate cart has items
        if not self.cart_items:
            MessageDialog.show_error("Error", "Please add items to cart")
            return

        # Calculate totals
        subtotal = sum(item['total'] for item in self.cart_items)
        discount = float(self.discount_entry.get() or 0)

        service_charge = 0
        if self.category_service_cost > 0 and any(item['type'] == 'Service' for item in self.cart_items):
            service_charge = self.category_service_cost

        total = max(0, subtotal + service_charge - discount)

        # Get cash given (optional, for display only)
        cash_given_str = self.paid_entry.get().strip()
        cash_given = 0.0
        if cash_given_str:
            if not self.validate_number(cash_given_str, True):
                MessageDialog.show_error("Error", "Please enter valid cash amount")
                return
            cash_given = float(cash_given_str)

        # Calculate advance amount and balance due based on payment type
        advance_amount = 0.0
        balance_due = 0.0
        
        if self.payment_type == "advance":
            # Advance payment - validate advance amount
            advance_str = self.advance_entry.get().strip()
            if not advance_str or not self.validate_number(advance_str, True):
                MessageDialog.show_error("Error", "Please enter valid advance payment amount")
                return
            
            advance_amount = float(advance_str)
            
            if advance_amount <= 0:
                MessageDialog.show_error("Error", "Advance payment must be greater than 0")
                return
            
            if advance_amount > total:
                MessageDialog.show_error("Error", "Advance payment cannot exceed total amount")
                return
            
            balance_due = total - advance_amount
        else:
            # Full payment - no advance or balance
            advance_amount = total
            balance_due = 0.0

        bill_number = self.db_manager.generate_bill_number()

        if self.is_guest_customer:
            customer_id = None
            guest_name = self.guest_customer_name
        else:
            customer_id = self.selected_customer['id']
            guest_name = None

        # Create bill in database
        bill_id = self.db_manager.create_bill(
            bill_number,
            customer_id,
            subtotal,
            discount,
            total,
            self.auth_manager.get_user_id(),
            service_charge,
            cash_given,
            guest_name,
            advance_amount,
            balance_due
        )

        if not bill_id:
            MessageDialog.show_error("Error", "Failed to create bill")
            return

        # Add items to bill
        for item in self.cart_items:
            buying_price = 0
            if item['type'] == 'Frame':
                frame_data = self.db_manager.get_photo_frame_by_id(item['id'])
                if frame_data:
                    buying_price = frame_data.get('buying_price', 0) or 0

            self.db_manager.add_bill_item(
                bill_id,
                item['type'],
                item['id'],
                item['name'],
                item['quantity'],
                item['unit_price'],
                item['total'],
                buying_price * item['quantity']
            )

            # Update frame stock
            if item['type'] == 'Frame':
                self.db_manager.update_frame_quantity(item['id'], -item['quantity'])

        # Add service charge as separate item
        if service_charge > 0 and self.selected_category_name:
            self.db_manager.add_bill_item(
                bill_id,
                'CategoryService',
                0,
                f"Service Charge - {self.selected_category_name}",
                1,
                service_charge,
                service_charge,
                0
            )

        # Generate PDF bill
        bill_data = self.db_manager.get_bill_by_id(bill_id)
        items_data = self.db_manager.get_bill_items(bill_id)

        if self.is_guest_customer:
            customer_data = {
                'full_name': self.guest_customer_name,
                'mobile_number': 'Guest Customer'
            }
        else:
            customer_data = self.selected_customer

        try:
            pdf_path = self.bill_generator.generate_bill(
                bill_data,
                items_data,
                customer_data
            )

            MessageDialog.show_success("Success", f"Bill {bill_number} generated successfully!")
            self.bill_generator.open_bill(pdf_path)
            self.clear_all()

        except Exception as e:
            MessageDialog.show_error("Error", f"Failed to generate bill PDF: {str(e)}")

    def generate_invoice_from_booking(self, booking_id):
        """Generate A4 invoice for a booking - called from booking frame"""
        # This method can be called externally when completing a booking
        # Load booking data and generate invoice
        pass

    def clear_all(self):
        """Clear all fields"""
        self.selected_customer = None
        self.is_guest_customer = False
        self.guest_customer_name = ""
        self.cart_items = []
        self.category_service_cost = 0
        self.selected_category_name = None
        self.selected_category_id = None
        self.free_service_name = None
        self.payment_type = "full"
        self.booking_reference = None
        self.mobile_search.delete(0, 'end')
        self.guest_name_entry.delete(0, 'end')

        self.guest_switch_var.set("off")
        self.guest_name_container.pack_forget()
        self.search_container.pack(fill="x", padx=15, pady=5)
        self.clear_selected_customer()
        self.no_customer_label.configure(text="🔍 Search customer by mobile number or add a new one")

        self.discount_entry.delete(0, 'end')
        self.discount_entry.insert(0, "0")

        # Reset payment type to full
        self.payment_type_var.set("full")
        self.advance_entry.configure(state="normal")
        self.advance_entry.delete(0, 'end')
        self.advance_entry.insert(0, "0")
        self.advance_entry.configure(state="disabled")

        self.paid_entry.delete(0, 'end')

        self.item_type.set("Service")
        self.selected_category_frame.pack_forget()
        self.selected_category_label.configure(text="No category selected")
        self.free_service_label.configure(text="")
        self.select_category_btn.configure(state="normal")
        self.select_item_btn.configure(state="disabled")
        self.services_map = {}
        self.frames_map = {}
        self.refresh_cart()
        self.calculate_totals()
    
    def validate_mobile(self, mobile):
        """Validate mobile number format"""
        return mobile.isdigit() and len(mobile) == 10
    
    def validate_number(self, value, allow_float=False):
        """Validate numeric input"""
        try:
            if allow_float:
                float(value)
            else:
                int(value)
            return True
        except ValueError:
            return False
