from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Register Unicode font for Sinhala text support
try:
    # Try Iskoola Pota first (Windows built-in, best for Sinhala)
    pdfmetrics.registerFont(TTFont('IskooPota', 'C:/Windows/Fonts/iskpota.ttf'))
    pdfmetrics.registerFont(TTFont('IskooPota-Bold', 'C:/Windows/Fonts/iskpotab.ttf'))
    SINHALA_FONT = 'IskooPota'
    SINHALA_FONT_BOLD = 'IskooPota-Bold'
except:
    try:
        # Fallback to Nirmala UI
        pdfmetrics.registerFont(TTFont('NirmalaUI', 'C:/Windows/Fonts/Nirmala.ttf'))
        pdfmetrics.registerFont(TTFont('NirmalaUI-Bold', 'C:/Windows/Fonts/NirmalaB.ttf'))
        SINHALA_FONT = 'NirmalaUI'
        SINHALA_FONT_BOLD = 'NirmalaUI-Bold'
    except:
        try:
            # Fallback to Arial Unicode MS
            pdfmetrics.registerFont(TTFont('ArialUnicode', 'C:/Windows/Fonts/ARIALUNI.TTF'))
            SINHALA_FONT = 'ArialUnicode'
            SINHALA_FONT_BOLD = 'ArialUnicode'
        except:
            # Final fallback - use default font (Sinhala won't render)
            SINHALA_FONT = 'Helvetica'
            SINHALA_FONT_BOLD = 'Helvetica-Bold'


