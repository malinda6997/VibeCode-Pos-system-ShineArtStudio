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
        
        # Get admin name for verification
        admin_name = "Administrator"
        
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
        
        # Centered Report Title - EXPENSE ANALYTICS REPORT
        report_title = Paragraph(
            "<b>EXPENSE ANALYTICS REPORT</b>",
            ParagraphStyle(
                'ReportTitle',
                fontSize=22,
                textColor=colors.HexColor('#8C00FF'),
                alignment=TA_CENTER,
                fontName='Helvetica-Bold',
                spaceBefore=3*mm,
                spaceAfter=3*mm
            )
        )
        story.append(report_title)
        
        # Subtitle - Report Period
        period_subtitle = Paragraph(
            f"<b>Report Period:</b> {period_label}",
            ParagraphStyle(
                'Period',
                fontSize=13,
                alignment=TA_CENTER,
                fontName='Helvetica',
                spaceBefore=2*mm,
                spaceAfter=8*mm
            )
        )
        story.append(period_subtitle)
        
        # Separator line
        separator = HRFlowable(
            width="100%",
            thickness=2,
            color=colors.HexColor('#8C00FF'),
            spaceBefore=3*mm,
            spaceAfter=8*mm
        )
        story.append(separator)
        
        # ==================== SUMMARY BOX ====================
        # Clean shaded box with key metrics
        summary_data = [
            ['TOTAL EXPENDITURE', f'LKR {total_expenses:,.2f}'],
            ['TRANSACTION COUNT', str(len(expenses_data))]
        ]
        
        summary_table = Table(summary_data, colWidths=[page_width * 0.45, page_width * 0.55])
        summary_table.setStyle(TableStyle([
            # Background shading
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F5F5F5')),
            # Text styling
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#8C00FF')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, -1), 12),
            ('FONTSIZE', (1, 0), (1, -1), 16),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#8C00FF')),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor('#DDDDDD')),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10*mm))
        
        # ==================== DATA TABLE ====================
        if expenses_data:
            # Expense table headers with Black background and White text
            expense_table_data = [
                ['Date', 'Description', 'Added By', 'Amount (LKR)']
            ]
            
            # Add expense rows
            for item in expenses_data:
                expense_date = datetime.strptime(item['expense_date'], '%Y-%m-%d').strftime('%b %d, %Y')
                expense_table_data.append([
                    expense_date,
                    item['description'][:45] + '...' if len(item['description']) > 45 else item['description'],
                    item['created_by_name'],
                    f"{item['amount']:,.2f}"
                ])
            
            # Create expense table with professional styling
            expense_table = Table(
                expense_table_data,
                colWidths=[page_width * 0.18, page_width * 0.44, page_width * 0.20, page_width * 0.18]
            )
            expense_table.setStyle(TableStyle([
                # Header styling - Solid Black with White Text
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                
                # Data rows styling
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date center
                ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Description left
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Added By center
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Amount right
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                
                # Alternating row colors (Light Gray)
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
                
                # Grid and borders
                ('GRID', (0, 0), (-1, -1), 0.75, colors.grey),
                ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ]))
            story.append(expense_table)
        else:
            no_data = Paragraph(
                "<i>No expense records found for this period.</i>",
                ParagraphStyle(
                    'NoData',
                    fontSize=12,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceBefore=10*mm,
                    spaceAfter=10*mm
                )
            )
            story.append(no_data)
        
        # ==================== FOOTER ====================
        story.append(Spacer(1, 12*mm))
        
        # Generation and Verification info
        generation_info = Paragraph(
            f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>"
            f"<b>Verified by:</b> {admin_name}",
            ParagraphStyle(
                'GenerationInfo',
                fontSize=10,
                textColor=colors.black,
                alignment=TA_LEFT,
                spaceBefore=5*mm,
                spaceAfter=8*mm
            )
        )
        story.append(generation_info)
        
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
            "Contact: +94 76 220 6157 | Email: malindaprabath876@gmail.com",
            ParagraphStyle(
                'Footer',
                fontSize=9,
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
