from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os


class BillGenerator:
    """Generate thermal receipt style bills (black & white only)"""
    
    def __init__(self, bills_folder='bills'):
        self.bills_folder = bills_folder
        os.makedirs(bills_folder, exist_ok=True)
    
    def generate_bill(self, bill_data, items, customer_data):
        """Generate compact thermal style receipt bill - black & white only"""
        
        filename = f"BILL_{bill_data['bill_number']}.pdf"
        filepath = os.path.join(self.bills_folder, filename)
        
        # Thermal receipt size: narrow width (80mm)
        page_width = 80 * mm
        page_height = 200 * mm  # Dynamic, will expand as needed
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=(page_width, page_height),
            leftMargin=3*mm,
            rightMargin=3*mm,
            topMargin=3*mm,
            bottomMargin=3*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Compact styles - minimal spacing
        header_style = ParagraphStyle(
            'BillHeader',
            fontSize=11,
            textColor=colors.black,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=0,
            spaceBefore=0,
            leading=13
        )
        
        subheader_style = ParagraphStyle(
            'BillSubheader',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        normal_style = ParagraphStyle(
            'BillNormal',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        mono_style = ParagraphStyle(
            'BillMono',
            fontSize=7,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Courier',
            spaceAfter=0,
            spaceBefore=0,
            leading=9
        )
        
        center_style = ParagraphStyle(
            'BillCenter',
            fontSize=8,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        separator = "─" * 32
        
        # === HEADER SECTION WITH LOGO ===
        logo_path = os.path.join('assets', 'logos', 'billLogo.png')
        if os.path.exists(logo_path):
            try:
                # Logo width optimized for 80mm thermal receipt
                logo = Image(logo_path, width=55*mm, height=20*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 1*mm))
            except:
                # Fallback to text if logo fails
                story.append(Paragraph("STUDIO SHINE ART", header_style))
        else:
            # Fallback to text if logo not found
            story.append(Paragraph("STUDIO SHINE ART", header_style))
        
        story.append(Paragraph("No:52/1/1, Maravila Road", subheader_style))
        story.append(Paragraph("Nattandiya", subheader_style))
        story.append(Paragraph("Tel: 0767898604", subheader_style))
        story.append(Spacer(1, 1.5*mm))
        story.append(Paragraph(separator, center_style))
        story.append(Spacer(1, 2*mm))
        
        # === BILL INFO SECTION ===
        bill_info = f"Bill No: {bill_data['bill_number']}"
        story.append(Paragraph(bill_info, normal_style))
        
        date_str = bill_data['created_at']
        story.append(Paragraph(f"Date: {date_str}", normal_style))
        
        cashier = bill_data.get('created_by_name', 'Staff')
        story.append(Paragraph(f"Cashier: {cashier}", normal_style))
        story.append(Spacer(1, 2*mm))
        
        # === CUSTOMER INFO ===
        customer_name = customer_data.get('full_name', 'Guest')
        story.append(Paragraph(f"Customer: {customer_name}", normal_style))
        
        mobile = customer_data.get('mobile_number', '')
        if mobile and mobile != 'Guest Customer':
            story.append(Paragraph(f"Mobile: {mobile}", normal_style))
        story.append(Spacer(1, 3*mm))
        
        # === ITEMIZED LIST (Monospace for alignment) ===
        # Column headers
        header_line = f"{'Item':<18}{'Amt':>8}"
        story.append(Paragraph(header_line, mono_style))
        story.append(Spacer(1, 1*mm))
        
        # Items
        for item in items:
            item_name = item['item_name'][:17]  # Truncate long names
            qty = item['quantity']
            price = item['unit_price']
            total = item['total_price']
            
            # Item name line
            story.append(Paragraph(item_name, mono_style))
            # Qty x Price = Amount line
            detail_line = f"  {qty} x Rs.{price:<7.2f} Rs.{total:>7.2f}"
            story.append(Paragraph(detail_line, mono_style))
        
        story.append(Spacer(1, 3*mm))
        
        # === TOTALS SECTION ===
        subtotal = bill_data['subtotal']
        discount = bill_data.get('discount', 0) or 0
        service_charge = bill_data.get('service_charge', 0) or 0
        total = bill_data['total_amount']
        
        story.append(Paragraph(f"{'Subtotal:':<16} Rs.{subtotal:>8.2f}", mono_style))
        
        if discount > 0:
            story.append(Paragraph(f"{'Discount:':<16} Rs.{discount:>8.2f}", mono_style))
        
        if service_charge > 0:
            story.append(Paragraph(f"{'Service Charge:':<16} Rs.{service_charge:>8.2f}", mono_style))
        
        story.append(Spacer(1, 1*mm))
        
        # TOTAL - Bold style
        total_style = ParagraphStyle(
            'TotalBold',
            fontSize=9,
            textColor=colors.black,
            fontName='Courier-Bold',
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            leading=11
        )
        story.append(Paragraph(f"{'TOTAL:':<16} Rs.{total:>8.2f}", total_style))
        
        # Cash handling
        cash_given = bill_data.get('cash_given', 0) or 0
        if cash_given > 0:
            story.append(Paragraph(f"{'Paid:':<16} Rs.{cash_given:>8.2f}", mono_style))
            balance = cash_given - total
            if balance >= 0:
                story.append(Paragraph(f"{'Change:':<16} Rs.{balance:>8.2f}", mono_style))
        
        story.append(Spacer(1, 5*mm))
        
        # === FOOTER ===
        story.append(Paragraph(f"Issued by: {cashier}", center_style))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph("Thank you! Come again.", center_style))
        story.append(Spacer(1, 1*mm))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def open_bill(self, filepath):
        """Open bill in default PDF viewer"""
        try:
            os.startfile(filepath)
            return True
        except Exception as e:
            print(f"Error opening bill: {e}")
            return False
    
    def print_bill(self, filepath):
        """Print the bill using system default printer"""
        try:
            os.startfile(filepath, 'print')
            return True
        except Exception as e:
            print(f"Error printing bill: {e}")
            return False
