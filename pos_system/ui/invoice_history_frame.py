import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog
from services import InvoiceGenerator


class InvoiceHistoryFrame(BaseFrame):
    """Invoice history viewing and reprinting interface"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.invoice_generator = InvoiceGenerator()
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
        controls_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        controls_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            controls_frame,
            text="Search:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=15, pady=15)
        
        self.search_entry = ctk.CTkEntry(controls_frame, width=300, height=35)
        self.search_entry.pack(side="left", padx=10, pady=15)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_invoices())
        
        ctk.CTkButton(
            controls_frame,
            text="Refresh",
            command=self.load_invoices,
            width=120,
            height=35
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="View Details",
            command=self.view_invoice_details,
            width=120,
            height=35,
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            controls_frame,
            text="Reprint Invoice",
            command=self.reprint_invoice,
            width=140,
            height=35,
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        ).pack(side="left", padx=10)
        
        # Invoices table
        table_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table header
        table_header = ctk.CTkFrame(table_frame, fg_color="#252545", corner_radius=10, height=50)
        table_header.pack(fill="x", padx=10, pady=(10, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="📸 Booking Invoice Records",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#00d4ff"
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
        
        columns = ("Invoice #", "Date", "Customer", "Mobile", "Total", "Paid", "Balance")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=18)
        
        self.tree.heading("Invoice #", text="🔢 Invoice #")
        self.tree.heading("Date", text="📅 Date")
        self.tree.heading("Customer", text="👤 Customer")
        self.tree.heading("Mobile", text="📱 Mobile")
        self.tree.heading("Total", text="💰 Total (LKR)")
        self.tree.heading("Paid", text="✅ Paid (LKR)")
        self.tree.heading("Balance", text="⏳ Balance (LKR)")
        
        self.tree.column("Invoice #", width=120, anchor="center")
        self.tree.column("Date", width=150)
        self.tree.column("Customer", width=200)
        self.tree.column("Mobile", width=120, anchor="center")
        self.tree.column("Total", width=120, anchor="e")
        self.tree.column("Paid", width=120, anchor="e")
        self.tree.column("Balance", width=120, anchor="e")
        
        # Configure row tags
        self.tree.tag_configure('oddrow', background='#1e1e3f', foreground='#e0e0e0')
        self.tree.tag_configure('evenrow', background='#252545', foreground='#e0e0e0')
        self.tree.tag_configure('hasbalance', background='#3a2e1e', foreground='#ffd93d')
        
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        # Double-click to view
        self.tree.bind("<Double-Button-1>", lambda e: self.view_invoice_details())
    
    def load_invoices(self):
        """Load only booking invoices (not bills)"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get only booking invoices (invoice_number starts with 'BK-' or has booking_id)
        all_invoices = self.db_manager.get_all_invoices(limit=200)
        invoices = [inv for inv in all_invoices if inv['invoice_number'].startswith('BK-') or inv.get('booking_id')]
        
        for i, invoice in enumerate(invoices):
            balance = invoice['balance_amount']
            # Highlight invoices with pending balance
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.tree.insert("", "end", values=(
                invoice['invoice_number'],
                invoice['created_at'],
                invoice['full_name'],
                invoice['mobile_number'],
                f"{invoice['total_amount']:.2f}",
                f"{invoice['paid_amount']:.2f}",
                f"{invoice['balance_amount']:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(invoices)} records")
    
    def search_invoices(self):
        """Search booking invoices only"""
        search_term = self.search_entry.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_invoices()
            return
        
        all_invoices = self.db_manager.search_invoices(search_term)
        # Filter to only booking invoices
        invoices = [inv for inv in all_invoices if inv['invoice_number'].startswith('BK-') or inv.get('booking_id')]
        
        for i, invoice in enumerate(invoices):
            balance = invoice['balance_amount']
            if balance > 0:
                tag = 'hasbalance'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.tree.insert("", "end", values=(
                invoice['invoice_number'],
                invoice['created_at'],
                invoice['full_name'],
                invoice['mobile_number'],
                f"{invoice['total_amount']:.2f}",
                f"{invoice['paid_amount']:.2f}",
                f"{invoice['balance_amount']:.2f}"
            ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(invoices)} records")
    
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
            height=40
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
