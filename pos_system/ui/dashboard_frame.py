import customtkinter as ctk
from services.dashboard_service import DashboardService
from datetime import datetime


class DashboardFrame(ctk.CTkFrame):
    """Dashboard page with statistics and summary cards"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.dashboard_service = DashboardService()
        
        self.create_widgets()
        self.load_stats()
    
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
        
        # Scrollable stats cards container
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Stats cards container
        self.cards_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True)
        
        # Row 1 - Main stats
        row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row1.pack(fill="x", pady=10)
        
        self.today_sales_card = self.create_stat_card(
            row1, "Today's Sales", "LKR 0.00", "💰", "#00d4ff"
        )
        self.today_sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.today_invoices_card = self.create_stat_card(
            row1, "Today's Invoices", "0", "📄", "#00ff88"
        )
        self.today_invoices_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.pending_balance_card = self.create_stat_card(
            row1, "Pending Balances", "LKR 0.00", "⏳", "#ff6b6b"
        )
        self.pending_balance_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Row 2 - Secondary stats
        row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row2.pack(fill="x", pady=10)
        
        self.total_customers_card = self.create_stat_card(
            row2, "Total Customers", "0", "👥", "#ffd93d"
        )
        self.total_customers_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.pending_bookings_card = self.create_stat_card(
            row2, "Pending Bookings", "0", "📅", "#c44dff"
        )
        self.pending_bookings_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.low_stock_card = self.create_stat_card(
            row2, "Low Stock Items", "0", "⚠️", "#ff9f43"
        )
        self.low_stock_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Row 3 - Sales summary
        row3 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row3.pack(fill="x", pady=10)
        
        self.weekly_sales_card = self.create_stat_card(
            row3, "Weekly Sales", "LKR 0.00", "📈", "#4ecdc4"
        )
        self.weekly_sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.monthly_sales_card = self.create_stat_card(
            row3, "Monthly Sales", "LKR 0.00", "📊", "#45b7d1"
        )
        self.monthly_sales_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.total_invoices_card = self.create_stat_card(
            row3, "Total Invoices", "0", "📋", "#96ceb4"
        )
        self.total_invoices_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # Quick actions - inside scrollable area
        actions_frame = ctk.CTkFrame(scroll_container, fg_color="#1e1e3f", corner_radius=15)
        actions_frame.pack(fill="x", pady=20)
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        actions_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        actions_btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        actions = [
            ("➕ New Invoice", "#00d4ff"),
            ("👤 Add Customer", "#00ff88"),
            ("📅 New Booking", "#c44dff"),
            ("🖼️ Add Frame", "#ffd93d"),
        ]
        
        for text, color in actions:
            btn = ctk.CTkButton(
                actions_btn_frame,
                text=text,
                width=150,
                height=40,
                fg_color=color,
                text_color="#1a1a2e",
                hover_color=color,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            btn.pack(side="left", padx=5)
    
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
        stats = self.dashboard_service.get_dashboard_stats()
        
        # Update cards
        self.today_sales_card.value_label.configure(
            text=f"LKR {stats['today_sales']:,.2f}"
        )
        self.today_invoices_card.value_label.configure(
            text=str(stats['today_invoices'])
        )
        self.pending_balance_card.value_label.configure(
            text=f"LKR {stats['pending_balances']:,.2f}"
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
        self.weekly_sales_card.value_label.configure(
            text=f"LKR {stats['weekly_sales']:,.2f}"
        )
        self.monthly_sales_card.value_label.configure(
            text=f"LKR {stats['monthly_sales']:,.2f}"
        )
        self.total_invoices_card.value_label.configure(
            text=str(stats['total_invoices'])
        )
