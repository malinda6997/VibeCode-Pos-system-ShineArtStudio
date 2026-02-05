import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, date
from tkcalendar import DateEntry
from ui.components import Toast
from services.staff_report_generator import StaffReportGenerator


class StaffReportsFrame(ctk.CTkFrame):
    """Admin frame for viewing and generating staff daily work reports"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.report_generator = StaffReportGenerator()
        self.selected_user_id = None
        self.selected_user_data = None
        
        self.create_ui()
        self.load_users()
    
    def create_ui(self):
        """Create the staff reports UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            header_content,
            text="📋 Staff Daily Reports",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            header_content,
            text="View and download staff daily work records",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle_label.pack(side="left", padx=(20, 0))
        
        # Controls section
        controls_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        controls_frame.pack(fill="x", padx=20, pady=10)
        
        controls_content = ctk.CTkFrame(controls_frame, fg_color="transparent")
        controls_content.pack(fill="x", padx=20, pady=15)
        
        # Staff selection
        staff_label = ctk.CTkLabel(
            controls_content,
            text="Select Staff:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        staff_label.pack(side="left")
        
        self.staff_dropdown = ctk.CTkComboBox(
            controls_content,
            values=["Loading..."],
            width=250,
            height=35,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=12),
            fg_color="#0d0d1a",
            border_color="#333355",
            button_color="#8C00FF",
            button_hover_color="#7300D6",
            command=self.on_staff_selected,
            corner_radius=15
        )
        self.staff_dropdown.pack(side="left", padx=(10, 30))
        
        # Date selection
        date_label = ctk.CTkLabel(
            controls_content,
            text="Select Date:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        )
        date_label.pack(side="left")
        
        # Date entry with calendar
        date_frame = ctk.CTkFrame(controls_content, fg_color="transparent")
        date_frame.pack(side="left", padx=(10, 30))
        
        self.date_entry = DateEntry(
            date_frame,
            width=15,
            background='#1a1a2e',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Segoe UI', 11)
        )
        self.date_entry.pack()
        
        # View button
        view_btn = ctk.CTkButton(
            controls_content,
            text="📊 View Records",
            command=self.view_records,
            width=140,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        view_btn.pack(side="left", padx=(0, 10))
        
        # Download PDF button
        self.download_btn = ctk.CTkButton(
            controls_content,
            text="📄 Download PDF",
            command=self.download_report,
            width=140,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            font=ctk.CTkFont(size=13, weight="bold"),
            corner_radius=20
        )
        self.download_btn.pack(side="left")
        
        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - Summary cards
        left_panel = ctk.CTkFrame(content_frame, fg_color="#1a1a2e", corner_radius=10, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        summary_title = ctk.CTkLabel(
            left_panel,
            text="📈 Daily Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        summary_title.pack(pady=(20, 15), padx=20, anchor="w")
        
        # Summary cards container
        self.summary_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        self.summary_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # Initial summary display
        self.create_summary_cards({})
        
        # Right panel - Details tables
        right_panel = ctk.CTkFrame(content_frame, fg_color="#1a1a2e", corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Tabs for different record types
        self.tab_view = ctk.CTkTabview(
            right_panel,
            fg_color="#1a1a2e",
            segmented_button_fg_color="#0d0d1a",
            segmented_button_selected_color="#8C00FF",
            segmented_button_selected_hover_color="#7300D6",
            segmented_button_unselected_color="#333355",
            segmented_button_unselected_hover_color="#444477"
        )
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tab_invoices = self.tab_view.add("💳 Invoices")
        self.tab_bookings = self.tab_view.add("📅 Bookings")
        self.tab_customers = self.tab_view.add("👥 Customers")
        
        # Create tables for each tab
        self.create_invoices_table()
        self.create_bookings_table()
        self.create_customers_table()
    
    def create_summary_cards(self, summary: dict):
        """Create summary stat cards"""
        # Clear existing
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        cards_data = [
            ("💳", "Invoices Created", summary.get('invoice_count', 0), "#27ae60"),
            ("💰", "Invoice Amount", f"LKR {summary.get('total_invoice_amount', 0):,.2f}", "#27ae60"),
            ("💵", "Payments Received", f"LKR {summary.get('total_paid', 0):,.2f}", "#2ecc71"),
            ("📅", "Bookings Created", summary.get('booking_count', 0), "#3498db"),
            ("📊", "Booking Value", f"LKR {summary.get('total_booking_amount', 0):,.2f}", "#3498db"),
            ("💎", "Advance Collected", f"LKR {summary.get('total_advance', 0):,.2f}", "#9b59b6"),
        ]
        
        for icon, label, value, color in cards_data:
            card = ctk.CTkFrame(self.summary_frame, fg_color="#0d0d1a", corner_radius=8)
            card.pack(fill="x", pady=5)
            
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="x", padx=12, pady=10)
            
            # Icon
            icon_label = ctk.CTkLabel(
                card_content,
                text=icon,
                font=ctk.CTkFont(size=20),
                width=30
            )
            icon_label.pack(side="left")
            
            # Text container
            text_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))
            
            label_text = ctk.CTkLabel(
                text_frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color="#888888",
                anchor="w"
            )
            label_text.pack(anchor="w")
            
            value_text = ctk.CTkLabel(
                text_frame,
                text=str(value),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=color,
                anchor="w"
            )
            value_text.pack(anchor="w")
    
    def create_invoices_table(self):
        """Create invoices table"""
        # Table header
        header_frame = ctk.CTkFrame(self.tab_invoices, fg_color="#0d0d1a", corner_radius=10, height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="🧾 Invoice Records",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8C00FF"
        ).pack(side="left", padx=15, pady=8)
        
        # Table container
        table_container = ctk.CTkFrame(self.tab_invoices, fg_color="#1a1a2e", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ('invoice_no', 'customer', 'total', 'paid', 'balance', 'time')
        
        self.invoices_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=12
        )
        
        self.invoices_tree.heading('invoice_no', text='🔢 Invoice #')
        self.invoices_tree.heading('customer', text='👤 Customer')
        self.invoices_tree.heading('total', text='💰 Total')
        self.invoices_tree.heading('paid', text='✅ Paid')
        self.invoices_tree.heading('balance', text='⏳ Balance')
        self.invoices_tree.heading('time', text='🕐 Time')
        
        self.invoices_tree.column('invoice_no', width=100, anchor='center')
        self.invoices_tree.column('customer', width=150, anchor='w')
        self.invoices_tree.column('total', width=100, anchor='e')
        self.invoices_tree.column('paid', width=100, anchor='e')
        self.invoices_tree.column('balance', width=100, anchor='e')
        self.invoices_tree.column('time', width=80, anchor='center')
        
        # Configure row tags
        self.invoices_tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.invoices_tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.invoices_tree.yview)
        self.invoices_tree.configure(yscrollcommand=scrollbar.set)
        
        self.invoices_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
    
    def create_bookings_table(self):
        """Create bookings table"""
        # Table header
        header_frame = ctk.CTkFrame(self.tab_bookings, fg_color="#0d0d1a", corner_radius=10, height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="📅 Booking Records",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8C00FF"
        ).pack(side="left", padx=15, pady=8)
        
        # Table container
        table_container = ctk.CTkFrame(self.tab_bookings, fg_color="#1a1a2e", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ('customer', 'category', 'date', 'amount', 'advance', 'status')
        
        self.bookings_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=12
        )
        
        self.bookings_tree.heading('customer', text='👤 Customer')
        self.bookings_tree.heading('category', text='📁 Category')
        self.bookings_tree.heading('date', text='📅 Date')
        self.bookings_tree.heading('amount', text='💰 Amount')
        self.bookings_tree.heading('advance', text='💵 Advance')
        self.bookings_tree.heading('status', text='📊 Status')
        
        self.bookings_tree.column('customer', width=150, anchor='w')
        self.bookings_tree.column('category', width=120, anchor='w')
        self.bookings_tree.column('date', width=100, anchor='center')
        self.bookings_tree.column('amount', width=100, anchor='e')
        self.bookings_tree.column('advance', width=100, anchor='e')
        self.bookings_tree.column('status', width=80, anchor='center')
        
        # Configure row tags
        self.bookings_tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.bookings_tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscrollcommand=scrollbar.set)
        
        self.bookings_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
    
    def create_customers_table(self):
        """Create customers table"""
        # Table header
        header_frame = ctk.CTkFrame(self.tab_customers, fg_color="#0d0d1a", corner_radius=10, height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="👥 Customer Records",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#8C00FF"
        ).pack(side="left", padx=15, pady=8)
        
        # Table container
        table_container = ctk.CTkFrame(self.tab_customers, fg_color="#1a1a2e", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ('name', 'mobile', 'added_at')
        
        self.customers_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=12
        )
        
        self.customers_tree.heading('name', text='👤 Customer Name')
        self.customers_tree.heading('mobile', text='📱 Mobile Number')
        self.customers_tree.heading('added_at', text='📅 Added At')
        
        self.customers_tree.column('name', width=200, anchor='w')
        self.customers_tree.column('mobile', width=150, anchor='center')
        self.customers_tree.column('added_at', width=150, anchor='center')
        
        # Configure row tags
        self.customers_tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.customers_tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
    
    def load_users(self):
        """Load all users into dropdown"""
        users = self.db_manager.get_all_users_for_reports()
        self.users_map = {}
        
        user_options = []
        for user in users:
            display_name = f"{user['full_name']} ({user['role']})"
            user_options.append(display_name)
            self.users_map[display_name] = user
        
        if user_options:
            self.staff_dropdown.configure(values=user_options)
            self.staff_dropdown.set(user_options[0])
            self.selected_user_data = self.users_map[user_options[0]]
            self.selected_user_id = self.selected_user_data['id']
        else:
            self.staff_dropdown.configure(values=["No users found"])
            self.staff_dropdown.set("No users found")
    
    def on_staff_selected(self, selection):
        """Handle staff selection change"""
        if selection in self.users_map:
            self.selected_user_data = self.users_map[selection]
            self.selected_user_id = self.selected_user_data['id']
    
    def view_records(self):
        """View records for selected staff and date"""
        if not self.selected_user_id:
            Toast.show_toast(self, "Error", "Please select a staff member.", "error")
            return
        
        selected_date = self.date_entry.get_date().strftime('%Y-%m-%d')
        
        # Get records
        invoices = self.db_manager.get_staff_invoices_by_date(self.selected_user_id, selected_date)
        bookings = self.db_manager.get_staff_bookings_by_date(self.selected_user_id, selected_date)
        customers = self.db_manager.get_staff_customers_by_date(self.selected_user_id, selected_date)
        
        # Update summary
        summary = self.db_manager.get_staff_daily_summary(self.selected_user_id, selected_date)
        self.create_summary_cards(summary)
        
        # Update invoices table
        for item in self.invoices_tree.get_children():
            self.invoices_tree.delete(item)
        
        for inv in invoices:
            created_time = inv.get('created_at', '')
            if ' ' in created_time:
                created_time = created_time.split(' ')[1][:5]
            
            self.invoices_tree.insert('', 'end', values=(
                inv.get('invoice_number', '-'),
                inv.get('customer_name', '-'),
                f"{inv.get('total_amount', 0):,.2f}",
                f"{inv.get('paid_amount', 0):,.2f}",
                f"{inv.get('balance_amount', 0):,.2f}",
                created_time
            ))
        
        # Update bookings table
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)
        
        for b in bookings:
            self.bookings_tree.insert('', 'end', values=(
                b.get('customer_name', '-'),
                b.get('photoshoot_category', '-'),
                b.get('booking_date', '-'),
                f"{b.get('full_amount', 0):,.2f}",
                f"{b.get('advance_payment', 0):,.2f}",
                b.get('status', '-')
            ))
        
        # Update customers table
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        for c in customers:
            created_at = c.get('created_at', '-')
            self.customers_tree.insert('', 'end', values=(
                c.get('full_name', '-'),
                c.get('mobile_number', '-'),
                created_at
            ))
        
        # Store current records for PDF generation
        self.current_records = {
            'invoices': invoices,
            'bookings': bookings,
            'customers': customers
        }
        
        Toast.show_toast(self, "Records Loaded", f"Showing records for {selected_date}", "success")
    
    def download_report(self):
        """Generate and download PDF report"""
        if not self.selected_user_id or not self.selected_user_data:
            Toast.show_toast(self, "Error", "Please select a staff member.", "error")
            return
        
        if not hasattr(self, 'current_records'):
            Toast.show_toast(self, "Error", "Please view records first.", "warning")
            return
        
        selected_date = self.date_entry.get_date().strftime('%Y-%m-%d')
        
        try:
            filepath = self.report_generator.generate_daily_report(
                self.selected_user_data,
                selected_date,
                self.current_records
            )
            
            # Open the PDF
            self.report_generator.open_report(filepath)
            Toast.show_toast(self, "Success", "PDF report generated successfully!", "success")
            
        except Exception as e:
            Toast.show_toast(self, "Error", f"Failed to generate report: {str(e)}", "error")
