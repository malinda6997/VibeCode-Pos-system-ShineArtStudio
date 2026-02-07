from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
import os
import sqlite3
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import resource_path

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


class ExpenseReportGenerator:
    """Generate professional expense PDF reports for Daily, Weekly, and Monthly periods"""
    
    def __init__(self, report_folder='reports', db_path='pos_database.db'):
        self.report_folder = report_folder
        self.db_path = db_path
        os.makedirs(report_folder, exist_ok=True)
    
    def generate_daily_report(self, report_date: str = None):
        """Generate daily expense report"""
        if report_date is None:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        start_date = report_date
        end_date = report_date
        period_type = "Daily"
        period_label = datetime.strptime(report_date, '%Y-%m-%d').strftime('%B %d, %Y')
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def generate_weekly_report(self, start_date: str, end_date: str):
        """Generate weekly expense report"""
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        period_type = "Weekly"
        period_label = f"{start_date_obj.strftime('%b %d')} - {end_date_obj.strftime('%b %d, %Y')}"
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def generate_monthly_report(self, year: int, month: int):
        """Generate monthly expense report"""
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        
        # Get last day of month
        if month == 12:
            end_date = datetime(year, 12, 31).strftime('%Y-%m-%d')
        else:
            end_date = (datetime(year, month + 1, 1) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        period_type = "Monthly"
        period_label = datetime(year, month, 1).strftime('%B %Y')
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def generate_custom_report(self, start_date: str, end_date: str):
        """Generate custom date range expense report"""
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        
        period_type = "Custom"
        period_label = f"{start_date_obj.strftime('%b %d, %Y')} - {end_date_obj.strftime('%b %d, %Y')}"
        
        return self._generate_report(start_date, end_date, period_type, period_label)
    
    def _generate_report(self, start_date: str, end_date: str, period_type: str, period_label: str):
        """Generate the actual PDF report"""
        
        # Create filename
        filename = f"Expense_{period_type}_Report_{start_date}_to_{end_date}.pdf"
        filepath = os.path.join(self.report_folder, filename)
        
        # Fetch expense data
        expenses_data = self._get_expenses_data(start_date, end_date)
        
        # Calculate totals
        total_expenses = sum(item['amount'] for item in expenses_data)
        
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
        
        # ==================== HEADER ====================
        # Logo - Centered
        logo_path = resource_path(os.path.join('assets', 'logos', 'invoiceLogo.png'))
        if os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=80*mm, height=32*mm)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 3*mm))
            except:
                pass
        
        # Studio Name
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
        
        # Separator line
        separator = HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#8C00FF'),
            spaceBefore=2*mm,
            spaceAfter=5*mm
        )
        story.append(separator)
        
        # Report Title
        report_title = Paragraph(
            f"<b>EXPENSE REPORT - {period_type.upper()}</b>",
            ParagraphStyle(
                'ReportTitle',
                fontSize=18,
                textColor=colors.HexColor('#000000'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceBefore=5*mm,
                spaceAfter=2*mm
            )
        )
        story.append(report_title)
        
        # Period Label
        period_para = Paragraph(
            f"<b>Period:</b> {period_label}",
            ParagraphStyle(
                'Period',
                fontSize=12,
                alignment=TA_CENTER,
                spaceBefore=2*mm,
                spaceAfter=5*mm
            )
        )
        story.append(period_para)
        
        # Generation timestamp
        timestamp = Paragraph(
            f"<i>Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>",
            ParagraphStyle(
                'Timestamp',
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER,
                spaceAfter=8*mm
            )
        )
        story.append(timestamp)
        
        # ==================== SUMMARY SECTION ====================
        summary_title = Paragraph(
            "<b>SUMMARY</b>",
            ParagraphStyle(
                'SectionTitle',
                fontSize=14,
                textColor=colors.HexColor('#8C00FF'),
                fontName='Helvetica-Bold',
                spaceBefore=5*mm,
                spaceAfter=3*mm
            )
        )
        story.append(summary_title)
        
        # Summary table
        summary_data = [
            ['Total Expenses:', f'LKR {total_expenses:,.2f}'],
            ['Number of Entries:', str(len(expenses_data))]
        ]
        
        summary_table = Table(summary_data, colWidths=[page_width * 0.5, page_width * 0.5])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 8*mm))
        
        # ==================== EXPENSE DETAILS ====================
        if expenses_data:
            details_title = Paragraph(
                "<b>EXPENSE DETAILS</b>",
                ParagraphStyle(
                    'SectionTitle',
                    fontSize=14,
                    textColor=colors.HexColor('#8C00FF'),
                    fontName='Helvetica-Bold',
                    spaceBefore=3*mm,
                    spaceAfter=3*mm
                )
            )
            story.append(details_title)
            
            # Expense table headers
            expense_table_data = [
                ['Date', 'Description', 'Added By', 'Amount (LKR)']
            ]
            
            # Add expense rows
            for item in expenses_data:
                expense_date = datetime.strptime(item['expense_date'], '%Y-%m-%d').strftime('%b %d, %Y')
                expense_table_data.append([
                    expense_date,
                    item['description'][:40] + '...' if len(item['description']) > 40 else item['description'],
                    item['created_by_name'],
                    f"{item['amount']:,.2f}"
                ])
            
            # Create expense table
            expense_table = Table(
                expense_table_data,
                colWidths=[page_width * 0.18, page_width * 0.42, page_width * 0.22, page_width * 0.18]
            )
            expense_table.setStyle(TableStyle([
                # Header styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                
                # Data rows styling
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date center
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description left
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Added By center
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Amount right
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(expense_table)
        else:
            no_data = Paragraph(
                "<i>No expense records found for this period.</i>",
                ParagraphStyle(
                    'NoData',
                    fontSize=11,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceBefore=10*mm,
                    spaceAfter=10*mm
                )
            )
            story.append(no_data)
        
        # ==================== FOOTER ====================
        story.append(Spacer(1, 10*mm))
        footer_separator = HRFlowable(
            width="100%",
            thickness=1,
            color=colors.grey,
            spaceBefore=5*mm,
            spaceAfter=3*mm
        )
        story.append(footer_separator)
        
        footer_text = Paragraph(
            "<b>Shine Art Studio</b> | Professional Photography & Framing Services<br/>"
            "Contact: +94 XXX XXX XXX | Email: info@shineartstudio.lk",
            ParagraphStyle(
                'Footer',
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer_text)
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def _get_expenses_data(self, start_date: str, end_date: str) -> list:
        """Get expense details for date range"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT me.id, me.description, me.amount, me.expense_date, 
                       u.full_name as created_by_name, me.created_at
                FROM manual_expenses me
                JOIN users u ON me.created_by = u.id
                WHERE me.expense_date BETWEEN ? AND ?
                ORDER BY me.expense_date DESC, me.created_at DESC
            ''', (start_date, end_date))
            
            expenses = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return expenses
        except sqlite3.Error as e:
            print(f"Error getting expense data: {e}")
            return []
