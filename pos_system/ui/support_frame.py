import customtkinter as ctk
from tkinter import messagebox
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
            text="💬 Support & Help",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(side="left")
        
        # Main container
        main = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Contact Information Section
        contact_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        contact_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            contact_section,
            text="📞 Contact Developer",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))
        
        contact_info = ctk.CTkFrame(contact_section, fg_color="transparent")
        contact_info.pack(fill="x", padx=25, pady=(0, 20))
        
        contact_items = [
            ("Developer:", "Your Development Team"),
            ("Email:", "support@shineartstudio.com"),
            ("Phone:", "+94 XX XXX XXXX"),
            ("WhatsApp:", "+94 XX XXX XXXX"),
            ("Working Hours:", "Mon - Sat, 9:00 AM - 6:00 PM"),
        ]
        
        for label, value in contact_items:
            row = ctk.CTkFrame(contact_info, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                row,
                text=label,
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
        
        # Quick Actions
        actions_frame = ctk.CTkFrame(contact_section, fg_color="transparent")
        actions_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkButton(
            actions_frame,
            text="📧 Send Email",
            height=40,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#00d4ff",
            text_color="#1a1a2e",
            hover_color="#00a8cc",
            command=self.open_email
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            actions_frame,
            text="💬 WhatsApp",
            height=40,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#25D366",
            text_color="white",
            hover_color="#1DA851",
            command=self.open_whatsapp
        ).pack(side="left")
        
        # FAQ Section
        faq_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        faq_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            faq_section,
            text="❓ Frequently Asked Questions",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))
        
        faqs = [
            ("How do I create a new invoice?", 
             "Go to Billing from the sidebar, add items to cart, select a customer, and click Generate Invoice."),
            ("How do I add a new customer?",
             "Navigate to Customers from the sidebar, fill in the customer details in the form, and click Add Customer."),
            ("How do I manage bookings?",
             "Go to Bookings from the sidebar. You can view pending bookings, add new ones, and mark them as complete."),
            ("How do I backup my data?",
             "Go to Settings > Backup & Data and click 'Backup Database'. Save the file in a secure location."),
            ("I forgot my password, what should I do?",
             "Contact the administrator or developer to reset your password."),
            ("How do I print an invoice?",
             "After generating an invoice, click the Print button. The invoice will open as a PDF which you can print."),
            ("How do I add new services or frames?",
             "Navigate to Services or Photo Frames from the sidebar and use the Add form to create new entries."),
        ]
        
        faq_content = ctk.CTkFrame(faq_section, fg_color="transparent")
        faq_content.pack(fill="x", padx=25, pady=(0, 20))
        
        for question, answer in faqs:
            self.create_faq_item(faq_content, question, answer)
        
        # System Information
        system_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        system_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            system_section,
            text="ℹ️ System Information",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))
        
        system_info = ctk.CTkFrame(system_section, fg_color="transparent")
        system_info.pack(fill="x", padx=25, pady=(0, 20))
        
        info_items = [
            ("Application:", "Shine Art Studio POS"),
            ("Version:", "1.0.0"),
            ("Build Date:", "2025"),
            ("Database:", "SQLite (Local)"),
            ("Technology:", "Python, CustomTkinter"),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(system_info, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=120,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12),
                text_color="#888888"
            ).pack(side="left")
        
        # Report Issue
        report_section = ctk.CTkFrame(main, fg_color="#1e1e3f", corner_radius=15)
        report_section.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            report_section,
            text="🐛 Report an Issue",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w", padx=25, pady=(20, 15))
        
        report_content = ctk.CTkFrame(report_section, fg_color="transparent")
        report_content.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkLabel(
            report_content,
            text="Issue Description:",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.issue_text = ctk.CTkTextbox(report_content, height=100, font=ctk.CTkFont(size=13))
        self.issue_text.pack(fill="x", pady=(0, 15))
        
        ctk.CTkButton(
            report_content,
            text="📤 Submit Issue Report",
            height=45,
            width=200,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#ff6b6b",
            text_color="white",
            hover_color="#e55555",
            command=self.submit_issue
        ).pack(anchor="w")
    
    def create_faq_item(self, parent, question: str, answer: str):
        """Create an FAQ item"""
        item = ctk.CTkFrame(parent, fg_color="#252545", corner_radius=8)
        item.pack(fill="x", pady=5)
        
        q_label = ctk.CTkLabel(
            item,
            text=f"Q: {question}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00d4ff",
            wraplength=700,
            justify="left"
        )
        q_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        a_label = ctk.CTkLabel(
            item,
            text=f"A: {answer}",
            font=ctk.CTkFont(size=12),
            text_color="#aaaaaa",
            wraplength=700,
            justify="left"
        )
        a_label.pack(anchor="w", padx=15, pady=(0, 10))
    
    def open_email(self):
        """Open email client"""
        webbrowser.open("mailto:support@shineartstudio.com?subject=POS%20Support%20Request")
    
    def open_whatsapp(self):
        """Open WhatsApp"""
        webbrowser.open("https://wa.me/94XXXXXXXXX")
    
    def submit_issue(self):
        """Submit issue report"""
        issue = self.issue_text.get("1.0", "end-1c").strip()
        
        if not issue:
            messagebox.showerror("Error", "Please describe the issue")
            return
        
        # In a real app, this would send to a server or email
        messagebox.showinfo(
            "Issue Reported", 
            "Your issue has been recorded. Our support team will contact you soon.\n\n"
            "For urgent issues, please contact us directly via phone or WhatsApp."
        )
        self.issue_text.delete("1.0", "end")
