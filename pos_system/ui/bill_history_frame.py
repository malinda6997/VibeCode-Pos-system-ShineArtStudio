import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services.bill_generator import BillGenerator
from datetime import datetime
import os


class BillHistoryFrame(BaseFrame):
    """Bill history viewing and reprinting interface (thermal bills)"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.bill_generator = BillGenerator()
        self.filter_type = "all"  # 'all', 'registered', 'guest'
        self.payment_status = "all"  # 'all', 'paid', 'pending'
        self.create_widgets()
        self.load_bills()
    
    def create_widgets(self):
        """Create bill history widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Bills History",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Search and controls
        controls_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            controls_frame,
            text="Search:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=15, pady=15)
        
        self.search_entry = ctk.CTkEntry(controls_frame, width=300, height=35, corner_radius=15, border_width=1)
        self.search_entry.pack(side="left", padx=10, pady=15)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_bills())
        
        # Payment Status Filter - MOVED TO LEFT
        payment_filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        payment_filter_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            payment_filter_frame,
            text="Payment Status:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        self.payment_status_selector = ctk.CTkSegmentedButton(
            payment_filter_frame,
            values=["All", "Fully Paid", "Pending"],
            command=self.on_payment_status_change,
            selected_color="#8C00FF",
            selected_hover_color="#7300D6",
            unselected_color="#2d2d5a",
            unselected_hover_color="#3d3d7a",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=20,
            border_width=2
        )
        self.payment_status_selector.set("All")
        self.payment_status_selector.pack(side="left")
        
        # Customer Type Filter
        filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        filter_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(
            filter_frame,
            text="Customer:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(0, 5))
        
        self.filter_var = ctk.StringVar(value="all")
        
        ctk.CTkRadioButton(
            filter_frame,
            text="All",
            variable=self.filter_var,
            value="all",
            command=self.apply_filter,
            fg_color="#8C00FF",
            hover_color="#7300D6"
        ).pack(side="left", padx=3)
        
        ctk.CTkRadioButton(
            filter_frame,
            text="Registered",
            variable=self.filter_var,
            value="registered",
            command=self.apply_filter,
            fg_color="#8C00FF",
            hover_color="#7300D6"
        ).pack(side="left", padx=3)
        
        ctk.CTkRadioButton(
            filter_frame,
            text="Guest",
            variable=self.filter_var,
            value="guest",
            command=self.apply_filter,
            fg_color="#8C00FF",
            hover_color="#7300D6"
        ).pack(side="left", padx=3)
        
        # Add Refresh button
        ctk.CTkButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.load_bills,
            width=120,
            height=35,
            fg_color="#4a4a6a",
            hover_color="#5a5a7a",
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="View Details",
            command=self.view_bill_details,
            width=120,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="💰 Settle Balance",
            command=self.settle_balance,
            width=150,
            height=35,
            fg_color="#00cc66",
            text_color="white",
            hover_color="#00aa55",
            corner_radius=20,
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            controls_frame,
            text="🖨 Reprint",
            command=self.reprint_bill,
            width=120,
            height=35,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="right", padx=5)
        
        # Admin-only delete buttons
        if self.auth_manager.current_user and self.auth_manager.current_user.get('role') == 'Admin':
            ctk.CTkButton(
                controls_frame,
                text="Delete Selected",
                command=self.delete_selected_bill,
                width=140,
                height=35,
                fg_color="#ff4444",
                text_color="white",
                hover_color="#cc0000"
            ).pack(side="left", padx=10)
        
        # Bills table
        table_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table header
        table_header = ctk.CTkFrame(table_frame, fg_color="#0d0d1a", corner_radius=10, height=50)
        table_header.pack(fill="x", padx=10, pady=(10, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="🧾 Bill Records",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8C00FF"
        ).pack(side="left", padx=15, pady=10)
        
        self.record_count_label = ctk.CTkLabel(
            table_header,
            text="0 records",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.record_count_label.pack(side="right", padx=15, pady=10)
        
        # Table container
        table_container = ctk.CTkFrame(table_frame, fg_color="#1a1a2e", corner_radius=10)
        table_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        columns = ("Bill #", "Date", "Customer", "Mobile", "Items", "Total", "Paid", "Balance")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)
        
        self.tree.heading("Bill #", text="🔢 Bill #")
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Customer", text="👤 Customer")
        self.tree.heading("Mobile", text="📱 Mobile")
        self.tree.heading("Items", text="📦 Items")
        self.tree.heading("Total", text="💰 Total (LKR)")
        self.tree.heading("Paid", text="✅ Paid (LKR)")
        self.tree.heading("Balance", text="⏳ Balance (LKR)")
        
        self.tree.column("Bill #", width=120, anchor="center")
        self.tree.column("Date", width=140)
        self.tree.column("Customer", width=180)
        self.tree.column("Mobile", width=120, anchor="center")
        self.tree.column("Items", width=80, anchor="center")
        self.tree.column("Total", width=110, anchor="e")
        self.tree.column("Paid", width=110, anchor="e")
        self.tree.column("Balance", width=110, anchor="e")
        
        # Configure row tags
        self.tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        self.tree.tag_configure('hasbalance', background='#3a2e1e', foreground='#ffd93d')
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        # Double-click to view details or settle if pending
        self.tree.bind("<Double-Button-1>", self.on_double_click)
        # Right-click context menu
        self.tree.bind("<Button-3>", self.show_context_menu)
    
    def on_double_click(self, event):
        """Handle double-click on bill row"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        balance_str = item['values'][7]  # Balance column
        
        try:
            balance = float(balance_str)
        except:
            balance = 0
        
        # If pending balance, open settlement dialog; otherwise view details
        if balance > 0:
            self.settle_balance()
        else:
            self.view_bill_details()
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select row under cursor
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            
            # Get bill balance
            item = self.tree.item(row_id)
            balance_str = item['values'][7]
            
            try:
                balance = float(balance_str)
            except:
                balance = 0
            
            # Create context menu
            menu = ctk.CTkToplevel(self)
            menu.wm_overrideredirect(True)
            menu.configure(fg_color="#2d2d2d", corner_radius=15)
            
            # Position menu at cursor
            x = event.x_root
            y = event.y_root
            menu.geometry(f"+{x}+{y}")
            
            # Menu frame for rounded appearance
            menu_frame = ctk.CTkFrame(menu, fg_color="#2d2d2d", corner_radius=15)
            menu_frame.pack(padx=2, pady=2)
            
            # Menu items
            if balance > 0:
                ctk.CTkButton(
                    menu_frame,
                    text="💰 Settle Balance",
                    command=lambda: [menu.destroy(), self.settle_balance()],
                    fg_color="#00cc66",
                    hover_color="#00aa55",
                    corner_radius=15,
                    width=180,
                    height=35,
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(padx=5, pady=(5, 3))
            
            ctk.CTkButton(
                menu_frame,
                text="📄 View Details",
                command=lambda: [menu.destroy(), self.view_bill_details()],
                fg_color="#8C00FF",
                hover_color="#7300D6",
                corner_radius=15,
                width=180,
                height=35,
                font=ctk.CTkFont(size=12)
            ).pack(padx=5, pady=3)
            
            ctk.CTkButton(
                menu_frame,
                text="🖨 Reprint Bill",
                command=lambda: [menu.destroy(), self.reprint_bill()],
                fg_color="#8C00FF",
                hover_color="#7300D6",
                corner_radius=15,
                width=180,
                height=35,
                font=ctk.CTkFont(size=12)
            ).pack(padx=5, pady=(3, 5))
            
            # Close menu when clicking elsewhere
            def close_menu(e=None):
                try:
                    menu.destroy()
                except:
                    pass
            
            menu.bind("<FocusOut>", close_menu)
            menu.bind("<Escape>", close_menu)
            self.winfo_toplevel().bind("<Button-1>", lambda e: close_menu(), add="+")
            
            menu.focus_set()
    
    def load_bills(self):
        """Load bills from bills table with filter support"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all bills
        all_bills = self.db_manager.get_all_bills(limit=500)
        
        # Apply customer type filter
        self.filter_type = self.filter_var.get()
        if self.filter_type == "registered":
            bills = [b for b in all_bills if b['customer_id'] is not None]
        elif self.filter_type == "guest":
            bills = [b for b in all_bills if b['customer_id'] is None and b['guest_name']]
        else:  # all
            bills = all_bills
        
        # Apply payment status filter (NEW)
        if self.payment_status == "paid":
            bills = [b for b in bills if (b.get('balance_due', 0) or 0) == 0]
        elif self.payment_status == "pending":
            bills = [b for b in bills if (b.get('balance_due', 0) or 0) > 0]
        
        for i, bill in enumerate(bills):
            # Calculate balance
            balance = bill.get('balance_due', 0) or 0
            advance = bill.get('advance_amount', 0) or 0
            
            # Highlight bills with pending balance
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Count items for this bill
            items = self.db_manager.get_bill_items(bill['id'])
            item_count = len(items)
            
            # Display mobile or "Guest Customer"
            mobile_display = bill['mobile_number'] if bill['mobile_number'] else 'Guest Customer'
            
            self.tree.insert("", "end", values=(
                bill['bill_number'],
                bill['created_at'],
                bill['full_name'] or 'Unknown',
                mobile_display,
                item_count,
                f"{bill['total_amount']:.2f}",
                f"{advance:.2f}",
                f"{balance:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bills)} records")
    
    def apply_filter(self):
        """Apply the selected filter and reload bills"""
        self.load_bills()
    
    def on_payment_status_change(self, value):
        """Handle payment status filter change"""
        if value == "All":
            self.payment_status = "all"
        elif value == "Fully Paid":
            self.payment_status = "paid"
        elif value == "Pending":
            self.payment_status = "pending"
        self.load_bills()
    
    def search_bills(self):
        """Search bills with filter support"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_bills()
            return
        
        # Search in bills table
        all_bills = self.db_manager.search_bills(search_term)
        
        # Apply customer type filter
        self.filter_type = self.filter_var.get()
        if self.filter_type == "registered":
            bills = [b for b in all_bills if b['customer_id'] is not None]
        elif self.filter_type == "guest":
            bills = [b for b in all_bills if b['customer_id'] is None and b['guest_name']]
        else:  # all
            bills = all_bills
        
        # Apply payment status filter (NEW)
        if self.payment_status == "paid":
            bills = [b for b in bills if (b.get('balance_due', 0) or 0) == 0]
        elif self.payment_status == "pending":
            bills = [b for b in bills if (b.get('balance_due', 0) or 0) > 0]
        
        for i, bill in enumerate(bills):
            # Calculate balance
            balance = bill.get('balance_due', 0) or 0
            advance = bill.get('advance_amount', 0) or 0
            
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Count items for this bill
            items = self.db_manager.get_bill_items(bill['id'])
            item_count = len(items)
            
            # Display mobile or "Guest Customer"
            mobile_display = bill['mobile_number'] if bill['mobile_number'] else 'Guest Customer'
            
            self.tree.insert("", "end", values=(
                bill['bill_number'],
                bill['created_at'],
                bill['full_name'] or 'Unknown',
                mobile_display,
                item_count,
                f"{bill['total_amount']:.2f}",
                f"{advance:.2f}",
                f"{balance:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(bills)} records")
    
    def view_bill_details(self):
        """View detailed bill information"""
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select a bill to view")
            return
        
        item = self.tree.item(selection[0])
        bill_number = item['values'][0]
        
        bill = self.db_manager.get_bill_by_number(bill_number)
        if not bill:
            MessageDialog.show_error("Error", "Bill not found")
            return
        
        items = self.db_manager.get_bill_items(bill['id'])
        
        # Create details dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Bill Details - {bill_number}")
        dialog.geometry("700x650")
        dialog.transient(self)
        dialog.grab_set()
        
        # Helper to properly close dialog
        def close_dialog():
            try:
                dialog.grab_release()
            except:
                pass
            dialog.destroy()
            # Restore focus to main window
            self.winfo_toplevel().focus_force()
        
        # Handle window close
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)
        
        # Content frame
        details_frame = ctk.CTkScrollableFrame(dialog)
        details_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Bill info
        customer_type = "👤 Guest Customer" if bill.get('guest_name') else "👤 Registered Customer"
        mobile_display = bill['mobile_number'] if bill['mobile_number'] else 'Guest Customer'
        
        info_text = f"""
📄 Bill Number: {bill['bill_number']}
📅 Date: {bill['created_at']}
{customer_type}
👤 Customer: {bill['full_name'] or 'Unknown'}
📱 Mobile: {mobile_display}
        """
        
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=ctk.CTkFont(size=13),
            justify="left"
        )
        info_label.pack(pady=10)
        
        # Items table
        ctk.CTkLabel(
            details_frame,
            text="Items:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))
        
        items_frame = ctk.CTkFrame(details_frame)
        items_frame.pack(fill="both", expand=True, pady=10)
        
        items_columns = ("Item", "Qty", "Unit Price", "Total")
        items_tree = ttk.Treeview(items_frame, columns=items_columns, show="headings", height=8)
        
        for col in items_columns:
            items_tree.heading(col, text=col)
            items_tree.column(col, width=150)
        
        for item_data in items:
            items_tree.insert("", "end", values=(
                item_data['item_name'],
                item_data['quantity'],
                f"{item_data['unit_price']:.2f}",
                f"{item_data['total_price']:.2f}"
            ))
        
        items_tree.pack(fill="both", expand=True)
        
        # Payment details
        service_charge = bill.get('service_charge', 0) or 0
        advance = bill.get('advance_amount', 0) or 0
        balance = bill.get('balance_due', 0) or 0
        
        payment_text = f"""
-----------------------------------
Subtotal: LKR {bill['subtotal']:.2f}
Discount: LKR {bill.get('discount', 0):.2f}
Service Charge: LKR {service_charge:.2f}
Total Amount: LKR {bill['total_amount']:.2f}
Advance Paid: LKR {advance:.2f}
Balance Due: LKR {balance:.2f}
        """
        
        payment_label = ctk.CTkLabel(
            details_frame,
            text=payment_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            justify="left"
        )
        payment_label.pack(pady=10, padx=20)
        
        # Close button
        ctk.CTkButton(
            details_frame,
            text="Close",
            command=close_dialog,
            width=150,
            height=40,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(pady=10)
    
    def reprint_bill(self):
        """Reprint selected bill"""
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select a bill to reprint")
            return
        
        item = self.tree.item(selection[0])
        bill_number = item['values'][0]
        
        bill = self.db_manager.get_bill_by_number(bill_number)
        if not bill:
            MessageDialog.show_error("Error", "Bill not found")
            return
        
        items = self.db_manager.get_bill_items(bill['id'])
        
        # Handle guest vs registered customer
        if bill.get('guest_name'):
            customer = {
                'full_name': bill['guest_name'],
                'mobile_number': 'Guest Customer'
            }
        else:
            customer = {
                'full_name': bill['full_name'] or 'Unknown',
                'mobile_number': bill['mobile_number'] or 'N/A'
            }
        
        try:
            # Prepare bill data with correct field names
            bill_data = {
                'bill_number': bill['bill_number'],
                'created_at': bill['created_at'],
                'subtotal': bill['subtotal'],
                'discount': bill.get('discount', 0),
                'service_charge': bill.get('service_charge', 0),
                'total_amount': bill['total_amount'],
                'cash_given': bill.get('cash_given', 0),
                'advance_amount': bill.get('advance_amount', 0),
                'balance_due': bill.get('balance_due', 0),
                'created_by_name': bill.get('created_by_name', 'Staff')
            }
            pdf_path = self.bill_generator.generate_bill(bill_data, items, customer)
            MessageDialog.show_success("Success", f"Bill {bill_number} reprinted successfully!")
            self.bill_generator.open_bill(pdf_path)
        except Exception as e:
            MessageDialog.show_error("Error", f"Failed to reprint bill: {str(e)}")
    
    def delete_selected_bill(self):
        """Delete selected bill (Admin only)"""
        # Verify admin role
        if not self.auth_manager.current_user or self.auth_manager.current_user.get('role') != 'Admin':
            MessageDialog.show_error("Permission Denied", "Only administrators can delete bills")
            return
        
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select a bill to delete")
            return
        
        item = self.tree.item(selection[0])
        bill_number = item['values'][0]
        
        # Confirm deletion
        confirm = MessageDialog.show_confirm(
            "Confirm Deletion",
            f"Are you sure you want to delete bill {bill_number}?\nThis action cannot be undone!"
        )
        
        if not confirm:
            return
        
        bill = self.db_manager.get_bill_by_number(bill_number)
        if not bill:
            MessageDialog.show_error("Error", "Bill not found")
            return
        
        # Delete bill and its items
        try:
            # Delete bill items first
            self.db_manager.execute_query('DELETE FROM bill_items WHERE bill_id = ?', (bill['id'],))
            # Delete bill
            self.db_manager.execute_query('DELETE FROM bills WHERE id = ?', (bill['id'],))
            MessageDialog.show_success("Success", f"Bill {bill_number} deleted successfully")
            self.load_bills()
        except Exception as e:
            MessageDialog.show_error("Error", f"Failed to delete bill: {str(e)}")
        
        # Restore focus to main window
        self.restore_focus()
    
    def settle_balance(self):
        """Settle the remaining balance for a pending bill"""
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select a bill to settle")
            return
        
        item = self.tree.item(selection[0])
        bill_number = item['values'][0]
        balance_str = item['values'][7]  # Balance column
        
        # Check if bill has pending balance
        try:
            balance = float(balance_str)
        except:
            balance = 0
        
        if balance <= 0:
            MessageDialog.show_error("Error", "This bill is already fully paid")
            return
        
        # Get full bill data
        bill = self.db_manager.get_bill_by_number(bill_number)
        if not bill:
            MessageDialog.show_error("Error", "Bill not found")
            return
        
        # Get bill items
        items = self.db_manager.get_bill_items(bill['id'])
        
        # Create settlement dialog
        self.show_settlement_dialog(bill, items)
    
    def show_settlement_dialog(self, bill, items):
        """Show modern settlement dialog with payment input"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Settle Balance - Bill #{bill['bill_number']}")
        dialog.geometry("600x700")
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
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 300
        y = (dialog.winfo_screenheight() // 2) - 350
        dialog.geometry(f"600x700+{x}+{y}")
        
        # Title
        title_frame = ctk.CTkFrame(dialog, fg_color="#8C00FF", corner_radius=20)
        title_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text=f"\ud83d\udcb5 Balance Settlement",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(pady=15)
        
        # Scrollable content
        scroll_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="#0d0d1a",
            corner_radius=20,
            border_width=2,
            border_color="#444444"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Original Bill Details Section
        details_section = ctk.CTkFrame(scroll_frame, fg_color="#1e3a2f", corner_radius=15, border_width=2, border_color="#00ff88")
        details_section.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            details_section,
            text="📋 Original Bill Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff88"
        ).pack(pady=10)
        
        # Parse date to show original advance date clearly
        original_date = bill['created_at']
        if ' ' in original_date:
            advance_date = original_date.split(' ')[0]  # Get date part only
        else:
            advance_date = original_date
        
        bill_info = f"""Bill Number: {bill['bill_number']}
Original Advance Date: {advance_date}
Customer: {bill.get('full_name') or bill.get('guest_name', 'Unknown')}
Mobile: {bill.get('mobile_number', 'Guest Customer')}"""
        
        ctk.CTkLabel(
            details_section,
            text=bill_info,
            font=ctk.CTkFont(size=13),
            justify="left",
            text_color="white"
        ).pack(pady=10, padx=20)
        
        # Items Purchased
        items_section = ctk.CTkFrame(scroll_frame, fg_color="#2d2d5a", corner_radius=15)
        items_section.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            items_section,
            text="\ud83d\udce6 Items Purchased",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=10)
        
        for item in items:
            item_text = f"{item['item_name']} x{item['quantity']} - Rs. {item['total_price']:.2f}"
            ctk.CTkLabel(
                items_section,
                text=item_text,
                font=ctk.CTkFont(size=12),
                text_color="white"
            ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(items_section, text="").pack(pady=5)
        
        # Financial Summary Section
        financial_section = ctk.CTkFrame(scroll_frame, fg_color="#1a1a3e", corner_radius=15, border_width=2, border_color="#ffd93d")
        financial_section.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            financial_section,
            text="\ud83d\udcca Financial Summary",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffd93d"
        ).pack(pady=10)
        
        total_amount = bill['total_amount']
        advance_paid = bill.get('advance_amount', 0) or 0
        balance_due = bill.get('balance_due', 0) or 0
        
        # Financial details
        fin_details_frame = ctk.CTkFrame(financial_section, fg_color="transparent")
        fin_details_frame.pack(fill="x", padx=20, pady=10)
        
        # Total Amount
        total_frame = ctk.CTkFrame(fin_details_frame, fg_color="transparent")
        total_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(total_frame, text="Total Amount:", font=ctk.CTkFont(size=13)).pack(side="left")
        ctk.CTkLabel(total_frame, text=f"Rs. {total_amount:.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="white").pack(side="right")
        
        # Advance Paid
        advance_frame = ctk.CTkFrame(fin_details_frame, fg_color="transparent")
        advance_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(advance_frame, text="Advance Paid:", font=ctk.CTkFont(size=13), text_color="#00ff88").pack(side="left")
        ctk.CTkLabel(advance_frame, text=f"Rs. {advance_paid:.2f}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#00ff88").pack(side="right")
        
        # Remaining Balance
        balance_frame = ctk.CTkFrame(fin_details_frame, fg_color="transparent")
        balance_frame.pack(fill="x", pady=3)
        ctk.CTkLabel(balance_frame, text="Remaining Balance:", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ff6b6b").pack(side="left")
        ctk.CTkLabel(balance_frame, text=f"Rs. {balance_due:.2f}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ff6b6b").pack(side="right")
        
        # Payment Input Section
        payment_section = ctk.CTkFrame(scroll_frame, fg_color="#0d0d1a", corner_radius=15, border_width=2, border_color="#8C00FF")
        payment_section.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            payment_section,
            text="\ud83d\udcb0 Payment Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8C00FF"
        ).pack(pady=10)
        
        # Cash Received Input
        cash_frame = ctk.CTkFrame(payment_section, fg_color="transparent")
        cash_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            cash_frame,
            text="Cash Received:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        cash_entry = ctk.CTkEntry(
            cash_frame,
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            placeholder_text="Enter amount",
            corner_radius=20,
            border_width=2,
            border_color="#8C00FF"
        )
        cash_entry.pack(side="right")
        cash_entry.insert(0, f"{balance_due:.2f}")
        
        # Change Display
        change_frame = ctk.CTkFrame(payment_section, fg_color="transparent")
        change_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            change_frame,
            text="Change to Return:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        change_label = ctk.CTkLabel(
            change_frame,
            text="Rs. 0.00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff88"
        )
        change_label.pack(side="right")
        
        def calculate_change(event=None):
            try:
                cash = float(cash_entry.get() or 0)
                change = cash - balance_due
                if change >= 0:
                    change_label.configure(text=f"Rs. {change:.2f}", text_color="#00ff88")
                else:
                    change_label.configure(text=f"Rs. {change:.2f}", text_color="#ff6b6b")
            except:
                change_label.configure(text="Invalid", text_color="#ff6b6b")
        
        cash_entry.bind("<KeyRelease>", calculate_change)
        calculate_change()
        
        # Action Buttons
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        def process_settlement():
            try:
                cash_received = float(cash_entry.get() or 0)
            except:
                MessageDialog.show_error("Error", "Please enter a valid cash amount")
                return
            
            if cash_received < balance_due:
                MessageDialog.show_error("Error", f"Cash received (Rs. {cash_received:.2f}) is less than balance due (Rs. {balance_due:.2f})")
                return
            
            # Update bill in database - mark as fully paid
            try:
                # Update bill - add the settlement amount to advance_amount and set balance to 0
                new_advance = advance_paid + balance_due
                
                # Use execute_update for proper database transaction
                success = self.db_manager.execute_update(
                    '''UPDATE bills 
                       SET advance_amount = ?,
                           balance_due = 0
                       WHERE id = ?''',
                    (new_advance, bill['id'])
                )
                
                if not success:
                    MessageDialog.show_error("Error", "Failed to update bill in database")
                    return
                
                # Generate settlement receipt
                settlement_data = {
                    'bill_number': bill['bill_number'],
                    'original_date': bill['created_at'],
                    'settlement_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_amount': total_amount,
                    'advance_paid': advance_paid,
                    'balance_settled': balance_due,
                    'cash_received': cash_received,
                    'change_given': cash_received - balance_due,
                    'created_by_name': bill.get('created_by_name', 'Staff')
                }
                
                # Handle guest vs registered customer
                if bill.get('guest_name'):
                    customer = {
                        'full_name': bill['guest_name'],
                        'mobile_number': 'Guest Customer'
                    }
                else:
                    customer = {
                        'full_name': bill['full_name'] or 'Unknown',
                        'mobile_number': bill['mobile_number'] or 'N/A'
                    }
                
                # Generate settlement receipt
                pdf_path = self.generate_settlement_receipt(settlement_data, items, customer)
                
                MessageDialog.show_success("Success", f"Balance settled successfully!\nReceipt generated.")
                close_dialog()
                self.load_bills()
                
                # Open the receipt
                self.bill_generator.open_bill(pdf_path)
                
            except Exception as e:
                MessageDialog.show_error("Error", f"Failed to settle balance: {str(e)}")
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=close_dialog,
            width=150,
            height=50,
            fg_color="#555555",
            hover_color="#444444",
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="✔ Process Settlement",
            command=process_settlement,
            width=220,
            height=50,
            fg_color="#00ff88",
            text_color="#1a1a2e",
            hover_color="#00cc6a",
            corner_radius=20,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        cash_entry.focus()
    
    def generate_settlement_receipt(self, settlement_data, items, customer):
        """Generate a professional settlement receipt"""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch, mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib import colors
        
        filename = f"SETTLEMENT_{settlement_data['bill_number']}.pdf"
        filepath = os.path.join(self.bill_generator.bills_folder, filename)
        
        # Thermal receipt size
        page_width = 80 * mm
        page_height = 250 * mm
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=(page_width, page_height),
            leftMargin=3*mm,
            rightMargin=3*mm,
            topMargin=3*mm,
            bottomMargin=3*mm
        )
        
        story = []
        
        # Define styles with pure black on white - no gray
        header_style = ParagraphStyle(
            'Header',
            fontSize=11,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
            leading=13
        )
        
        subheader_style = ParagraphStyle(
            'Subheader',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        left_meta_style = ParagraphStyle(
            'LeftMeta',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica',
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        right_total_style = ParagraphStyle(
            'RightTotal',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_RIGHT,
            fontName='Helvetica',
            spaceAfter=2,
            spaceBefore=0,
            leading=10
        )
        
        grand_total_style = ParagraphStyle(
            'GrandTotal',
            fontSize=10,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=2,
            spaceBefore=0,
            leading=12
        )
        
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=7,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=9
        )
        
        def create_solid_line():
            """Create a solid black line divider"""
            from reportlab.platypus import Table as ReportLabTable
            line_data = [['']]
            line_table = ReportLabTable(line_data, colWidths=[74*mm])
            line_table.setStyle(TableStyle([
                ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.black),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))
            return line_table
        
        # === HEADER WITH LOGO ===
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logos', 'billLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50*mm, height=15*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 2*mm))
            except:
                pass
        
        # Official Studio Details
        story.append(Paragraph("<b>Shine Art Studio</b>", header_style))
        story.append(Paragraph("No: 52/1/1, Maravila Road, Nattandiya", subheader_style))
        story.append(Paragraph("Reg No: 26/3610", subheader_style))
        story.append(Paragraph("Tel: 0767898604 / 0322051680", subheader_style))
        story.append(Spacer(1, 3*mm))
        story.append(create_solid_line())
        story.append(Spacer(1, 3*mm))
        
        # === SETTLEMENT RECEIPT TITLE ===
        story.append(Paragraph("<b>BALANCE SETTLEMENT RECEIPT</b>", header_style))
        story.append(Spacer(1, 3*mm))
        
        # Extract date from original date
        original_date = settlement_data['original_date']
        if ' ' in original_date:
            advance_date_display = original_date.split(' ')[0]
        else:
            advance_date_display = original_date
        
        # Bill and Customer Details (Left-Aligned)
        story.append(Paragraph(f"<b>Bill No:</b> {settlement_data['bill_number']}", left_meta_style))
        story.append(Paragraph(f"<b>Original Advance Date:</b> {advance_date_display}", left_meta_style))
        story.append(Spacer(1, 2*mm))
        
        story.append(Paragraph(f"<b>Customer:</b> {customer['full_name']}", left_meta_style))
        story.append(Paragraph(f"<b>Mobile:</b> {customer['mobile_number']}", left_meta_style))
        story.append(Spacer(1, 2*mm))
        
        story.append(Paragraph(f"<b>Settlement Date:</b> {settlement_data['settlement_date']}", left_meta_style))
        story.append(Spacer(1, 3*mm))
        story.append(create_solid_line())
        story.append(Spacer(1, 3*mm))
        
        # === PAYMENT HISTORY ===
        story.append(Paragraph("<b>Payment History</b>", header_style))
        story.append(Spacer(1, 2*mm))
        
        # Create financial breakdown table for proper alignment
        financial_data = [
            ['Original Total Amount:', f'Rs. {settlement_data["total_amount"]:.2f}'],
            [f'Advance Paid ({advance_date_display}):', f'Rs. {settlement_data["advance_paid"]:.2f}'],
            ['Remaining Balance:', f'Rs. {settlement_data["balance_settled"]:.2f}']
        ]
        
        financial_table = Table(financial_data, colWidths=[45*mm, 29*mm])
        financial_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(financial_table)
        story.append(Spacer(1, 3*mm))
        story.append(create_solid_line())
        story.append(Spacer(1, 3*mm))
        
        # === ITEMS TABLE ===
        story.append(Paragraph("<b>Items Purchased</b>", left_meta_style))
        story.append(Spacer(1, 2*mm))
        
        # Build items table
        item_data = [['Item', 'Qty', 'Amount']]
        for item in items:
            item_data.append([
                item['item_name'],
                str(item['quantity']),
                f"Rs. {item['total_price']:.2f}"
            ])
        
        col_widths = [42*mm, 12*mm, 20*mm]
        item_table = Table(item_data, colWidths=col_widths)
        item_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(item_table)
        story.append(Spacer(1, 3*mm))
        story.append(create_solid_line())
        story.append(Spacer(1, 3*mm))
        
        # === FINAL SETTLEMENT SUMMARY ===
        story.append(Paragraph("<b>Settlement Summary</b>", header_style))
        story.append(Spacer(1, 2*mm))
        
        # Cash and change details
        settlement_summary_data = [
            ['Cash Received:', f'Rs. {settlement_data["cash_received"]:.2f}'],
            ['Balance Settled:', f'Rs. {settlement_data["balance_settled"]:.2f}']
        ]
        
        if settlement_data['change_given'] > 0:
            settlement_summary_data.append(['Change Returned:', f'Rs. {settlement_data["change_given"]:.2f}'])
        
        settlement_table = Table(settlement_summary_data, colWidths=[45*mm, 29*mm])
        settlement_table.setStyle(TableStyle([
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        story.append(settlement_table)
        story.append(Spacer(1, 3*mm))
        
        # STATUS: FULLY PAID
        story.append(Paragraph("<b>STATUS: FULLY PAID</b>", grand_total_style))
        story.append(Spacer(1, 3*mm))
        story.append(create_solid_line())
        story.append(Spacer(1, 3*mm))
        
        # === PROFESSIONAL FOOTER ===
        story.append(Paragraph("Capturing your dreams, Creating the art.", footer_style))
        story.append(Spacer(1, 3*mm))
        
        # Developer credit
        story.append(Paragraph("System Developed by: Malinda Prabath | Email: malindaprabath876@gmail.com", footer_style))
        story.append(Spacer(1, 2*mm))
        
        # Build PDF
        doc.build(story)
        
        return filepath
