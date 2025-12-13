import customtkinter as ctk
from ui.components import Toast
import webbrowser


class SupportFrame(ctk.CTkFrame):
    """Support and help page"""
    
    def __init__(self, parent, auth_manager, db_manager):
        super().__init__(parent, fg_color="transparent")
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create support widgets"""
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header,
            text="💬 Support & Help Center",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main container
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Quick Help Cards Row
        cards_row = ctk.CTkFrame(main, fg_color="transparent")
        cards_row.pack(fill="x", pady=10)
        
        # Card 1 - Phone Support
        self.create_help_card(
            cards_row,
            "📞",
            "Phone Support",
            "Call us directly for immediate assistance",
            "+94 77 123 4567",
            "#00d4ff",
            self.call_support
        )
        
        # Card 2 - WhatsApp
        self.create_help_card(
            cards_row,
            "💬",
            "WhatsApp",
            "Chat with us on WhatsApp",
            "+94 77 123 4567",
            "#25D366",
            self.open_whatsapp
        )
        
        # Card 3 - Email
        self.create_help_card(
            cards_row,
            "📧",
            "Email Support",
            "Send us a detailed message",
            "support@shineart.lk",
            "#ff6b6b",
            self.open_email
        )
        
        # Contact Information Section
        contact_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        contact_section.pack(fill="x", pady=10)
        
        # Section Header
        header_frame = ctk.CTkFrame(contact_section, fg_color="#252545", corner_radius=10)
        header_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            header_frame,
            text="👨‍💻 Developer Contact Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00d4ff"
        ).pack(anchor="w", padx=15, pady=12)
        
        contact_info = ctk.CTkFrame(contact_section, fg_color="transparent")
        contact_info.pack(fill="x", padx=25, pady=(0, 20))
        
        contact_items = [
            ("🏢", "Developer:", "Shine Art Studio Development Team"),
            ("📧", "Email:", "support@shineart.lk"),
            ("📱", "Phone:", "+94 77 123 4567"),
            ("💬", "WhatsApp:", "+94 77 123 4567"),
            ("🌐", "Website:", "www.shineartstudio.lk"),
            ("📍", "Location:", "Colombo, Sri Lanka"),
            ("🕐", "Working Hours:", "Mon - Sat, 9:00 AM - 6:00 PM"),
        ]
        
        for icon, label, value in contact_items:
            self.create_contact_row(contact_info, icon, label, value)
        
        # FAQ Section
        faq_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        faq_section.pack(fill="x", pady=10)
        
        # Section Header
        faq_header = ctk.CTkFrame(faq_section, fg_color="#252545", corner_radius=10)
        faq_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            faq_header,
            text="❓ Frequently Asked Questions",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffd93d"
        ).pack(anchor="w", padx=15, pady=12)
        
        faqs = [
            ("How do I create a new invoice?", 
             "Go to Billing → Search customer → Add items to cart → Click Generate Invoice"),
            ("How do I add a new customer?",
             "Go to Customers → Fill the form → Click Add Customer"),
            ("How do I manage bookings?",
             "Go to Bookings → Select date and customer → Add booking details → Save"),
            ("How do I backup my data?",
             "Go to Settings → Backup & Data → Click 'Backup Database'"),
            ("I forgot my password, what should I do?",
             "Contact the administrator to reset your password"),
            ("How do I print an invoice?",
             "After generating invoice, click Print button to open PDF"),
            ("How do I check low stock items?",
             "Check Dashboard for alerts or go to Photo Frames to see stock levels"),
            ("Can I edit an invoice after it's created?",
             "No, invoices cannot be edited. Create a new one if needed"),
        ]
        
        faq_content = ctk.CTkFrame(faq_section, fg_color="transparent")
        faq_content.pack(fill="x", padx=15, pady=(0, 15))
        
        for question, answer in faqs:
            self.create_faq_item(faq_content, question, answer)
        
        # System Information
        system_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        system_section.pack(fill="x", pady=10)
        
        # Section Header
        sys_header = ctk.CTkFrame(system_section, fg_color="#252545", corner_radius=10)
        sys_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            sys_header,
            text="ℹ️ System Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#00ff88"
        ).pack(anchor="w", padx=15, pady=12)
        
        system_info = ctk.CTkFrame(system_section, fg_color="transparent")
        system_info.pack(fill="x", padx=25, pady=(0, 20))
        
        # System info in a grid
        info_frame = ctk.CTkFrame(system_info, fg_color="#252545", corner_radius=10)
        info_frame.pack(fill="x", pady=5)
        
        info_items = [
            ("Application", "Shine Art Studio POS"),
            ("Version", "1.0.0"),
            ("Release Date", "December 2025"),
            ("Database", "SQLite (Local Storage)"),
            ("Framework", "Python + CustomTkinter"),
            ("Platform", "Windows Desktop"),
        ]
        
        for i, (label, value) in enumerate(info_items):
            row = ctk.CTkFrame(info_frame, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=8)
            
            ctk.CTkLabel(
                row,
                text=f"📌 {label}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=150,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=13),
                text_color="#00d4ff"
            ).pack(side="left")
        
        # Report Issue Section
        report_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        report_section.pack(fill="x", pady=10)
        
        # Section Header
        report_header = ctk.CTkFrame(report_section, fg_color="#252545", corner_radius=10)
        report_header.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            report_header,
            text="🐛 Report an Issue or Bug",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ff6b6b"
        ).pack(anchor="w", padx=15, pady=12)
        
        report_content = ctk.CTkFrame(report_section, fg_color="transparent")
        report_content.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkLabel(
            report_content,
            text="Describe the issue you encountered:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 8))
        
        self.issue_text = ctk.CTkTextbox(
            report_content, 
            height=120, 
            font=ctk.CTkFont(size=13),
            fg_color="#252545",
            border_width=2,
            border_color="#333355"
        )
        self.issue_text.pack(fill="x", pady=(0, 15))
        
        btn_frame = ctk.CTkFrame(report_content, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="📤 Submit Issue Report",
            height=45,
            width=200,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            command=self.submit_issue
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear",
            height=45,
            width=100,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#2d2d5a",
            hover_color="#3d3d7a",
            command=lambda: self.issue_text.delete("1.0", "end")
        ).pack(side="left")
    
    def create_help_card(self, parent, icon, title, desc, contact, color, command):
        """Create a help card"""
        card = ctk.CTkFrame(parent, fg_color="#1e1e3f", corner_radius=15, width=250)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        # Icon circle
        icon_frame = ctk.CTkFrame(card, fg_color=color, width=60, height=60, corner_radius=30)
        icon_frame.pack(pady=(20, 10))
        icon_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=28),
            text_color="white" if color != "#ffd93d" else "#1a1a2e"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(5, 2))
        
        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            card,
            text=contact,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=color
        ).pack(pady=(0, 10))
        
        ctk.CTkButton(
            card,
            text=f"Contact Now",
            height=35,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=color,
            text_color="white" if color != "#ffd93d" else "#1a1a2e",
            hover_color=color,
            command=command
        ).pack(pady=(0, 20), padx=20, fill="x")
    
    def create_contact_row(self, parent, icon, label, value):
        """Create a contact info row"""
        row = ctk.CTkFrame(parent, fg_color="#252545", corner_radius=8)
        row.pack(fill="x", pady=4)
        
        ctk.CTkLabel(
            row,
            text=icon,
            font=ctk.CTkFont(size=16),
            width=40
        ).pack(side="left", padx=(15, 5), pady=10)
        
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            width=130,
            anchor="w"
        ).pack(side="left", pady=10)
        
        ctk.CTkLabel(
            row,
            text=value,
            font=ctk.CTkFont(size=13),
            text_color="#00d4ff"
        ).pack(side="left", pady=10)
    
    def create_faq_item(self, parent, question: str, answer: str):
        """Create an FAQ item"""
        item = ctk.CTkFrame(parent, fg_color="#252545", corner_radius=10)
        item.pack(fill="x", pady=4)
        
        q_label = ctk.CTkLabel(
            item,
            text=f"❓ {question}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#ffd93d",
            wraplength=750,
            justify="left",
            anchor="w"
        )
        q_label.pack(anchor="w", fill="x", padx=15, pady=(12, 5))
        
        a_label = ctk.CTkLabel(
            item,
            text=f"➤ {answer}",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            wraplength=750,
            justify="left",
            anchor="w"
        )
        a_label.pack(anchor="w", fill="x", padx=15, pady=(0, 12))
    
    def call_support(self):
        """Open phone dialer"""
        Toast.info(self, "Call: +94 77 123 4567")
    
    def open_email(self):
        """Open email client"""
        webbrowser.open("mailto:support@shineart.lk?subject=POS%20Support%20Request")
        Toast.success(self, "Opening email client...")
    
    def open_whatsapp(self):
        """Open WhatsApp"""
        webbrowser.open("https://wa.me/94771234567")
        Toast.success(self, "Opening WhatsApp...")
    
    def submit_issue(self):
        """Submit issue report"""
        issue = self.issue_text.get("1.0", "end-1c").strip()
        
        if not issue:
            Toast.error(self, "Please describe the issue")
            return
        
        if len(issue) < 10:
            Toast.error(self, "Please provide more details")
            return
        
        # In a real app, this would send to a server or email
        Toast.success(self, "Issue submitted! We'll contact you soon.")
        self.issue_text.delete("1.0", "end")
