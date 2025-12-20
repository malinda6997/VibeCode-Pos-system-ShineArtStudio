import customtkinter as ctk
from tkinter import ttk
from ui.components import BaseFrame, MessageDialog


class CategoryManagementFrame(BaseFrame):
    """Category management interface - Admin only for add/edit/delete"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, auth_manager, db_manager)
        self.selected_category_id = None
        self.create_widgets()
        self.load_categories()
    
    def create_widgets(self):
        """Create category management widgets"""
        
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Category Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left panel - Form
        left_panel = ctk.CTkFrame(main_container, fg_color="#1e1e3f", corner_radius=15, width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Form section
        form_frame = ctk.CTkFrame(left_panel, fg_color="#252545", corner_radius=10)
        form_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            form_frame,
            text="📁 Category Details",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 20))
        
        # Category name
        ctk.CTkLabel(
            form_frame,
            text="Category Name:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.name_entry = ctk.CTkEntry(
            form_frame, 
            width=300, 
            height=40,
            font=ctk.CTkFont(size=13),
            placeholder_text="Enter category name"
        )
        self.name_entry.pack(padx=20, pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ Add Category",
            command=self.add_category,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc"
        )
        self.add_btn.pack(fill="x", pady=5)
        
        self.update_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Update Category",
            command=self.update_category,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            state="disabled"
        )
        self.update_btn.pack(fill="x", pady=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Category",
            command=self.delete_category,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff4757",
            hover_color="#ff3344",
            state="disabled"
        )
        self.delete_btn.pack(fill="x", pady=5)
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Clear Form",
            command=self.clear_form,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a"
        )
        clear_btn.pack(fill="x", pady=5)
        
        # Admin check - disable buttons for non-admin
        if not self.is_admin():
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            
            # Show info message
            info_label = ctk.CTkLabel(
                form_frame,
                text="⚠️ Only admins can manage categories",
                font=ctk.CTkFont(size=11),
                text_color="#ffd93d"
            )
            info_label.pack(pady=(0, 15))
        
        # Right panel - Table
        right_panel = ctk.CTkFrame(main_container, fg_color="#1e1e3f", corner_radius=15)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Search section
        search_frame = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=10)
        search_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            search_frame, 
            text="🔍 Search:", 
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(search_frame, width=250, height=35)
        self.search_entry.pack(side="left", padx=5, pady=10)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_categories())
        
        ctk.CTkButton(
            search_frame,
            text="Refresh",
            command=self.load_categories,
            width=100,
            height=35
        ).pack(side="left", padx=10)
        
        # Table section
        table_frame = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create Treeview
        columns = ("ID", "Category Name", "Created At")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Category Name", text="Category Name")
        self.tree.heading("Created At", text="Created At")
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Category Name", width=300)
        self.tree.column("Created At", width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def add_category(self):
        """Add new category - Admin only"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can add categories")
            return
        
        name = self.name_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter category name")
            return
        
        # Check if category already exists
        existing = self.db_manager.get_category_by_name(name)
        if existing:
            MessageDialog.show_error("Error", "Category with this name already exists")
            return
        
        category_id = self.db_manager.add_category(name)
        
        if category_id:
            MessageDialog.show_success("Success", "Category added successfully")
            self.clear_form()
            self.load_categories()
        else:
            MessageDialog.show_error("Error", "Failed to add category")
    
    def update_category(self):
        """Update selected category - Admin only"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can update categories")
            return
        
        if not self.selected_category_id:
            MessageDialog.show_error("Error", "Please select a category to update")
            return
        
        name = self.name_entry.get().strip()
        
        if not name:
            MessageDialog.show_error("Error", "Please enter category name")
            return
        
        # Check if name exists for other category
        existing = self.db_manager.get_category_by_name(name)
        if existing and existing['id'] != self.selected_category_id:
            MessageDialog.show_error("Error", "Category with this name already exists")
            return
        
        success = self.db_manager.update_category(self.selected_category_id, name)
        
        if success:
            MessageDialog.show_success("Success", "Category updated successfully")
            self.clear_form()
            self.load_categories()
        else:
            MessageDialog.show_error("Error", "Failed to update category")
    
    def delete_category(self):
        """Delete selected category - Admin only"""
        if not self.is_admin():
            MessageDialog.show_error("Access Denied", "Only admins can delete categories")
            return
        
        if not self.selected_category_id:
            MessageDialog.show_error("Error", "Please select a category to delete")
            return
        
        if not MessageDialog.show_confirm("Confirm Delete", "Are you sure you want to delete this category?\nServices linked to this category will be unlinked."):
            return
        
        success = self.db_manager.delete_category(self.selected_category_id)
        
        if success:
            MessageDialog.show_success("Success", "Category deleted successfully")
            self.clear_form()
            self.load_categories()
        else:
            MessageDialog.show_error("Error", "Failed to delete category")
    
    def clear_form(self):
        """Clear input fields"""
        self.name_entry.delete(0, 'end')
        self.selected_category_id = None
        
        if self.is_admin():
            self.add_btn.configure(state="normal")
            self.update_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
        
        self.name_entry.focus()
    
    def load_categories(self):
        """Load all categories"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = self.db_manager.get_all_categories()
        
        for category in categories:
            self.tree.insert("", "end", values=(
                category['id'],
                category['category_name'],
                category['created_at']
            ))
    
    def search_categories(self):
        """Search categories by name"""
        search_term = self.search_entry.get().strip().lower()
        
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        categories = self.db_manager.get_all_categories()
        
        for category in categories:
            if not search_term or search_term in category['category_name'].lower():
                self.tree.insert("", "end", values=(
                    category['id'],
                    category['category_name'],
                    category['created_at']
                ))
    
    def on_select(self, event):
        """Handle row selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        self.selected_category_id = values[0]
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, values[1])
        
        if self.is_admin():
            self.add_btn.configure(state="disabled")
            self.update_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
