import customtkinter as ctk
from services.dashboard_service import DashboardService
from datetime import datetime


class DashboardFrame(ctk.CTkFrame):
    """Dashboard page with statistics and summary cards"""
    
    def __init__(self, parent, auth_manager, db_manager, main_app=None):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.dashboard_service = DashboardService()
        self.main_app = main_app
        
        self.create_widgets()
        self.load_stats()
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.auth_manager.is_admin()
    
    def navigate_to(self, page: str):
        """Navigate to another page via main app"""
        if self.main_app:
            self.main_app.navigate_to(page)
    
    def create_widgets(self):
        """Create dashboard widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Date display
        date_label = ctk.CTkLabel(
            header_frame,
            text=datetime.now().strftime("%A, %B %d, %Y"),
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        date_label.pack(side="right")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.load_stats,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        )
        refresh_btn.pack(side="right", padx=20)
        
        # Welcome message
        user = self.auth_manager.get_current_user()
        welcome = ctk.CTkLabel(
            self,
            text=f"Welcome back, {user['full_name']}! 👋",
            font=ctk.CTkFont(size=16),
            text_color="#aaaaaa"
        )
        welcome.pack(anchor="w", padx=30, pady=(0, 10))
        
        # Quick actions at the top
        actions_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        actions_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        actions_btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Quick action buttons with navigation commands
        new_invoice_btn = ctk.CTkButton(
            actions_btn_frame,
            text="➕ New Invoice",
            width=150,
            height=40,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.navigate_to("billing")
        )
        new_invoice_btn.pack(side="left", padx=5)
        
        add_customer_btn = ctk.CTkButton(
            actions_btn_frame,
            text="👤 Add Customer",
            width=150,
            height=40,
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00cc6a",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.navigate_to("customers")
        )
        add_customer_btn.pack(side="left", padx=5)
        
        new_booking_btn = ctk.CTkButton(
            actions_btn_frame,
            text="📅 New Booking",
            width=150,
            height=40,
            fg_color="#c44dff",
            text_color="#1a1a2e",
            hover_color="#a33dd6",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.navigate_to("bookings")
        )
        new_booking_btn.pack(side="left", padx=5)
        
        add_frame_btn = ctk.CTkButton(
            actions_btn_frame,
            text="🖼️ Add Frame",
            width=150,
            height=40,
            fg_color="#ffd93d",
            text_color="#1a1a2e",
            hover_color="#e6c235",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.navigate_to("frames")
        )
        add_frame_btn.pack(side="left", padx=5)
        
        # Scrollable stats cards container
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Stats cards container
        self.cards_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True)
        
        # Store scroll_container reference for staff widgets
        self.scroll_container = scroll_container
        
        # ==================== Financial Cards (Admin Only) ====================
        if self.is_admin():
            # Admin header for financial section
            admin_header = ctk.CTkFrame(self.cards_frame, fg_color="#1e3a2f", corner_radius=10)
            admin_header.pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(
                admin_header,
                text="💰 Financial Overview (Admin Only)",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#00ff88"
            ).pack(pady=10, padx=15, anchor="w")
            
            # Row 1 - Financial stats (Admin Only)
            row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            row1.pack(fill="x", pady=10)
            
            self.today_sales_card = self.create_stat_card(
                row1, "Today's Sales", "LKR 0.00", "💰", "#00d4ff"
            )
            self.today_sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            self.pending_balance_card = self.create_stat_card(
                row1, "Pending Balances", "LKR 0.00", "⏳", "#ff6b6b"
            )
            self.pending_balance_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.weekly_sales_card = self.create_stat_card(
                row1, "Weekly Sales", "LKR 0.00", "📈", "#4ecdc4"
            )
            self.weekly_sales_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            # Row 2 - More financial stats
            row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            row2.pack(fill="x", pady=10)
            
            self.monthly_sales_card = self.create_stat_card(
                row2, "Monthly Sales", "LKR 0.00", "📊", "#45b7d1"
            )
            self.monthly_sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            # Placeholder cards to maintain layout
            placeholder_frame1 = ctk.CTkFrame(row2, fg_color="transparent", height=140)
            placeholder_frame1.pack(side="left", fill="both", expand=True, padx=10)
            
            placeholder_frame2 = ctk.CTkFrame(row2, fg_color="transparent", height=140)
            placeholder_frame2.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # ==================== General Stats (Both Admin and Staff) ====================
        general_header = ctk.CTkFrame(self.cards_frame, fg_color="#1e1e3f", corner_radius=10)
        general_header.pack(fill="x", pady=(10, 10))
        
        ctk.CTkLabel(
            general_header,
            text="📊 General Statistics",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00d4ff"
        ).pack(pady=10, padx=15, anchor="w")
        
        # Row 3 - General stats (visible to all)
        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=10)
        
        self.today_invoices_card = self.create_stat_card(
            row3, "Today's Invoices", "0", "📄", "#00ff88"
        )
        self.today_invoices_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.total_invoices_card = self.create_stat_card(
            row3, "Total Invoices", "0", "📋", "#96ceb4"
        )
        self.total_invoices_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.total_customers_card = self.create_stat_card(
            row3, "Total Customers", "0", "👥", "#ffd93d"
        )
        self.total_customers_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Row 4 - More general stats
        row4 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row4.pack(fill="x", pady=10)
        
        self.pending_bookings_card = self.create_stat_card(
            row4, "Pending Bookings", "0", "📅", "#c44dff"
        )
        self.pending_bookings_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.low_stock_card = self.create_stat_card(
            row4, "Low Stock Items", "0", "⚠️", "#ff9f43"
        )
        self.low_stock_card.pack(side="left", fill="both", expand=True, padx=10)
        
        # Placeholder for layout balance
        placeholder_row4 = ctk.CTkFrame(row4, fg_color="transparent", height=140)
        placeholder_row4.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Admin-only section: Photo Frame Profit Tracking
        if self.is_admin():
            # Section header
            profit_header = ctk.CTkFrame(scroll_container, fg_color="#1e1e3f", corner_radius=10)
            profit_header.pack(fill="x", pady=(20, 10))
            
            ctk.CTkLabel(
                profit_header,
                text="📊 Photo Frame Profit Analysis (Admin Only)",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#00d4ff"
            ).pack(pady=15, padx=20, anchor="w")
            
            # Row 5 - Frame profit stats (Admin only)
            row5 = ctk.CTkFrame(scroll_container, fg_color="transparent")
            row5.pack(fill="x", pady=10)
            
            self.frames_sold_card = self.create_stat_card(
                row5, "Total Frames Sold", "0", "🖼️", "#00d4ff"
            )
            self.frames_sold_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            self.buying_cost_card = self.create_stat_card(
                row5, "Total Buying Cost", "LKR 0.00", "💵", "#ff9f43"
            )
            self.buying_cost_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.selling_amount_card = self.create_stat_card(
                row5, "Total Selling Amount", "LKR 0.00", "💳", "#4ecdc4"
            )
            self.selling_amount_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.net_profit_card = self.create_stat_card(
                row5, "Net Frame Profit", "LKR 0.00", "💎", "#00ff88"
            )
            self.net_profit_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            # Row 6 - Today and Monthly Frame Profit
            row6 = ctk.CTkFrame(scroll_container, fg_color="transparent")
            row6.pack(fill="x", pady=10)
            
            self.today_frame_profit_card = self.create_stat_card(
                row6, "Today's Frame Profit", "LKR 0.00", "📅", "#c44dff"
            )
            self.today_frame_profit_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            self.monthly_frame_profit_card = self.create_stat_card(
                row6, "Monthly Frame Profit", "LKR 0.00", "📆", "#45b7d1"
            )
            self.monthly_frame_profit_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.monthly_frames_sold_card = self.create_stat_card(
                row6, "Monthly Frames Sold", "0", "🛒", "#ffd93d"
            )
            self.monthly_frames_sold_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # ==================== Staff Widgets Section ====================
        if not self.is_admin():
            # Staff widgets header
            staff_header = ctk.CTkFrame(scroll_container, fg_color="#1e3a2f", corner_radius=10)
            staff_header.pack(fill="x", pady=(20, 10))
            
            ctk.CTkLabel(
                staff_header,
                text="📋 Quick Overview",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#00ff88"
            ).pack(pady=15, padx=20, anchor="w")
            
            # Three-column widget layout
            widgets_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
            widgets_row.pack(fill="x", pady=10)
            widgets_row.grid_columnconfigure((0, 1, 2), weight=1, uniform="widgets")
            
            # Upcoming Bookings Widget
            self.bookings_widget = ctk.CTkFrame(widgets_row, fg_color="#1e1e3f", corner_radius=15)
            self.bookings_widget.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            
            bookings_header = ctk.CTkFrame(self.bookings_widget, fg_color="#2d2d5a", corner_radius=10)
            bookings_header.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                bookings_header,
                text="📅 Upcoming Bookings",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#c44dff"
            ).pack(pady=8, padx=10, anchor="w")
            
            self.bookings_list_frame = ctk.CTkFrame(self.bookings_widget, fg_color="transparent")
            self.bookings_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Recent Customers Widget
            self.customers_widget = ctk.CTkFrame(widgets_row, fg_color="#1e1e3f", corner_radius=15)
            self.customers_widget.grid(row=0, column=1, sticky="nsew", padx=5)
            
            customers_header = ctk.CTkFrame(self.customers_widget, fg_color="#2d2d5a", corner_radius=10)
            customers_header.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                customers_header,
                text="👥 Recent Customers",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ffd93d"
            ).pack(pady=8, padx=10, anchor="w")
            
            self.customers_list_frame = ctk.CTkFrame(self.customers_widget, fg_color="transparent")
            self.customers_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Frame Stock Widget
            self.stock_widget = ctk.CTkFrame(widgets_row, fg_color="#1e1e3f", corner_radius=15)
            self.stock_widget.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
            
            stock_header = ctk.CTkFrame(self.stock_widget, fg_color="#2d2d5a", corner_radius=10)
            stock_header.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkLabel(
                stock_header,
                text="🖼️ Frame Stock",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#ff9f43"
            ).pack(pady=8, padx=10, anchor="w")
            
            self.stock_list_frame = ctk.CTkFrame(self.stock_widget, fg_color="transparent")
            self.stock_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        

    
    def create_stat_card(self, parent, title: str, value: str, icon: str, 
                        color: str) -> ctk.CTkFrame:
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color="#1e1e3f", corner_radius=15, height=140)
        card.pack_propagate(False)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=30),
        )
        icon_label.pack(anchor="w", padx=20, pady=(20, 5))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        title_label.pack(anchor="w", padx=20)
        
        # Value
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=color
        )
        value_label.pack(anchor="w", padx=20, pady=(5, 20))
        
        # Store reference for updating
        card.value_label = value_label
        
        return card
    
    def load_stats(self):
        """Load dashboard statistics"""
        # Load appropriate stats based on user role
        if self.is_admin():
            stats = self.dashboard_service.get_admin_dashboard_stats()
        else:
            stats = self.dashboard_service.get_dashboard_stats()
        
        # Update general stats (visible to all)
        self.today_invoices_card.value_label.configure(
            text=str(stats['today_invoices'])
        )
        self.total_invoices_card.value_label.configure(
            text=str(stats['total_invoices'])
        )
        self.total_customers_card.value_label.configure(
            text=str(stats['total_customers'])
        )
        self.pending_bookings_card.value_label.configure(
            text=str(stats['pending_bookings'])
        )
        self.low_stock_card.value_label.configure(
            text=str(stats['low_stock_frames'])
        )
        
        # Update admin-only financial cards
        if self.is_admin():
            self.today_sales_card.value_label.configure(
                text=f"LKR {stats['today_sales']:,.2f}"
            )
            self.pending_balance_card.value_label.configure(
                text=f"LKR {stats['pending_balances']:,.2f}"
            )
            self.weekly_sales_card.value_label.configure(
                text=f"LKR {stats['weekly_sales']:,.2f}"
            )
            self.monthly_sales_card.value_label.configure(
                text=f"LKR {stats['monthly_sales']:,.2f}"
            )
            
            # Update admin-only frame profit cards
            frame_profit = stats.get('frame_profit', {})
            today_profit = stats.get('today_frame_profit', {})
            monthly_profit = stats.get('monthly_frame_profit', {})
            
            self.frames_sold_card.value_label.configure(
                text=str(frame_profit.get('total_frames_sold', 0))
            )
            self.buying_cost_card.value_label.configure(
                text=f"LKR {frame_profit.get('total_buying_cost', 0):,.2f}"
            )
            self.selling_amount_card.value_label.configure(
                text=f"LKR {frame_profit.get('total_selling_amount', 0):,.2f}"
            )
            
            net_profit = frame_profit.get('net_profit', 0)
            profit_color = "#00ff88" if net_profit >= 0 else "#ff6b6b"
            self.net_profit_card.value_label.configure(
                text=f"LKR {net_profit:,.2f}",
                text_color=profit_color
            )
            
            today_frame_profit = today_profit.get('net_profit', 0)
            today_color = "#00ff88" if today_frame_profit >= 0 else "#ff6b6b"
            self.today_frame_profit_card.value_label.configure(
                text=f"LKR {today_frame_profit:,.2f}",
                text_color=today_color
            )
            
            monthly_frame_profit = monthly_profit.get('net_profit', 0)
            monthly_color = "#00ff88" if monthly_frame_profit >= 0 else "#ff6b6b"
            self.monthly_frame_profit_card.value_label.configure(
                text=f"LKR {monthly_frame_profit:,.2f}",
                text_color=monthly_color
            )
            
            self.monthly_frames_sold_card.value_label.configure(
                text=str(monthly_profit.get('total_frames_sold', 0))
            )
        else:
            # Load staff-specific widget data
            self.load_staff_widgets()
    
    def load_staff_widgets(self):
        """Load staff-specific widget data"""
        staff_stats = self.dashboard_service.get_staff_dashboard_stats()
        
        # Clear existing widget contents
        for widget in self.bookings_list_frame.winfo_children():
            widget.destroy()
        for widget in self.customers_list_frame.winfo_children():
            widget.destroy()
        for widget in self.stock_list_frame.winfo_children():
            widget.destroy()
        
        # Load Upcoming Bookings
        bookings = staff_stats.get('upcoming_bookings', [])
        if bookings:
            for booking in bookings:
                booking_item = ctk.CTkFrame(self.bookings_list_frame, fg_color="#2d2d5a", corner_radius=8)
                booking_item.pack(fill="x", pady=3)
                
                # Format date nicely
                event_date = booking.get('event_date', 'N/A')
                event_time = booking.get('event_time', '')
                customer_name = booking.get('customer_name', 'Unknown')
                event_type = booking.get('event_type', 'Event')
                status = booking.get('status', 'Pending')
                
                # Status color
                status_color = "#00ff88" if status == "Confirmed" else "#ffd93d"
                
                info_frame = ctk.CTkFrame(booking_item, fg_color="transparent")
                info_frame.pack(fill="x", padx=8, pady=6)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📅 {event_date}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#00d4ff"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"{event_type} - {customer_name}",
                    font=ctk.CTkFont(size=10),
                    text_color="#aaaaaa"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"⏰ {event_time} • {status}",
                    font=ctk.CTkFont(size=9),
                    text_color=status_color
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                self.bookings_list_frame,
                text="No upcoming bookings",
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            ).pack(pady=20)
        
        # Load Recent Customers
        customers = staff_stats.get('recent_customers', [])
        if customers:
            for customer in customers:
                customer_item = ctk.CTkFrame(self.customers_list_frame, fg_color="#2d2d5a", corner_radius=8)
                customer_item.pack(fill="x", pady=3)
                
                info_frame = ctk.CTkFrame(customer_item, fg_color="transparent")
                info_frame.pack(fill="x", padx=8, pady=6)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"👤 {customer.get('full_name', 'Unknown')}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#ffd93d"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📱 {customer.get('mobile_number', 'N/A')}",
                    font=ctk.CTkFont(size=10),
                    text_color="#aaaaaa"
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                self.customers_list_frame,
                text="No customers yet",
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            ).pack(pady=20)
        
        # Load Frame Stock
        frames = staff_stats.get('frame_stock', [])
        if frames:
            for frame in frames:
                frame_item = ctk.CTkFrame(self.stock_list_frame, fg_color="#2d2d5a", corner_radius=8)
                frame_item.pack(fill="x", pady=3)
                
                quantity = frame.get('quantity', 0)
                
                # Low stock warning
                if quantity < 5:
                    stock_color = "#ff6b6b"
                    stock_icon = "⚠️"
                elif quantity < 10:
                    stock_color = "#ffd93d"
                    stock_icon = "📦"
                else:
                    stock_color = "#00ff88"
                    stock_icon = "✅"
                
                info_frame = ctk.CTkFrame(frame_item, fg_color="transparent")
                info_frame.pack(fill="x", padx=8, pady=6)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"🖼️ {frame.get('frame_name', 'Unknown')}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#00d4ff"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📐 {frame.get('size', 'N/A')} • {stock_icon} {quantity} in stock",
                    font=ctk.CTkFont(size=10),
                    text_color=stock_color
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                self.stock_list_frame,
                text="No frames in inventory",
                font=ctk.CTkFont(size=11),
                text_color="#888888"
            ).pack(pady=20)
