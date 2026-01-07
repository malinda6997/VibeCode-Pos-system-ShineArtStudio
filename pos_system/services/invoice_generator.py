from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from datetime import datetime
import os


class InvoiceGenerator:
    """Generate PDF invoices using ReportLab - A4 Professional Format"""
    
    def __init__(self, invoice_folder='invoices'):
        self.invoice_folder = invoice_folder
        os.makedirs(invoice_folder, exist_ok=True)
    
    def generate_invoice(self, invoice_data, items, customer_data, booking_ref=None):
        """Generate A4 professional invoice"""
        
        filename = f"INV_{invoice_data['invoice_number']}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 40*mm  # Available width after margins
        
        # === HEADER SECTION: Logo Left, INVOICE + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50*mm, height=50*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        # Right side: INVOICE title + meta info
        invoice_title = Paragraph(
            "<b>INVOICE</b>",
            ParagraphStyle('InvTitle', fontSize=28, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold')
        )
        
        meta_style = ParagraphStyle('Meta', fontSize=10, alignment=TA_RIGHT, leading=14)
        invoice_no = Paragraph(f"Invoice No: <b>{invoice_data['invoice_number']}</b>", meta_style)
        invoice_date = Paragraph(f"Date: {invoice_data['created_at']}", meta_style)
        
        # Build right column content
        right_content = Table([
            [invoice_title],
            [Spacer(1, 3*mm)],
            [invoice_no],
            [invoice_date]
        ], colWidths=[page_width*0.5])
        right_content.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.5, page_width*0.5])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 8*mm))
        
        # === COMPANY & CLIENT INFO SECTION ===
        # Left: Company details
        company_info = Table([
            [Paragraph("<b>STUDIO SHINE ART</b>", ParagraphStyle('Co', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph("No:52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=9, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604", ParagraphStyle('Tel', fontSize=9, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Right: Bill To
        bill_to_data = [
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=10, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {customer_data['full_name']}", ParagraphStyle('Cust', fontSize=9))],
        ]
        if customer_data.get('mobile_number') and customer_data['mobile_number'] != 'Guest Customer':
            bill_to_data.append([Paragraph(f"Mobile: {customer_data['mobile_number']}", ParagraphStyle('Mob', fontSize=9))])
        if booking_ref:
            bill_to_data.append([Paragraph(f"Booking Ref: {booking_ref}", ParagraphStyle('Ref', fontSize=9))])
        
        bill_to_info = Table(bill_to_data, colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 10*mm))
        
        # === ITEMS TABLE ===
        desc_style = ParagraphStyle('Desc', fontSize=9, leading=11)
        
        table_data = [[
            Paragraph("<b>Description</b>", desc_style),
            Paragraph("<b>Qty</b>", ParagraphStyle('H', fontSize=9, alignment=TA_CENTER)),
            Paragraph("<b>Unit Price</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT)),
            Paragraph("<b>Amount</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT))
        ]]
        
        for item in items:
            item_name = item['item_name']
            if item.get('item_type') == 'CategoryService':
                item_name = 'Service Charge'
            
            table_data.append([
                Paragraph(item_name, desc_style),
                Paragraph(str(item['quantity']), ParagraphStyle('Q', fontSize=9, alignment=TA_CENTER)),
                Paragraph(f"Rs. {item['unit_price']:,.2f}", ParagraphStyle('P', fontSize=9, alignment=TA_RIGHT)),
                Paragraph(f"Rs. {item['total_price']:,.2f}", ParagraphStyle('A', fontSize=9, alignment=TA_RIGHT))
            ])
        
        col_widths = [page_width*0.50, page_width*0.12, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            # Header row - light gray background
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # All cells - thin borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#999999')),
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 8*mm))
        
        # === FINANCIAL SUMMARY (Bottom Right) ===
        subtotal = invoice_data['subtotal']
        discount = invoice_data.get('discount', 0) or 0
        service_charge = invoice_data.get('category_service_cost', 0) or 0
        total = invoice_data['total_amount']
        advance = invoice_data.get('advance_payment', 0) or 0
        balance = invoice_data.get('balance_amount', total) or total
        
        summary_style = ParagraphStyle('Sum', fontSize=10, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        
        summary_data = [
            [Paragraph("Subtotal:", summary_style), Paragraph(f"Rs. {subtotal:,.2f}", summary_style)],
        ]
        
        if discount > 0:
            summary_data.append([Paragraph("Discount:", summary_style), Paragraph(f"Rs. {discount:,.2f}", summary_style)])
        
        if service_charge > 0:
            summary_data.append([Paragraph("Service Charge:", summary_style), Paragraph(f"Rs. {service_charge:,.2f}", summary_style)])
        
        # TOTAL - Bold and prominent
        summary_data.append([
            Paragraph("<b>TOTAL:</b>", summary_bold), 
            Paragraph(f"<b>Rs. {total:,.2f}</b>", summary_bold)
        ])
        
        if advance > 0:
            summary_data.append([Paragraph("Advance Paid:", summary_style), Paragraph(f"Rs. {advance:,.2f}", summary_style)])
            # Balance Due - Highlighted
            balance_style = ParagraphStyle('Bal', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#c0392b'))
            summary_data.append([Paragraph("Balance Due:", balance_style), Paragraph(f"Rs. {balance:,.2f}", balance_style)])
        
        summary_table = Table(summary_data, colWidths=[45*mm, 45*mm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, -1 if advance == 0 else -3), (-1, -1 if advance == 0 else -3), 1, colors.HexColor('#333333')),
        ]))
        
        # Right-align the summary
        summary_container = Table([[Spacer(1, 1), summary_table]], colWidths=[page_width - 90*mm, 90*mm])
        summary_container.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(summary_container)
        story.append(Spacer(1, 20*mm))
        
        # === FOOTER SECTION ===
        footer_style = ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        dev_style = ParagraphStyle('Dev', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("Developed by Malinda Prabath | 076 220 6157 | malindaprabath876@gmail.com", dev_style))
        
        doc.build(story)
        return filepath
    
    def open_invoice(self, filepath):
        """Open invoice in default PDF viewer"""
        try:
            os.startfile(filepath)
            return True
        except Exception as e:
            print(f"Error opening invoice: {e}")
            return False
    
    def generate_booking_invoice(self, booking_data, created_by_name):
        """Generate PDF booking receipt matching invoice layout"""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        invoice_number = f"BK-{timestamp}"
        
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 40*mm
        
        # === HEADER: Logo Left, Title + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50*mm, height=50*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        # Right side: Title + meta
        title = Paragraph("<b>BOOKING RECEIPT</b>", ParagraphStyle('Title', fontSize=24, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=10, alignment=TA_RIGHT, leading=14)
        receipt_no = Paragraph(f"Receipt No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style)
        
        right_content = Table([[title], [Spacer(1, 3*mm)], [receipt_no], [receipt_date]], colWidths=[page_width*0.5])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.5, page_width*0.5])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 8*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>STUDIO SHINE ART</b>", ParagraphStyle('Co', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph("No:52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=9, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604", ParagraphStyle('Tel', fontSize=9, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=10, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {booking_data['customer_name']}", ParagraphStyle('Cust', fontSize=9))],
            [Paragraph(f"Mobile: {booking_data['mobile_number']}", ParagraphStyle('Mob', fontSize=9))],
            [Paragraph(f"Booking Date: {booking_data['booking_date']}", ParagraphStyle('Date', fontSize=9))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 10*mm))
        
        # === ITEMS TABLE ===
        desc_style = ParagraphStyle('Desc', fontSize=9, leading=11)
        
        # Parse service name
        photoshoot_cat = booking_data['photoshoot_category']
        if ' - ' in photoshoot_cat:
            parts = photoshoot_cat.split(' - ', 1)
            service_name = f"{parts[0]} - {parts[1]}"
        else:
            service_name = photoshoot_cat
        
        full_amount = float(booking_data['full_amount'])
        
        table_data = [
            [Paragraph("<b>Description</b>", desc_style), Paragraph("<b>Qty</b>", ParagraphStyle('H', fontSize=9, alignment=TA_CENTER)), Paragraph("<b>Unit Price</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT)), Paragraph("<b>Amount</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT))],
            [Paragraph(service_name, desc_style), Paragraph("1", ParagraphStyle('Q', fontSize=9, alignment=TA_CENTER)), Paragraph(f"Rs. {full_amount:,.2f}", ParagraphStyle('P', fontSize=9, alignment=TA_RIGHT)), Paragraph(f"Rs. {full_amount:,.2f}", ParagraphStyle('A', fontSize=9, alignment=TA_RIGHT))]
        ]
        
        col_widths = [page_width*0.50, page_width*0.12, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#999999')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 8*mm))
        
        # === FINANCIAL SUMMARY (Right-aligned) ===
        advance_payment = float(booking_data['advance_payment'])
        balance = full_amount - advance_payment
        
        summary_style = ParagraphStyle('Sum', fontSize=10, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        balance_style = ParagraphStyle('Bal', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#c0392b'))
        
        summary_data = [
            [Paragraph("Subtotal:", summary_style), Paragraph(f"Rs. {full_amount:,.2f}", summary_style)],
            [Paragraph("<b>TOTAL:</b>", summary_bold), Paragraph(f"<b>Rs. {full_amount:,.2f}</b>", summary_bold)],
            [Paragraph("Advance Paid:", summary_style), Paragraph(f"Rs. {advance_payment:,.2f}", summary_style)],
            [Paragraph("Balance Due:", balance_style), Paragraph(f"Rs. {balance:,.2f}", balance_style)],
        ]
        
        summary_table = Table(summary_data, colWidths=[45*mm, 45*mm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#333333')),
        ]))
        
        summary_container = Table([[Spacer(1, 1), summary_table]], colWidths=[page_width - 90*mm, 90*mm])
        summary_container.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(summary_container)
        story.append(Spacer(1, 20*mm))
        
        # === FOOTER ===
        footer_style = ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        dev_style = ParagraphStyle('Dev', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("Developed by Malinda Prabath | 076 220 6157 | malindaprabath876@gmail.com", dev_style))
        
        doc.build(story)
        return filepath
    
    def generate_booking_invoice_reprint(self, booking_data, created_by_name, invoice_number):
        """Reprint booking receipt with existing invoice number - matches invoice layout"""
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 40*mm
        
        # === HEADER: Logo Left, Title + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=50*mm, height=50*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        title = Paragraph("<b>BOOKING RECEIPT</b>", ParagraphStyle('Title', fontSize=24, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=10, alignment=TA_RIGHT, leading=14)
        receipt_no = Paragraph(f"Receipt No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Date: {booking_data.get('booking_date', '')}", meta_style)
        
        right_content = Table([[title], [Spacer(1, 3*mm)], [receipt_no], [receipt_date]], colWidths=[page_width*0.5])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.5, page_width*0.5])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 8*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>STUDIO SHINE ART</b>", ParagraphStyle('Co', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph("No:52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=9, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604", ParagraphStyle('Tel', fontSize=9, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=10, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {booking_data['customer_name']}", ParagraphStyle('Cust', fontSize=9))],
            [Paragraph(f"Mobile: {booking_data.get('mobile_number', 'N/A')}", ParagraphStyle('Mob', fontSize=9))],
            [Paragraph(f"Booking Date: {booking_data.get('booking_date', 'N/A')}", ParagraphStyle('Date', fontSize=9))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 10*mm))
        
        # === ITEMS TABLE ===
        desc_style = ParagraphStyle('Desc', fontSize=9, leading=11)
        service_name = booking_data.get('photoshoot_category', 'Photography Service')
        full_amount = float(booking_data.get('full_amount', 0))
        
        table_data = [
            [Paragraph("<b>Description</b>", desc_style), Paragraph("<b>Qty</b>", ParagraphStyle('H', fontSize=9, alignment=TA_CENTER)), Paragraph("<b>Unit Price</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT)), Paragraph("<b>Amount</b>", ParagraphStyle('H', fontSize=9, alignment=TA_RIGHT))],
            [Paragraph(service_name, desc_style), Paragraph("1", ParagraphStyle('Q', fontSize=9, alignment=TA_CENTER)), Paragraph(f"Rs. {full_amount:,.2f}", ParagraphStyle('P', fontSize=9, alignment=TA_RIGHT)), Paragraph(f"Rs. {full_amount:,.2f}", ParagraphStyle('A', fontSize=9, alignment=TA_RIGHT))]
        ]
        
        col_widths = [page_width*0.50, page_width*0.12, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e8e8e8')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#999999')),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 8*mm))
        
        # === FINANCIAL SUMMARY ===
        advance_payment = float(booking_data.get('advance_payment', 0))
        balance = full_amount - advance_payment
        
        summary_style = ParagraphStyle('Sum', fontSize=10, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        balance_style = ParagraphStyle('Bal', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#c0392b'))
        
        summary_data = [
            [Paragraph("Subtotal:", summary_style), Paragraph(f"Rs. {full_amount:,.2f}", summary_style)],
            [Paragraph("<b>TOTAL:</b>", summary_bold), Paragraph(f"<b>Rs. {full_amount:,.2f}</b>", summary_bold)],
            [Paragraph("Advance Paid:", summary_style), Paragraph(f"Rs. {advance_payment:,.2f}", summary_style)],
            [Paragraph("Balance Due:", balance_style), Paragraph(f"Rs. {balance:,.2f}", balance_style)],
        ]
        
        summary_table = Table(summary_data, colWidths=[45*mm, 45*mm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, 1), (-1, 1), 1, colors.HexColor('#333333')),
        ]))
        
        summary_container = Table([[Spacer(1, 1), summary_table]], colWidths=[page_width - 90*mm, 90*mm])
        summary_container.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(summary_container)
        story.append(Spacer(1, 20*mm))
        
        # === FOOTER ===
        footer_style = ParagraphStyle('Footer', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        dev_style = ParagraphStyle('Dev', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 3*mm))
        story.append(Paragraph("Developed by Malinda Prabath | 076 220 6157 | malindaprabath876@gmail.com", dev_style))
        
        doc.build(story)
        return filepath
    
    def print_invoice(self, filepath):
        """Print the invoice using system default printer"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(filepath, 'print')
                return True
            else:
                subprocess.run(['lpr', filepath])
                return True
        except Exception as e:
            print(f"Error printing invoice: {e}")
            return False
