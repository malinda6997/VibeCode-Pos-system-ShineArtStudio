import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services import InvoiceGenerator


class InvoiceHistoryFrame(BaseFrame):
    """Invoice history viewing and reprinting interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.invoice_generator = InvoiceGenerator()
        self.current_filter = "All"  # Show all records by default
        self.create_widgets()
        self.load_invoices()
    
    def create_widgets(self):
        """Create invoice history widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Booking Invoices",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Search and controls
        controls_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Left side - Status Filters
        filter_left = ctk.CTkFrame(controls_frame, fg_color="transparent")
        filter_left.pack(side="left", padx=15, pady=15)
        
        ctk.CTkLabel(
            filter_left,
            text="Status:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 5))
        
        self.filter_status = ctk.StringVar(value="All")
        
        ctk.CTkButton(
            filter_left,
            text="All",
            command=lambda: self.filter_by_status("All"),
            width=60,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            filter_left,
            text="Pending",
            command=lambda: self.filter_by_status("Pending"),
            width=75,
            height=35,
            fg_color="#ffa500",
            text_color="#1a1a2e",
            hover_color="#ff8c00",
            corner_radius=20
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            filter_left,
            text="Completed",
            command=lambda: self.filter_by_status("Completed"),
            width=85,
            height=35,
            fg_color="#8C00FF",
            text_color="#ffffff",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            filter_left,
            text="Cancelled",
            command=lambda: self.filter_by_status("Cancelled"),
            width=80,
            height=35,
            fg_color="#ff4757",
            hover_color="#ff3344",
            corner_radius=20
        ).pack(side="left", padx=2)
        
        # Middle - Search
        search_middle = ctk.CTkFrame(controls_frame, fg_color="transparent")
        search_middle.pack(side="left", padx=15, pady=15, fill="x", expand=True)
        
        ctk.CTkLabel(
            search_middle,
            text="Search:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(search_middle, width=200, height=35, corner_radius=15, border_width=1)
        self.search_entry.pack(side="left", padx=5, pady=15)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_invoices())
        
        # Right side - Action buttons
        actions_right = ctk.CTkFrame(controls_frame, fg_color="transparent")
        actions_right.pack(side="right", padx=15, pady=15)
        
        ctk.CTkButton(
            actions_right,
            text="Refresh",
            command=self.load_invoices,
            width=100,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_right,
            text="View Details",
            command=self.view_invoice_details,
            width=110,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_right,
            text="Reprint Invoice",
            command=self.reprint_invoice,
            width=120,
            height=35,
            fg_color="#8C00FF",
            text_color="white",
            hover_color="#7300D6",
            corner_radius=20
        ).pack(side="left", padx=5)
        
        # Admin-only delete buttons
        if self.auth_manager.current_user and self.auth_manager.current_user.get('role') == 'Admin':
            ctk.CTkButton(
                actions_right,
                text="Delete Selected",
                command=self.delete_selected_invoice,
                width=120,
                height=35,
                fg_color="#ff4444",
                text_color="white",
                hover_color="#cc0000",
                corner_radius=20
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                actions_right,
                text="Delete All",
                command=self.delete_all_invoices,
                width=100,
                height=35,
                fg_color="#aa0000",
                text_color="white",
                hover_color="#880000",
                corner_radius=20
            ).pack(side="left", padx=5)
        
        # Invoices table
        table_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table header
        table_header = ctk.CTkFrame(table_frame, fg_color="#0d0d1a", corner_radius=10, height=50)
        table_header.pack(fill="x", padx=10, pady=(10, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="📸 Booking Invoice Records",
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
        
        columns = ("Invoice #", "Date", "Customer", "Mobile", "Service", "Total", "Paid", "Balance")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)
        
        self.tree.heading("Invoice #", text="🔢 Invoice #")
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Customer", text="👤 Customer")
        self.tree.heading("Mobile", text="📱 Mobile")
        self.tree.heading("Service", text="📸 Service")
        self.tree.heading("Total", text="💰 Total (LKR)")
        self.tree.heading("Paid", text="✅ Paid (LKR)")
        self.tree.heading("Balance", text="⏳ Balance (LKR)")
        
        self.tree.column("Invoice #", width=120, anchor="center")
        self.tree.column("Date", width=140)
        self.tree.column("Customer", width=180)
        self.tree.column("Mobile", width=110, anchor="center")
        self.tree.column("Service", width=200)
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
        self.tree.bind("<Double-Button-1>", lambda e: self.view_invoice_details())
    
    def format_service_name(self, service_name):
        """Format service name: remove 'Booking - ' prefix and 'Photoshoot'/'Photography' suffix"""
        if not service_name or service_name == 'N/A':
            return service_name
        
        # Remove 'Booking - ' prefix
        if service_name.startswith('Booking - '):
            service_name = service_name[10:]  # len('Booking - ') = 10
        
        # Remove 'Photoshoot' or 'Photography' suffix (case-insensitive)
        service_name = service_name.strip()
        if service_name.lower().endswith(' photoshoot'):
            service_name = service_name[:-11].strip()  # len(' photoshoot') = 11
        elif service_name.lower().endswith(' photography'):
            service_name = service_name[:-12].strip()  # len(' photography') = 12
        
        return service_name
    
    def get_booking_status(self, booking_id):
        """Get booking status if this is a booking invoice"""
        if not booking_id:
            return "Completed"  # Default for non-booking invoices
        
        booking = self.db_manager.get_booking_by_id(booking_id)
        if booking:
            return booking.get('status', 'Completed')
        return "Completed"
    
    def load_invoices(self):
        """Load booking invoices (respects current filter)"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get only booking invoices (invoice_number starts with 'BK-' or has booking_id)
        all_invoices = self.db_manager.get_all_invoices(limit=200)
        booking_invoices = [inv for inv in all_invoices if inv['invoice_number'].startswith('BK-') or inv.get('booking_id')]
        
        # Apply status filter
        if self.current_filter != "All":
            invoices = []
            for inv in booking_invoices:
                booking_status = self.get_booking_status(inv.get('booking_id'))
                if booking_status == self.current_filter:
                    invoices.append(inv)
        else:
            invoices = booking_invoices
        
        for i, invoice in enumerate(invoices):
            balance = invoice['balance_amount']
            # Highlight invoices with pending balance
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Get service name from booking
            service_name = 'N/A'
            if invoice.get('booking_id'):
                booking = self.db_manager.get_booking_by_id(invoice['booking_id'])
                if booking:
                    service_name = booking.get('photoshoot_category', 'N/A')
                    # Format service name
                    service_name = self.format_service_name(service_name)
            
            self.tree.insert("", "end", values=(
                invoice['invoice_number'],
                invoice['created_at'],
                invoice['full_name'],
                invoice['mobile_number'],
                service_name,
                f"{invoice['total_amount']:.2f}",
                f"{invoice['paid_amount']:.2f}",
                f"{invoice['balance_amount']:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(invoices)} records")
    
    def search_invoices(self):
        """Search booking invoices (respects current filter)"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_invoices()
            return
        
        all_invoices = self.db_manager.search_invoices(search_term)
        # Filter to only booking invoices
        booking_invoices = [inv for inv in all_invoices if inv['invoice_number'].startswith('BK-') or inv.get('booking_id')]
        
        # Apply status filter
        if self.current_filter != "All":
            invoices = []
            for inv in booking_invoices:
                booking_status = self.get_booking_status(inv.get('booking_id'))
                if booking_status == self.current_filter:
                    invoices.append(inv)
        else:
            invoices = booking_invoices
        
        for i, invoice in enumerate(invoices):
            balance = invoice['balance_amount']
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            # Get service name from booking
            service_name = 'N/A'
            if invoice.get('booking_id'):
                booking = self.db_manager.get_booking_by_id(invoice['booking_id'])
                if booking:
                    service_name = booking.get('photoshoot_category', 'N/A')
                    # Format service name
                    service_name = self.format_service_name(service_name)
            
            self.tree.insert("", "end", values=(
                invoice['invoice_number'],
                invoice['created_at'],
                invoice['full_name'],
                invoice['mobile_number'],
                service_name,
                f"{invoice['total_amount']:.2f}",
                f"{invoice['paid_amount']:.2f}",
                f"{invoice['balance_amount']:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(invoices)} records")
    
    def filter_by_status(self, status):
        """Filter invoices by booking status"""
        self.current_filter = status
        self.filter_status.set(status)
        self.load_invoices()
    
    def view_invoice_details(self):
        """View detailed invoice information"""
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select an invoice to view")
            return
        
        item = self.tree.item(selection[0])
        invoice_number = item['values'][0]
        
        invoice = self.db_manager.get_invoice_by_number(invoice_number)
        if not invoice:
            MessageDialog.show_error("Error", "Invoice not found")
            return
        
        items = self.db_manager.get_invoice_items(invoice['id'])
        
        # Create details dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Invoice Details - {invoice_number}")
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
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 350
        y = (dialog.winfo_screenheight() // 2) - 325
        dialog.geometry(f"700x650+{x}+{y}")
        
        # Title
        ctk.CTkLabel(
            dialog,
            text=f"Invoice: {invoice_number}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Details frame
        details_frame = ctk.CTkFrame(dialog)
        details_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Invoice info
        info_text = f"""
Invoice Date: {invoice['created_at']}
Created By: {invoice['created_by_name']}

Customer: {invoice['full_name']}
Mobile: {invoice['mobile_number']}

-----------------------------------
        """
        
        info_label = ctk.CTkLabel(
            details_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=10, padx=20)
        
        # Items table
        ctk.CTkLabel(
            details_frame,
            text="Invoice Items:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        items_tree_frame = ctk.CTkFrame(details_frame)
        items_tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        items_columns = ("Item", "Type", "Qty", "Price", "Total")
        items_tree = ttk.Treeview(items_tree_frame, columns=items_columns, show="headings", height=8)
        
        items_tree.heading("Item", text="Item")
        items_tree.heading("Type", text="Type")
        items_tree.heading("Qty", text="Qty")
        items_tree.heading("Price", text="Unit Price")
        items_tree.heading("Total", text="Total")
        
        items_tree.column("Item", width=250)
        items_tree.column("Type", width=100, anchor="center")
        items_tree.column("Qty", width=60, anchor="center")
        items_tree.column("Price", width=100, anchor="e")
        items_tree.column("Total", width=100, anchor="e")
        
        for item in items:
            items_tree.insert("", "end", values=(
                item['item_name'],
                item['item_type'],
                item['quantity'],
                f"{item['unit_price']:.2f}",
                f"{item['total_price']:.2f}"
            ))
        
        items_tree.pack(fill="both", expand=True)
        
        # Payment details
        payment_text = f"""
-----------------------------------
Subtotal: LKR {invoice['subtotal']:.2f}
Discount: LKR {invoice['discount']:.2f}
Total Amount: LKR {invoice['total_amount']:.2f}
Paid Amount: LKR {invoice['paid_amount']:.2f}
Balance: LKR {invoice['balance_amount']:.2f}
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
    
    def reprint_invoice(self):
        """Reprint selected invoice"""
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select an invoice to reprint")
            return
        
        item = self.tree.item(selection[0])
        invoice_number = item['values'][0]
        
        invoice = self.db_manager.get_invoice_by_number(invoice_number)
        if not invoice:
            MessageDialog.show_error("Error", "Invoice not found")
            return
        
        items = self.db_manager.get_invoice_items(invoice['id'])
        customer = {
            'full_name': invoice['full_name'] or 'Guest',
            'mobile_number': invoice['mobile_number'] or 'N/A'
        }
        
        try:
            # Check if this is a booking invoice (starts with 'BK-')
            if invoice_number.startswith('BK-'):
                # Get booking data for booking invoice
                booking_data = {
                    'customer_name': invoice['full_name'] or invoice.get('guest_name', 'Guest'),
                    'mobile_number': invoice['mobile_number'] or 'N/A',
                    'photoshoot_category': items[0]['item_name'] if items else 'Photography Service',
                    'full_amount': invoice['total_amount'],
                    'advance_payment': invoice.get('advance_payment', 0) or invoice['paid_amount'],
                    'booking_date': invoice['created_at'].split(' ')[0] if invoice['created_at'] else '',
                    'location': '',
                    'description': ''
                }
                # Use existing invoice number instead of generating new one
                pdf_path = self.invoice_generator.generate_booking_invoice_reprint(
                    booking_data, 
                    invoice.get('created_by_name', 'Staff'),
                    invoice_number
                )
            else:
                pdf_path = self.invoice_generator.generate_invoice(invoice, items, customer)
            
            MessageDialog.show_success("Success", f"Invoice {invoice_number} reprinted successfully!")
            self.invoice_generator.open_invoice(pdf_path)
        except Exception as e:
            MessageDialog.show_error("Error", f"Failed to reprint invoice: {str(e)}")
    
    def delete_selected_invoice(self):
        """Delete selected invoice (Admin only)"""
        # Verify admin role
        if not self.auth_manager.current_user or self.auth_manager.current_user.get('role') != 'Admin':
            MessageDialog.show_error("Permission Denied", "Only administrators can delete invoices")
            return
        
        selection = self.tree.selection()
        if not selection:
            MessageDialog.show_error("Error", "Please select an invoice to delete")
            return
        
        item = self.tree.item(selection[0])
        invoice_number = item['values'][0]
        
        # Confirm deletion
        confirm = MessageDialog.show_confirm(
            "Confirm Deletion",
            f"Are you sure you want to delete invoice {invoice_number}?\nThis action cannot be undone!"
        )
        
        if not confirm:
            return
        
        invoice = self.db_manager.get_invoice_by_number(invoice_number)
        if not invoice:
            MessageDialog.show_error("Error", "Invoice not found")
            return
        
        if self.db_manager.delete_invoice(invoice['id']):
            MessageDialog.show_success("Success", f"Invoice {invoice_number} deleted successfully")
            self.load_invoices()
        else:
            MessageDialog.show_error("Error", "Failed to delete invoice")
        
        # Restore focus to main window
        self.restore_focus()
    
    def delete_all_invoices(self):
        """Delete all invoices (Admin only)"""
        # Verify admin role
        if not self.auth_manager.current_user or self.auth_manager.current_user.get('role') != 'Admin':
            MessageDialog.show_error("Permission Denied", "Only administrators can delete all invoices")
            return
        
        # Confirm deletion with warning
        confirm = MessageDialog.show_confirm(
            "⚠️ DANGER: Delete All Invoices",
            "Are you absolutely sure you want to delete ALL invoices?\n\n" +
            "This will permanently remove ALL invoice records and cannot be undone!\n\n" +
            "Click OK to continue to final confirmation."
        )
        
        if not confirm:
            return
        
        # Second confirmation with text input
        from tkinter import simpledialog
        confirmation_text = simpledialog.askstring(
            "Final Confirmation",
            "Type 'DELETE ALL' to confirm:",
            parent=self
        )
        
        if confirmation_text != "DELETE ALL":
            MessageDialog.show_warning("Cancelled", "Deletion cancelled - confirmation text did not match")
            return
        
        if self.db_manager.delete_all_invoices():
            MessageDialog.show_success("Success", "All invoices deleted successfully")
            self.load_invoices()
        else:
            MessageDialog.show_error("Error", "Failed to delete all invoices")
        
        # Restore focus to main window
        self.restore_focus()
