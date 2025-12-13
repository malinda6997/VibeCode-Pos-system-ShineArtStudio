import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class FrameManagementFrame(BaseFrame):
    """Photo frame management interface"""
    
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
        input_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Frame name
        name_label = ctk.CTkLabel(input_frame, text="Frame Name:", font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")
        
        self.name_entry = ctk.CTkEntry(input_frame, width=200, height=35)
        self.name_entry.grid(row=0, column=1, padx=15, pady=10)
        
        # Size
        size_label = ctk.CTkLabel(input_frame, text="Size:", font=ctk.CTkFont(size=13, weight="bold"))
        size_label.grid(row=0, column=2, padx=15, pady=10, sticky="w")
        
        self.size_entry = ctk.CTkEntry(input_frame, width=120, height=35)
        self.size_entry.grid(row=0, column=3, padx=15, pady=10)
        
        # Price
        price_label = ctk.CTkLabel(input_frame, text="Price (LKR):", font=ctk.CTkFont(size=13, weight="bold"))
        price_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.price_entry = ctk.CTkEntry(input_frame, width=200, height=35)
        self.price_entry.grid(row=1, column=1, padx=15, pady=10)
        
        # Quantity
        quantity_label = ctk.CTkLabel(input_frame, text="Quantity:", font=ctk.CTkFont(size=13, weight="bold"))
        quantity_label.grid(row=1, column=2, padx=15, pady=10, sticky="w")
        
        self.quantity_entry = ctk.CTkEntry(input_frame, width=120, height=35)
        self.quantity_entry.grid(row=1, column=3, padx=15, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=4, pady=15)
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="Add Frame",
            command=self.add_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="Update Frame",
            command=self.update_frame,
            width=120,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="orange",
            hover_color="darkorange",
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
            fg_color="red",
            hover_color="darkred",
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Clear",
            command=self.clear_form,
            width=120,
            height=35,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=5)
        
        # Check admin permissions
        if not self.is_admin():
            self.delete_btn.configure(state="disabled")
        
        # Table section
        table_frame = ctk.CTkFrame(self, fg_color="#1e1e3f", corner_radius=15)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create Treeview
        columns = ("ID", "Frame Name", "Size", "Price", "Quantity", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Frame Name", text="Frame Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Price", text="Price (LKR)")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Frame Name", width=200)
        self.tree.column("Size", width=100, anchor="center")
        self.tree.column("Price", width=120, anchor="e")
        self.tree.column("Quantity", width=100, anchor="center")
        self.tree.column("Created At", width=180)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_frame(self):
        """Add new photo frame"""
        name = self.name_entry.get().strip()
        size = self.size_entry.get().strip()
        price = self.price_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter frame name")
            return
        
        if not size:
            MessageDialog.show_error("Error", "Please enter size")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        if not quantity or not self.validate_number(quantity):
            MessageDialog.show_error("Error", "Please enter valid quantity")
            return
        
        frame_id = self.db_manager.add_photo_frame(name, size, float(price), int(quantity))
        
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
        
        if not name:
            MessageDialog.show_error("Error", "Please enter frame name")
            return
        
        if not size:
            MessageDialog.show_error("Error", "Please enter size")
            return
        
        if not price or not self.validate_number(price, allow_decimal=True):
            MessageDialog.show_error("Error", "Please enter valid price")
            return
        
        if not quantity or not self.validate_number(quantity):
            MessageDialog.show_error("Error", "Please enter valid quantity")
            return
        
        success = self.db_manager.update_photo_frame(
            self.selected_frame_id, name, size, float(price), int(quantity)
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
        
        for frame in frames:
            # Color code low stock items
            tags = ('low_stock',) if frame['quantity'] < 10 else ()
            self.tree.insert("", "end", values=(
                frame['id'],
                frame['frame_name'],
                frame['size'],
                f"{frame['price']:.2f}",
                frame['quantity'],
                frame['created_at']
            ), tags=tags)
        
        # Configure tag colors
        self.tree.tag_configure('low_stock', background='#8B0000')
    
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
        self.price_entry.delete(0, 'end')
        self.price_entry.insert(0, values[3])
        self.quantity_entry.delete(0, 'end')
        self.quantity_entry.insert(0, values[4])
        
        self.add_btn.configure(state="disabled")
        self.update_btn.configure(state="normal")
        if self.is_admin():
            self.delete_btn.configure(state="normal")
