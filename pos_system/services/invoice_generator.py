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
        """Generate A4 professional invoice - ONLY for bookings"""
        
        filename = f"INV_{invoice_data['invoice_number']}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm  # Available width
        
        # === HEADER SECTION: Logo Left, INVOICE Title Right ===
        header_data = []
        
        # Logo cell - optimized width for A4
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=55*mm, height=55*mm)
                logo_cell = logo
            except:
                logo_cell = Paragraph("STUDIO SHINE ART", ParagraphStyle('Logo', fontSize=18, fontName='Helvetica-Bold'))
        else:
            logo_cell = Paragraph("STUDIO SHINE ART", ParagraphStyle('Logo', fontSize=18, fontName='Helvetica-Bold'))
        
        # Invoice title (right-aligned, bold, large)
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            fontSize=28,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            leading=32
        )
        invoice_title = Paragraph("INVOICE", invoice_title_style)
        
        header_table = Table([[logo_cell, invoice_title]], colWidths=[page_width*0.5, page_width*0.5])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY INFO (Below header) ===
        company_style = ParagraphStyle(
            'CompanyName',
            fontSize=14,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=2
        )
        address_style = ParagraphStyle(
            'Address',
            fontSize=9,
            textColor=colors.HexColor('#555555'),
            alignment=TA_LEFT,
            leading=12
        )
        
        story.append(Paragraph("STUDIO SHINE ART", company_style))
        story.append(Paragraph("No:52/1/1, Maravila Road, Nattandiya", address_style))
        story.append(Paragraph("Tel: 0767898604", address_style))
        story.append(Spacer(1, 8*mm))
        
        # === INVOICE META + CUSTOMER INFO (Two columns) ===
        meta_left = [
            ['Invoice No:', invoice_data['invoice_number']],
            ['Date:', invoice_data['created_at']],
        ]
        if booking_ref:
            meta_left.append(['Booking Ref:', booking_ref])
        
        meta_right = [
            ['Bill To:', ''],
            ['Customer:', customer_data['full_name']],
        ]
        if customer_data.get('mobile_number') and customer_data['mobile_number'] != 'Guest Customer':
            meta_right.append(['Mobile:', customer_data['mobile_number']])
        
        # Left meta table
        left_table = Table(meta_left, colWidths=[30*mm, 55*mm])
        left_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        # Right meta table
        right_table = Table(meta_right, colWidths=[25*mm, 60*mm])
        right_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        meta_combined = Table([[left_table, right_table]], colWidths=[page_width*0.5, page_width*0.5])
        meta_combined.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(meta_combined)
        story.append(Spacer(1, 10*mm))
        
        # === ITEMS TABLE (Professional with zebra stripes) ===
        table_data = [['Description', 'Qty', 'Unit Price', 'Amount']]
        
        for item in items:
            item_name = item['item_name']
            if item.get('item_type') == 'CategoryService':
                item_name = 'Service Charge'
            
            # Wrap long descriptions
            desc_style = ParagraphStyle('ItemDesc', fontSize=9, leading=11)
            item_para = Paragraph(item_name, desc_style)
            
            table_data.append([
                item_para,
                str(item['quantity']),
                f"Rs. {item['unit_price']:.2f}",
                f"Rs. {item['total_price']:.2f}"
            ])
        
        # Column widths: Description wider, others compact
        col_widths = [page_width*0.50, page_width*0.12, page_width*0.19, page_width*0.19]
        
        items_table = Table(table_data, colWidths=col_widths)
        
        # Build style with zebra stripes
        table_style = [
            # Header row - shaded gray
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            
            # All cells - borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#4a4a4a')),
            
            # Content alignment
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # Qty
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),   # Unit Price
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),   # Amount
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),    # Description
            
            # Font size for data rows
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]
        
        # Add zebra stripes (alternating row colors)
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5')))
            else:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        items_table.setStyle(TableStyle(table_style))
        story.append(items_table)
        story.append(Spacer(1, 8*mm))
        
        # === SUMMARY SECTION (Right-aligned) ===
        subtotal = invoice_data['subtotal']
        service_charge = invoice_data.get('category_service_cost', 0) or 0
        discount = invoice_data.get('discount', 0) or 0
        total = invoice_data['total_amount']
        advance = invoice_data.get('advance_payment', 0) or 0
        balance = invoice_data.get('balance_amount', total) or total
        
        summary_data = []
        summary_data.append(['Subtotal:', f"Rs. {subtotal:.2f}"])
        
        if discount > 0:
            summary_data.append(['Discount:', f"Rs. {discount:.2f}"])
        
        if service_charge > 0:
            summary_data.append(['Service Charge:', f"Rs. {service_charge:.2f}"])
        
        # Create summary table (right-aligned within page)
        summary_col_widths = [50*mm, 40*mm]
        summary_table = Table(summary_data, colWidths=summary_col_widths)
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))
        
        # Wrap in container to right-align
        summary_container = Table([[summary_table]], colWidths=[page_width])
        summary_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        story.append(summary_container)
        
        # TOTAL row - Bold, prominent
        total_data = [['TOTAL:', f"Rs. {total:.2f}"]]
        total_table = Table(total_data, colWidths=summary_col_widths)
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.HexColor('#4a4a4a')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a1a2e')),
        ]))
        
        total_container = Table([[total_table]], colWidths=[page_width])
        total_container.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        story.append(total_container)
        
        # Advance and Balance (if applicable)
        if advance > 0:
            story.append(Spacer(1, 3*mm))
            payment_data = [
                ['Advance Paid:', f"Rs. {advance:.2f}"],
                ['Balance Due:', f"Rs. {balance:.2f}"],
            ]
            payment_table = Table(payment_data, colWidths=summary_col_widths)
            payment_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#c0392b')),
            ]))
            
            payment_container = Table([[payment_table]], colWidths=[page_width])
            payment_container.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
            ]))
            story.append(payment_container)
        
        story.append(Spacer(1, 15*mm))
        
        # === PROFESSIONAL FOOTER ===
        footer_style = ParagraphStyle(
            'InvoiceFooter',
            fontSize=8,
            textColor=colors.HexColor('#888888'),
            alignment=TA_CENTER,
            leading=11
        )
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 2*mm))
        
        dev_footer = ParagraphStyle(
            'DevFooter',
            fontSize=7,
            textColor=colors.HexColor('#aaaaaa'),
            alignment=TA_CENTER,
            leading=10
        )
        story.append(Paragraph("Developed by Malinda Prabath | 076 220 6157 | malindaprabath876@gmail.com", dev_footer))
        
        # Build PDF
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
        """Generate PDF invoice for a booking/photoshoot"""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        invoice_number = f"BK-{timestamp}"
        
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm
        
        # === HEADER: Logo Left, INVOICE Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=55*mm, height=55*mm)
                logo_cell = logo
            except:
                logo_cell = Paragraph("STUDIO SHINE ART", ParagraphStyle('Logo', fontSize=18, fontName='Helvetica-Bold'))
        else:
            logo_cell = Paragraph("STUDIO SHINE ART", ParagraphStyle('Logo', fontSize=18, fontName='Helvetica-Bold'))
        
        title_style = ParagraphStyle(
            'BookingTitle',
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
            leading=28
        )
        title_cell = Paragraph("BOOKING RECEIPT", title_style)
        
        header_table = Table([[logo_cell, title_cell]], colWidths=[page_width*0.5, page_width*0.5])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # Company info
        company_style = ParagraphStyle('CompanyName', fontSize=14, textColor=colors.HexColor('#1a1a2e'), fontName='Helvetica-Bold', spaceAfter=2)
        address_style = ParagraphStyle('Address', fontSize=9, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("STUDIO SHINE ART", company_style))
        story.append(Paragraph("No:52/1/1, Maravila Road, Nattandiya | Tel: 0767898604", address_style))
        story.append(Spacer(1, 8*mm))
        
        # Receipt info
        info_data = [
            ['Receipt No:', invoice_number, 'Date:', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Created By:', created_by_name, 'Status:', 'BOOKED'],
        ]
        
        info_table = Table(info_data, colWidths=[25*mm, 55*mm, 20*mm, 45*mm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f8f8')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#e67e22')),
            ('FONTNAME', (3, 1), (3, 1), 'Helvetica-Bold'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 10*mm))
        
        # Section heading style
        section_style = ParagraphStyle(
            'SectionHeading',
            fontSize=11,
            textColor=colors.HexColor('#1a1a2e'),
            fontName='Helvetica-Bold',
            spaceAfter=5,
            spaceBefore=8
        )
        
        # Customer Details
        story.append(Paragraph("Customer Details", section_style))
        customer_data = [
            ['Name:', booking_data['customer_name']],
            ['Mobile:', booking_data['mobile_number']],
        ]
        
        customer_table = Table(customer_data, colWidths=[35*mm, 130*mm])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 8*mm))
        
        # Booking Details
        story.append(Paragraph("Booking Details", section_style))
        
        photoshoot_cat = booking_data['photoshoot_category']
        if ' - ' in photoshoot_cat:
            parts = photoshoot_cat.split(' - ', 1)
            category = parts[0]
            service = parts[1] if len(parts) > 1 else 'N/A'
        else:
            category = photoshoot_cat
            service = 'N/A'
        
        booking_details = [
            ['Category:', category],
            ['Service:', service],
            ['Booking Date:', booking_data['booking_date']],
            ['Location:', booking_data.get('location', 'N/A') or 'N/A'],
        ]
        
        if booking_data.get('description'):
            booking_details.append(['Description:', booking_data['description']])
        
        booking_table = Table(booking_details, colWidths=[35*mm, 130*mm])
        booking_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(booking_table)
        story.append(Spacer(1, 10*mm))
        
        # Payment Summary
        story.append(Paragraph("Payment Summary", section_style))
        
        full_amount = float(booking_data['full_amount'])
        advance_payment = float(booking_data['advance_payment'])
        balance = full_amount - advance_payment
        
        payment_data = [
            ['Full Amount:', f"Rs. {full_amount:,.2f}"],
            ['Advance Paid:', f"Rs. {advance_payment:,.2f}"],
        ]
        
        payment_table = Table(payment_data, colWidths=[page_width*0.6, page_width*0.4])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ]))
        story.append(payment_table)
        
        # Balance Due - Highlighted
        if balance > 0:
            balance_color = colors.HexColor('#e74c3c')
            balance_text = f"BALANCE DUE: Rs. {balance:,.2f}"
        else:
            balance_color = colors.HexColor('#27ae60')
            balance_text = "FULLY PAID"
        
        balance_style = ParagraphStyle(
            'BalanceText',
            fontSize=13,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        balance_data = [[Paragraph(balance_text, balance_style)]]
        balance_table = Table(balance_data, colWidths=[page_width])
        balance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), balance_color),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(Spacer(1, 5*mm))
        story.append(balance_table)
        story.append(Spacer(1, 12*mm))
        
        # Terms and Conditions
        terms_style = ParagraphStyle(
            'Terms',
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            spaceAfter=3,
            leading=10
        )
        
        story.append(Paragraph("<b>Terms & Conditions:</b>", terms_style))
        story.append(Paragraph("• Advance payment is non-refundable.", terms_style))
        story.append(Paragraph("• Please arrive 15 minutes before your scheduled time.", terms_style))
        story.append(Paragraph("• Rescheduling must be done 24 hours in advance.", terms_style))
        story.append(Paragraph("• Balance payment is due on the day of the photoshoot.", terms_style))
        
        story.append(Spacer(1, 15*mm))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#333333'),
            spaceAfter=3
        )
        
        story.append(Paragraph("Thank you for choosing Studio Shine Art!", footer_style))
        story.append(Spacer(1, 3*mm))
        
        dev_footer = ParagraphStyle('DevFooter', fontSize=7, textColor=colors.HexColor('#aaaaaa'), alignment=TA_CENTER)
        story.append(Paragraph("Developed by Malinda Prabath | 076 220 6157 | malindaprabath876@gmail.com", dev_footer))
        
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
