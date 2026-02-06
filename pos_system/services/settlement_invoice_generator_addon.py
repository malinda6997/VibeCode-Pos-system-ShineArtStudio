# Settlement Invoice Generator - Add-on for InvoiceGenerator class
# This should be added to invoice_generator.py after the generate_booking_invoice method

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
