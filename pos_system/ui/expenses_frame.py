import customtkinter as ctk
from tkinter import ttk, messagebox
from ui.components import BaseFrame, MessageDialog
from services.expense_report_generator import ExpenseReportGenerator
from services.dashboard_service import DashboardService
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os
import sys
import subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import resource_path


class ExpensesManagementFrame(BaseFrame):
    """Expense management interface for viewing, editing, deleting, and generating reports"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.expense_report_generator = ExpenseReportGenerator()
        self.dashboard_service = DashboardService()
        self.filter_mode = "daily"  # 'daily', 'weekly', 'monthly', 'custom'
        self.selected_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_start_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_end_date = datetime.now().strftime('%Y-%m-%d')
        self.create_widgets()
        self.load_expenses()
    
    def create_widgets(self):
        """Create expense management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="💰 Expense Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Filter and controls section
        controls_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Filter mode selector
        filter_mode_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        filter_mode_frame.pack(side="left", padx=15, pady=15)
        
        ctk.CTkLabel(
            filter_mode_frame,
            text="Filter:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        self.filter_selector = ctk.CTkSegmentedButton(
            filter_mode_frame,
            values=["Daily", "Weekly", "Monthly", "Custom"],
            command=self.on_filter_change,
            selected_color="#8C00FF",
            selected_hover_color="#7300D6",
            unselected_color="#2d2d5a",
            unselected_hover_color="#3d3d7a",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            border_width=2
        )
        self.filter_selector.set("Daily")
        self.filter_selector.pack(side="left")
        
        # Date picker frame (changes based on filter mode)
        self.date_picker_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        self.date_picker_frame.pack(side="left", padx=20, pady=15)
        
        self.create_date_pickers()
        
        # Generate Report button
        self.generate_report_btn = ctk.CTkButton(
            controls_frame,
            text="📄 Generate Report",
            command=self.generate_report,
            fg_color="#00A86B",
            hover_color="#008C5A",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=35,
            corner_radius=15
        )
        self.generate_report_btn.pack(side="right", padx=15, pady=15)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.load_expenses,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=120,
            height=35,
            corner_radius=15
        )
        self.refresh_btn.pack(side="right", padx=5, pady=15)
        
        # Summary section
        summary_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#8C00FF", corner_radius=15)
        summary_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        summary_inner = ctk.CTkFrame(summary_frame, fg_color="transparent")
        summary_inner.pack(fill="x", padx=20, pady=15)
        
        # Total expenses label
        total_frame = ctk.CTkFrame(summary_inner, fg_color="#1a1a2e", corner_radius=10)
        total_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            total_frame,
            text="Total Expenses:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#AAAAAA"
        ).pack(side="left", padx=15, pady=10)
        
        self.total_expenses_label = ctk.CTkLabel(
            total_frame,
            text="LKR 0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FF6B6B"
        )
        self.total_expenses_label.pack(side="left", padx=15, pady=10)
        
        # Count label
        count_frame = ctk.CTkFrame(summary_inner, fg_color="#1a1a2e", corner_radius=10)
        count_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(
            count_frame,
            text="Total Entries:",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#AAAAAA"
        ).pack(side="left", padx=15, pady=10)
        
        self.total_count_label = ctk.CTkLabel(
            count_frame,
            text="0",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00A86B"
        )
        self.total_count_label.pack(side="left", padx=15, pady=10)
        
        # Expenses table section
        table_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table title
        table_title = ctk.CTkLabel(
            table_frame,
            text="Expense Records",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        table_title.pack(pady=(15, 10))
        
        # Create treeview for expenses
        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        y_scrollbar.pack(side="right", fill="y")
        
        x_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal")
        x_scrollbar.pack(side="bottom", fill="x")
        
        # Treeview
        columns = ("ID", "Date", "Description", "Amount", "Added By", "Created At")
        self.expenses_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
            height=15
        )
        
        # Configure columns
        self.expenses_tree.heading("ID", text="ID")
        self.expenses_tree.heading("Date", text="Expense Date")
        self.expenses_tree.heading("Description", text="Description")
        self.expenses_tree.heading("Amount", text="Amount (LKR)")
        self.expenses_tree.heading("Added By", text="Added By")
        self.expenses_tree.heading("Created At", text="Created At")
        
        self.expenses_tree.column("ID", width=50, anchor="center")
        self.expenses_tree.column("Date", width=120, anchor="center")
        self.expenses_tree.column("Description", width=300, anchor="w")
        self.expenses_tree.column("Amount", width=120, anchor="e")
        self.expenses_tree.column("Added By", width=150, anchor="center")
        self.expenses_tree.column("Created At", width=150, anchor="center")
        
        y_scrollbar.config(command=self.expenses_tree.yview)
        x_scrollbar.config(command=self.expenses_tree.xview)
        
        self.expenses_tree.pack(fill="both", expand=True)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                       background="#1a1a2e",
                       foreground="white",
                       fieldbackground="#1a1a2e",
                       borderwidth=0,
                       font=('Helvetica', 10))
        style.configure("Treeview.Heading",
                       background="#8C00FF",
                       foreground="white",
                       borderwidth=1,
                       font=('Helvetica', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#8C00FF')])
        
        # Right-click context menu (Admin only)
        if self.auth_manager.is_admin():
            self.expenses_tree.bind("<Button-3>", self.show_context_menu)
    
    def create_date_pickers(self):
        """Create date picker widgets based on filter mode"""
        # Clear existing widgets
        for widget in self.date_picker_frame.winfo_children():
            widget.destroy()
        
        if self.filter_mode == "daily":
            # Single date picker
            ctk.CTkLabel(
                self.date_picker_frame,
                text="Date:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=5)
            
            self.date_entry = DateEntry(
                self.date_picker_frame,
                width=12,
                background='#8C00FF',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.date_entry.set_date(datetime.strptime(self.selected_date, '%Y-%m-%d'))
            self.date_entry.pack(side="left", padx=5)
            self.date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_date_selected())
            
        elif self.filter_mode == "weekly":
            # Start date picker
            ctk.CTkLabel(
                self.date_picker_frame,
                text="From:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=5)
            
            self.start_date_entry = DateEntry(
                self.date_picker_frame,
                width=12,
                background='#8C00FF',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.start_date_entry.set_date(datetime.strptime(self.selected_start_date, '%Y-%m-%d'))
            self.start_date_entry.pack(side="left", padx=5)
            
            # End date picker
            ctk.CTkLabel(
                self.date_picker_frame,
                text="To:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=15)
            
            self.end_date_entry = DateEntry(
                self.date_picker_frame,
                width=12,
                background='#8C00FF',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.end_date_entry.set_date(datetime.strptime(self.selected_end_date, '%Y-%m-%d'))
            self.end_date_entry.pack(side="left", padx=5)
            
            self.start_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_date_range_selected())
            self.end_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_date_range_selected())
            
        elif self.filter_mode == "monthly":
            # Month and year selectors
            ctk.CTkLabel(
                self.date_picker_frame,
                text="Month:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=5)
            
            current_date = datetime.now()
            self.month_var = ctk.StringVar(value=current_date.strftime('%B'))
            self.month_menu = ctk.CTkOptionMenu(
                self.date_picker_frame,
                variable=self.month_var,
                values=["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"],
                command=self.on_month_year_selected,
                fg_color="#8C00FF",
                button_color="#7300D6",
                button_hover_color="#5A00A3",
                width=130
            )
            self.month_menu.pack(side="left", padx=5)
            
            ctk.CTkLabel(
                self.date_picker_frame,
                text="Year:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=15)
            
            years = [str(year) for year in range(2020, current_date.year + 2)]
            self.year_var = ctk.StringVar(value=str(current_date.year))
            self.year_menu = ctk.CTkOptionMenu(
                self.date_picker_frame,
                variable=self.year_var,
                values=years,
                command=self.on_month_year_selected,
                fg_color="#8C00FF",
                button_color="#7300D6",
                button_hover_color="#5A00A3",
                width=100
            )
            self.year_menu.pack(side="left", padx=5)
            
        elif self.filter_mode == "custom":
            # Custom date range
            ctk.CTkLabel(
                self.date_picker_frame,
                text="From:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=5)
            
            self.custom_start_date_entry = DateEntry(
                self.date_picker_frame,
                width=12,
                background='#8C00FF',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.custom_start_date_entry.set_date(datetime.strptime(self.selected_start_date, '%Y-%m-%d'))
            self.custom_start_date_entry.pack(side="left", padx=5)
            
            ctk.CTkLabel(
                self.date_picker_frame,
                text="To:",
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=15)
            
            self.custom_end_date_entry = DateEntry(
                self.date_picker_frame,
                width=12,
                background='#8C00FF',
                foreground='white',
                borderwidth=2,
                date_pattern='yyyy-mm-dd'
            )
            self.custom_end_date_entry.set_date(datetime.strptime(self.selected_end_date, '%Y-%m-%d'))
            self.custom_end_date_entry.pack(side="left", padx=5)
            
            self.custom_start_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_custom_date_selected())
            self.custom_end_date_entry.bind("<<DateEntrySelected>>", lambda e: self.on_custom_date_selected())
    
    def on_filter_change(self, value):
        """Handle filter mode change"""
        self.filter_mode = value.lower()
        
        # Set default dates based on filter mode
        if self.filter_mode == "daily":
            self.selected_date = datetime.now().strftime('%Y-%m-%d')
        elif self.filter_mode == "weekly":
            # Default to current week (last 7 days)
            self.selected_end_date = datetime.now().strftime('%Y-%m-%d')
            self.selected_start_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        elif self.filter_mode == "custom":
            # Default to current month
            self.selected_end_date = datetime.now().strftime('%Y-%m-%d')
            self.selected_start_date = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        
        self.create_date_pickers()
        self.load_expenses()
    
    def on_date_selected(self):
        """Handle daily date selection"""
        self.selected_date = self.date_entry.get_date().strftime('%Y-%m-%d')
        self.load_expenses()
    
    def on_date_range_selected(self):
        """Handle weekly date range selection"""
        self.selected_start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
        self.selected_end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
        self.load_expenses()
    
    def on_month_year_selected(self, _=None):
        """Handle monthly selection"""
        self.load_expenses()
    
    def on_custom_date_selected(self):
        """Handle custom date range selection"""
        self.selected_start_date = self.custom_start_date_entry.get_date().strftime('%Y-%m-%d')
        self.selected_end_date = self.custom_end_date_entry.get_date().strftime('%Y-%m-%d')
        self.load_expenses()
    
    def load_expenses(self):
        """Load expenses based on current filter"""
        # Clear existing data
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Get date range based on filter mode
        if self.filter_mode == "daily":
            start_date = self.selected_date
            end_date = self.selected_date
        elif self.filter_mode == "weekly":
            start_date = self.selected_start_date
            end_date = self.selected_end_date
        elif self.filter_mode == "monthly":
            month_name = self.month_var.get()
            year = int(self.year_var.get())
            month = datetime.strptime(month_name, '%B').month
            
            start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
            if month == 12:
                end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
            else:
                end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
        elif self.filter_mode == "custom":
            start_date = self.selected_start_date
            end_date = self.selected_end_date
        
        # Admin sees all expenses, no filtering needed
        expenses = self.dashboard_service.get_expense_details_by_range(start_date, end_date)
        
        # Calculate totals
        total_amount = 0
        
        # Populate table
        for expense in expenses:
            expense_date = datetime.strptime(expense['expense_date'], '%Y-%m-%d').strftime('%b %d, %Y')
            created_at = datetime.strptime(expense['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%b %d, %Y %I:%M %p')
            
            self.expenses_tree.insert(
                "",
                "end",
                values=(
                    expense['id'],
                    expense_date,
                    expense['description'],
                    f"{expense['amount']:,.2f}",
                    expense['created_by_name'],
                    created_at
                )
            )
            total_amount += expense['amount']
        
        # Update summary labels
        self.total_expenses_label.configure(text=f"LKR {total_amount:,.2f}")
        self.total_count_label.configure(text=str(len(expenses)))
    
    def show_context_menu(self, event):
        """Show right-click context menu (Admin only)"""
        # Select item under cursor
        item = self.expenses_tree.identify_row(event.y)
        if item:
            self.expenses_tree.selection_set(item)
            
            # Create context menu
            menu = ctk.CTkToplevel(self)
            menu.withdraw()
            menu.overrideredirect(True)
            menu.configure(fg_color="#1a1a2e", border_width=2, border_color="#8C00FF")
            
            # Edit button
            edit_btn = ctk.CTkButton(
                menu,
                text="✏ Edit Expense",
                command=lambda: self.edit_expense(menu),
                fg_color="transparent",
                hover_color="#8C00FF",
                anchor="w",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            edit_btn.pack(fill="x", padx=5, pady=5)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                menu,
                text="🗑 Delete Expense",
                command=lambda: self.delete_expense(menu),
                fg_color="transparent",
                text_color="#ff6b6b",
                hover_color="#8C00FF",
                anchor="w",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold")
            )
            delete_btn.pack(fill="x", padx=5, pady=5)
            
            # Position menu at cursor
            menu.geometry(f"+{event.x_root}+{event.y_root}")
            menu.deiconify()
            
            # Close menu when clicking outside
            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_set()
    
    def edit_expense(self, menu):
        """Edit selected expense"""
        menu.destroy()
        
        selected = self.expenses_tree.selection()
        if not selected:
            return
        
        item = self.expenses_tree.item(selected[0])
        expense_id = item['values'][0]
        current_description = item['values'][2]
        current_amount = float(item['values'][3].replace(',', ''))
        
        # Create edit dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Expense")
        dialog.geometry("500x300")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color="#1a1a2e")
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 150
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Title
        ctk.CTkLabel(
            dialog,
            text="Edit Expense",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=20)
        
        # Description field
        desc_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        desc_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            desc_frame,
            text="Description:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        desc_entry = ctk.CTkEntry(
            desc_frame,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        desc_entry.insert(0, current_description)
        desc_entry.pack(fill="x")
        
        # Amount field
        amount_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        amount_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            amount_frame,
            text="Amount (LKR):",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        amount_entry = ctk.CTkEntry(
            amount_frame,
            height=40,
            font=ctk.CTkFont(size=12)
        )
        amount_entry.insert(0, str(current_amount))
        amount_entry.pack(fill="x")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=20)
        
        def save_changes():
            new_description = desc_entry.get().strip()
            new_amount_str = amount_entry.get().strip()
            
            if not new_description:
                messagebox.showerror("Error", "Description cannot be empty")
                return
            
            try:
                new_amount = float(new_amount_str)
                if new_amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than zero")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format")
                return
            
            # Update expense in database
            try:
                import sqlite3
                conn = sqlite3.connect('pos_database.db')
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE manual_expenses 
                    SET description = ?, amount = ?
                    WHERE id = ?
                ''', (new_description, new_amount, expense_id))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Expense updated successfully!")
                dialog.destroy()
                self.load_expenses()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update expense: {e}")
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            command=save_changes,
            fg_color="#00A86B",
            hover_color="#008C5A",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40
        ).pack(side="left", expand=True, padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            fg_color="#ff6b6b",
            hover_color="#e55555",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40
        ).pack(side="left", expand=True, padx=5)
    
    def delete_expense(self, menu):
        """Delete selected expense"""
        menu.destroy()
        
        selected = self.expenses_tree.selection()
        if not selected:
            return
        
        item = self.expenses_tree.item(selected[0])
        expense_id = item['values'][0]
        description = item['values'][2]
        
        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this expense?\n\n{description}\n\nThis action cannot be undone.",
            icon='warning'
        )
        
        if confirm:
            try:
                import sqlite3
                conn = sqlite3.connect('pos_database.db')
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM manual_expenses WHERE id = ?', (expense_id,))
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.load_expenses()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete expense: {e}")
    
    def generate_report(self):
        """Generate expense report based on current filter"""
        try:
            if self.filter_mode == "daily":
                filepath = self.expense_report_generator.generate_daily_report(self.selected_date)
            elif self.filter_mode == "weekly":
                filepath = self.expense_report_generator.generate_weekly_report(
                    self.selected_start_date,
                    self.selected_end_date
                )
            elif self.filter_mode == "monthly":
                month_name = self.month_var.get()
                year = int(self.year_var.get())
                month = datetime.strptime(month_name, '%B').month
                filepath = self.expense_report_generator.generate_monthly_report(year, month)
            elif self.filter_mode == "custom":
                filepath = self.expense_report_generator.generate_custom_report(
                    self.selected_start_date,
                    self.selected_end_date
                )
            
            # Open the generated report
            if os.path.exists(filepath):
                os.startfile(filepath)
                messagebox.showinfo("Success", f"Report generated successfully!\n\n{os.path.basename(filepath)}")
            else:
                messagebox.showerror("Error", "Report file not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
