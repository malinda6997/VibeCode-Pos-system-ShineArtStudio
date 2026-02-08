from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib import colors
from datetime import datetime
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import resource_path


class StaffReportGenerator:
    """Generate PDF reports for staff daily work records"""
    
    def __init__(self, report_folder='reports'):
        self.report_folder = report_folder
        os.makedirs(report_folder, exist_ok=True)
    
    def generate_daily_report(self, staff_data: dict, date: str, work_records: dict):
        """Generate PDF report for staff daily work
        
        Args:
            staff_data: dict with staff info (id, full_name, username, role)
            date: Date string (YYYY-MM-DD)
            work_records: dict with invoices, bookings, customers data
        """
        
        # Create filename
        safe_name = staff_data['full_name'].replace(' ', '_')
        filename = f"Staff_Report_{safe_name}_{date}.pdf"
        filepath = os.path.join(self.report_folder, filename)
        
        # Create PDF document
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
        
        # ==================== PROFESSIONAL HEADER ====================
        # Logo at top left
        logo_path = resource_path(os.path.join('assets', 'logos', 'invoiceLogo.png'))
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=60*mm, height=24*mm)
                logo.hAlign = 'LEFT'
                story.append(logo)
                story.append(Spacer(1, 5*mm))
            except:
                pass
        
        # Report Title
        title = Paragraph(
            "<b>STAFF DAILY WORK REPORT</b>",
            ParagraphStyle(
                'Title',
                fontSize=22,
                textColor=colors.HexColor('#8C00FF'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceBefore=3*mm,
                spaceAfter=5*mm
            )
        )
        story.append(title)
        
        # Separator
        separator = HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#8C00FF'),
            spaceBefore=2*mm,
            spaceAfter=8*mm
        )
        story.append(separator)
        
        # Staff Information Box - clearly separated
        formatted_date = datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
        staff_info_data = [
            ['Staff Name:', staff_data['full_name'], 'Username:', f"@{staff_data['username']}"],
            ['Role:', staff_data.get('role', 'Staff'), 'Report Date:', formatted_date]
        ]
        
        staff_table = Table(staff_info_data, colWidths=[page_width * 0.22, page_width * 0.28, page_width * 0.22, page_width * 0.28])
        staff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#F0F0F0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ]))
        story.append(staff_table)
        story.append(Spacer(1, 10*mm))
        
        # ==================== PERFORMANCE DASHBOARD ====================
        invoices = work_records.get('invoices', [])
        bookings = work_records.get('bookings', [])
        customers = work_records.get('customers', [])
        
        total_invoice_amount = sum(inv.get('total_amount', 0) for inv in invoices)
        total_paid = sum(inv.get('paid_amount', 0) for inv in invoices)
        total_booking_amount = sum(b.get('full_amount', 0) for b in bookings)
        total_advance = sum(b.get('advance_payment', 0) for b in bookings)
        
        # Dashboard title
        dashboard_title = Paragraph(
            "<b>PERFORMANCE DASHBOARD</b>",
            ParagraphStyle(
                'DashboardTitle',
                fontSize=14,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceBefore=3*mm,
                spaceAfter=5*mm
            )
        )
        story.append(dashboard_title)
        
        # 2-Column Grid Layout for metrics
        dashboard_data = [
            ['INVOICES CREATED', 'PAYMENTS RECEIVED (LKR)'],
            [str(len(invoices)), f"{total_paid:,.2f}"],
            ['BOOKINGS CREATED', 'ADVANCE COLLECTED (LKR)'],
            [str(len(bookings)), f"{total_advance:,.2f}"],
            ['CUSTOMERS ADDED', ''],
            [str(len(customers)), '']
        ]
        
        dashboard_table = Table(dashboard_data, colWidths=[page_width * 0.5, page_width * 0.5])
        dashboard_table.setStyle(TableStyle([
            # Headers (rows 0, 2, 4)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
            ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F0F0F0')),
            ('BACKGROUND', (0, 4), (0, 4), colors.HexColor('#F0F0F0')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (0, 4), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            
            # Values (rows 1, 3, 5)
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTNAME', (0, 5), (0, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 16),
            ('FONTSIZE', (0, 3), (-1, 3), 16),
            ('FONTSIZE', (0, 5), (0, 5), 16),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#8C00FF')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#8C00FF')),
            ('TEXTCOLOR', (0, 5), (0, 5), colors.HexColor('#8C00FF')),
            
            # Alignment
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            
            # Borders
            ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ]))
        story.append(dashboard_table)
        story.append(Spacer(1, 10*mm))
        
        # ==================== DETAILED ACTIVITY SECTIONS ====================
        
        # INVOICES CREATED Section
        section_header = Paragraph(
            "<b>INVOICES CREATED</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=13,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceBefore=5*mm,
                spaceAfter=3*mm
            )
        )
        story.append(section_header)
        
        if invoices:
            inv_data = [['#', 'Invoice No.', 'Customer', 'Total (LKR)', 'Paid (LKR)', 'Time']]
            for idx, inv in enumerate(invoices, 1):
                created_time = inv.get('created_at', '')
                if ' ' in created_time:
                    created_time = created_time.split(' ')[1][:5]  # Get HH:MM
                inv_data.append([
                    str(idx),
                    inv.get('invoice_number', '-'),
                    inv.get('customer_name', '-')[:25],
                    f"{inv.get('total_amount', 0):,.2f}",
                    f"{inv.get('paid_amount', 0):,.2f}",
                    created_time
                ])
            
            inv_table = Table(
                inv_data,
                colWidths=[page_width * 0.08, page_width * 0.20, page_width * 0.32, 
                          page_width * 0.18, page_width * 0.18, page_width * 0.10]
            )
            inv_table.setStyle(TableStyle([
                # Black Header with White Text
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (2, 1), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(inv_table)
        else:
            no_data = Paragraph(
                "<i>No records found for this period</i>",
                ParagraphStyle(
                    'NoData',
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceBefore=5*mm,
                    spaceAfter=5*mm
                )
            )
            story.append(no_data)
        
        story.append(Spacer(1, 8*mm))
        
        # BOOKINGS CREATED Section
        section_header = Paragraph(
            "<b>BOOKINGS CREATED</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=13,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceBefore=5*mm,
                spaceAfter=3*mm
            )
        )
        story.append(section_header)
        
        if bookings:
            book_data = [['#', 'Customer', 'Category', 'Date', 'Amount (LKR)', 'Advance (LKR)']]
            for idx, b in enumerate(bookings, 1):
                book_data.append([
                    str(idx),
                    b.get('customer_name', '-')[:20],
                    b.get('photoshoot_category', '-')[:18],
                    b.get('booking_date', '-'),
                    f"{b.get('full_amount', 0):,.2f}",
                    f"{b.get('advance_payment', 0):,.2f}"
                ])
            
            book_table = Table(
                book_data,
                colWidths=[page_width * 0.08, page_width * 0.24, page_width * 0.22,
                          page_width * 0.16, page_width * 0.15, page_width * 0.15]
            )
            book_table.setStyle(TableStyle([
                # Black Header with White Text
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (2, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(book_table)
        else:
            no_data = Paragraph(
                "<i>No records found for this period</i>",
                ParagraphStyle(
                    'NoData',
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceBefore=5*mm,
                    spaceAfter=5*mm
                )
            )
            story.append(no_data)
        
        story.append(Spacer(1, 8*mm))
        
        # NEW CUSTOMERS Section
        section_header = Paragraph(
            "<b>NEW CUSTOMERS</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=13,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceBefore=5*mm,
                spaceAfter=3*mm
            )
        )
        story.append(section_header)
        
        if customers:
            cust_data = [['#', 'Customer Name', 'Mobile Number', 'Added At']]
            for idx, c in enumerate(customers, 1):
                created_time = c.get('created_at', '')
                if ' ' in created_time:
                    created_time = created_time.split(' ')[1][:5]
                cust_data.append([
                    str(idx),
                    c.get('full_name', '-'),
                    c.get('mobile_number', '-'),
                    created_time
                ])
            
            cust_table = Table(
                cust_data,
                colWidths=[page_width * 0.10, page_width * 0.45, page_width * 0.25, page_width * 0.20]
            )
            cust_table.setStyle(TableStyle([
                # Black Header with White Text
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                
                # Borders
                ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(cust_table)
        else:
            no_data = Paragraph(
                "<i>No records found for this period</i>",
                ParagraphStyle(
                    'NoData',
                    fontSize=10,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceBefore=5*mm,
                    spaceAfter=5*mm
                )
            )
            story.append(no_data)
        
        # ==================== FOOTER ====================
        story.append(Spacer(1, 15*mm))
        
        footer_separator = HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey,
            spaceBefore=5*mm,
            spaceAfter=3*mm
        )
        story.append(footer_separator)
        
        # Standard contact details
        footer_text = Paragraph(
            "<b>Shine Art Studio</b> | Professional Photography & Framing Services<br/>"
            "No: 52/1/1, Maravila Road, Nattandiya<br/>"
            "Contact: +94 XXX XXX XXX | Email: info@shineartstudio.lk",
            ParagraphStyle(
                'Footer',
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=3*mm
            )
        )
        story.append(footer_text)
        
        # Auto-generation tag
        auto_gen = Paragraph(
            "<i>This report was automatically generated by Shine Art Studio POS System</i>",
            ParagraphStyle(
                'AutoGen',
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(auto_gen)
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def open_report(self, filepath):
        """Open report in default PDF viewer"""
        try:
            os.startfile(filepath)
            return True
        except Exception as e:
            print(f"Error opening report: {e}")
            return False
