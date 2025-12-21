import customtkinter as ctk
from ui.components import Toast


class PermissionsFrame(ctk.CTkFrame):
    """Admin frame for managing staff user permissions"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.selected_user_id = None
        self.permission_switches = {}
        
        # Permission definitions with friendly names
        self.permissions_config = [
            ("can_access_dashboard", "📊 Dashboard", "View dashboard analytics and statistics"),
            ("can_access_billing", "💳 Billing", "Create bills and process payments"),
            ("can_access_customers", "👥 Customers", "Manage customer records"),
            ("can_access_categories", "📁 Categories", "Manage service categories"),
            ("can_access_services", "🎨 Services", "Manage photography services"),
            ("can_access_frames", "🖼 Photo Frames", "Manage photo frame inventory"),
            ("can_access_bookings", "📅 Bookings", "Manage customer bookings"),
            ("can_access_invoices", "📄 Invoices", "View invoice history"),
            ("can_access_support", "💬 Support", "Access support page"),
            ("can_access_user_guide", "📖 User Guide", "Access user guide"),
        ]
        
        self.create_ui()
        self.load_staff_users()
    
    def create_ui(self):
        """Create the permissions management UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#1a1a2e", corner_radius=10)
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        title_label = ctk.CTkLabel(
            header_content,
            text="🛡️ User Permissions Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(
            header_content,
            text="Control which features each staff member can access",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        subtitle_label.pack(side="left", padx=(20, 0))
        
        # Main content container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel - User selection
        left_panel = ctk.CTkFrame(content_frame, fg_color="#1a1a2e", corner_radius=10, width=300)
        left_panel.pack(side="left", fill="y", padx=(0, 10))
        left_panel.pack_propagate(False)
        
        user_header = ctk.CTkLabel(
            left_panel,
            text="👤 Select Staff User",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        user_header.pack(pady=(20, 10), padx=20, anchor="w")
        
        # User list scrollable frame
        self.user_list_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        self.user_list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 20))
        
        # Right panel - Permissions
        right_panel = ctk.CTkFrame(content_frame, fg_color="#1a1a2e", corner_radius=10)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Selected user info
        self.selected_user_frame = ctk.CTkFrame(right_panel, fg_color="#252545", corner_radius=8)
        self.selected_user_frame.pack(fill="x", padx=20, pady=20)
        
        self.selected_user_label = ctk.CTkLabel(
            self.selected_user_frame,
            text="Select a staff user from the list",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        self.selected_user_label.pack(pady=15)
        
        # Permissions grid
        perm_header = ctk.CTkLabel(
            right_panel,
            text="Feature Access Permissions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        perm_header.pack(pady=(10, 15), padx=20, anchor="w")
        
        # Scrollable permissions area
        self.perm_scroll = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="transparent",
            scrollbar_button_color="#333355",
            scrollbar_button_hover_color="#444477"
        )
        self.perm_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        # Create permission switches
        for perm_key, perm_name, perm_desc in self.permissions_config:
            self.create_permission_row(perm_key, perm_name, perm_desc)
        
        # Disable switches initially
        self.toggle_switches_state(False)
        
        # Action buttons
        action_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Enable/Disable all buttons
        enable_all_btn = ctk.CTkButton(
            action_frame,
            text="✅ Enable All",
            command=self.enable_all_permissions,
            width=120,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        enable_all_btn.pack(side="left", padx=(0, 10))
        
        disable_all_btn = ctk.CTkButton(
            action_frame,
            text="❌ Disable All",
            command=self.disable_all_permissions,
            width=120,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        disable_all_btn.pack(side="left", padx=(0, 10))
        
        # Save button
        self.save_btn = ctk.CTkButton(
            action_frame,
            text="💾 Save Changes",
            command=self.save_permissions,
            width=150,
            height=40,
            fg_color="#00d4ff",
            hover_color="#00a8cc",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.save_btn.pack(side="right")
    
    def create_permission_row(self, perm_key: str, perm_name: str, perm_desc: str):
        """Create a permission toggle row"""
        row_frame = ctk.CTkFrame(self.perm_scroll, fg_color="#252545", corner_radius=8)
        row_frame.pack(fill="x", pady=5)
        
        content = ctk.CTkFrame(row_frame, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=12)
        
        # Left side - name and description
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=perm_name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        desc_label = ctk.CTkLabel(
            info_frame,
            text=perm_desc,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w"
        )
        desc_label.pack(anchor="w")
        
        # Right side - switch
        switch = ctk.CTkSwitch(
            content,
            text="",
            width=50,
            progress_color="#00d4ff",
            button_color="white",
            button_hover_color="#f0f0f0",
            fg_color="#444466"
        )
        switch.pack(side="right", padx=(10, 0))
        
        self.permission_switches[perm_key] = switch
    
    def load_staff_users(self):
        """Load staff users into the list"""
        # Clear existing
        for widget in self.user_list_frame.winfo_children():
            widget.destroy()
        
        staff_users = self.db_manager.get_all_staff_users()
        
        if not staff_users:
            no_staff_label = ctk.CTkLabel(
                self.user_list_frame,
                text="No staff users found",
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            )
            no_staff_label.pack(pady=20)
            return
        
        for user in staff_users:
            self.create_user_card(user)
    
    def create_user_card(self, user: dict):
        """Create a user selection card"""
        card = ctk.CTkFrame(
            self.user_list_frame,
            fg_color="#252545",
            corner_radius=8,
            cursor="hand2"
        )
        card.pack(fill="x", pady=5)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=12, pady=10)
        
        # Avatar
        avatar = ctk.CTkLabel(
            content,
            text="👤",
            font=ctk.CTkFont(size=20),
            width=40
        )
        avatar.pack(side="left")
        
        # User info
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=user['full_name'],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        username_label = ctk.CTkLabel(
            info_frame,
            text=f"@{user['username']}",
            font=ctk.CTkFont(size=11),
            text_color="#00d4ff",
            anchor="w"
        )
        username_label.pack(anchor="w")
        
        # Status indicator
        status = "🟢" if user.get('is_active', 1) else "🔴"
        status_label = ctk.CTkLabel(
            content,
            text=status,
            font=ctk.CTkFont(size=14)
        )
        status_label.pack(side="right")
        
        # Bind click event
        user_id = user['id']
        for widget in [card, content, avatar, info_frame, name_label, username_label]:
            widget.bind("<Button-1>", lambda e, uid=user_id, u=user: self.select_user(uid, u))
        
        # Store card reference for highlighting
        card.user_id = user_id
    
    def select_user(self, user_id: int, user: dict):
        """Handle user selection"""
        self.selected_user_id = user_id
        
        # Update selected user display
        self.selected_user_label.configure(
            text=f"👤 {user['full_name']} (@{user['username']})",
            text_color="white"
        )
        
        # Highlight selected card
        for widget in self.user_list_frame.winfo_children():
            if hasattr(widget, 'user_id'):
                if widget.user_id == user_id:
                    widget.configure(fg_color="#00d4ff")
                else:
                    widget.configure(fg_color="#252545")
        
        # Enable switches
        self.toggle_switches_state(True)
        
        # Load user permissions
        self.load_user_permissions(user_id)
    
    def load_user_permissions(self, user_id: int):
        """Load permissions for selected user"""
        permissions = self.db_manager.get_user_permissions(user_id)
        
        if permissions:
            for perm_key, switch in self.permission_switches.items():
                value = permissions.get(perm_key, 1)
                if value:
                    switch.select()
                else:
                    switch.deselect()
        else:
            # Default: all enabled
            for switch in self.permission_switches.values():
                switch.select()
    
    def toggle_switches_state(self, enabled: bool):
        """Enable or disable all switches"""
        state = "normal" if enabled else "disabled"
        for switch in self.permission_switches.values():
            switch.configure(state=state)
    
    def enable_all_permissions(self):
        """Enable all permission switches"""
        if not self.selected_user_id:
            Toast.warning(self, "Please select a staff user first")
            return
        
        for switch in self.permission_switches.values():
            switch.select()
    
    def disable_all_permissions(self):
        """Disable all permission switches"""
        if not self.selected_user_id:
            Toast.warning(self, "Please select a staff user first")
            return
        
        for switch in self.permission_switches.values():
            switch.deselect()
    
    def save_permissions(self):
        """Save permission changes to database"""
        if not self.selected_user_id:
            Toast.warning(self, "Please select a staff user first")
            return
        
        # Gather permission values
        permissions = {}
        for perm_key, switch in self.permission_switches.items():
            permissions[perm_key] = 1 if switch.get() else 0
        
        # Save to database
        success = self.db_manager.update_user_permissions(self.selected_user_id, permissions)
        
        if success:
            Toast.success(self, "Permissions saved successfully!")
        else:
            Toast.error(self, "Failed to save permissions")
