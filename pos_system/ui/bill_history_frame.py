import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services.bill_generator import BillGenerator


class BillHistoryFrame(BaseFrame):
    """Bill history viewing and reprinting interface (thermal bills)"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.bill_generator = BillGenerator()
        self.filter_type = "all"  # 'all', 'registered', 'guest'
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
        
        self.search_entry = ctk.CTkEntry(controls_frame, width=300, height=35)
        self.search_entry.pack(side="left", padx=10, pady=15)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_bills())
        
        ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self.load_bills,
            width=120,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        filter_frame.pack(side="left", padx=15)
        
        ctk.CTkLabel(
            filter_frame,
            text="Filter:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
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
        
        ctk.CTkButton(
            controls_frame,
            text="View Details",
            command=self.view_bill_details,
            width=120,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="Reprint Bill",
            command=self.reprint_bill,
            width=140,
            height=35,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=10)
        
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
        
        # Double-click to view
        self.tree.bind("<Double-Button-1>", lambda e: self.view_bill_details())
    
    def load_bills(self):
        """Load bills from bills table with filter support"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get all bills
        all_bills = self.db_manager.get_all_bills(limit=500)
        
        # Apply filter
        self.filter_type = self.filter_var.get()
        if self.filter_type == "registered":
            bills = [b for b in all_bills if b['customer_id'] is not None]
        elif self.filter_type == "guest":
            bills = [b for b in all_bills if b['customer_id'] is None and b['guest_name']]
        else:  # all
            bills = all_bills
        
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
        
        # Apply filter
        self.filter_type = self.filter_var.get()
        if self.filter_type == "registered":
            bills = [b for b in all_bills if b['customer_id'] is not None]
        elif self.filter_type == "guest":
            bills = [b for b in all_bills if b['customer_id'] is None and b['guest_name']]
        else:  # all
            bills = all_bills
        
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
