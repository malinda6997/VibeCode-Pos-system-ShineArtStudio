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
        
        # === MINIMALIST LUXURY STYLES ===
        # Left-aligned metadata style
        left_meta_style = ParagraphStyle(
            'LeftMeta',
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=1.5*mm,
            spaceBefore=0,
            leading=11
        )
        
        # Right-aligned totals style
        right_total_style = ParagraphStyle(
            'RightTotal',
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica',
            alignment=TA_RIGHT,
            spaceAfter=1*mm,
            spaceBefore=0,
            leading=11
        )
        
        # Grand total bold style
        grand_total_style = ParagraphStyle(
            'GrandTotal',
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            spaceAfter=0,
            spaceBefore=0,
            leading=13
        )
        
        # Elegant footer style
        footer_elegant_style = ParagraphStyle(
            'FooterElegant',
            fontSize=8,
            textColor=colors.black,
            fontName='Times-Italic',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        # Ultra-thin solid gray line (not dashed) - Fixed import
        from reportlab.graphics.shapes import Drawing, Line as RLLine
        
        def create_thin_line():
            drawing = Drawing(74*mm, 1*mm)
            line = RLLine(0, 0.5*mm, 74*mm, 0.5*mm)
            line.strokeColor = colors.HexColor('#CCCCCC')
            line.strokeWidth = 0.5
            drawing.add(line)
            return drawing
        
        # === HEADER & BRANDING (CENTERED ONLY) ===
        # Logo at top center
        logo_path = os.path.join('assets', 'logos', 'billLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60*mm, height=22*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 2*mm))
            except:
                pass
        
        # Centered studio identity
        story.append(Paragraph("No: 52/1/1, Maravila Road, Nattandiya", subheader_style))
        story.append(Paragraph("Reg No: 26/3610 | Tel: 0767898604 / 0322051680", subheader_style))
        story.append(Spacer(1, 3*mm))
        
        # Ultra-thin solid gray separator
        story.append(create_thin_line())
        story.append(Spacer(1, 3*mm))
        
        # === BILL METADATA (PROFESSIONAL LEFT-ALIGN) ===
        # Extract date and time
        date_str = bill_data['created_at']
        try:
            if len(date_str) > 10:
                dt_parts = date_str.split(' ')
                bill_date = dt_parts[0] if len(dt_parts) > 0 else date_str
                bill_time = dt_parts[1] if len(dt_parts) > 1 else ''
            else:
                bill_date = date_str
                bill_time = ''
        except:
            bill_date = date_str
            bill_time = ''
        
        cashier = bill_data.get('created_by_name', 'Staff')
        customer_name = customer_data.get('full_name', 'Guest')
        
        # All metadata left-aligned with adequate spacing
        story.append(Paragraph(f"<b>Bill No:</b> {bill_data['bill_number']}", left_meta_style))
        story.append(Paragraph(f"<b>Date/Time:</b> {bill_date} | {bill_time}", left_meta_style))
        story.append(Paragraph(f"<b>Cashier:</b> {cashier}", left_meta_style))
        story.append(Paragraph(f"<b>Customer:</b> {customer_name}", left_meta_style))
        
        mobile = customer_data.get('mobile_number', '')
        if mobile and mobile != 'Guest Customer':
            story.append(Paragraph(f"<b>Mobile:</b> {mobile}", left_meta_style))
        
        story.append(Spacer(1, 3*mm))
        story.append(create_thin_line())
        story.append(Spacer(1, 3*mm))
        
        # === THE ITEM TABLE (MODERN STANDARD) ===
        # Table header style - subtle bold
        table_header_style = ParagraphStyle(
            'TableHeader',
            fontSize=8,
            textColor=colors.black,
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            leading=10
        )
        
        # Build table data with proper alignment
        table_data = []
        
        # Header row
        header_row = [
            Paragraph("<b>ITEM</b>", table_header_style),
            Paragraph("<b>QTY</b>", ParagraphStyle('TableHeaderCenter', parent=table_header_style, alignment=TA_CENTER)),
            Paragraph("<b>AMT</b>", ParagraphStyle('TableHeaderRight', parent=table_header_style, alignment=TA_RIGHT))
        ]
        table_data.append(header_row)
        
        # Item rows with proper alignment
        for item in items:
            item_name = item['item_name']
            qty = item['quantity']
            total = item['total_price']
            
            item_row = [
                Paragraph(item_name, normal_style),
                Paragraph(str(qty), ParagraphStyle('CenterAlign', parent=normal_style, alignment=TA_CENTER)),
                Paragraph(f"Rs. {total:.2f}", ParagraphStyle('RightAlign', parent=normal_style, alignment=TA_RIGHT))
            ]
            table_data.append(item_row)
        
        # Create table with clean styling
        item_table = Table(table_data, colWidths=[42*mm, 15*mm, 17*mm])
        item_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
            ('LEFTPADDING', (0, 0), (-1, -1), 1*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1*mm),
            # Subtle line below header
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
            # Professional spacing with whitespace (no lines between items)
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(item_table)
        story.append(Spacer(1, 4*mm))
        story.append(create_thin_line())
        story.append(Spacer(1, 3*mm))
        
        # === FINANCIAL SUMMARY (RIGHT-ALIGNED BLOCK) ===
        subtotal = bill_data['subtotal']
        discount = bill_data.get('discount', 0) or 0
        service_charge = bill_data.get('service_charge', 0) or 0
        total = bill_data['total_amount']
        
        # Right-aligned financial block
        story.append(Paragraph(f"Subtotal: Rs. {subtotal:.2f}", right_total_style))
        
        if service_charge > 0:
            story.append(Paragraph(f"Service Charges: Rs. {service_charge:.2f}", right_total_style))
        
        if discount > 0:
            story.append(Paragraph(f"Discount: Rs. {discount:.2f}", right_total_style))
        
        story.append(Spacer(1, 2*mm))
        
        # Grand Total - larger and bold (focal point)
        story.append(Paragraph(f"<b>TOTAL: Rs. {total:.2f}</b>", grand_total_style))
        story.append(Spacer(1, 2*mm))
        
        # === PAYMENT BREAKDOWN ===
        advance_amount = bill_data.get('advance_amount', 0) or 0
        balance_due = bill_data.get('balance_due', 0) or 0
        
        if advance_amount > 0 and balance_due > 0:
            # Advance payment
            story.append(Paragraph(f"Advance Paid: Rs. {advance_amount:.2f}", right_total_style))
            story.append(Paragraph(f"<b>Balance Due: Rs. {balance_due:.2f}</b>", grand_total_style))
        else:
            # Full payment - Cash and Change
            cash_given = bill_data.get('cash_given', 0) or 0
            if cash_given > 0:
                story.append(Paragraph(f"Cash Received: Rs. {cash_given:.2f}", right_total_style))
                change = cash_given - total
                if change >= 0:
                    story.append(Paragraph(f"Change: Rs. {change:.2f}", right_total_style))
        
        story.append(Spacer(1, 4*mm))
        story.append(create_thin_line())
        story.append(Spacer(1, 4*mm))
        
        # === THE FOOTER (PROFESSIONAL SIGNATURE) ===
        # Elegant tagline - centered with serif font
        story.append(Paragraph("<i>Capturing your dreams, Creating the art.</i>", footer_elegant_style))
        story.append(Spacer(1, 4*mm))
        
        # Developer credit - tiny subtle gray font
        developer_style = ParagraphStyle(
            'DeveloperCredit',
            fontSize=5,
            textColor=colors.HexColor('#999999'),
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=6
        )
        story.append(Paragraph("System Developed by: Malinda Prabath | Email: malindaprabath876@gmail.com", developer_style))
        story.append(Spacer(1, 2*mm))
        
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
