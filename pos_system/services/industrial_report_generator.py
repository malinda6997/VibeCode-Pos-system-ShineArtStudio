"""
Industrial-Grade Financial Analytics Report Generator
Multi-Page Executive Document with Cover Page, TOC, and Dynamic Insights
"""

import os
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Tuple, Any
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import resource_path

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, HRFlowable, KeepTogether, PageBreak, TableOfContents
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Matplotlib imports for charts
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class IndustrialReportGenerator:
    """Generate multi-page executive financial analytics PDF reports"""
    
    # MINIMALIST COLOR PALETTE - Black & White with purple accent
    COLOR_BLACK = colors.HexColor('#000000')
    COLOR_DARKGRAY = colors.HexColor('#333333')
    COLOR_MEDIUMGRAY = colors.HexColor('#666666')
    COLOR_LIGHTGRAY = colors.HexColor('#999999')
    COLOR_VERYLIGHTGRAY = colors.HexColor('#CCCCCC')
    COLOR_ULTRALIGHTGRAY = colors.HexColor('#F5F5F5')
    COLOR_WHITE = colors.HexColor('#FFFFFF')
    COLOR_PURPLE_ACCENT = colors.HexColor('#8C00FF')  # Premium accent color
    
    # Thin elegant line thickness
    LINE_THIN = 0.5
    LINE_MEDIUM = 1.0
    LINE_ACCENT = 2.0  # For purple accent lines
    
    # Professional font sizes
    FONT_TITLE = 18
    FONT_HEADER = 11
    FONT_SUBHEADER = 10
    FONT_BODY = 9
    FONT_SMALL = 8
    FONT_TINY = 7
    
    # Company Information
    COMPANY_NAME = "Studio Shine Art"
    COMPANY_REG = "Reg No: 26/3610"
    COMPANY_ADDRESS = "No: 52/1/1, Maravila Road, Nattandiya"
    COMPANY_CONTACT = "0767898604 / 0322051680"
    DEVELOPER_CREDIT = "System developed by Malinda Prabath | malindaprabath876@gmail.com | 076 220 6157"
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
        self.current_page = 1
        self.total_pages = 0
    
    def _add_page_footer(self, canvas_obj, doc):
        """Add footer with developer credit and page numbers to every page"""
        canvas_obj.saveState()
        page_width = A4[0]
        page_height = A4[1]
        
        # Developer credit on left
        canvas_obj.setFont('Helvetica', 7)
        canvas_obj.setFillColor(self.COLOR_LIGHTGRAY)
        canvas_obj.drawString(15*mm, 10*mm, self.DEVELOPER_CREDIT)
        
        # Page number on right
        page_num_text = f"Page {doc.page} of {self.total_pages}"
        canvas_obj.drawRightString(page_width - 15*mm, 10*mm, page_num_text)
        
        canvas_obj.restoreState()
    
    def _clean_html_tags(self, text: str) -> str:
        """Remove all HTML tags from text"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove common HTML tags
        cleaned = text.replace('<b>', '').replace('</b>', '')
        cleaned = cleaned.replace('<i>', '').replace('</i>', '')
        cleaned = cleaned.replace('<u>', '').replace('</u>', '')
        
        # Remove font color tags
        import re
        cleaned = re.sub(r'<font[^>]*>', '', cleaned)
        cleaned = cleaned.replace('</font>', '')
        
        return cleaned
    
    def get_report_summary(self, analytics: Dict, summary: Dict) -> Dict[str, str]:
        """
        Generate dynamic contextual descriptions for each section
        Smart analysis of data to provide executive insights
        """
        insights = {}
        
        # Revenue Insight
        top_service = None
        top_revenue = 0
        if analytics['service_revenue']:
            for category, data in analytics['service_revenue'].items():
                if data['revenue'] > top_revenue:
                    top_revenue = data['revenue']
                    top_service = category
        
        if summary['net_balance'] < 0:
            insights['revenue'] = (
                f"Revenue Analysis: The reporting period shows a net loss of LKR {abs(summary['net_balance']):,.2f}. "
                f"{'The highest revenue generator was ' + top_service + ' category.' if top_service else 'Immediate corrective action is recommended.'} "
                f"Management should review expense optimization strategies and revenue enhancement opportunities."
            )
        else:
            insights['revenue'] = (
                f"Revenue Analysis: The period generated a net profit of LKR {summary['net_balance']:,.2f}. "
                f"{'The ' + top_service + ' category emerged as the top revenue contributor.' if top_service else 'Performance metrics indicate positive operational efficiency.'} "
                f"Total income reached LKR {summary['total_income']:,.2f} with controlled expenses of LKR {summary['total_expenses']:,.2f}."
            )
        
        # Customer Insight
        new_customers = analytics['user_insights'].get('new_customers', 0)
        total_customers = analytics['user_insights'].get('total_customers', 0)
        returning_customers = total_customers - new_customers
        
        insights['customers'] = (
            f"Customer Acquisition: During this period, {new_customers} new customers were acquired, "
            f"bringing the total active customer base to {total_customers}. "
            f"Returning customers account for {returning_customers} of the total base, indicating "
            f"{'strong' if returning_customers > new_customers else 'developing'} customer retention and loyalty metrics."
        )
        
        # Booking Insight
        total_bookings = 0
        completed_bookings = 0
        cancelled_bookings = 0
        
        for status, data in analytics['booking_status'].items():
            total_bookings += data['count']
            if status == 'Completed':
                completed_bookings = data['count']
            elif status == 'Cancelled':
                cancelled_bookings = data['count']
        
        if total_bookings > 0:
            completion_rate = (completed_bookings / total_bookings) * 100
            cancellation_rate = (cancelled_bookings / total_bookings) * 100
            
            insights['bookings'] = (
                f"Booking Performance: A total of {total_bookings} bookings were processed during this period, "
                f"achieving a {completion_rate:.1f}% completion rate with {cancelled_bookings} cancellations ({cancellation_rate:.1f}%). "
                f"{'This completion rate exceeds industry benchmarks.' if completion_rate >= 80 else 'Completion rate requires attention to improve operational efficiency.'}"
            )
        else:
            insights['bookings'] = (
                f"Booking Performance: No bookings were recorded during this reporting period. "
                f"This may indicate seasonal variations or requires investigation into market conditions and promotional strategies."
            )
        
        # Payment Insight
        advance_received = analytics['payment_metrics'].get('advance_received', 0)
        balance_due = analytics['payment_metrics'].get('balance_due', 0)
        
        if advance_received + balance_due > 0:
            advance_percentage = (advance_received / (advance_received + balance_due)) * 100
            insights['payments'] = (
                f"Payment Collection: Advance payments of LKR {advance_received:,.2f} were collected, "
                f"representing {advance_percentage:.1f}% of total booking values. "
                f"Outstanding balances amount to LKR {balance_due:,.2f}, requiring follow-up and collection procedures."
            )
        else:
            insights['payments'] = (
                f"Payment Collection: No payment transactions were recorded during this period. "
                f"Financial operations appear dormant and require management attention."
            )
        
        # Expense Insight
        expense_count = len(analytics['expense_details'])
        insights['expenses'] = (
            f"Expense Management: {expense_count} manual expense transactions totaling LKR {summary['total_expenses']:,.2f} "
            f"were recorded. Expense tracking and categorization are functioning as designed. "
            f"{'Expense levels are within acceptable operational parameters.' if summary['net_balance'] >= 0 else 'Expense optimization is recommended to improve profitability.'}"
        )
        
        return insights
    
    def _create_chart(self, chart_type: str, data: Dict, title: str) -> BytesIO:
        """Generate matplotlib chart with purple accents and return as BytesIO"""
        fig, ax = plt.subplots(figsize=(6, 3), facecolor='white')
        
        if chart_type == 'pie':
            # Revenue distribution pie chart
            labels = list(data.keys())
            sizes = list(data.values())
            
            # Filter out zero values
            filtered_data = [(l, s) for l, s in zip(labels, sizes) if s > 0]
            if not filtered_data:
                plt.close()
                return None
            
            labels, sizes = zip(*filtered_data)
            
            # Black, white, and gray color scheme with purple accent for top slice
            colors_list = ['#8C00FF', '#333333', '#666666', '#999999', '#CCCCCC']
            
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                startangle=90, colors=colors_list[:len(labels)],
                textprops={'fontsize': 8, 'color': 'black'}
            )
            
            # Make percentage text bold and white on dark slices
            for i, autotext in enumerate(autotexts):
                autotext.set_color('white' if i == 0 else 'black')
                autotext.set_fontsize(7)
                autotext.set_weight('bold')
            
            ax.axis('equal')
            
        elif chart_type == 'bar':
            # Expense vs Income comparison
            categories = list(data.keys())
            values = list(data.values())
            
            # Purple for income, dark gray for expenses
            bar_colors = ['#8C00FF' if cat == 'Income' else '#333333' for cat in categories]
            bars = ax.barh(categories, values, color=bar_colors)
            
            # Add value labels on bars
            for i, (bar, value) in enumerate(zip(bars, values)):
                ax.text(value + max(values) * 0.02, i, f'LKR {value:,.0f}',
                       va='center', fontsize=8, color='#333333')
            
            ax.set_xlabel('Amount (LKR)', fontsize=8, color='#333333')
            ax.tick_params(axis='both', labelsize=7, colors='#666666')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#CCCCCC')
            ax.spines['bottom'].set_color('#CCCCCC')
            ax.grid(axis='x', alpha=0.2, linestyle='--', color='#CCCCCC')
        
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def _fetch_analytics_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch comprehensive analytics data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        analytics = {
            'user_insights': {},
            'top_customers': [],
            'service_revenue': {},
            'booking_status': {},
            'payment_metrics': {},
            'income_details': [],
            'expense_details': [],
            'booking_details': []
        }
        
        # User Insights: New customers in period
        cursor.execute('''
            SELECT COUNT(*) FROM customers 
            WHERE DATE(created_at) BETWEEN ? AND ?
        ''', (start_date, end_date))
        new_customers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0]
        
        analytics['user_insights'] = {
            'new_customers': new_customers,
            'total_customers': total_customers,
            'returning_customers': total_customers - new_customers
        }
        
        # Top Customers by booking value
        cursor.execute('''
            SELECT b.customer_name, b.mobile_number, 
                   SUM(b.full_amount) as total_spent,
                   COUNT(*) as booking_count
            FROM bookings b
            WHERE DATE(b.booking_date) BETWEEN ? AND ?
            GROUP BY b.customer_name, b.mobile_number
            ORDER BY total_spent DESC
            LIMIT 5
        ''', (start_date, end_date))
        analytics['top_customers'] = cursor.fetchall()
        
        # Service Revenue Breakdown by category
        cursor.execute('''
            SELECT b.photoshoot_category, 
                   SUM(b.full_amount) as category_revenue,
                   COUNT(*) as booking_count
            FROM bookings b
            WHERE DATE(b.booking_date) BETWEEN ? AND ?
              AND b.status = 'Completed'
            GROUP BY b.photoshoot_category
            ORDER BY category_revenue DESC
        ''', (start_date, end_date))
        for row in cursor.fetchall():
            analytics['service_revenue'][row[0]] = {
                'revenue': row[1],
                'count': row[2]
            }
        
        # Booking Status Summary
        cursor.execute('''
            SELECT status, COUNT(*) as count, SUM(full_amount) as total_value
            FROM bookings
            WHERE DATE(booking_date) BETWEEN ? AND ?
            GROUP BY status
        ''', (start_date, end_date))
        for row in cursor.fetchall():
            analytics['booking_status'][row[0]] = {
                'count': row[1],
                'value': row[2]
            }
        
        # Payment Metrics
        cursor.execute('''
            SELECT 
                SUM(advance_payment) as total_advance,
                SUM(balance_amount) as total_balance
            FROM bookings
            WHERE DATE(booking_date) BETWEEN ? AND ?
        ''', (start_date, end_date))
        payment_data = cursor.fetchone()
        analytics['payment_metrics'] = {
            'advance_received': payment_data[0] or 0,
            'balance_due': payment_data[1] or 0
        }
        
        # Income Details (Completed Bookings)
        cursor.execute('''
            SELECT booking_date, customer_name, photoshoot_category, 
                   full_amount, status, advance_payment
            FROM bookings
            WHERE DATE(booking_date) BETWEEN ? AND ?
              AND status = 'Completed'
            ORDER BY booking_date DESC
        ''', (start_date, end_date))
        analytics['income_details'] = cursor.fetchall()
        
        # Booking Details (All)
        cursor.execute('''
            SELECT booking_date, customer_name, photoshoot_category, 
                   full_amount, status
            FROM bookings
            WHERE DATE(booking_date) BETWEEN ? AND ?
            ORDER BY booking_date DESC
        ''', (start_date, end_date))
        analytics['booking_details'] = cursor.fetchall()
        
        # Expense Details
        cursor.execute('''
            SELECT me.expense_date, 'Manual Expense' as category, me.description, 
                   me.amount, u.full_name
            FROM manual_expenses me
            LEFT JOIN users u ON me.created_by = u.id
            WHERE DATE(me.expense_date) BETWEEN ? AND ?
            ORDER BY me.expense_date DESC
        ''', (start_date, end_date))
        analytics['expense_details'] = cursor.fetchall()
        
        conn.close()
        return analytics
    
    def _create_thin_line(self, width: str = "100%") -> HRFlowable:
        """Create elegant thin horizontal line"""
        return HRFlowable(
            width=width,
            thickness=self.LINE_THIN,
            color=self.COLOR_VERYLIGHTGRAY,
            spaceBefore=2*mm,
            spaceAfter=2*mm
        )
    
    def _create_section_title(self, title: str) -> Paragraph:
        """Create minimalist section title"""
        style = ParagraphStyle(
            'SectionTitle',
            fontSize=self.FONT_HEADER,
            fontName='Helvetica-Bold',
            textColor=self.COLOR_BLACK,
            spaceAfter=3*mm,
            spaceBefore=3*mm
        )
        return Paragraph(title, style)
    
    def _create_subsection_title(self, title: str) -> Paragraph:
        """Create subsection title"""
        style = ParagraphStyle(
            'SubsectionTitle',
            fontSize=self.FONT_SUBHEADER,
            fontName='Helvetica-Bold',
            textColor=self.COLOR_DARKGRAY,
            spaceAfter=2*mm
        )
        return Paragraph(title, style)
    
    def _create_body_text(self, text: str, bold: bool = False) -> Paragraph:
        """Create body text without HTML tags"""
        style = ParagraphStyle(
            'BodyText',
            fontSize=self.FONT_BODY,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=self.COLOR_DARKGRAY
        )
        # Remove all HTML tags and format cleanly
        clean_text = text.replace('<b>', '').replace('</b>', '')
        clean_text = clean_text.replace('<font color', '').replace('</font>', '')
        clean_text = clean_text.replace('<i>', '').replace('</i>', '')
        return Paragraph(clean_text, style)
    
    def _format_currency(self, amount: float) -> str:
        """Format currency with LKR prefix and proper decimals"""
        return f"LKR {amount:,.2f}"
    
    def generate_report(self, start_date: str, end_date: str, 
                       report_type: str = 'Daily') -> Dict[str, Any]:
        """
        Generate comprehensive industrial financial analytics report
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            report_type: 'Daily', 'Weekly', or 'Monthly'
        """
        # Create filename
        filename = f"Financial_Analytics_{report_type}_{start_date}_to_{end_date}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        story = []
        page_width = A4[0] - 30*mm
        
        # ==================== HEADER & BRANDING ====================
        # Logo (centered, top)
        logo_path = resource_path('assets/logos/logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=70*mm, height=28*mm)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 3*mm))
        
        # Elegant thin line
        story.append(self._create_thin_line())
        
        # Report Title - Minimalist
        title_style = ParagraphStyle(
            'Title',
            fontSize=self.FONT_HEADER,
            fontName='Helvetica-Bold',
            textColor=self.COLOR_BLACK,
            alignment=TA_CENTER,
            spaceAfter=2*mm
        )
        story.append(Paragraph(f"FINANCIAL ANALYTICS REPORT", title_style))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            fontSize=self.FONT_BODY,
            fontName='Helvetica',
            textColor=self.COLOR_MEDIUMGRAY,
            alignment=TA_CENTER,
            spaceAfter=2*mm
        )
        story.append(Paragraph(f"{report_type} Period Analysis", subtitle_style))
        
        # Metadata - Right aligned
        metadata_style = ParagraphStyle(
            'Metadata',
            fontSize=self.FONT_SMALL,
            fontName='Helvetica',
            textColor=self.COLOR_LIGHTGRAY,
            alignment=TA_RIGHT,
            spaceAfter=2*mm
        )
        story.append(Paragraph(f"Period: {start_date} to {end_date}", metadata_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", metadata_style))
        
        story.append(self._create_thin_line())
        story.append(Spacer(1, 3*mm))
        
        # ==================== FETCH DATA ====================
        analytics = self._fetch_analytics_data(start_date, end_date)
        
        # Calculate financial summary
        total_income = sum(row[3] for row in analytics['income_details'])
        total_expenses = sum(row[3] for row in analytics['expense_details'])
        net_balance = total_income - total_expenses
        
        # Get opening balance
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT opening_balance FROM daily_balances 
            WHERE balance_date = ?
        ''', (start_date,))
        result = cursor.fetchone()
        opening_balance = result[0] if result else 0.0
        
        closing_balance = opening_balance + net_balance
        conn.close()
        
        # ==================== EXECUTIVE SUMMARY ====================
        story.append(self._create_section_title("EXECUTIVE SUMMARY"))
        
        summary_data = [
            ['Opening Balance', self._format_currency(opening_balance)],
            ['Total Income', self._format_currency(total_income)],
            ['Total Expenses', self._format_currency(total_expenses)],
            ['Net Profit / Loss', self._format_currency(net_balance)],
            ['Closing Balance', self._format_currency(closing_balance)]
        ]
        
        summary_table = Table(summary_data, colWidths=[page_width * 0.6, page_width * 0.4])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLOR_DARKGRAY),
            ('TEXTCOLOR', (1, 0), (1, 2), self.COLOR_DARKGRAY),
            ('TEXTCOLOR', (1, 3), (1, 3), self.COLOR_BLACK if net_balance >= 0 else self.COLOR_DARKGRAY),
            ('TEXTCOLOR', (1, 4), (1, 4), self.COLOR_BLACK),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEABOVE', (0, 0), (-1, 0), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
            ('LINEBELOW', (0, -1), (-1, -1), self.LINE_MEDIUM, self.COLOR_BLACK),
            ('LINEBELOW', (0, 2), (-1, 2), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
            ('BACKGROUND', (0, 3), (-1, 3), self.COLOR_ULTRALIGHTGRAY if net_balance >= 0 else self.COLOR_WHITE),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 5*mm))
        
        # ==================== USER INSIGHTS ====================
        story.append(self._create_section_title("USER INSIGHTS"))
        
        user_data = [
            ['New Customers Acquired', str(analytics['user_insights']['new_customers'])],
            ['Total Active Customers', str(analytics['user_insights']['total_customers'])],
            ['Returning Customers', str(analytics['user_insights']['returning_customers'])]
        ]
        
        user_table = Table(user_data, colWidths=[page_width * 0.7, page_width * 0.3])
        user_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_DARKGRAY),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 4*mm))
        
        # ==================== TOP CUSTOMERS ====================
        if analytics['top_customers']:
            story.append(self._create_section_title("TOP CUSTOMERS"))
            
            top_cust_header = [['Customer Name', 'Mobile', 'Total Spent', 'Bookings']]
            top_cust_data = []
            
            for cust in analytics['top_customers']:
                top_cust_data.append([
                    cust[0],
                    cust[1],
                    self._format_currency(cust[2]),
                    str(cust[3])
                ])
            
            top_cust_table = Table(
                top_cust_header + top_cust_data,
                colWidths=[page_width * 0.35, page_width * 0.25, page_width * 0.25, page_width * 0.15]
            )
            top_cust_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (0, 0), (1, -1), 'LEFT'),
                ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), self.LINE_MEDIUM, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(top_cust_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== SERVICE REVENUE BREAKDOWN ====================
        if analytics['service_revenue']:
            story.append(self._create_section_title("SERVICE REVENUE BREAKDOWN"))
            
            service_header = [['Service Category', 'Bookings', 'Revenue']]
            service_data = []
            
            for category, data in analytics['service_revenue'].items():
                service_data.append([
                    category,
                    str(data['count']),
                    self._format_currency(data['revenue'])
                ])
            
            service_table = Table(
                service_header + service_data,
                colWidths=[page_width * 0.5, page_width * 0.2, page_width * 0.3]
            )
            service_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), self.LINE_MEDIUM, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(service_table)
            story.append(Spacer(1, 4*mm))
            
            # Add Revenue Distribution Chart
            if len(analytics['service_revenue']) > 0:
                chart_data = {cat: data['revenue'] for cat, data in analytics['service_revenue'].items()}
                chart_buffer = self._create_chart('pie', chart_data, 'Revenue Distribution')
                if chart_buffer:
                    chart_img = Image(chart_buffer, width=140*mm, height=70*mm)
                    chart_img.hAlign = 'CENTER'
                    story.append(chart_img)
                    story.append(Spacer(1, 4*mm))
        
        # ==================== BOOKING STATUS SUMMARY ====================
        if analytics['booking_status']:
            story.append(self._create_section_title("BOOKING STATUS SUMMARY"))
            
            booking_header = [['Status', 'Count', 'Total Value']]
            booking_data = []
            
            for status in ['Completed', 'Pending', 'Cancelled']:
                if status in analytics['booking_status']:
                    data = analytics['booking_status'][status]
                    booking_data.append([
                        status,
                        str(data['count']),
                        self._format_currency(data['value'])
                    ])
            
            booking_table = Table(
                booking_header + booking_data,
                colWidths=[page_width * 0.4, page_width * 0.3, page_width * 0.3]
            )
            booking_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), self.LINE_MEDIUM, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(booking_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== PAYMENT METRICS ====================
        story.append(self._create_section_title("PAYMENT METRICS"))
        
        payment_data = [
            ['Total Advance Payments Received', 
             self._format_currency(analytics['payment_metrics']['advance_received'])],
            ['Total Balance Amount Due', 
             self._format_currency(analytics['payment_metrics']['balance_due'])]
        ]
        
        payment_table = Table(payment_data, colWidths=[page_width * 0.65, page_width * 0.35])
        payment_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_DARKGRAY),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
        ]))
        story.append(payment_table)
        story.append(Spacer(1, 4*mm))
        
        # ==================== INCOME vs EXPENSE VISUALIZATION ====================
        if total_income > 0 or total_expenses > 0:
            story.append(self._create_section_title("INCOME vs EXPENSES"))
            chart_data = {'Income': total_income, 'Expenses': total_expenses}
            chart_buffer = self._create_chart('bar', chart_data, 'Financial Comparison')
            if chart_buffer:
                chart_img = Image(chart_buffer, width=140*mm, height=50*mm)
                chart_img.hAlign = 'CENTER'
                story.append(chart_img)
                story.append(Spacer(1, 4*mm))
        
        # ==================== DETAILED INCOME TRANSACTIONS ====================
        if analytics['income_details']:
            story.append(PageBreak())
            story.append(self._create_section_title("DETAILED INCOME TRANSACTIONS"))
            
            income_header = [['Date', 'Customer', 'Category', 'Amount', 'Status']]
            income_data = []
            
            for row in analytics['income_details']:
                income_data.append([
                    row[0],
                    row[1][:20] + '...' if len(row[1]) > 20 else row[1],
                    row[2][:15] + '...' if len(row[2]) > 15 else row[2],
                    self._format_currency(row[3]),
                    row[4]
                ])
            
            income_table = Table(
                income_header + income_data,
                colWidths=[page_width * 0.15, page_width * 0.25, page_width * 0.25, 
                          page_width * 0.20, page_width * 0.15]
            )
            income_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_SMALL),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (0, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, 0), self.LINE_MEDIUM, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(income_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== DETAILED EXPENSE TRANSACTIONS ====================
        if analytics['expense_details']:
            story.append(self._create_section_title("DETAILED EXPENSE TRANSACTIONS"))
            
            expense_header = [['Date', 'Category', 'Description', 'Amount', 'Added By']]
            expense_data = []
            
            for row in analytics['expense_details']:
                expense_data.append([
                    row[0],
                    row[1][:15] + '...' if len(row[1]) > 15 else row[1],
                    row[2][:25] + '...' if len(row[2]) > 25 else row[2],
                    self._format_currency(row[3]),
                    row[4][:15] + '...' if row[4] and len(row[4]) > 15 else (row[4] or 'N/A')
                ])
            
            expense_table = Table(
                expense_header + expense_data,
                colWidths=[page_width * 0.12, page_width * 0.18, page_width * 0.35, 
                          page_width * 0.20, page_width * 0.15]
            )
            expense_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_SMALL),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (0, 0), (2, -1), 'LEFT'),
                ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, 0), self.LINE_MEDIUM, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), self.LINE_THIN, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(expense_table)
            story.append(Spacer(1, 5*mm))
        
        # ==================== FOOTER ====================
        story.append(Spacer(1, 5*mm))
        footer_style = ParagraphStyle(
            'Footer',
            fontSize=self.FONT_TINY,
            fontName='Helvetica-Oblique',
            textColor=self.COLOR_LIGHTGRAY,
            alignment=TA_CENTER
        )
        story.append(Paragraph(
            "This report was automatically generated by Shine Art Studio Financial Analytics System",
            footer_style
        ))
        
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
                'closing_balance': closing_balance
            },
            'analytics': analytics
        }


# Convenience functions for different report types
def generate_daily_report(db_path='pos_database.db', target_date=None):
    """Generate daily financial analytics report"""
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    
    generator = IndustrialReportGenerator(db_path)
    return generator.generate_report(target_date, target_date, 'Daily')


def generate_weekly_report(db_path='pos_database.db', end_date=None):
    """Generate weekly financial analytics report"""
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    start_date = end_date - timedelta(days=6)
    
    generator = IndustrialReportGenerator(db_path)
    return generator.generate_report(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        'Weekly'
    )


def generate_monthly_report(db_path='pos_database.db', year=None, month=None):
    """Generate monthly financial analytics report"""
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    
    start_date = datetime(year, month, 1)
    
    # Get last day of month
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    generator = IndustrialReportGenerator(db_path)
    return generator.generate_report(
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        'Monthly'
    )
