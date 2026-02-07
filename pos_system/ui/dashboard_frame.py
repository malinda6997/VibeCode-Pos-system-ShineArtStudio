import customtkinter as ctk
from services.dashboard_service import DashboardService
from services.executive_report_generator import (
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report
)
from datetime import datetime, timedelta
from tkinter import messagebox
import os
import platform
import subprocess


class DashboardFrame(ctk.CTkFrame):
    """Revamped Admin Dashboard with Financial Analytics and Expense Tracking"""
    
    def __init__(self, parent, auth_manager, db_manager, main_app=None):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.dashboard_service = DashboardService()
        self.main_app = main_app
        
        # Filter variables
        self.filter_mode = "daily"  # daily, weekly, monthly
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_month = datetime.now().month
        self.selected_year = datetime.now().year
        self.selected_week = 1
        
        self.create_widgets()
        self.load_stats()
        
        # Initialize report button visibility
        if self.is_admin():
            self.update_report_button_visibility()
        
        # Auto-refresh on startup
        self.update_daily_balance()
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.auth_manager.is_admin()
    
    def navigate_to(self, page: str):
        """Navigate to another page via main app"""
        if self.main_app:
            self.main_app.navigate_to(page)
    
    def update_daily_balance(self):
        """Auto-refresh daily balance logic"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.dashboard_service.update_daily_balance(today)
    
    def create_widgets(self):
        """Create dashboard widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Financial Dashboard",
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
        self.refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh",
            width=100,
            height=35,
            command=self.refresh_with_animation,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        )
        self.refresh_btn.pack(side="right", padx=20)
        
        # Welcome message
        user = self.auth_manager.get_current_user()
        welcome = ctk.CTkLabel(
            self,
            text=f"Welcome back, {user['full_name']}! 👋",
            font=ctk.CTkFont(size=16),
            text_color="#aaaaaa"
        )
        welcome.pack(anchor="w", padx=30, pady=(0, 10))
        
        # ==================== FILTERING HEADER ====================
        filter_frame = ctk.CTkFrame(self, fg_color="#060606", corner_radius=20, border_width=2, border_color="#444444")
        filter_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        filter_title = ctk.CTkLabel(
            filter_frame,
            text="📊 Financial Analytics Filters",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        )
        filter_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        filter_btn_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Filter buttons
        self.daily_filter_btn = ctk.CTkButton(
            filter_btn_frame,
            text="📅 Daily",
            width=120,
            height=40,
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            command=lambda: self.apply_filter("daily")
        )
        self.daily_filter_btn.pack(side="left", padx=5)
        
        self.weekly_filter_btn = ctk.CTkButton(
            filter_btn_frame,
            text="📆 Weekly",
            width=120,
            height=40,
            fg_color="#444444",
            text_color="#ffffff",
            hover_color="#555555",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            command=lambda: self.apply_filter("weekly")
        )
        self.weekly_filter_btn.pack(side="left", padx=5)
        
        self.monthly_filter_btn = ctk.CTkButton(
            filter_btn_frame,
            text="📊 Monthly",
            width=120,
            height=40,
            fg_color="#444444",
            text_color="#ffffff",
            hover_color="#555555",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            command=lambda: self.apply_filter("monthly")
        )
        self.monthly_filter_btn.pack(side="left", padx=5)
        
        # Separator
        separator = ctk.CTkFrame(filter_btn_frame, width=2, height=30, fg_color="#444444")
        separator.pack(side="left", padx=15)
        
        # Year Selector
        ctk.CTkLabel(
            filter_btn_frame,
            text="Year:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=(0, 5))
        
        current_year = datetime.now().year
        # Year starts from 2026
        years = [str(year) for year in range(2026, current_year + 2)]
        self.year_selector = ctk.CTkOptionMenu(
            filter_btn_frame,
            values=years,
            width=100,
            height=35,
            fg_color="#2d2d5a",
            button_color="#8C00FF",
            button_hover_color="#7300D6",
            dropdown_fg_color="#2d2d5a",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=15,
            command=self.on_year_changed
        )
        self.year_selector.set(str(current_year))
        self.year_selector.pack(side="left", padx=5)
        
        # Month Selector
        ctk.CTkLabel(
            filter_btn_frame,
            text="Month:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=(15, 5))
        
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.month_selector = ctk.CTkOptionMenu(
            filter_btn_frame,
            values=months,
            width=130,
            height=35,
            fg_color="#2d2d5a",
            button_color="#8C00FF",
            button_hover_color="#7300D6",
            dropdown_fg_color="#2d2d5a",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=15,
            command=self.on_month_changed
        )
        self.month_selector.set(months[datetime.now().month - 1])
        self.month_selector.pack(side="left", padx=5)
        
        # Week Selector
        ctk.CTkLabel(
            filter_btn_frame,
            text="Week:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=(15, 5))
        
        weeks = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
        self.week_selector = ctk.CTkOptionMenu(
            filter_btn_frame,
            values=weeks,
            width=100,
            height=35,
            fg_color="#2d2d5a",
            button_color="#8C00FF",
            button_hover_color="#7300D6",
            dropdown_fg_color="#2d2d5a",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=15,
            command=self.on_week_changed
        )
        self.week_selector.set("Week 1")
        self.week_selector.pack(side="left", padx=5)
        
        # Date Picker Toggle
        ctk.CTkLabel(
            filter_btn_frame,
            text="Custom Date:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=(15, 5))
        
        self.date_picker_toggle = ctk.CTkSwitch(
            filter_btn_frame,
            text="",
            width=50,
            height=25,
            progress_color="#8C00FF",
            button_color="#ffffff",
            button_hover_color="#e0e0e0",
            command=self.toggle_date_picker
        )
        self.date_picker_toggle.pack(side="left", padx=5)
        
        # Selected period label
        self.period_label = ctk.CTkLabel(
            filter_btn_frame,
            text=f"Viewing: {datetime.now().strftime('%B %d, %Y')}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00ff88"
        )
        self.period_label.pack(side="right", padx=20)
        
        # Scrollable stats container
        scroll_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Stats cards container
        self.cards_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True)
        
        # ==================== MANUAL EXPENSE ENTRY ====================
        # Show to Admin OR Staff with expense permission
        user = self.auth_manager.get_current_user()
        can_manage_expenses = False
        if self.is_admin():
            can_manage_expenses = True
        elif user:
            # Check permission for staff
            perms = self.db_manager.get_user_permissions(user['id'])
            if perms and perms.get('can_manage_expenses', 0) == 1:
                can_manage_expenses = True
        
        if can_manage_expenses:
            expense_frame = ctk.CTkFrame(self.cards_frame, fg_color="#060606", corner_radius=20, border_width=2, border_color="#444444")
            expense_frame.pack(fill="x", pady=(0, 10))
            
            expense_title = ctk.CTkLabel(
                expense_frame,
                text="💸 Manual Expense Entry",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ff6b6b"
            )
            expense_title.pack(anchor="w", padx=20, pady=(15, 10))
            
            expense_input_frame = ctk.CTkFrame(expense_frame, fg_color="transparent")
            expense_input_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # Description input
            ctk.CTkLabel(
                expense_input_frame,
                text="Description:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff"
            ).pack(side="left", padx=(0, 10))
            
            self.expense_desc_entry = ctk.CTkEntry(
                expense_input_frame,
                placeholder_text="Enter expense description...",
                width=300,
                height=40,
                font=ctk.CTkFont(size=12),
                border_color="#8C00FF",
                border_width=2,
                corner_radius=15
            )
            self.expense_desc_entry.pack(side="left", padx=5)
            
            # Amount input
            ctk.CTkLabel(
                expense_input_frame,
                text="Amount (LKR):",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#ffffff"
            ).pack(side="left", padx=(20, 10))
            
            self.expense_amount_entry = ctk.CTkEntry(
                expense_input_frame,
                placeholder_text="0.00",
                width=150,
                height=40,
                font=ctk.CTkFont(size=12),
                border_color="#8C00FF",
                border_width=2,
                corner_radius=15
            )
            self.expense_amount_entry.pack(side="left", padx=5)
            
            # Add expense button
            add_expense_btn = ctk.CTkButton(
                expense_input_frame,
                text="➕ Add Expense",
                width=150,
                height=40,
                fg_color="#ff6b6b",
                text_color="#ffffff",
                hover_color="#ff5252",
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=20,
                command=self.add_expense
            )
            add_expense_btn.pack(side="left", padx=20)
        
        # ==================== OPENING/CLOSING BALANCE & SUMMARY ====================
        if self.is_admin():
            balance_frame = ctk.CTkFrame(self.cards_frame, fg_color="#1e3a2f", corner_radius=20, border_width=2, border_color="#00ff88")
            balance_frame.pack(fill="x", pady=(0, 10))
            
            balance_title = ctk.CTkLabel(
                balance_frame,
                text="💰 Daily Balance Summary",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#00ff88"
            )
            balance_title.pack(anchor="w", padx=20, pady=(15, 10))
            
            balance_row = ctk.CTkFrame(balance_frame, fg_color="transparent")
            balance_row.pack(fill="x", padx=20, pady=(0, 15))
            
            # Opening Balance
            opening_card = ctk.CTkFrame(balance_row, fg_color="#2d2d5a", corner_radius=15, border_width=2, border_color="#8C00FF")
            opening_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            ctk.CTkLabel(
                opening_card,
                text="Opening Balance",
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            ).pack(pady=(15, 5))
            
            self.opening_balance_label = ctk.CTkLabel(
                opening_card,
                text="LKR 0.00",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#ffffff"
            )
            self.opening_balance_label.pack(pady=(0, 15))
            
            # Total Income
            income_card = ctk.CTkFrame(balance_row, fg_color="#2d2d5a", corner_radius=15, border_width=2, border_color="#00ff88")
            income_card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                income_card,
                text="Total Income",
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            ).pack(pady=(15, 5))
            
            self.total_income_label = ctk.CTkLabel(
                income_card,
                text="LKR 0.00",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#00ff88"
            )
            self.total_income_label.pack(pady=(0, 15))
            
            # Total Expenses
            expense_card = ctk.CTkFrame(balance_row, fg_color="#2d2d5a", corner_radius=15, border_width=2, border_color="#ff6b6b")
            expense_card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(
                expense_card,
                text="Total Expenses",
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            ).pack(pady=(15, 5))
            
            self.total_expenses_label = ctk.CTkLabel(
                expense_card,
                text="LKR 0.00",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#ff6b6b"
            )
            self.total_expenses_label.pack(pady=(0, 15))
            
            # Net Profit
            profit_card = ctk.CTkFrame(balance_row, fg_color="#2d2d5a", corner_radius=15, border_width=2, border_color="#8C00FF")
            profit_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            ctk.CTkLabel(
                profit_card,
                text="Net Profit/Loss",
                font=ctk.CTkFont(size=13),
                text_color="#888888"
            ).pack(pady=(15, 5))
            
            self.net_profit_label = ctk.CTkLabel(
                profit_card,
                text="LKR 0.00",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#ffffff"
            )
            self.net_profit_label.pack(pady=(0, 15))
        
        # ==================== PDF REPORT GENERATION ====================
        if self.is_admin():
            report_frame = ctk.CTkFrame(self.cards_frame, fg_color="#060606", corner_radius=20, border_width=2, border_color="#444444")
            report_frame.pack(fill="x", pady=(0, 10))
            
            report_title = ctk.CTkLabel(
                report_frame,
                text="📄 Professional PDF Reports",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#8C00FF"
            )
            report_title.pack(anchor="w", padx=20, pady=(15, 10))
            
            report_btn_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
            report_btn_frame.pack(fill="x", padx=20, pady=(0, 15))
            
            # Daily Report Button (Hidden by default)
            self.daily_report_btn = ctk.CTkButton(
                report_btn_frame,
                text="📅 Generate Daily Report",
                width=200,
                height=45,
                fg_color="#8C00FF",
                text_color="#ffffff",
                hover_color="#7300D6",
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=20,
                command=lambda: self.generate_report("daily")
            )
            # Don't pack by default - will be shown based on filter
            
            # Weekly Report Button (Hidden by default)
            self.weekly_report_btn = ctk.CTkButton(
                report_btn_frame,
                text="📆 Generate Weekly Report",
                width=200,
                height=45,
                fg_color="#8C00FF",
                text_color="#ffffff",
                hover_color="#7300D6",
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=20,
                command=lambda: self.generate_report("weekly")
            )
            # Don't pack by default - will be shown based on filter
            
            # Monthly Report Button (Hidden by default)
            self.monthly_report_btn = ctk.CTkButton(
                report_btn_frame,
                text="📊 Generate Monthly Report",
                width=200,
                height=45,
                fg_color="#8C00FF",
                text_color="#ffffff",
                hover_color="#7300D6",
                font=ctk.CTkFont(size=13, weight="bold"),
                corner_radius=20,
                command=lambda: self.generate_report("monthly")
            )
            # Don't pack by default - will be shown based on filter
            
            # Store reference to report button frame
            self.report_btn_frame = report_btn_frame
        
        # ==================== Financial Cards ====================
        if self.is_admin():
            # Admin header for financial section
            admin_header = ctk.CTkFrame(self.cards_frame, fg_color="#1e3a2f", corner_radius=10)
            admin_header.pack(fill="x", pady=(10, 10))
            
            ctk.CTkLabel(
                admin_header,
                text="💰 Financial Overview (Admin Only)",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#00ff88"
            ).pack(pady=10, padx=15, anchor="w")
            
            # Row 1 - Financial stats
            row1 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
            row1.pack(fill="x", pady=10)
            
            self.today_sales_card = self.create_stat_card(
                row1, "Today's Sales", "LKR 0.00", "💰", "#8C00FF"
            )
            self.today_sales_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            self.pending_balance_card = self.create_stat_card(
                row1, "Pending Balances", "LKR 0.00", "⏳", "#ff6b6b"
            )
            self.pending_balance_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.weekly_sales_card = self.create_stat_card(
                row1, "Weekly Sales", "LKR 0.00", "📈", "#4ecdc4"
            )
            self.weekly_sales_card.pack(side="left", fill="both", expand=True, padx=10)
            
            self.monthly_sales_card = self.create_stat_card(
                row1, "Monthly Sales", "LKR 0.00", "📊", "#45b7d1"
            )
            self.monthly_sales_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        
        # ==================== General Stats ====================
        general_header = ctk.CTkFrame(self.cards_frame, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=10)
        general_header.pack(fill="x", pady=(10, 10))
        
        ctk.CTkLabel(
            general_header,
            text="📊 General Statistics",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=10, padx=15, anchor="w")
        
        # Row 2 - General stats
        row2 = ctk.CTkFrame(self.cards_frame, fg_color="transparent")
        row2.pack(fill="x", pady=10)
        
        self.today_invoices_card = self.create_stat_card(
            row2, "Today's Invoices", "0", "📄", "#00ff88"
        )
        self.today_invoices_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.total_invoices_card = self.create_stat_card(
            row2, "Total Invoices", "0", "📋", "#96ceb4"
        )
        self.total_invoices_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.total_customers_card = self.create_stat_card(
            row2, "Total Customers", "0", "👥", "#ffd93d"
        )
        self.total_customers_card.pack(side="left", fill="both", expand=True, padx=10)
        
        self.pending_bookings_card = self.create_stat_card(
            row2, "Pending Bookings", "0", "📅", "#c44dff"
        )
        self.pending_bookings_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
    
    def create_stat_card(self, parent, title: str, value: str, icon: str, 
                        color: str) -> ctk.CTkFrame:
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color="#060606", corner_radius=20, height=140, border_width=2, border_color="#444444")
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
    
    def toggle_date_picker(self):
        """Toggle date picker visibility and functionality"""
        if self.date_picker_toggle.get():
            # Date picker is ON - show custom date selection
            # For now, we'll use the daily filter as the custom date mode
            self.apply_filter("daily")
            messagebox.showinfo(
                "Date Picker Enabled",
                "Custom date picker is now active!\n\nYou can select specific dates using the Year, Month, and Week selectors.\n\nTip: Use 'Daily' filter for specific dates."
            )
        else:
            # Date picker is OFF - return to normal filtering
            pass
    
    def update_report_button_visibility(self):
        """Update visibility of report buttons based on current filter mode"""
        # Hide all buttons first
        self.daily_report_btn.pack_forget()
        self.weekly_report_btn.pack_forget()
        self.monthly_report_btn.pack_forget()
        
        # Show only the relevant button based on filter mode
        if self.filter_mode == "daily" or self.date_picker_toggle.get():
            # Show daily report button for daily filter or custom date
            self.daily_report_btn.pack(side="left", padx=5)
        elif self.filter_mode == "weekly":
            # Show weekly report button for weekly filter
            self.weekly_report_btn.pack(side="left", padx=5)
        elif self.filter_mode == "monthly":
            # Show monthly report button for monthly filter
            self.monthly_report_btn.pack(side="left", padx=5)
    
    def on_year_changed(self, selected_year: str):
        """Handle year selection change"""
        self.selected_year = int(selected_year)
        self.update_period_label()
        self.load_stats()
        self.update_report_button_visibility()
    
    def on_month_changed(self, selected_month: str):
        """Handle month selection change"""
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        self.selected_month = months.index(selected_month) + 1
        self.update_period_label()
        self.load_stats()
        self.update_report_button_visibility()
    
    def on_week_changed(self, selected_week: str):
        """Handle week selection change"""
        self.selected_week = int(selected_week.split()[1])  # Extract number from "Week X"
        self.update_period_label()
        self.load_stats()
        self.update_report_button_visibility()
    
    def update_period_label(self):
        """Update the period label based on current selections"""
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        
        if self.filter_mode == "daily":
            self.period_label.configure(text=f"Viewing: {datetime.now().strftime('%B %d, %Y')}")
        elif self.filter_mode == "weekly":
            # Calculate week date range
            start_date, end_date = self.get_week_range(self.selected_year, self.selected_month, self.selected_week)
            self.period_label.configure(text=f"Viewing: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')} (Week {self.selected_week})")
        elif self.filter_mode == "monthly":
            month_name = months[self.selected_month - 1]
            self.period_label.configure(text=f"Viewing: {month_name} {self.selected_year}")
    
    def get_week_range(self, year: int, month: int, week_num: int):
        """Calculate start and end dates for a specific week of a month"""
        from calendar import monthrange
        
        # Get first day of month
        first_day = datetime(year, month, 1)
        
        # Calculate start date of the week
        start_day = 1 + (week_num - 1) * 7
        
        # Get last day of month
        _, last_day_of_month = monthrange(year, month)
        
        # Calculate end day of the week (7 days later or last day of month)
        end_day = min(start_day + 6, last_day_of_month)
        
        start_date = datetime(year, month, start_day)
        end_date = datetime(year, month, end_day)
        
        return start_date, end_date
    
    def apply_filter(self, filter_mode: str):
        """Apply date filter"""
        self.filter_mode = filter_mode
        
        # Update button styles
        self.daily_filter_btn.configure(fg_color="#444444")
        self.weekly_filter_btn.configure(fg_color="#444444")
        self.monthly_filter_btn.configure(fg_color="#444444")
        
        if filter_mode == "daily":
            self.daily_filter_btn.configure(fg_color="#8C00FF")
        elif filter_mode == "weekly":
            self.weekly_filter_btn.configure(fg_color="#8C00FF")
        elif filter_mode == "monthly":
            self.monthly_filter_btn.configure(fg_color="#8C00FF")
        
        # Update period label and refresh stats
        self.update_period_label()
        self.load_stats()
        self.update_report_button_visibility()
    
    def add_expense(self):
        """Add manual expense"""
        description = self.expense_desc_entry.get().strip()
        amount_text = self.expense_amount_entry.get().strip()
        
        if not description:
            messagebox.showerror("Error", "Please enter expense description")
            return
        
        if not amount_text:
            messagebox.showerror("Error", "Please enter expense amount")
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than zero")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format")
            return
        
        # Get current user
        user = self.auth_manager.get_current_user()
        
        # Add expense
        success = self.dashboard_service.add_manual_expense(
            description=description,
            amount=amount,
            created_by=user['id'],
            expense_date=self.selected_date
        )
        
        if success:
            messagebox.showinfo("Success", f"Expense added successfully!\n\n{description}: LKR {amount:,.2f}")
            
            # Clear inputs
            self.expense_desc_entry.delete(0, 'end')
            self.expense_amount_entry.delete(0, 'end')
            
            # Refresh dashboard
            self.load_stats()
        else:
            messagebox.showerror("Error", "Failed to add expense")
    
    def generate_report(self, report_type: str):
        """Generate Executive PDF report with cover page and TOC"""
        try:
            if report_type == "daily":
                result = generate_daily_report()
            elif report_type == "weekly":
                # Check if using specific week filter
                if self.filter_mode == "weekly":
                    # Generate report for specific week
                    start_date, end_date = self.get_week_range(self.selected_year, self.selected_month, self.selected_week)
                    result = generate_weekly_report(
                        start_date=start_date.strftime('%Y-%m-%d'),
                        end_date=end_date.strftime('%Y-%m-%d')
                    )
                else:
                    result = generate_weekly_report()
            elif report_type == "monthly":
                # Check if using specific month filter
                if self.filter_mode == "monthly":
                    # Generate report for specific month and year
                    result = generate_monthly_report(year=self.selected_year, month=self.selected_month)
                else:
                    today = datetime.now()
                    result = generate_monthly_report(year=today.year, month=today.month)
            else:
                messagebox.showerror("Error", "Invalid report type")
                return
            
            if result['success']:
                summary = result['summary']
                analytics = result.get('analytics', {})
                
                # Enhanced message with analytics
                analytics_info = ""
                if 'user_insights' in analytics:
                    user_insights = analytics['user_insights']
                    analytics_info = (
                        f"\n📈 Analytics:\n"
                        f"New Customers: {user_insights.get('new_customers', 0)}\n"
                        f"Total Customers: {user_insights.get('total_customers', 0)}\n"
                    )
                
                # Add filter information to message
                filter_info = ""
                if report_type == "weekly" and self.filter_mode == "weekly":
                    start_date, end_date = self.get_week_range(self.selected_year, self.selected_month, self.selected_week)
                    months = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                    month_name = months[self.selected_month - 1]
                    filter_info = f"\n📅 Period: Week {self.selected_week} of {month_name} {self.selected_year}\n"
                elif report_type == "monthly" and self.filter_mode == "monthly":
                    months = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                    month_name = months[self.selected_month - 1]
                    filter_info = f"\n📅 Period: {month_name} {self.selected_year}\n"
                
                message = (
                    f"✅ {report_type.capitalize()} Executive Report Generated!\n"
                    f"{filter_info}\n"
                    f"📊 Financial Summary:\n"
                    f"Opening Balance: LKR {summary['opening_balance']:,.2f}\n"
                    f"Total Income: LKR {summary['total_income']:,.2f}\n"
                    f"Total Expenses: LKR {summary['total_expenses']:,.2f}\n"
                    f"Net Profit/Loss: LKR {summary['net_balance']:,.2f}\n"
                    f"Closing Balance: LKR {summary['closing_balance']:,.2f}"
                    f"{analytics_info}\n"
                    f"📄 Features: Cover Page, Table of Contents, Dynamic Insights\n"
                    f"👨‍💻 Developer: Malinda Prabath\n\n"
                    f"📁 Saved as: {result['filename']}"
                )
                
                response = messagebox.askyesno(
                    "Report Generated",
                    f"{message}\n\nWould you like to open the report now?"
                )
                
                if response:
                    self.open_file(result['filepath'])
            else:
                messagebox.showerror("Error", "Failed to generate report")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating report:\n{str(e)}")
    
    def open_file(self, filepath: str):
        """Open file with default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{str(e)}")
    
    def refresh_with_animation(self):
        """Refresh dashboard with loading animation"""
        # Disable refresh button during animation
        self.refresh_btn.configure(state="disabled", text="⏳ Loading...")
        
        # Perform refresh after short delay
        self.after(500, self.complete_refresh)
    
    def complete_refresh(self):
        """Complete the refresh process"""
        try:
            # Update daily balance
            self.update_daily_balance()
            # Reload stats
            self.load_stats()
        finally:
            # Re-enable refresh button
            self.refresh_btn.configure(state="normal", text="🔄 Refresh")
    
    def load_stats(self):
        """Load dashboard statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Load appropriate stats based on user role
        if self.is_admin():
            stats = self.dashboard_service.get_admin_dashboard_stats()
            
            # Update balance summary based on filter mode
            opening_balance = self.dashboard_service.get_opening_balance(today)
            
            # Get income and expenses based on filter
            if self.filter_mode == "daily":
                total_income = stats['today_sales']
                total_expenses = self.dashboard_service.get_expenses_by_date(today)
            elif self.filter_mode == "weekly":
                # Get specific week range
                start_date, end_date = self.get_week_range(self.selected_year, self.selected_month, self.selected_week)
                total_income = self.dashboard_service.get_income_by_range(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                total_expenses = self.dashboard_service.get_expenses_by_range(
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
            elif self.filter_mode == "monthly":
                # Get specific month data
                total_income = self.dashboard_service.get_income_by_month(self.selected_year, self.selected_month)
                total_expenses = self.dashboard_service.get_expenses_by_month(self.selected_year, self.selected_month)
            else:
                total_income = 0.0
                total_expenses = 0.0
            
            net_profit = total_income - total_expenses
            
            # Update balance labels
            self.opening_balance_label.configure(text=f"LKR {opening_balance:,.2f}")
            self.total_income_label.configure(text=f"LKR {total_income:,.2f}")
            self.total_expenses_label.configure(text=f"LKR {total_expenses:,.2f}")
            
            profit_color = "#00ff88" if net_profit >= 0 else "#ff6b6b"
            self.net_profit_label.configure(text=f"LKR {net_profit:,.2f}", text_color=profit_color)
            
            # Update financial cards
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
        else:
            stats = self.dashboard_service.get_dashboard_stats()
        
        # Update general stats
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
