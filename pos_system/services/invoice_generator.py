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
            leftMargin=20*mm,
            rightMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Logo - COLOR version (LARGE)
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=70*mm, height=70*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 8*mm))
            except:
                pass
        
        # Invoice title - LARGE
        invoice_title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=5
        )
        story.append(Paragraph("INVOICE", invoice_title_style))
        
        # Company name - smaller than INVOICE
        company_style = ParagraphStyle(
            'CompanyName',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=3
        )
        story.append(Paragraph("SHINE ART STUDIO", company_style))
        
        # Address - clean
        address_style = ParagraphStyle(
            'Address',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=1
        )
        story.append(Paragraph("No:52/1/1, Maravila Road, Nattandiya", address_style))
        story.append(Paragraph("Tel: 0767898604", address_style))
        story.append(Spacer(1, 10*mm))
        
        # Invoice metadata
        normal_style = ParagraphStyle(
            'InvoiceNormal',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )
        
        info_bold = ParagraphStyle(
            'InfoBold',
            parent=styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold'
        )
        
        meta_data = [
            ['Invoice No:', invoice_data['invoice_number']],
            ['Date:', invoice_data['created_at']],
        ]
        
        if booking_ref:
            meta_data.append(['Booking Ref:', booking_ref])
        
        meta_data.append(['Customer:', customer_data['full_name']])
        
        if customer_data.get('mobile_number') and customer_data['mobile_number'] != 'Guest Customer':
            meta_data.append(['Mobile:', customer_data['mobile_number']])
        
        meta_table = Table(meta_data, colWidths=[40*mm, 130*mm])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 8*mm))
        
        story.append(Spacer(1, 8*mm))
        
        # Items table
        table_data = [['Description', 'Qty', 'Unit Price', 'Amount']]
        
        for item in items:
            item_name = item['item_name']
            if item['item_type'] == 'CategoryService':
                item_name = 'Service Charge'
            
            table_data.append([
                item_name,
                str(item['quantity']),
                f"Rs. {item['unit_price']:.2f}",
                f"Rs. {item['total_price']:.2f}"
            ])
        
        items_table = Table(table_data, colWidths=[85*mm, 20*mm, 35*mm, 30*mm])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # Totals section
        subtotal = invoice_data['subtotal']
        service_charge = invoice_data.get('category_service_cost', 0) or 0
        discount = invoice_data['discount']
        total = invoice_data['total_amount']
        advance = invoice_data.get('advance_payment', 0) or 0
        balance = invoice_data['balance_amount']
        
        totals_data = [
            ['Subtotal:', f"Rs. {subtotal:.2f}"],
        ]
        
        if discount > 0:
            totals_data.append(['Discount:', f"Rs. {discount:.2f}"])
        
        if service_charge > 0:
            totals_data.append(['Service Charge:', f"Rs. {service_charge:.2f}"])
        
        totals_table = Table(totals_data, colWidths=[120*mm, 50*mm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(totals_table)
        
        # Total line - BOLD
        total_data = [['TOTAL:', f"Rs. {total:.2f}"]]
        total_table = Table(total_data, colWidths=[120*mm, 50*mm])
        total_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, 0), 1.5, colors.black),
        ]))
        
        story.append(total_table)
        story.append(Spacer(1, 10*mm))
        
        # Footer
        footer_style = ParagraphStyle(
            'InvoiceFooter',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#555555'),
            alignment=TA_CENTER,
            leading=11
        )
        
        footer_text = ("Thank you for your business. Shine Art Studio - Nattandiya invoice system "
                      "was developed by Malinda Prabath. For inquiries or support, please contact "
                      "076 220 6157 or email malindaprabath876@gmail.com")
        
        story.append(Paragraph(footer_text, footer_style))
        
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
        
        # Create booking invoice number
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        invoice_number = f"BK-{timestamp}"
        
        # Create filename
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=10,
            alignment=TA_CENTER
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=25
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=12,
            spaceBefore=15
        )
        
        normal_style = styles["Normal"]
        
        # Header - Studio name with styling
        story.append(Paragraph("✨ Shine Art Studio ✨", title_style))
        story.append(Paragraph("Professional Photography Services", subtitle_style))
        
        # Divider line
        divider_table = Table([['']], colWidths=[7*inch])
        divider_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#00d4ff')),
        ]))
        story.append(divider_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Booking Receipt Header
        receipt_header = ParagraphStyle(
            'ReceiptHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#00d4ff'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        story.append(Paragraph("📋 BOOKING RECEIPT", receipt_header))
        
        # Invoice info box
        invoice_info = [
            [Paragraph(f"<b>Receipt No:</b> {invoice_number}", normal_style),
             Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", normal_style)],
            [Paragraph(f"<b>Created By:</b> {created_by_name}", normal_style),
             Paragraph(f"<b>Status:</b> <font color='#ffd93d'>BOOKED</font>", normal_style)]
        ]
        
        info_table = Table(invoice_info, colWidths=[3.5*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a1a2e')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Customer details section
        story.append(Paragraph("👤 Customer Details", heading_style))
        
        customer_data = [
            ['Customer Name:', booking_data['customer_name']],
            ['Mobile Number:', booking_data['mobile_number']],
        ]
        
        customer_table = Table(customer_data, colWidths=[2*inch, 5*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Booking details section
        story.append(Paragraph("📸 Booking Details", heading_style))
        
        # Parse category and service
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
        
        booking_table = Table(booking_details, colWidths=[2*inch, 5*inch])
        booking_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(booking_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Payment details section
        story.append(Paragraph("💰 Payment Summary", heading_style))
        
        full_amount = float(booking_data['full_amount'])
        advance_payment = float(booking_data['advance_payment'])
        balance = full_amount - advance_payment
        
        payment_data = [
            ['Full Amount:', f"LKR {full_amount:,.2f}"],
            ['Advance Paid:', f"LKR {advance_payment:,.2f}"],
        ]
        
        payment_table = Table(payment_data, colWidths=[3*inch, 2.5*inch])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1a1a2e')),
        ]))
        story.append(payment_table)
        
        # Balance due box
        if balance > 0:
            balance_color = colors.HexColor('#ff6b6b')
            balance_text = f"BALANCE DUE: LKR {balance:,.2f}"
        else:
            balance_color = colors.HexColor('#00ff88')
            balance_text = "FULLY PAID"
        
        balance_data = [[Paragraph(f"<b>{balance_text}</b>", ParagraphStyle(
            'Balance',
            parent=normal_style,
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER
        ))]]
        
        balance_table = Table(balance_data, colWidths=[5.5*inch])
        balance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), balance_color),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('BOX', (0, 0), (-1, -1), 2, balance_color),
        ]))
        story.append(Spacer(1, 0.2 * inch))
        story.append(balance_table)
        story.append(Spacer(1, 0.4 * inch))
        
        # Terms and conditions
        terms_style = ParagraphStyle(
            'Terms',
            parent=normal_style,
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=5
        )
        
        story.append(Paragraph("<b>Terms & Conditions:</b>", terms_style))
        story.append(Paragraph("• Advance payment is non-refundable.", terms_style))
        story.append(Paragraph("• Please arrive 15 minutes before your scheduled time.", terms_style))
        story.append(Paragraph("• Rescheduling must be done 24 hours in advance.", terms_style))
        story.append(Paragraph("• Balance payment is due on the day of the photoshoot.", terms_style))
        
        story.append(Spacer(1, 0.4 * inch))
        
        # Divider
        story.append(divider_table)
        story.append(Spacer(1, 0.2 * inch))
        
        # Footer with owner details
        footer_style = ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a1a2e'),
            leading=14
        )
        
        story.append(Paragraph("Thank you for choosing Shine Art Studio! 📷", footer_style))
        story.append(Spacer(1, 0.1 * inch))
        
        # Owner details
        story.append(Paragraph("<b>Malinda Prabath</b>", footer_style))
        story.append(Paragraph("0762206157", footer_style))
        story.append(Paragraph("malindaprabath876@gmail.com", footer_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def print_invoice(self, filepath):
        """Print the invoice using system default printer"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                # Use Windows print command
                os.startfile(filepath, 'print')
                return True
            else:
                # For Linux/Mac
                subprocess.run(['lpr', filepath])
                return True
        except Exception as e:
            print(f"Error printing invoice: {e}")
            return False
