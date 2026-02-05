from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line as RLLine
from datetime import datetime
import os


class BillGenerator:
    """Generate high-contrast thermal receipt bills (Pure Black & White ONLY)"""
    
    def __init__(self, bills_folder='bills'):
        self.bills_folder = bills_folder
        os.makedirs(bills_folder, exist_ok=True)
    
    def generate_bill(self, bill_data, items, customer_data):
        """Generate thermal style receipt bill - 300 DPI, Pure Black & White, No Gray"""
        
        filename = f"BILL_{bill_data['bill_number']}.pdf"
        filepath = os.path.join(self.bills_folder, filename)
        
        # Thermal receipt size: 80mm width (standard thermal printer)
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
        
        # === PURE BLACK & WHITE STYLES (No Gray) ===
        # Studio name - Bold centered
        studio_name_style = ParagraphStyle(
            'StudioName',
            fontSize=12,
            textColor=colors.HexColor('#000000'),  # Pure Black
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=1*mm,
            spaceBefore=0,
            leading=14
        )
        
        # Address and contact - centered
        subheader_style = ParagraphStyle(
            'BillSubheader',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            alignment=TA_CENTER,
            spaceAfter=0.5*mm,
            spaceBefore=0,
            leading=11
        )
        
        # Left-aligned metadata (Bill No, Date, Cashier, Customer)
        left_meta_style = ParagraphStyle(
            'LeftMeta',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Helvetica',
            alignment=TA_LEFT,
            spaceAfter=1*mm,
            spaceBefore=0,
            leading=11
        )
        
        # Normal text for table items
        normal_style = ParagraphStyle(
            'BillNormal',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            leading=11
        )
        
        # Right-aligned totals style
        right_total_style = ParagraphStyle(
            'RightTotal',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Helvetica',
            alignment=TA_RIGHT,
            spaceAfter=1*mm,
            spaceBefore=0,
            leading=11
        )
        
        # Grand total - BOLD and larger
        grand_total_style = ParagraphStyle(
            'GrandTotal',
            fontSize=12,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Helvetica-Bold',
            alignment=TA_RIGHT,
            spaceAfter=0,
            spaceBefore=0,
            leading=14
        )
        
        # Elegant tagline footer
        footer_elegant_style = ParagraphStyle(
            'FooterElegant',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Times-Italic',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=11
        )
        
        # Developer credit - small but still pure black
        developer_style = ParagraphStyle(
            'DeveloperCredit',
            fontSize=6,
            textColor=colors.HexColor('#000000'),  # Pure Black (not gray)
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            leading=7
        )
        
        # Hair-thin solid BLACK line separator (0.5pt)
        def create_black_separator():
            drawing = Drawing(74*mm, 1*mm)
            line = RLLine(0, 0.5*mm, 74*mm, 0.5*mm)
            line.strokeColor = colors.HexColor('#000000')  # Pure Black
            line.strokeWidth = 0.5  # Hair-thin line
            drawing.add(line)
            return drawing
        
        # === OFFICIAL BRANDING & HEADER (CENTERED) ===
        # Logo at top center - Pure B&W rendering
        logo_path = os.path.join('assets', 'logos', 'billLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60*mm, height=22*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 2*mm))
            except Exception as e:
                print(f"Logo error: {e}")
        
        # Studio Name - BOLD
        story.append(Paragraph("<b>STUDIO SHINE ART</b>", studio_name_style))
        story.append(Spacer(1, 1*mm))
        
        # Centered studio identity
        story.append(Paragraph("No: 52/1/1, Maravila Road, Nattandiya", subheader_style))
        story.append(Paragraph("Reg No: 26/3610 | Tel: 0767898604 / 0322051680", subheader_style))
        story.append(Spacer(1, 3*mm))
        
        # Solid BLACK separator (no gray)
        story.append(create_black_separator())
        story.append(Spacer(1, 3*mm))
        
        # === BODY & TRANSACTION DETAILS (LEFT-ALIGNED) ===
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
        
        # All metadata LEFT-ALIGNED (Clean Sans-Serif)
        story.append(Paragraph(f"<b>Bill No:</b> {bill_data['bill_number']}", left_meta_style))
        story.append(Paragraph(f"<b>Date/Time:</b> {bill_date} | {bill_time}", left_meta_style))
        story.append(Paragraph(f"<b>Cashier:</b> {cashier}", left_meta_style))
        story.append(Paragraph(f"<b>Customer:</b> {customer_name}", left_meta_style))
        
        mobile = customer_data.get('mobile_number', '')
        if mobile and mobile != 'Guest Customer':
            story.append(Paragraph(f"<b>Mobile:</b> {mobile}", left_meta_style))
        
        story.append(Spacer(1, 3*mm))
        story.append(create_black_separator())
        story.append(Spacer(1, 3*mm))
        
        # === ITEMIZATION TABLE (MINIMALIST GRID - No Gray Backgrounds) ===
        # Table header style - BOLD
        table_header_style = ParagraphStyle(
            'TableHeader',
            fontSize=9,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Helvetica-Bold',
            alignment=TA_LEFT,
            spaceAfter=0,
            spaceBefore=0,
            leading=11
        )
        
        # Build table data with proper alignment
        table_data = []
        
        # Header row: ITEM (Left), QTY (Center), AMT (Right)
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
        
        # Create table with PURE BLACK & WHITE styling
        item_table = Table(table_data, colWidths=[42*mm, 15*mm, 17*mm])
        item_table.setStyle(TableStyle([
            # NO BACKGROUND (Pure White)
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFFFF')),  # Pure White
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#000000')),  # Pure Black
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
            ('LEFTPADDING', (0, 0), (-1, -1), 1*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1*mm),
            # Solid BLACK line below header only
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.HexColor('#000000')),  # Pure Black
            # No vertical lines (minimalist)
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        story.append(item_table)
        story.append(Spacer(1, 4*mm))
        story.append(create_black_separator())
        story.append(Spacer(1, 3*mm))
        
        # === SUMMARY & FOOTER (PROFESSIONAL FINISH) ===
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
        
        # Grand Total - BOLD and larger (focal point)
        story.append(Paragraph(f"<b>TOTAL: Rs. {total:.2f}</b>", grand_total_style))
        story.append(Spacer(1, 2*mm))
        
        # === PAYMENT BREAKDOWN ===
        advance_amount = bill_data.get('advance_amount', 0) or 0
        balance_due = bill_data.get('balance_due', 0) or 0
        
        # Determine payment status
        payment_status = "FULL PAYMENT" if balance_due == 0 else "ADVANCE PAYMENT"
        
        # Payment status label - Bold and clear
        payment_status_style = ParagraphStyle(
            'PaymentStatus',
            fontSize=10,
            textColor=colors.HexColor('#000000'),  # Pure Black
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=2*mm,
            spaceBefore=0,
            leading=12
        )
        
        story.append(Paragraph(f"<b>[ {payment_status} ]</b>", payment_status_style))
        story.append(Spacer(1, 2*mm))
        
        if advance_amount > 0 and balance_due > 0:
            # ADVANCE PAYMENT
            story.append(Paragraph(f"<b>Advance Paid: Rs. {advance_amount:.2f}</b>", right_total_style))
            story.append(Paragraph(f"<b>Remaining Balance: Rs. {balance_due:.2f}</b>", grand_total_style))
        else:
            # FULL PAYMENT - Cash and Change
            cash_given = bill_data.get('cash_given', 0) or 0
            if cash_given > 0:
                story.append(Paragraph(f"Cash Received: Rs. {cash_given:.2f}", right_total_style))
                change = cash_given - total
                if change >= 0:
                    story.append(Paragraph(f"Change: Rs. {change:.2f}", right_total_style))
        
        story.append(Spacer(1, 4*mm))
        story.append(create_black_separator())
        story.append(Spacer(1, 4*mm))
        
        # === FOOTER (PROFESSIONAL SIGNATURE) ===
        # Elegant tagline
        story.append(Paragraph("<i>Capturing your dreams, Creating the art.</i>", footer_elegant_style))
        story.append(Spacer(1, 4*mm))
        
        # Developer attribution - Pure Black (not gray)
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