class InvoiceGenerator:
    """Generate PDF invoices using ReportLab - A4 Professional Format"""
    
    def __init__(self, invoice_folder='invoices'):
        self.invoice_folder = invoice_folder
        os.makedirs(invoice_folder, exist_ok=True)
    
    def generate_invoice(self, invoice_data, items, customer_data, booking_ref=None):
        """Generate A4 professional invoice with premium black theme"""
        
        filename = f"INV_{invoice_data['invoice_number']}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=12*mm,
            bottomMargin=12*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm  # Available width after margins
        
        # === HEADER SECTION: Wide Logo Left, INVOICE + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                # Wide landscape-style logo
                logo = Image(logo_path, width=70*mm, height=28*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        # Right side: INVOICE title + meta info
        invoice_title = Paragraph(
            "<b>INVOICE</b>",
            ParagraphStyle('InvTitle', fontSize=28, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold')
        )
        
        meta_style = ParagraphStyle('Meta', fontSize=11, alignment=TA_RIGHT, leading=15)
        invoice_no = Paragraph(f"Invoice No: <b>{invoice_data['invoice_number']}</b>", meta_style)
        invoice_date = Paragraph(f"Date: {invoice_data['created_at']}", meta_style)
        
        # Build right column content
        right_content = Table([
            [invoice_title],
            [Spacer(1, 2*mm)],
            [invoice_no],
            [invoice_date]
        ], colWidths=[page_width*0.45])
        right_content.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.55, page_width*0.45])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY & CLIENT INFO SECTION ===
        # Left: Company details
        company_info = Table([
            [Paragraph("<b>Studio Shine Art</b>", ParagraphStyle('Co', fontSize=13, fontName='Helvetica-Bold'))],
            [Paragraph("No: 52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=10, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604 / 0322051680", ParagraphStyle('Tel', fontSize=10, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        
        # Right: Bill To
        bill_to_data = [
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {customer_data['full_name']}", ParagraphStyle('Cust', fontSize=11))],
        ]
        if customer_data.get('mobile_number') and customer_data['mobile_number'] != 'Guest Customer':
            bill_to_data.append([Paragraph(f"Mobile: {customer_data['mobile_number']}", ParagraphStyle('Mob', fontSize=11))])
        if booking_ref:
            bill_to_data.append([Paragraph(f"Booking Ref: {booking_ref}", ParagraphStyle('Ref', fontSize=11))])
        
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
        story.append(Spacer(1, 8*mm))
        
        # === ITEMS TABLE (PREMIUM BLACK THEME WITH ZEBRA STRIPING) ===
        # Header styles - white text for black background
        header_desc_style = ParagraphStyle('HDesc', fontSize=11, leading=13, textColor=colors.white, fontName='Helvetica-Bold')
        header_center_style = ParagraphStyle('HCenter', fontSize=11, alignment=TA_CENTER, textColor=colors.white, fontName='Helvetica-Bold')
        header_right_style = ParagraphStyle('HRight', fontSize=11, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold')
        
        # Data row styles
        desc_style = ParagraphStyle('Desc', fontSize=11, leading=13)
        center_style = ParagraphStyle('Center', fontSize=11, alignment=TA_CENTER)
        right_style = ParagraphStyle('Right', fontSize=11, alignment=TA_RIGHT)
        
        table_data = [[
            Paragraph("Description", header_desc_style),
            Paragraph("Advance Amount", header_center_style),
            Paragraph("Full Amount", header_right_style),
            Paragraph("Amount", header_right_style)
        ]]
        
        # Import db_manager to fetch service names
        from database.db_manager import DatabaseManager
        db = DatabaseManager()
        
        # Check if this is a booking invoice and fetch service name once
        booking_service_name = None
        if invoice_data.get('booking_id'):
            booking = db.get_booking_by_id(invoice_data['booking_id'])
            if booking and booking.get('photoshoot_category'):
                # Remove "Booking - " prefix if it exists
                service_name = booking['photoshoot_category']
                if ' - ' in service_name:
                    # Split and take the part after the dash
                    booking_service_name = service_name.split(' - ', 1)[1]
                else:
                    booking_service_name = service_name
        
        for item in items:
            item_name = item['item_name']
            
            # For any service-related item in a booking invoice, use the booking service name
            if booking_service_name and item.get('item_type') in ['Service', 'BookingService']:
                item_name = booking_service_name
            # Get service name from database for regular Service type items (non-booking)
            elif item.get('item_type') == 'Service' and not invoice_data.get('booking_id'):
                service_data = db.get_service_by_id(item['item_id'])
                if service_data:
                    service_name = service_data.get('service_name', '')
                    # Use the actual service name
                    if service_name:
                        item_name = service_name
            elif item.get('item_type') == 'CategoryService':
                item_name = 'Service Charge'
            
            # For services, show advance amount and full amount
            # For frames, keep showing quantity and unit price
            if item.get('item_type') in ['Service', 'BookingService']:
                advance_amt = invoice_data.get('advance_payment', 0) or 0
                full_amount = item['total_price']
                table_data.append([
                    Paragraph(item_name, desc_style),
                    Paragraph(f"Rs. {advance_amt:,.2f}", center_style),
                    Paragraph(f"Rs. {full_amount:,.2f}", right_style),
                    Paragraph(f"Rs. {item['total_price']:,.2f}", right_style)
                ])
            else:
                # For frames and other items, show quantity and unit price as before
                table_data.append([
                    Paragraph(item_name, desc_style),
                    Paragraph(str(item['quantity']), center_style),
                    Paragraph(f"Rs. {item['unit_price']:,.2f}", right_style),
                    Paragraph(f"Rs. {item['total_price']:,.2f}", right_style)
                ])
        
        # Adjusted column widths: wider Advance Amount column
        col_widths = [page_width*0.44, page_width*0.18, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        
        # Base table styling
        table_style = [
            # Header row - BLACK background with WHITE text
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # All cells - thin elegant borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # Data rows - padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Right-align price columns
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]
        
        # Add zebra striping - alternating light gray rows for better readability
        for i in range(1, len(table_data)):
            if i % 2 == 0:  # Even rows get light gray background
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5')))
            else:  # Odd rows stay white
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.white))
        
        items_table.setStyle(TableStyle(table_style))
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # === FINANCIAL SUMMARY (Bottom Right) ===
        subtotal = invoice_data['subtotal']
        discount = invoice_data.get('discount', 0) or 0
        service_charge = invoice_data.get('category_service_cost', 0) or 0
        total = invoice_data['total_amount']
        advance = invoice_data.get('advance_payment', 0) or 0
        balance = invoice_data.get('balance_amount', total) or total
        
        summary_style = ParagraphStyle('Sum', fontSize=11, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        
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
        story.append(Spacer(1, 10*mm))
        
        # === TERMS & CONDITIONS (LEFT-ALIGNED) ===
        terms_title_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#333333'))
        terms_text_style = ParagraphStyle('TermsText', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("<b>Terms &amp; Conditions:</b>", terms_title_style))
        story.append(Spacer(1, 1*mm))
        # Professional English terms
        terms_text = "Orders must be collected within 30 days of the advance payment. Please note that advance payments are non-refundable after this 30-day period."
        story.append(Paragraph(terms_text, terms_text_style))
        story.append(Spacer(1, 6*mm))
        
        # === CONTACT INFO WITH ICONS (CENTER-ALIGNED) ===
        contact_text_style = ParagraphStyle('ContactText', fontSize=10, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=13)
        
        # Social media and contact info with icons
        email_icon_path = os.path.join('assets', 'icons', 'email.png')
        fb_icon_path = os.path.join('assets', 'icons', 'facebook.png')
        
        # Email with icon
        if os.path.exists(email_icon_path):
            try:
                email_icon = Image(email_icon_path, width=4*mm, height=4*mm)
            except:
                email_icon = Paragraph("✉", contact_text_style)
        else:
            email_icon = Paragraph("✉", contact_text_style)
        
        email_text = Paragraph("studioshineart05@gmail.com", contact_text_style)
        
        # Facebook with icon
        if os.path.exists(fb_icon_path):
            try:
                fb_icon = Image(fb_icon_path, width=4*mm, height=4*mm)
            except:
                fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        else:
            fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        
        fb_text = Paragraph("Pasindu P Wijethunga Photography", contact_text_style)
        
        # Create contact info table with icons
        contact_table = Table([
            [email_icon, email_text, Spacer(8*mm, 1), fb_icon, fb_text]
        ], colWidths=[5*mm, 60*mm, 8*mm, 5*mm, 60*mm])
        contact_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'LEFT'),
        ]))
        
        # Center the contact table
        contact_container = Table([[contact_table]], colWidths=[page_width])
        contact_container.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(contact_container)
        story.append(Spacer(1, 6*mm))
        
        # === DETAILED FOOTER (2-LINE CENTER-ALIGNED) ===
        footer1_style = ParagraphStyle('Footer1', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
        footer2_style = ParagraphStyle('Footer2', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#999999'), leading=11)
        
        footer_line1 = "Thank you for choosing Shine Art Studio – Nattandiya."
        footer_line2 = "This invoice system is developed and maintained by Malinda Prabath. For further information, please contact 076 220 6157 or malindaprabath876@gmail.com."
        
        story.append(Paragraph(footer_line1, footer1_style))
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(footer_line2, footer2_style))
        
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
        """Generate PDF booking invoice with premium black theme"""
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        invoice_number = f"BK-{timestamp}"
        
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=12*mm,
            bottomMargin=12*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm
        
        # === HEADER: Wide Logo Left, INVOICE + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                # Wide landscape-style logo
                logo = Image(logo_path, width=70*mm, height=28*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        # Right side: INVOICE title + meta
        title = Paragraph("<b>INVOICE</b>", ParagraphStyle('Title', fontSize=28, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=11, alignment=TA_RIGHT, leading=15)
        receipt_no = Paragraph(f"Invoice No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style)
        
        right_content = Table([[title], [Spacer(1, 2*mm)], [receipt_no], [receipt_date]], colWidths=[page_width*0.45])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.55, page_width*0.45])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>Studio Shine Art</b>", ParagraphStyle('Co', fontSize=13, fontName='Helvetica-Bold'))],
            [Paragraph("No: 52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=10, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604 / 0322051680", ParagraphStyle('Tel', fontSize=10, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {booking_data['customer_name']}", ParagraphStyle('Cust', fontSize=11))],
            [Paragraph(f"Mobile: {booking_data['mobile_number']}", ParagraphStyle('Mob', fontSize=11))],
            [Paragraph(f"Booking Date: {booking_data['booking_date']}", ParagraphStyle('Date', fontSize=11))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 8*mm))
        
        # === ITEMS TABLE (PREMIUM BLACK THEME WITH ZEBRA STRIPING) ===
        # Header styles - white text for black background
        header_desc_style = ParagraphStyle('HDesc', fontSize=11, leading=13, textColor=colors.white, fontName='Helvetica-Bold')
        header_center_style = ParagraphStyle('HCenter', fontSize=11, alignment=TA_CENTER, textColor=colors.white, fontName='Helvetica-Bold')
        header_right_style = ParagraphStyle('HRight', fontSize=11, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold')
        
        # Data row styles
        desc_style = ParagraphStyle('Desc', fontSize=11, leading=13)
        center_style = ParagraphStyle('Center', fontSize=11, alignment=TA_CENTER)
        right_style = ParagraphStyle('Right', fontSize=11, alignment=TA_RIGHT)
        
        # Parse service name
        photoshoot_cat = booking_data['photoshoot_category']
        if ' - ' in photoshoot_cat:
            parts = photoshoot_cat.split(' - ', 1)
            service_name = f"{parts[0]} - {parts[1]}"
        else:
            service_name = photoshoot_cat
        
        full_amount = float(booking_data['full_amount'])
        advance_payment = float(booking_data.get('advance_payment', 0))
        
        table_data = [
            [Paragraph("Description", header_desc_style), Paragraph("Advance Amount", header_center_style), Paragraph("Full Amount", header_right_style), Paragraph("Amount", header_right_style)],
            [Paragraph(service_name, desc_style), Paragraph(f"Rs. {advance_payment:,.2f}", center_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style)]
        ]
        
        col_widths = [page_width*0.44, page_width*0.18, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        
        # Base table styling
        table_style = [
            # Header row - BLACK background with WHITE text
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # All cells - thin elegant borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # Data rows - padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Right-align price columns
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            # All data rows: white background only (no gray zebra striping)
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]
        
        # NO zebra striping - removed for high-contrast thermal printing
        
        items_table.setStyle(TableStyle(table_style))
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # === FINANCIAL SUMMARY (Right-aligned) ===
        advance_payment = float(booking_data['advance_payment'])
        balance = full_amount - advance_payment
        
        summary_style = ParagraphStyle('Sum', fontSize=11, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold')
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
        story.append(Spacer(1, 10*mm))
        
        # === TERMS & CONDITIONS (LEFT-ALIGNED) ===
        terms_title_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#333333'))
        terms_text_style = ParagraphStyle('TermsText', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("<b>Terms &amp; Conditions:</b>", terms_title_style))
        story.append(Spacer(1, 1*mm))
        terms_text = "Orders must be collected within 30 days of the advance payment. Please note that advance payments are non-refundable after this 30-day period."
        story.append(Paragraph(terms_text, terms_text_style))
        story.append(Spacer(1, 6*mm))
        
        # === FOOTER SECTION (Social Media & Contact with Icons) ===
        footer_style = ParagraphStyle('Footer', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        social_style = ParagraphStyle('Social', fontSize=8, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=11)
        
        # === CONTACT INFO WITH ICONS (CENTER-ALIGNED) ===
        contact_text_style = ParagraphStyle('ContactText', fontSize=10, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=13)
        
        email_icon_path = os.path.join('assets', 'icons', 'email.png')
        fb_icon_path = os.path.join('assets', 'icons', 'facebook.png')
        
        # Email with icon
        if os.path.exists(email_icon_path):
            try:
                email_icon = Image(email_icon_path, width=4*mm, height=4*mm)
            except:
                email_icon = Paragraph("✉", contact_text_style)
        else:
            email_icon = Paragraph("✉", contact_text_style)
        
        email_text = Paragraph("studioshineart05@gmail.com", contact_text_style)
        
        # Facebook with icon
        if os.path.exists(fb_icon_path):
            try:
                fb_icon = Image(fb_icon_path, width=4*mm, height=4*mm)
            except:
                fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        else:
            fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        
        fb_text = Paragraph("Pasindu P Wijethunga Photography", contact_text_style)
        
        # Create contact info table with icons
        contact_table = Table([
            [email_icon, email_text, Spacer(8*mm, 1), fb_icon, fb_text]
        ], colWidths=[5*mm, 60*mm, 8*mm, 5*mm, 60*mm])
        contact_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'LEFT'),
        ]))
        
        # Center the contact table
        contact_container = Table([[contact_table]], colWidths=[page_width])
        contact_container.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(contact_container)
        story.append(Spacer(1, 6*mm))
        
        # === DETAILED FOOTER (2-LINE CENTER-ALIGNED) ===
        footer1_style = ParagraphStyle('Footer1', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
        footer2_style = ParagraphStyle('Footer2', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#999999'), leading=11)
        
        footer_line1 = "Thank you for choosing Shine Art Studio – Nattandiya."
        footer_line2 = "This invoice system is developed and maintained by Malinda Prabath. For further information, please contact 076 220 6157 or malindaprabath876@gmail.com."
        
        story.append(Paragraph(footer_line1, footer1_style))
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(footer_line2, footer2_style))
        
        doc.build(story)
        return filepath
    
    def generate_booking_invoice_reprint(self, booking_data, created_by_name, invoice_number):
        """Reprint booking invoice with existing invoice number - premium black theme"""
        filename = f"Booking_{invoice_number}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=12*mm,
            bottomMargin=12*mm
        )
        
        story = []
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm
        
        # === HEADER: Wide Logo Left, INVOICE + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                # Wide landscape-style logo
                logo = Image(logo_path, width=70*mm, height=28*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        title = Paragraph("<b>INVOICE</b>", ParagraphStyle('Title', fontSize=28, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=11, alignment=TA_RIGHT, leading=15)
        receipt_no = Paragraph(f"Invoice No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Date: {booking_data.get('booking_date', '')}", meta_style)
        
        right_content = Table([[title], [Spacer(1, 2*mm)], [receipt_no], [receipt_date]], colWidths=[page_width*0.45])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.55, page_width*0.45])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>STUDIO SHINE ART</b>", ParagraphStyle('Co', fontSize=13, fontName='Helvetica-Bold'))],
            [Paragraph("<b>Reg No:</b> 26/3610", ParagraphStyle('Reg', fontSize=10, textColor=colors.HexColor('#444444')))],
            [Paragraph("No:52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=10, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604 / 0322051680", ParagraphStyle('Tel', fontSize=10, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {booking_data['customer_name']}", ParagraphStyle('Cust', fontSize=11))],
            [Paragraph(f"Mobile: {booking_data.get('mobile_number', 'N/A')}", ParagraphStyle('Mob', fontSize=11))],
            [Paragraph(f"Booking Date: {booking_data.get('booking_date', 'N/A')}", ParagraphStyle('Date', fontSize=11))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 8*mm))
        
        # === ITEMS TABLE (PREMIUM BLACK THEME WITH ZEBRA STRIPING) ===
        # Header styles - white text for black background
        header_desc_style = ParagraphStyle('HDesc', fontSize=11, leading=13, textColor=colors.white, fontName='Helvetica-Bold')
        header_center_style = ParagraphStyle('HCenter', fontSize=11, alignment=TA_CENTER, textColor=colors.white, fontName='Helvetica-Bold')
        header_right_style = ParagraphStyle('HRight', fontSize=11, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold')
        
        # Data row styles
        desc_style = ParagraphStyle('Desc', fontSize=11, leading=13)
        center_style = ParagraphStyle('Center', fontSize=11, alignment=TA_CENTER)
        right_style = ParagraphStyle('Right', fontSize=11, alignment=TA_RIGHT)
        
        service_name = booking_data.get('photoshoot_category', 'Photography Service')
        full_amount = float(booking_data.get('full_amount', 0))
        advance_payment = float(booking_data.get('advance_payment', 0))
        
        table_data = [
            [Paragraph("Description", header_desc_style), Paragraph("Advance Amount", header_center_style), Paragraph("Full Amount", header_right_style), Paragraph("Amount", header_right_style)],
            [Paragraph(service_name, desc_style), Paragraph(f"Rs. {advance_payment:,.2f}", center_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style)]
        ]
        
        col_widths = [page_width*0.44, page_width*0.18, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        
        # Base table styling
        table_style = [
            # Header row - BLACK background with WHITE text
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # All cells - thin elegant borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # Data rows - padding
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Right-align price columns
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            # All data rows: white background only (no gray zebra striping)
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]
        
        # NO zebra striping - removed for high-contrast thermal printing
        
        items_table.setStyle(TableStyle(table_style))
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # === FINANCIAL SUMMARY ===
        advance_payment = float(booking_data.get('advance_payment', 0))
        balance = full_amount - advance_payment
        
        summary_style = ParagraphStyle('Sum', fontSize=11, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold')
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
        story.append(Spacer(1, 10*mm))
        
        # === TERMS & CONDITIONS (Increased font sizes) ===
        terms_title_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#333333'))
        terms_text_style = ParagraphStyle('TermsText', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("<b>Terms &amp; Conditions:</b>", terms_title_style))
        story.append(Spacer(1, 1*mm))
        terms_text = "Orders must be collected within 30 days of the advance payment. Please note that advance payments are non-refundable after this 30-day period."
        story.append(Paragraph(terms_text, terms_text_style))
        story.append(Spacer(1, 6*mm))
        
        # === FOOTER SECTION (Social Media & Contact with Icons) ===
        footer_style = ParagraphStyle('Footer', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        social_style = ParagraphStyle('Social', fontSize=8, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=11)
        dev_style = ParagraphStyle('Dev', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#cccccc'))
        
        # Social media and contact info with icons
        email_icon_path = os.path.join('assets', 'icons', 'email.png')
        fb_icon_path = os.path.join('assets', 'icons', 'facebook.png')
        
        # Email with icon
        if os.path.exists(email_icon_path):
            try:
                email_icon = Image(email_icon_path, width=4*mm, height=4*mm)
            except:
                email_icon = Paragraph("✉", social_style)
        else:
            email_icon = Paragraph("✉", social_style)
        
        email_text = Paragraph("studioshineart05@gmail.com", social_style)
        
        # Facebook with icon
        if os.path.exists(fb_icon_path):
            try:
                fb_icon = Image(fb_icon_path, width=4*mm, height=4*mm)
            except:
                fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        else:
            fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        
        fb_text = Paragraph("Pasindu P Wijethunga Photography", social_style)
        
        # Create contact info table with icons
        contact_table = Table([
            [email_icon, email_text, Spacer(8*mm, 1), fb_icon, fb_text]
        ], colWidths=[5*mm, 60*mm, 8*mm, 5*mm, 60*mm])
        contact_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'LEFT'),
        ]))
        
        # Center the contact table
        contact_container = Table([[contact_table]], colWidths=[page_width])
        contact_container.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(contact_container)
        story.append(Spacer(1, 3*mm))
        
        # Detailed footer with developer info
        footer1_style = ParagraphStyle('Footer1', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
        footer2_style = ParagraphStyle('Footer2', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#999999'), leading=10)
        
        footer_line1 = "Thank you for choosing Shine Art Studio – Nattandiya."
        footer_line2 = "This invoice system is developed and maintained by Malinda Prabath. For further information, please contact 076 220 6157 or malindaprabath876@gmail.com."
        
        story.append(Paragraph(footer_line1, footer1_style))
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(footer_line2, footer2_style))
        
        doc.build(story)
        return filepath
        
        title = Paragraph("<b>INVOICE</b>", ParagraphStyle('Title', fontSize=28, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=11, alignment=TA_RIGHT, leading=15)
        receipt_no = Paragraph(f"Invoice No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Date: {booking_data.get('booking_date', '')}", meta_style)
        
        right_content = Table([[title], [Spacer(1, 2*mm)], [receipt_no], [receipt_date]], colWidths=[page_width*0.45])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.55, page_width*0.45])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>STUDIO SHINE ART</b>", ParagraphStyle('Co', fontSize=13, fontName='Helvetica-Bold'))],
            [Paragraph("<b>Reg No:</b> 26/3610", ParagraphStyle('Reg', fontSize=10, textColor=colors.HexColor('#444444')))],
            [Paragraph("No:52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=10, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604 / 0322051680", ParagraphStyle('Tel', fontSize=10, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {booking_data['customer_name']}", ParagraphStyle('Cust', fontSize=11))],
            [Paragraph(f"Mobile: {booking_data.get('mobile_number', 'N/A')}", ParagraphStyle('Mob', fontSize=11))],
            [Paragraph(f"Booking Date: {booking_data.get('booking_date', 'N/A')}", ParagraphStyle('Date', fontSize=11))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 8*mm))
        
        # === ITEMS TABLE (PREMIUM BLACK THEME) ===
        # Header styles - white text for black background
        header_desc_style = ParagraphStyle('HDesc', fontSize=11, leading=13, textColor=colors.white, fontName='Helvetica-Bold')
        header_center_style = ParagraphStyle('HCenter', fontSize=11, alignment=TA_CENTER, textColor=colors.white, fontName='Helvetica-Bold')
        header_right_style = ParagraphStyle('HRight', fontSize=11, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold')
        
        # Data row styles
        desc_style = ParagraphStyle('Desc', fontSize=11, leading=13)
        center_style = ParagraphStyle('Center', fontSize=11, alignment=TA_CENTER)
        right_style = ParagraphStyle('Right', fontSize=11, alignment=TA_RIGHT)
        
        service_name = booking_data.get('photoshoot_category', 'Photography Service')
        full_amount = float(booking_data.get('full_amount', 0))
        advance_payment = float(booking_data.get('advance_payment', 0))
        
        table_data = [
            [Paragraph("Description", header_desc_style), Paragraph("Advance Amount", header_center_style), Paragraph("Full Amount", header_right_style), Paragraph("Amount", header_right_style)],
            [Paragraph(service_name, desc_style), Paragraph(f"Rs. {advance_payment:,.2f}", center_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style)]
        ]
        
        col_widths = [page_width*0.44, page_width*0.18, page_width*0.19, page_width*0.19]
        items_table = Table(table_data, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            # Header row - BLACK background with WHITE text
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            # All cells - thin black borders
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # Data rows - white background
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Right-align price columns
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # === FINANCIAL SUMMARY ===
        advance_payment = float(booking_data.get('advance_payment', 0))
        balance = full_amount - advance_payment
        
        summary_style = ParagraphStyle('Sum', fontSize=11, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=13, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        balance_style = ParagraphStyle('Bal', fontSize=12, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#c0392b'))
        
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
        story.append(Spacer(1, 10*mm))
        
        # === TERMS & CONDITIONS (Sinhala Policy) ===
        terms_title_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#333333'))
        terms_text_style = ParagraphStyle('TermsText', fontSize=9, fontName=SINHALA_FONT, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("<b>Terms &amp; Conditions:</b>", terms_title_style))
        story.append(Spacer(1, 1*mm))
        terms_text = "අත්තිකාරම් මුදල් ලබාදී දින 30ක් ඇතුළත ඇණවුම රැගෙන යා යුතුය. දින 30කට පසු අත්තිකාරම් මුදල් නැවත ලබා නොදෙන බව කරුණාවෙන් දන්වා සිටිමු."
        story.append(Paragraph(terms_text, terms_text_style))
        story.append(Spacer(1, 8*mm))
        
        # === FOOTER SECTION (Social Media & Contact with Icons) ===
        footer_style = ParagraphStyle('Footer', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        social_style = ParagraphStyle('Social', fontSize=8, alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=11)
        
        story.append(Paragraph("Thank you for your business!", footer_style))
        story.append(Spacer(1, 3*mm))
        
        # Social media and contact info with icons
        email_icon_path = os.path.join('assets', 'icons', 'email.png')
        fb_icon_path = os.path.join('assets', 'icons', 'facebook.png')
        
        # Email with icon
        if os.path.exists(email_icon_path):
            try:
                email_icon = Image(email_icon_path, width=4*mm, height=4*mm)
            except:
                email_icon = Paragraph("✉", social_style)
        else:
            email_icon = Paragraph("✉", social_style)
        
        email_text = Paragraph("studioshineart05@gmail.com", social_style)
        
        # Facebook with icon
        if os.path.exists(fb_icon_path):
            try:
                fb_icon = Image(fb_icon_path, width=4*mm, height=4*mm)
            except:
                fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        else:
            fb_icon = Paragraph("f", ParagraphStyle('FB', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#1877f2'), fontName='Helvetica-Bold'))
        
        fb_text = Paragraph("Pasindu P Wijethunga Photography", social_style)
        
        # Create contact info table with icons
        contact_table = Table([
            [email_icon, email_text, Spacer(8*mm, 1), fb_icon, fb_text]
        ], colWidths=[5*mm, 60*mm, 8*mm, 5*mm, 60*mm])
        contact_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'LEFT'),
            ('ALIGN', (3, 0), (3, 0), 'CENTER'),
            ('ALIGN', (4, 0), (4, 0), 'LEFT'),
        ]))
        
        # Center the contact table
        contact_container = Table([[contact_table]], colWidths=[page_width])
        contact_container.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        story.append(contact_container)
        story.append(Spacer(1, 3*mm))
        
        # Detailed footer with developer info
        footer1_style = ParagraphStyle('Footer1', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#666666'))
        footer2_style = ParagraphStyle('Footer2', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#999999'), leading=10)
        
        footer_line1 = "Thank you for choosing Shine Art Studio – Nattandiya."
        footer_line2 = "This invoice system is developed and maintained by Malinda Prabath. For further information, please contact 076 220 6157 or malindaprabath876@gmail.com."
        
        story.append(Paragraph(footer_line1, footer1_style))
        story.append(Spacer(1, 1*mm))
        story.append(Paragraph(footer_line2, footer2_style))
        
        doc.build(story)
        return filepath
    
    def generate_booking_settlement_invoice(self, settlement_data):
        """Generate final settlement invoice for booking with linked original data"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
        from reportlab.lib import colors
        from datetime import datetime
        import os
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        booking_id = settlement_data['booking_id']
        invoice_number = f"SETTLE-BK-{booking_id}"
        
        filename = f"SETTLE_BK_{booking_id}.pdf"
        filepath = os.path.join(self.invoice_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath, 
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=12*mm,
            bottomMargin=12*mm
        )
        
        story = []
        from reportlab.lib.styles import getSampleStyleSheet
        styles = getSampleStyleSheet()
        page_width = A4[0] - 30*mm
        
        # === HEADER: Wide Logo Left, INVOICE + Meta Right ===
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=70*mm, height=28*mm)
            except:
                logo = Paragraph("", styles['Normal'])
        else:
            logo = Paragraph("", styles['Normal'])
        
        # Right side: FINAL SETTLEMENT title + meta
        title = Paragraph("<b>FINAL SETTLEMENT</b>", ParagraphStyle('Title', fontSize=24, textColor=colors.HexColor('#1a1a2e'), alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        meta_style = ParagraphStyle('Meta', fontSize=11, alignment=TA_RIGHT, leading=15)
        receipt_no = Paragraph(f"Invoice No: <b>{invoice_number}</b>", meta_style)
        receipt_date = Paragraph(f"Settlement Date: {settlement_data['settlement_date']}", meta_style)
        original_date = Paragraph(f"Original Booking: {settlement_data['original_booking_date']}", ParagraphStyle('OrigDate', fontSize=10, alignment=TA_RIGHT, leading=15, textColor=colors.HexColor('#555555')))
        
        right_content = Table([[title], [Spacer(1, 2*mm)], [receipt_no], [receipt_date], [original_date]], colWidths=[page_width*0.45])
        right_content.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'RIGHT'), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        
        header_table = Table([[logo, right_content]], colWidths=[page_width*0.55, page_width*0.45])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('ALIGN', (0, 0), (0, 0), 'LEFT'), ('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(header_table)
        story.append(Spacer(1, 5*mm))
        
        # === COMPANY & CLIENT INFO ===
        company_info = Table([
            [Paragraph("<b>Studio Shine Art</b>", ParagraphStyle('Co', fontSize=13, fontName='Helvetica-Bold'))],
            [Paragraph("No: 52/1/1, Maravila Road, Nattandiya", ParagraphStyle('Addr', fontSize=10, textColor=colors.HexColor('#555555')))],
            [Paragraph("Tel: 0767898604 / 0322051680", ParagraphStyle('Tel', fontSize=10, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        company_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        bill_to_info = Table([
            [Paragraph("<b>Bill To:</b>", ParagraphStyle('BillTo', fontSize=12, fontName='Helvetica-Bold'))],
            [Paragraph(f"Customer: {settlement_data['customer_name']}", ParagraphStyle('Cust', fontSize=11))],
            [Paragraph(f"Mobile: {settlement_data['mobile_number']}", ParagraphStyle('Mob', fontSize=11))],
            [Paragraph(f"Booking ID: {settlement_data['booking_id']}", ParagraphStyle('BookID', fontSize=11, textColor=colors.HexColor('#555555')))],
        ], colWidths=[page_width*0.5])
        bill_to_info.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT'), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        
        info_table = Table([[company_info, bill_to_info]], colWidths=[page_width*0.5, page_width*0.5])
        info_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(info_table)
        story.append(Spacer(1, 8*mm))
        
        # === SETTLEMENT DETAILS TABLE ===
        header_style = ParagraphStyle('Header', fontSize=11, leading=13, textColor=colors.white, fontName='Helvetica-Bold')
        desc_style = ParagraphStyle('Desc', fontSize=11, leading=13)
        right_style = ParagraphStyle('Right', fontSize=11, alignment=TA_RIGHT)
        
        # Parse service name
        photoshoot_cat = settlement_data['photoshoot_category']
        if ' - ' in photoshoot_cat:
            parts = photoshoot_cat.split(' - ', 1)
            service_name = parts[1] if len(parts) > 1 else photoshoot_cat
        else:
            service_name = photoshoot_cat
        
        full_amount = float(settlement_data['full_amount'])
        original_advance = float(settlement_data['original_advance'])
        final_payment = float(settlement_data['final_payment'])
        
        table_data = [
            [Paragraph("Description", header_style), Paragraph("Amount", ParagraphStyle('HRight', fontSize=11, alignment=TA_RIGHT, textColor=colors.white, fontName='Helvetica-Bold'))],
            [Paragraph(service_name, desc_style), Paragraph(f"Rs. {full_amount:,.2f}", right_style)],
        ]
        
        col_widths = [page_width*0.65, page_width*0.35]
        items_table = Table(table_data, colWidths=col_widths)
        
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ]
        
        items_table.setStyle(TableStyle(table_style))
        story.append(items_table)
        story.append(Spacer(1, 6*mm))
        
        # === PAYMENT BREAKDOWN (Right-aligned) ===
        summary_style = ParagraphStyle('Sum', fontSize=11, alignment=TA_RIGHT)
        summary_bold = ParagraphStyle('SumBold', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold')
        paid_style = ParagraphStyle('Paid', fontSize=11, alignment=TA_RIGHT, fontName='Helvetica-Bold', textColor=colors.HexColor('#27ae60'))
        
        summary_data = [
            [Paragraph("Original Total:", summary_style), Paragraph(f"Rs. {full_amount:,.2f}", summary_style)],
            [Paragraph(f"Advance Paid ({settlement_data['original_booking_date']}):", summary_style), Paragraph(f"Rs. {original_advance:,.2f}", summary_style)],
            [Paragraph("<b>Final Payment Today:</b>", summary_bold), Paragraph(f"<b>Rs. {final_payment:,.2f}</b>", paid_style)],
            [Paragraph("<b>TOTAL PAID:</b>", summary_bold), Paragraph(f"<b>Rs. {full_amount:,.2f}</b>", summary_bold)],
            [Paragraph("Balance Due:", summary_style), Paragraph("Rs. 0.00", paid_style)],
        ]
        
        # Add cash received and change if applicable
        cash_received = float(settlement_data.get('cash_received', final_payment))
        change_given = float(settlement_data.get('change_given', 0))
        
        if change_given > 0:
            summary_data.append([Paragraph("Cash Received:", summary_style), Paragraph(f"Rs. {cash_received:,.2f}", summary_style)])
            summary_data.append([Paragraph("Change Given:", summary_style), Paragraph(f"Rs. {change_given:,.2f}", summary_style)])
        
        summary_table = Table(summary_data, colWidths=[50*mm, 40*mm])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('LINEABOVE', (0, -2), (-1, -2), 1, colors.HexColor('#333333')),
        ]))
        
        summary_container = Table([[Spacer(1, 1), summary_table]], colWidths=[page_width - 90*mm, 90*mm])
        summary_container.setStyle(TableStyle([('ALIGN', (1, 0), (1, 0), 'RIGHT')]))
        story.append(summary_container)
        story.append(Spacer(1, 10*mm))
        
        # === STATUS LABEL ===
        status_style = ParagraphStyle('Status', fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER, textColor=colors.HexColor('#27ae60'))
        story.append(Paragraph("✓ <b>FULLY PAID - BOOKING COMPLETED</b>", status_style))
        story.append(Spacer(1, 8*mm))
        
        # === TERMS & CONDITIONS ===
        terms_title_style = ParagraphStyle('TermsTitle', fontSize=10, fontName='Helvetica-Bold', alignment=TA_LEFT, textColor=colors.HexColor('#333333'))
        terms_text_style = ParagraphStyle('TermsText', fontSize=9, fontName='Helvetica', alignment=TA_LEFT, textColor=colors.HexColor('#555555'), leading=12)
        
        story.append(Paragraph("<b>Thank You!</b>", terms_title_style))
        story.append(Spacer(1, 1*mm))
        terms_text = "Thank you for your business. Your booking has been completed and fully paid. Please contact us if you have any questions."
        story.append(Paragraph(terms_text, terms_text_style))
        story.append(Spacer(1, 10*mm))
        
        # === FOOTER ===
        footer_style = ParagraphStyle('Footer', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#333333'))
        story.append(Paragraph("Studio Shine Art | No: 52/1/1, Maravila Road, Nattandiya | 0767898604 / 0322051680", footer_style))
        story.append(Spacer(1, 2*mm))
        
        dev_style = ParagraphStyle('Dev', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#888888'))
        story.append(Paragraph("System Developed by: Malinda Prabath", dev_style))
        
        # Build and save
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
