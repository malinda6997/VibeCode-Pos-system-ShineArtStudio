import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class FrameManagementFrame(BaseFrame):
    """Photo frame management interface with profit tracking"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_frame_id = None
        self.create_widgets()
        self.load_frames()
    
    def create_widgets(self):
        """Create frame management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Photo Frame Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Row 0: Frame name and Size
        name_label = ctk.CTkLabel(input_frame, text="Frame Name:", font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=200, height=35)
        self.name_entry.grid(row=0, column=1, padx=15, pady=10)
        
        size_label = ctk.CTkLabel(input_frame, text="Size:", font=ctk.CTkFont(size=13, weight="bold"))
        size_label.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        
        self.size_entry = ctk.CTkEntry(input_frame, width=120, height=35)
        self.size_entry.grid(row=0, column=3, padx=15, pady=10)
        
        # Row 1: Buying Price and Selling Price (Admin only for buying)
        buying_label = ctk.CTkLabel(input_frame, text="Buying Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        buying_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.buying_price_entry = ctk.CTkEntry(input_frame, width=200, height=35)
        self.buying_price_entry.grid(row=1, column=1, padx=15, pady=10)
        
        selling_label = ctk.CTkLabel(input_frame, text="Selling Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        selling_label.grid(row=1, column=2, padx=15, pady=10, sticky="w")
        
        self.selling_price_entry = ctk.CTkEntry(input_frame, width=120, height=35)
        self.selling_price_entry.grid(row=1, column=3, padx=15, pady=10)
        
        # Hide buying price for non-admin users
        if not self.is_admin():
            buying_label.grid_forget()
            self.buying_price_entry.grid_forget()
            # Move selling to buying position
            selling_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
            self.selling_price_entry.grid(row=1, column=1, padx=15, pady=10)
        
        # Row 2: Display Price (legacy) and Quantity
        price_label = ctk.CTkLabel(input_frame, text="Display Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        price_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.price_entry = ctk.CTkEntry(input_frame, width=200, height=35)
        self.price_entry.grid(row=2, column=1, padx=15, pady=10)
        
        quantity_label = ctk.CTkLabel(input_frame, text="Quantity:", font=ctk.CTkFont(size=13, weight="bold"))
        quantity_label.grid(row=2, column=2, padx=15, pady=10, sticky="w")
        
        self.quantity_entry = ctk.CTkEntry(input_frame, width=120, height=35)
        self.quantity_entry.grid(row=2, column=3, padx=15, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, columnspan=4, pady=15)
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Frame",
            command=self.add_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Frame",
            command=self.update_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20,
            state="disabled"
        )
        self.update_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Delete Frame",
            command=self.delete_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff4757",
            hover_color="#ff3344",
            corner_radius=20,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            width=120,
            height=35,
            fg_color="#8C00FF",
            hover_color="#7300D6",
            corner_radius=20
        )
        clear_btn.pack(side="left", padx=5)
        
        # Check admin permissions
        if not self.is_admin():
            self.delete_btn.configure(state="disabled")
        
        # Table section
        table_frame = ctk.CTkFrame(self, fg_color="#060606", border_width=2, border_color="#444444", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Table header
        table_header = ctk.CTkFrame(table_frame, fg_color="#0d0d1a", corner_radius=10, height=50)
        table_header.pack(fill="x", padx=10, pady=(10, 5))
        table_header.pack_propagate(False)
        
        ctk.CTkLabel(
            table_header,
            text="🖼️ Frame Inventory",
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
        
        # Create Treeview - columns vary based on admin status
        if self.is_admin():
            columns = ("ID", "Frame Name", "Size", "Buying", "Selling", "Price", "Qty", "Profit", "Created At")
            self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)
            
            self.tree.heading("ID", text="🔢 ID")
            self.tree.heading("Frame Name", text="🖼️ Frame Name")
            self.tree.heading("Size", text="📐 Size")
            self.tree.heading("Buying", text="💵 Buying")
            self.tree.heading("Selling", text="💰 Selling")
            self.tree.heading("Price", text="🏷️ Display")
            self.tree.heading("Qty", text="📦 Qty")
            self.tree.heading("Profit", text="📈 Profit")
            self.tree.heading("Created At", text="📅 Created")
            
            self.tree.column("ID", width=50, anchor="center")
            self.tree.column("Frame Name", width=150)
            self.tree.column("Size", width=70, anchor="center")
            self.tree.column("Buying", width=90, anchor="e")
            self.tree.column("Selling", width=90, anchor="e")
            self.tree.column("Price", width=90, anchor="e")
            self.tree.column("Qty", width=50, anchor="center")
            self.tree.column("Profit", width=80, anchor="e")
            self.tree.column("Created At", width=130)
        else:
            columns = ("ID", "Frame Name", "Size", "Price", "Quantity", "Created At")
            self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)
            
            self.tree.heading("ID", text="🔢 ID")
            self.tree.heading("Frame Name", text="🖼️ Frame Name")
            self.tree.heading("Size", text="📐 Size")
            self.tree.heading("Price", text="💰 Price (LKR)")
            self.tree.heading("Quantity", text="📦 Quantity")
            self.tree.heading("Created At", text="📅 Created At")
            
            self.tree.column("ID", width=60, anchor="center")
            self.tree.column("Frame Name", width=200)
            self.tree.column("Size", width=100, anchor="center")
            self.tree.column("Price", width=120, anchor="e")
            self.tree.column("Quantity", width=100, anchor="center")
            self.tree.column("Created At", width=180)
        
        # Configure row tags for alternating colors
        self.tree.tag_configure('oddrow', background='#060606', foreground='#e0e0e0')
        self.tree.tag_configure('evenrow', background='#0d0d1a', foreground='#e0e0e0')
        self.tree.tag_configure('lowstock', background='#3a2020', foreground='#ff6b6b')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 5))
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_frame(self):
        """Add new photo frame"""
        name = self.name_entry.get().strip()
        size = self.size_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        buying_price = self.buying_price_entry.get().strip() if self.is_admin() else "0"
        selling_price = self.selling_price_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter frame name")
            return
        
        if not size:
            MessageDialog.show_error("Error", "Please enter size")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid display price")
            return
        
        if not quantity or not self.validate_number(quantity):
            MessageDialog.show_error("Error", "Please enter valid quantity")
            return
        
        if not selling_price or not self.validate_number(selling_price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid selling price")
            return
        
        if self.is_admin() and buying_price and not self.validate_number(buying_price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid buying price")
            return
        
        buying = float(buying_price) if buying_price else 0
        selling = float(selling_price)
        
        # Validate selling price > buying price for profit
        if self.is_admin() and selling < buying:
            if not MessageDialog.show_confirm("Warning", "Selling price is less than buying price. Continue?"):
                return
        
        frame_id = self.db_manager.add_photo_frame(
            name, size, float(price), int(quantity), buying, selling
        )
        
        if frame_id:
            MessageDialog.show_success("Success", "Photo frame added successfully")
            self.clear_form()
            self.load_frames()
        else:
            MessageDialog.show_error("Error", "Failed to add photo frame")
    
    def update_frame(self):
        """Update selected photo frame"""
        if not self.selected_frame_id:
            MessageDialog.show_error("Error", "Please select a frame to update")
            return
        
        name = self.name_entry.get().strip()
        size = self.size_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        buying_price = self.buying_price_entry.get().strip() if self.is_admin() else "0"
        selling_price = self.selling_price_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter frame name")
            return
        
        if not size:
            MessageDialog.show_error("Error", "Please enter size")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid display price")
            return
        
        if not quantity or not self.validate_number(quantity):
            MessageDialog.show_error("Error", "Please enter valid quantity")
            return
        
        if not selling_price or not self.validate_number(selling_price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid selling price")
            return
        
        if self.is_admin() and buying_price and not self.validate_number(buying_price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid buying price")
            return
        
        buying = float(buying_price) if buying_price else 0
        selling = float(selling_price)
        
        # Get existing values if not admin (preserve buying price)
        if not self.is_admin():
            existing = self.db_manager.get_photo_frame_by_id(self.selected_frame_id)
            if existing:
                buying = existing.get('buying_price', 0) or 0
        
        success = self.db_manager.update_photo_frame(
            self.selected_frame_id, name, size, float(price), int(quantity), buying, selling
        )
        
        if success:
            MessageDialog.show_success("Success", "Photo frame updated successfully")
            self.clear_form()
            self.load_frames()
        else:
            MessageDialog.show_error("Error", "Failed to update photo frame")
    
    def delete_frame(self):
        """Delete selected photo frame"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can delete frames")
            return
        
        if not self.selected_frame_id:
            MessageDialog.show_error("Error", "Please select a frame to delete")
            return
        
        if not MessageDialog.show_confirm("Confirm", "Are you sure you want to delete this photo frame?"):
            return
        
        success = self.db_manager.delete_photo_frame(self.selected_frame_id)
        
        if success:
            MessageDialog.show_success("Success", "Photo frame deleted successfully")
            self.clear_form()
            self.load_frames()
        else:
            MessageDialog.show_error("Error", "Failed to delete photo frame")
    
    def clear_form(self):
        """Clear input fields"""
        self.name_entry.delete(0, 'end')
        self.size_entry.delete(0, 'end')
        self.price_entry.delete(0, 'end')
        self.quantity_entry.delete(0, 'end')
        self.selling_price_entry.delete(0, 'end')
        if self.is_admin():
            self.buying_price_entry.delete(0, 'end')
        self.selected_frame_id = None
        self.add_btn.configure(state="normal")
        self.update_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled" if not self.is_admin() else "normal")
        self.name_entry.focus()
    
    def load_frames(self):
        """Load all photo frames"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        frames = self.db_manager.get_all_photo_frames()
        
        for i, frame in enumerate(frames):
            buying = frame.get('buying_price', 0) or 0
            selling = frame.get('selling_price', 0) or 0
            profit = selling - buying
            
            # Color code low stock items, otherwise use alternating colors
            if frame['quantity'] < 10:
                tag = 'lowstock'
            else:
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            if self.is_admin():
                self.tree.insert("", "end", values=(
                    frame['id'],
                    frame['frame_name'],
                    frame['size'],
                    f"{buying:.2f}",
                    f"{selling:.2f}",
                    f"{frame['price']:.2f}",
                    frame['quantity'],
                    f"{profit:.2f}",
                    frame['created_at']
                ), tags=(tag,))
            else:
                self.tree.insert("", "end", values=(
                    frame['id'],
                    frame['frame_name'],
                    frame['size'],
                    f"{frame['price']:.2f}",
                    frame['quantity'],
                    frame['created_at']
                ), tags=(tag,))
        
        # Update record count
        self.record_count_label.configure(text=f"{len(frames)} records")
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_frame_id = values[0]
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, values[1])
        self.size_entry.delete(0, 'end')
        self.size_entry.insert(0, values[2])
        
        if self.is_admin():
            # Admin view: ID, Name, Size, Buying, Selling, Price, Qty, Profit, Created
            self.buying_price_entry.delete(0, 'end')
            self.buying_price_entry.insert(0, values[3])
            self.selling_price_entry.delete(0, 'end')
            self.selling_price_entry.insert(0, values[4])
            self.price_entry.delete(0, 'end')
            self.price_entry.insert(0, values[5])
            self.quantity_entry.delete(0, 'end')
            self.quantity_entry.insert(0, values[6])
        else:
            # Staff view: ID, Name, Size, Price, Qty, Created
            self.price_entry.delete(0, 'end')
            self.price_entry.insert(0, values[3])
            self.quantity_entry.delete(0, 'end')
            self.quantity_entry.insert(0, values[4])
            # Get selling price from database
            frame_data = self.db_manager.get_photo_frame_by_id(self.selected_frame_id)
            if frame_data:
                self.selling_price_entry.delete(0, 'end')
                self.selling_price_entry.insert(0, f"{frame_data.get('selling_price', 0) or 0:.2f}")
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")
        if self.is_admin():
            self.delete_btn.configure(state="normal")
