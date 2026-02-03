from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
import os
import sqlite3

# Register Unicode font for Sinhala text support
try:
    pdfmetrics.registerFont(TTFont('IskooPota', 'C:/Windows/Fonts/iskpota.ttf'))
    pdfmetrics.registerFont(TTFont('IskooPota-Bold', 'C:/Windows/Fonts/iskpotab.ttf'))
    SINHALA_FONT = 'IskooPota'
    SINHALA_FONT_BOLD = 'IskooPota-Bold'
except:
    try:
        pdfmetrics.registerFont(TTFont('NirmalaUI', 'C:/Windows/Fonts/Nirmala.ttf'))
        pdfmetrics.registerFont(TTFont('NirmalaUI-Bold', 'C:/Windows/Fonts/NirmalaB.ttf'))
        SINHALA_FONT = 'NirmalaUI'
        SINHALA_FONT_BOLD = 'NirmalaUI-Bold'
    except:
        SINHALA_FONT = 'Helvetica'
        SINHALA_FONT_BOLD = 'Helvetica-Bold'


class FinancialReportGenerator:
    """Generate professional financial PDF reports for Daily, Weekly, and Monthly periods"""
    
    def __init__(self, report_folder='reports', db_path='pos_database.db'):
        self.report_folder = report_folder
        self.db_path = db_path
        os.makedirs(report_folder, exist_ok=True)
    
    def generate_daily_report(self, report_date: str = None):
        """Generate daily financial report"""
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        start_date = report_date
        end_date = report_date
        period_type = "Daily"
        period_label = datetime.strptime(report_date, '%Y-%m-%d').strftime('%B %d, %Y')
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def generate_weekly_report(self, end_date: str = None):
        """Generate weekly financial report"""
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        start_date_obj = end_date_obj - timedelta(days=6)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        
        period_type = "Weekly"
        period_label = f"{start_date_obj.strftime('%b %d')} - {end_date_obj.strftime('%b %d, %Y')}"
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def generate_monthly_report(self, year: int = None, month: int = None):
        """Generate monthly financial report"""
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month
        
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        
        # Get last day of month
        if month == 12:
            end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
        else:
            end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        period_type = "Monthly"
        period_label = datetime(year, month, 1).strftime('%B %Y')
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def _generate_report(self, start_date: str, end_date: str, period_type: str, period_label: str):
        """Generate the actual PDF report"""
        
        # Create filename
        filename = f"{period_type}_Report_{start_date}_to_{end_date}.pdf"
        filepath = os.path.join(self.report_folder, filename)
        
        # Fetch data
        income_data = self._get_income_data(start_date, end_date)
        bookings_data = self._get_bookings_data(start_date, end_date)
        expenses_data = self._get_expenses_data(start_date, end_date)
        opening_balance = self._get_opening_balance(start_date)
        
        # Calculate totals
        total_income = sum(item['amount'] for item in income_data)
        total_expenses = sum(item['amount'] for item in expenses_data)
        net_balance = total_income - total_expenses
        final_balance = opening_balance + net_balance
        
        # Create PDF
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
        
        # ==================== ENHANCED HEADER ====================
        # Logo - Centered and High Resolution
        logo_path = os.path.join('assets', 'logos', 'invoiceLogo.png')
        if os.path.exists(logo_path):
            try:
                # Centered logo with better dimensions
                logo = Image(logo_path, width=80*mm, height=32*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 3*mm))
            except:
                pass
        
        # Studio Name - Bold and Prominent
        studio_title = Paragraph(
            "<b>SHINE ART STUDIO</b>",
            ParagraphStyle(
                'StudioTitle',
                fontSize=26,
                textColor=colors.HexColor('#8C00FF'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=2*mm
            )
        )
        story.append(studio_title)
        
        # Horizontal separator line with accent color
        from reportlab.platypus import HRFlowable
        separator = HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#8C00FF'),
            spaceBefore=2*mm,
            spaceAfter=4*mm
        )
        story.append(separator)
        
        # Report Title - Larger and Bold
        report_title = Paragraph(
            f"<b>{period_type.upper()} FINANCIAL REPORT</b>",
            ParagraphStyle(
                'ReportTitle',
                fontSize=20,
                textColor=colors.HexColor('#1a1a2e'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceAfter=5*mm
            )
        )
        story.append(report_title)
        
        # Metadata Section - Right Aligned
        metadata_data = [
            [Paragraph(
                f"<b>Period:</b> {period_label}",
                ParagraphStyle('MetaRight', fontSize=9, alignment=TA_RIGHT, fontName='Helvetica')
            )],
            [Paragraph(
                f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
                ParagraphStyle('MetaRight', fontSize=9, alignment=TA_RIGHT, textColor=colors.grey)
            )]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[page_width])
        metadata_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(metadata_table)
        
        story.append(Spacer(1, 8*mm))
        
        # ==================== OPENING BALANCE CARD ====================
        opening_card_data = [[
            Paragraph(
                f"<b>Opening Balance</b>",
                ParagraphStyle('CardLabel', fontSize=11, textColor=colors.grey)
            ),
            Paragraph(
                f"<b><font color='#333333' size='16'>LKR {opening_balance:,.2f}</font></b>",
                ParagraphStyle('CardValue', fontSize=16, alignment=TA_RIGHT, fontName='Helvetica-Bold')
            )
        ]]
        
        opening_card = Table(opening_card_data, colWidths=[page_width * 0.5, page_width * 0.5])
        opening_card.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#cccccc')),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        story.append(opening_card)
        story.append(Spacer(1, 8*mm))
        
        # ==================== INCOME SECTION ====================
        income_header = Paragraph(
            "<b>💰 INCOME BREAKDOWN</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=14,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceAfter=3*mm
            )
        )
        story.append(income_header)
        
        if income_data:
            income_table_data = [
                ['Date', 'Invoice #', 'Customer', 'Amount (LKR)']
            ]
            
            for item in income_data:
                income_table_data.append([
                    item['date'],
                    item['invoice_number'],
                    item['customer_name'],
                    f"LKR {item['amount']:,.2f}"
                ])
            
            income_table_data.append(['', '', '<b>TOTAL INCOME</b>', f"<b>LKR {total_income:,.2f}</b>"])
            
            income_table = Table(income_table_data, colWidths=[30*mm, 35*mm, 70*mm, 35*mm])
            
            # Enhanced table styling with better readability
            table_style = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8C00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows - increased padding
                ('TOPPADDING', (0, 1), (-1, -2), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                
                # Alignment
                ('ALIGN', (0, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
                ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#8C00FF')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#8C00FF')),
                
                # Total row
                ('LINEABOVE', (0, -1), (-1, -1), 2.5, colors.HexColor('#8C00FF')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ]
            
            income_table.setStyle(TableStyle(table_style))
            story.append(income_table)
        else:
            no_income = Paragraph(
                "<i>No income recorded for this period.</i>",
                ParagraphStyle('NoData', fontSize=10, textColor=colors.grey)
            )
            story.append(no_income)
        
        story.append(Spacer(1, 7*mm))
        
        # ==================== BOOKINGS SECTION ====================
        bookings_header = Paragraph(
            "<b>📅 SYSTEM BOOKINGS</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=14,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceAfter=3*mm
            )
        )
        story.append(bookings_header)
        
        if bookings_data:
            bookings_table_data = [
                ['Date', 'Customer', 'Category', 'Status', 'Amount (LKR)']
            ]
            
            total_bookings = 0
            for item in bookings_data:
                bookings_table_data.append([
                    item['date'],
                    item['customer_name'],
                    item['category'],
                    item['status'],
                    f"LKR {item['amount']:,.2f}"
                ])
                total_bookings += item['amount']
            
            bookings_table_data.append(['', '', '', '<b>TOTAL</b>', f"<b>LKR {total_bookings:,.2f}</b>"])
            
            bookings_table = Table(bookings_table_data, colWidths=[28*mm, 48*mm, 38*mm, 26*mm, 40*mm])
            
            # Enhanced table styling with increased row height
            table_style = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8C00FF')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows - increased padding for better readability
                ('TOPPADDING', (0, 1), (-1, -2), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -2), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                
                # Column alignment - Date, Customer, Category, Status (Left), Amount (Right)
                ('ALIGN', (0, 0), (3, -1), 'LEFT'),
                ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
                ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#8C00FF')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#8C00FF')),
                
                # Total row - clearly bolded and separated
                ('LINEABOVE', (0, -1), (-1, -1), 2.5, colors.HexColor('#8C00FF')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ]
            
            bookings_table.setStyle(TableStyle(table_style))
            story.append(bookings_table)
        else:
            no_bookings = Paragraph(
                "<i>No bookings recorded for this period.</i>",
                ParagraphStyle('NoData', fontSize=10, textColor=colors.grey)
            )
            story.append(no_bookings)
        
        story.append(Spacer(1, 7*mm))
        
        # ==================== EXPENSES SECTION ====================
        expenses_header = Paragraph(
            "<b>💸 MANUAL EXPENSES</b>",
            ParagraphStyle(
                'SectionHeader',
                fontSize=14,
                textColor=colors.HexColor('#ff6b6b'),
                fontName='Helvetica-Bold',
                spaceAfter=3*mm
            )
        )
        story.append(expenses_header)
        
        if expenses_data:
            expenses_table_data = [
                ['Date', 'Description', 'Added By', 'Amount (LKR)']
            ]
            
            for idx, item in enumerate(expenses_data):
                expenses_table_data.append([
                    item['date'],
                    item['description'],
                    item['added_by'],
                    f"LKR {item['amount']:,.2f}"
                ])
            
            expenses_table_data.append(['', '', '<b>TOTAL EXPENSES</b>', f"<b>LKR {total_expenses:,.2f}</b>"])
            
            expenses_table = Table(expenses_table_data, colWidths=[30*mm, 70*mm, 35*mm, 35*mm])
            
            # Enhanced table styling with zebra striping
            table_style = [
                # Header row
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b6b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                
                # Data rows - increased padding
                ('TOPPADDING', (0, 1), (-1, -2), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                
                # Alignment
                ('ALIGN', (0, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#dddddd')),
                ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#ff6b6b')),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#ff6b6b')),
                
                # Total row - clearly bolded and separated with thicker line
                ('LINEABOVE', (0, -1), (-1, -1), 2.5, colors.HexColor('#ff6b6b')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ]
            
            # Apply zebra striping - subtle light gray for alternating rows
            for i in range(1, len(expenses_data)):
                if i % 2 == 0:  # Even rows (data starts at row 1)
                    table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9f9f9')))
            
            expenses_table.setStyle(TableStyle(table_style))
            story.append(expenses_table)
        else:
            no_expenses = Paragraph(
                "<i>No manual expenses recorded for this period.</i>",
                ParagraphStyle('NoData', fontSize=10, textColor=colors.grey)
            )
            story.append(no_expenses)
        
        story.append(Spacer(1, 10*mm))
        
        # ==================== ENHANCED SUMMARY SECTION WITH VISUAL CARDS ====================
        summary_header = Paragraph(
            "<b>📊 FINANCIAL SUMMARY</b>",
            ParagraphStyle(
                'SummaryHeader',
                fontSize=18,
                textColor=colors.HexColor('#1a1a2e'),
                fontName='Helvetica-Bold',
                alignment=TA_CENTER,
                spaceAfter=6*mm
            )
        )
        story.append(summary_header)
        
        # Add horizontal separator
        from reportlab.platypus import HRFlowable
        separator2 = HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#cccccc'),
            spaceBefore=0,
            spaceAfter=6*mm
        )
        story.append(separator2)
        
        # Total Income Card - Green/Purple Highlight
        income_summary = [[
            Paragraph("<b>Total Income</b>", ParagraphStyle('CardLabel', fontSize=12, textColor=colors.HexColor('#8C00FF'))),
            Paragraph(f"<b><font color='#8C00FF' size='16'>LKR {total_income:,.2f}</font></b>", ParagraphStyle('CardValue', fontSize=16, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ]]
        income_table = Table(income_summary, colWidths=[page_width * 0.5, page_width * 0.5])
        income_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3e8ff')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8C00FF')),
        ]))
        story.append(income_table)
        story.append(Spacer(1, 4*mm))
        
        # Total Expenses Card - Red Highlight
        expenses_summary = [[
            Paragraph("<b>Total Expenses</b>", ParagraphStyle('CardLabel', fontSize=12, textColor=colors.HexColor('#ff6b6b'))),
            Paragraph(f"<b><font color='#ff6b6b' size='16'>LKR {total_expenses:,.2f}</font></b>", ParagraphStyle('CardValue', fontSize=16, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ]]
        expenses_summary_table = Table(expenses_summary, colWidths=[page_width * 0.5, page_width * 0.5])
        expenses_summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ffe8e8')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#ff6b6b')),
        ]))
        story.append(expenses_summary_table)
        story.append(Spacer(1, 4*mm))
        
        # Net Profit/Loss Card - Larger Font, Green if Profit, Red if Loss
        profit_color = '#00ff88' if net_balance >= 0 else '#ff6b6b'
        profit_bg = '#e8fff3' if net_balance >= 0 else '#ffe8e8'
        profit_label = "Net Profit" if net_balance >= 0 else "Net Loss"
        
        net_summary = [[
            Paragraph(f"<b>{profit_label}</b>", ParagraphStyle('CardLabel', fontSize=13, textColor=colors.HexColor(profit_color), fontName='Helvetica-Bold')),
            Paragraph(f"<b><font color='{profit_color}' size='18'>LKR {abs(net_balance):,.2f}</font></b>", ParagraphStyle('CardValue', fontSize=18, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ]]
        net_table = Table(net_summary, colWidths=[page_width * 0.5, page_width * 0.5])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(profit_bg)),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 3, colors.HexColor(profit_color)),
        ]))
        story.append(net_table)
        story.append(Spacer(1, 4*mm))
        
        # Closing Balance Card
        closing_summary = [[
            Paragraph("<b>Closing Balance</b>", ParagraphStyle('CardLabel', fontSize=12, textColor=colors.HexColor('#8C00FF'))),
            Paragraph(f"<b><font color='#8C00FF' size='16'>LKR {final_balance:,.2f}</font></b>", ParagraphStyle('CardValue', fontSize=16, alignment=TA_RIGHT, fontName='Helvetica-Bold'))
        ]]
        closing_table = Table(closing_summary, colWidths=[page_width * 0.5, page_width * 0.5])
        closing_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3e8ff')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8C00FF')),
        ]))
        story.append(closing_table)
        
        story.append(Spacer(1, 10*mm))
        
        # ==================== FOOTER ====================
        footer = Paragraph(
            "<i>This report was automatically generated by Shine Art Studio POS System</i>",
            ParagraphStyle(
                'Footer',
                fontSize=8,
                fontName='Helvetica-Oblique',
                textColor=colors.HexColor('#999999'),
                alignment=TA_CENTER,
                spaceAfter=5*mm
            )
        )
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'summary': {
                'opening_balance': opening_balance,
                'total_income': total_income,
                'total_expenses': total_expenses,
                'net_balance': net_balance,
                'closing_balance': final_balance
            }
        }
    
    def _get_income_data(self, start_date: str, end_date: str) -> list:
        """Fetch income data from invoices"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    DATE(i.created_at) as date,
                    i.invoice_number,
                    COALESCE(c.full_name, i.guest_name, 'Guest') as customer_name,
                    i.total_amount as amount
                FROM invoices i
                LEFT JOIN customers c ON i.customer_id = c.id
                WHERE DATE(i.created_at) BETWEEN ? AND ?
                ORDER BY i.created_at ASC
            ''', (start_date, end_date))
            
            income = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return income
        except sqlite3.Error as e:
            print(f"Error fetching income data: {e}")
            return []
    
    def _get_bookings_data(self, start_date: str, end_date: str) -> list:
        """Fetch bookings data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    booking_date as date,
                    customer_name,
                    photoshoot_category as category,
                    status,
                    full_amount as amount
                FROM bookings
                WHERE booking_date BETWEEN ? AND ?
                ORDER BY booking_date ASC
            ''', (start_date, end_date))
            
            bookings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return bookings
        except sqlite3.Error as e:
            print(f"Error fetching bookings data: {e}")
            return []
    
    def _get_expenses_data(self, start_date: str, end_date: str) -> list:
        """Fetch manual expenses data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    me.expense_date as date,
                    me.description,
                    u.full_name as added_by,
                    me.amount
                FROM manual_expenses me
                JOIN users u ON me.created_by = u.id
                WHERE me.expense_date BETWEEN ? AND ?
                ORDER BY me.expense_date ASC
            ''', (start_date, end_date))
            
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return expenses
        except sqlite3.Error as e:
            print(f"Error fetching expenses data: {e}")
            return []
    
    def _get_opening_balance(self, date: str) -> float:
        """Get opening balance for the period"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get previous day's closing balance
            prev_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT closing_balance FROM daily_balances
                WHERE balance_date = ?
            ''', (prev_date,))
            
            result = cursor.fetchone()
            conn.close()
            
            return float(result[0]) if result else 0.0
        except sqlite3.Error as e:
            print(f"Error fetching opening balance: {e}")
            return 0.0
