"""
Executive Multi-Page Financial Analytics Report Generator
Professional Cover Page, Auto TOC, Dynamic Insights, and Developer Credits
"""

import os
import sqlite3
from datetime import datetime, timedelta
from io import BytesIO
from typing import Dict, List, Tuple, Any
import re

# ReportLab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, HRFlowable, KeepTogether, PageBreak, Frame, PageTemplate
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdf_canvas

# Matplotlib imports
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


class NumberedCanvas(pdf_canvas.Canvas):
    """Custom canvas for page numbering and footers"""
    def __init__(self, *args, **kwargs):
        pdf_canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.developer_credit = "System developed by Malinda Prabath | malindaprabath876@gmail.com | 076 220 6157"

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_footer(num_pages)
            pdf_canvas.Canvas.showPage(self)
        pdf_canvas.Canvas.save(self)

    def draw_page_footer(self, page_count):
        self.saveState()
        self.setFont('Helvetica', 7)
        self.setFillColor(colors.HexColor('#999999'))
        
        # Developer credit on left
        self.drawString(15*mm, 10*mm, self.developer_credit)
        
        # Page number on right  
        if self._pageNumber > 1:  # Skip cover page
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(A4[0] - 15*mm, 10*mm, page_text)
        
        self.restoreState()


class ExecutiveReportGenerator:
    """Generate executive multi-page financial reports"""
    
    # Color palette
    COLOR_BLACK = colors.HexColor('#000000')
    COLOR_DARKGRAY = colors.HexColor('#333333')
    COLOR_MEDIUMGRAY = colors.HexColor('#666666')
    COLOR_LIGHTGRAY = colors.HexColor('#999999')
    COLOR_VERYLIGHTGRAY = colors.HexColor('#CCCCCC')
    COLOR_ULTRALIGHTGRAY = colors.HexColor('#F5F5F5')
    COLOR_PURPLE = colors.HexColor('#8C00FF')
    
    # Font sizes
    FONT_TITLE = 18
    FONT_HEADER = 11
    FONT_BODY = 9
    FONT_SMALL = 8
    FONT_TINY = 7
    
    # Company info
    COMPANY_NAME = "Studio Shine Art"
    COMPANY_REG = "Reg No: 26/3610"
    COMPANY_ADDRESS = "No: 52/1/1, Maravila Road, Nattandiya"
    COMPANY_CONTACT = "0767898604 / 0322051680"
    
    def __init__(self, db_path='pos_database.db'):
        self.db_path = db_path
        self.reports_dir = 'reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags"""
        if not isinstance(text, str):
            return str(text)
        text = re.sub(r'<[^>]+>', '', text)
        return text
    
    def _format_currency(self, amount: float) -> str:
        """Format currency"""
        return f"LKR {amount:,.2f}"
    
    def _create_chart(self, chart_type: str, data: Dict) -> BytesIO:
        """Generate chart with purple accent"""
        fig, ax = plt.subplots(figsize=(6, 3), facecolor='white')
        
        if chart_type == 'pie':
            labels = list(data.keys())
            sizes = list(data.values())
            filtered = [(l, s) for l, s in zip(labels, sizes) if s > 0]
            if not filtered:
                plt.close()
                return None
            
            labels, sizes = zip(*filtered)
            colors_list = ['#8C00FF', '#333333', '#666666', '#999999', '#CCCCCC']
            
            wedges, texts, autotexts = ax.pie(
                sizes, labels=labels, autopct='%1.1f%%',
                startangle=90, colors=colors_list[:len(labels)],
                textprops={'fontsize': 8}
            )
            
            for i, autotext in enumerate(autotexts):
                autotext.set_color('white' if i == 0 else 'black')
                autotext.set_fontsize(7)
                autotext.set_weight('bold')
            
            ax.axis('equal')
            
        elif chart_type == 'bar':
            categories = list(data.keys())
            values = list(data.values())
            colors_bar = ['#8C00FF' if c == 'Income' else '#333333' for c in categories]
            bars = ax.barh(categories, values, color=colors_bar)
            
            for i, (bar, value) in enumerate(zip(bars, values)):
                ax.text(value + max(values) * 0.02, i, f'LKR {value:,.0f}',
                       va='center', fontsize=8)
            
            ax.set_xlabel('Amount (LKR)', fontsize=8)
            ax.tick_params(axis='both', labelsize=7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(axis='x', alpha=0.2, linestyle='--')
        
        plt.tight_layout()
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        return img_buffer
    
    def get_report_summary(self, analytics: Dict, summary: Dict) -> Dict[str, str]:
        """Generate dynamic insights"""
        insights = {}
        
        # Revenue insight
        top_service = None
        top_revenue = 0
        if analytics['service_revenue']:
            for cat, data in analytics['service_revenue'].items():
                if data['revenue'] > top_revenue:
                    top_revenue = data['revenue']
                    top_service = cat
        
        if summary['net_balance'] < 0:
            insights['revenue'] = (
                f"Revenue Analysis: The reporting period shows a net loss of {self._format_currency(abs(summary['net_balance']))}. "
                f"{'The highest revenue generator was ' + top_service + ' category.' if top_service else 'Immediate corrective action is recommended.'} "
                f"Management should review expense optimization strategies."
            )
        else:
            insights['revenue'] = (
                f"Revenue Analysis: The period generated a net profit of {self._format_currency(summary['net_balance'])}. "
                f"{'The ' + top_service + ' category emerged as the top revenue contributor.' if top_service else 'Performance indicates positive efficiency.'} "
                f"Total income reached {self._format_currency(summary['total_income'])} with controlled expenses."
            )
        
        # Customer insight
        new_cust = analytics['user_insights'].get('new_customers', 0)
        total_cust = analytics['user_insights'].get('total_customers', 0)
        returning = total_cust - new_cust
        
        insights['customers'] = (
            f"Customer Acquisition: During this period, {new_cust} new customers were acquired, "
            f"bringing the total active base to {total_cust}. Returning customers account for {returning}, "
            f"indicating {'strong' if returning > new_cust else 'developing'} customer retention metrics."
        )
        
        # Booking insight
        total_book = sum(d['count'] for d in analytics['booking_status'].values())
        completed = analytics['booking_status'].get('Completed', {}).get('count', 0)
        cancelled = analytics['booking_status'].get('Cancelled', {}).get('count', 0)
        
        if total_book > 0:
            comp_rate = (completed / total_book) * 100
            canc_rate = (cancelled / total_book) * 100
            insights['bookings'] = (
                f"Booking Performance: {total_book} bookings processed, achieving {comp_rate:.1f}% completion rate "
                f"with {cancelled} cancellations ({canc_rate:.1f}%). "
                f"{'Exceeds industry benchmarks.' if comp_rate >= 80 else 'Requires attention for improvement.'}"
            )
        else:
            insights['bookings'] = (
                f"Booking Performance: No bookings recorded during this period. "
                f"This may indicate seasonal variations or requires investigation."
            )
        
        return insights
    
    def _fetch_analytics(self, start_date: str, end_date: str) -> Dict:
        """Fetch analytics data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        analytics = {
            'user_insights': {},
            'top_customers': [],
            'service_revenue': {},
            'booking_status': {},
            'payment_metrics': {},
            'income_details': [],
            'expense_details': []
        }
        
        # User insights
        cursor.execute('SELECT COUNT(*) FROM customers WHERE DATE(created_at) BETWEEN ? AND ?', 
                      (start_date, end_date))
        new_customers = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM customers')
        total_customers = cursor.fetchone()[0]
        analytics['user_insights'] = {
            'new_customers': new_customers,
            'total_customers': total_customers
        }
        
        # Top customers
        cursor.execute('''
            SELECT customer_name, mobile_number, SUM(full_amount), COUNT(*)
            FROM bookings WHERE DATE(booking_date) BETWEEN ? AND ?
            GROUP BY customer_name, mobile_number ORDER BY 3 DESC LIMIT 5
        ''', (start_date, end_date))
        analytics['top_customers'] = cursor.fetchall()
        
        # Service revenue
        cursor.execute('''
            SELECT photoshoot_category, SUM(full_amount), COUNT(*)
            FROM bookings WHERE DATE(booking_date) BETWEEN ? AND ? AND status = 'Completed'
            GROUP BY photoshoot_category ORDER BY 2 DESC
        ''', (start_date, end_date))
        for row in cursor.fetchall():
            analytics['service_revenue'][row[0]] = {'revenue': row[1], 'count': row[2]}
        
        # Booking status
        cursor.execute('''
            SELECT status, COUNT(*), SUM(full_amount)
            FROM bookings WHERE DATE(booking_date) BETWEEN ? AND ?
            GROUP BY status
        ''', (start_date, end_date))
        for row in cursor.fetchall():
            analytics['booking_status'][row[0]] = {'count': row[1], 'value': row[2]}
        
        # Payment metrics
        cursor.execute('''
            SELECT SUM(advance_payment), SUM(balance_amount)
            FROM bookings WHERE DATE(booking_date) BETWEEN ? AND ?
        ''', (start_date, end_date))
        pm = cursor.fetchone()
        analytics['payment_metrics'] = {'advance_received': pm[0] or 0, 'balance_due': pm[1] or 0}
        
        # Income details
        cursor.execute('''
            SELECT booking_date, customer_name, photoshoot_category, full_amount, status
            FROM bookings WHERE DATE(booking_date) BETWEEN ? AND ? AND status = 'Completed'
            ORDER BY booking_date DESC
        ''', (start_date, end_date))
        analytics['income_details'] = cursor.fetchall()
        
        # Expenses
        cursor.execute('''
            SELECT expense_date, 'Manual Expense', description, amount, u.full_name
            FROM manual_expenses me LEFT JOIN users u ON me.created_by = u.id
            WHERE DATE(expense_date) BETWEEN ? AND ? ORDER BY expense_date DESC
        ''', (start_date, end_date))
        analytics['expense_details'] = cursor.fetchall()
        
        conn.close()
        return analytics
    
    def generate_report(self, start_date: str, end_date: str, report_type: str = 'Daily'):
        """Generate executive report"""
        filename = f"Executive_Report_{report_type}_{start_date}_to_{end_date}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            rightMargin=15*mm, leftMargin=15*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )
        
        story = []
        page_width = A4[0] - 30*mm
        
        # Fetch data
        analytics = self._fetch_analytics(start_date, end_date)
        
        # Calculate financials
        total_income = sum(row[3] for row in analytics['income_details'])
        total_expenses = sum(row[3] for row in analytics['expense_details'])
        net_balance = total_income - total_expenses
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT opening_balance FROM daily_balances WHERE balance_date = ?', (start_date,))
        result = cursor.fetchone()
        opening_balance = result[0] if result else 0.0
        closing_balance = opening_balance + net_balance
        conn.close()
        
        summary = {
            'opening_balance': opening_balance,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_balance': net_balance,
            'closing_balance': closing_balance
        }
        
        # Get insights
        insights = self.get_report_summary(analytics, summary)
        
        # ==================== COVER PAGE ====================
        story.append(Spacer(1, 40*mm))
        
        # Logo
        logo_path = 'assets/logos/logo.png'
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=80*mm, height=32*mm)
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 10*mm))
        
        # Title
        title_style = ParagraphStyle(
            'CoverTitle', fontSize=self.FONT_TITLE, fontName='Helvetica-Bold',
            textColor=self.COLOR_BLACK, alignment=TA_CENTER, spaceAfter=8*mm
        )
        story.append(Paragraph("FINANCIAL ANALYTICS REPORT", title_style))
        
        # Purple accent line
        story.append(HRFlowable(
            width="50%", thickness=2, color=self.COLOR_PURPLE,
            spaceBefore=5*mm, spaceAfter=5*mm, hAlign='CENTER'
        ))
        
        # Report type and date
        subtitle_style = ParagraphStyle(
            'Subtitle', fontSize=self.FONT_HEADER, fontName='Helvetica',
            textColor=self.COLOR_MEDIUMGRAY, alignment=TA_CENTER, spaceAfter=3*mm
        )
        story.append(Paragraph(f"{report_type} Report", subtitle_style))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", subtitle_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style))
        
        story.append(Spacer(1, 50*mm))
        
        # Company info at bottom
        company_style = ParagraphStyle(
            'CompanyInfo', fontSize=self.FONT_BODY, fontName='Helvetica',
            textColor=self.COLOR_DARKGRAY, alignment=TA_CENTER, leading=14
        )
        story.append(Paragraph(f"<b>{self.COMPANY_NAME}</b>", company_style))
        story.append(Paragraph(self.COMPANY_REG, company_style))
        story.append(Paragraph(self.COMPANY_ADDRESS, company_style))
        story.append(Paragraph(f"Contact: {self.COMPANY_CONTACT}", company_style))
        
        story.append(PageBreak())
        
        # ==================== TABLE OF CONTENTS ====================
        toc_title_style = ParagraphStyle(
            'TOCTitle', fontSize=self.FONT_HEADER, fontName='Helvetica-Bold',
            textColor=self.COLOR_BLACK, spaceAfter=5*mm
        )
        story.append(Paragraph("TABLE OF CONTENTS", toc_title_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_VERYLIGHTGRAY, spaceAfter=5*mm))
        
        toc_items = [
            "1. Executive Summary",
            "2. Revenue Analysis",
            "3. Customer Insights",
            "4. Top Customers",
            "5. Service Revenue Breakdown",
            "6. Booking Performance",
            "7. Payment Metrics",
            "8. Income vs Expenses Analysis",
            "9. Detailed Income Transactions",
            "10. Detailed Expense Breakdown"
        ]
        
        toc_style = ParagraphStyle(
            'TOC', fontSize=self.FONT_BODY, fontName='Helvetica',
            textColor=self.COLOR_DARKGRAY, leftIndent=5*mm, spaceAfter=2*mm
        )
        for item in toc_items:
            story.append(Paragraph(item, toc_style))
        
        story.append(PageBreak())
        
        # ==================== EXECUTIVE SUMMARY ====================
        section_style = ParagraphStyle(
            'SectionTitle', fontSize=self.FONT_HEADER, fontName='Helvetica-Bold',
            textColor=self.COLOR_BLACK, spaceAfter=3*mm, spaceBefore=5*mm
        )
        story.append(Paragraph("1. EXECUTIVE SUMMARY", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=4*mm))
        
        summary_data = [
            ['Opening Balance', self._format_currency(opening_balance)],
            ['Total Income', self._format_currency(total_income)],
            ['Total Expenses', self._format_currency(total_expenses)],
            ['Net Profit / Loss', self._format_currency(net_balance)],
            ['Closing Balance', self._format_currency(closing_balance)]
        ]
        
        summary_table = Table(summary_data, colWidths=[page_width * 0.6, page_width * 0.4])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_DARKGRAY),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, -1), (-1, -1), 1, self.COLOR_BLACK),
            ('LINEBELOW', (0, 2), (-1, 2), 0.5, self.COLOR_VERYLIGHTGRAY),
            ('BACKGROUND', (0, 3), (-1, 3), self.COLOR_ULTRALIGHTGRAY if net_balance >= 0 else self.COLOR_WHITE),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 5*mm))
        
        # ==================== REVENUE ANALYSIS ====================
        story.append(Paragraph("2. REVENUE ANALYSIS", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
        
        insight_style = ParagraphStyle(
            'Insight', fontSize=self.FONT_BODY, fontName='Helvetica',
            textColor=self.COLOR_DARKGRAY, alignment=TA_JUSTIFY, spaceAfter=4*mm
        )
        story.append(Paragraph(insights['revenue'], insight_style))
        story.append(Spacer(1, 3*mm))
        
        # ==================== CUSTOMER INSIGHTS ====================
        story.append(Paragraph("3. CUSTOMER INSIGHTS", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
        story.append(Paragraph(insights['customers'], insight_style))
        
        user_data = [
            ['New Customers Acquired', str(analytics['user_insights']['new_customers'])],
            ['Total Active Customers', str(analytics['user_insights']['total_customers'])],
            ['Returning Customers', str(analytics['user_insights']['total_customers'] - analytics['user_insights']['new_customers'])]
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
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
        ]))
        story.append(user_table)
        story.append(Spacer(1, 4*mm))
        
        # ==================== TOP CUSTOMERS ====================
        if analytics['top_customers']:
            story.append(Paragraph("4. TOP CUSTOMERS", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            
            top_cust_data = [['Customer', 'Mobile', 'Total Spent', 'Bookings']]
            for cust in analytics['top_customers']:
                top_cust_data.append([
                    cust[0][:20] + '...' if len(cust[0]) > 20 else cust[0],
                    cust[1],
                    self._format_currency(cust[2]),
                    str(cust[3])
                ])
            
            top_table = Table(top_cust_data, colWidths=[page_width*0.35, page_width*0.25, page_width*0.25, page_width*0.15])
            top_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (2, 0), (3, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(top_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== SERVICE REVENUE ====================
        if analytics['service_revenue']:
            story.append(Paragraph("5. SERVICE REVENUE BREAKDOWN", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            
            svc_data = [['Service Category', 'Bookings', 'Revenue']]
            for cat, data in analytics['service_revenue'].items():
                svc_data.append([cat, str(data['count']), self._format_currency(data['revenue'])])
            
            svc_table = Table(svc_data, colWidths=[page_width*0.5, page_width*0.2, page_width*0.3])
            svc_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(svc_table)
            story.append(Spacer(1, 3*mm))
            
            # Chart
            if len(analytics['service_revenue']) > 0:
                chart_data = {cat: data['revenue'] for cat, data in analytics['service_revenue'].items()}
                chart_buffer = self._create_chart('pie', chart_data)
                if chart_buffer:
                    chart_img = Image(chart_buffer, width=140*mm, height=70*mm)
                    chart_img.hAlign = 'CENTER'
                    story.append(chart_img)
                    story.append(Spacer(1, 4*mm))
        
        # ==================== BOOKING PERFORMANCE ====================
        if analytics['booking_status']:
            story.append(PageBreak())
            story.append(Paragraph("6. BOOKING PERFORMANCE", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            story.append(Paragraph(insights['bookings'], insight_style))
            
            book_data = [['Status', 'Count', 'Total Value']]
            for status in ['Completed', 'Pending', 'Cancelled']:
                if status in analytics['booking_status']:
                    data = analytics['booking_status'][status]
                    book_data.append([status, str(data['count']), self._format_currency(data['value'])])
            
            book_table = Table(book_data, colWidths=[page_width*0.4, page_width*0.3, page_width*0.3])
            book_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(book_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== PAYMENT METRICS ====================
        story.append(Paragraph("7. PAYMENT METRICS", section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
        
        pay_data = [
            ['Total Advance Payments Received', self._format_currency(analytics['payment_metrics']['advance_received'])],
            ['Total Balance Amount Due', self._format_currency(analytics['payment_metrics']['balance_due'])]
        ]
        
        pay_table = Table(pay_data, colWidths=[page_width*0.65, page_width*0.35])
        pay_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), self.FONT_BODY),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLOR_DARKGRAY),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
        ]))
        story.append(pay_table)
        story.append(Spacer(1, 4*mm))
        
        # ==================== INCOME VS EXPENSES ====================
        if total_income > 0 or total_expenses > 0:
            story.append(Paragraph("8. INCOME vs EXPENSES ANALYSIS", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            
            chart_data = {'Income': total_income, 'Expenses': total_expenses}
            chart_buffer = self._create_chart('bar', chart_data)
            if chart_buffer:
                chart_img = Image(chart_buffer, width=140*mm, height=50*mm)
                chart_img.hAlign = 'CENTER'
                story.append(chart_img)
                story.append(Spacer(1, 4*mm))
        
        # ==================== DETAILED INCOME ====================
        if analytics['income_details']:
            story.append(PageBreak())
            story.append(Paragraph("9. DETAILED INCOME TRANSACTIONS", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            
            income_data = [['Date', 'Customer', 'Category', 'Amount', 'Status']]
            for row in analytics['income_details']:
                income_data.append([
                    row[0],
                    row[1][:20] + '...' if len(row[1]) > 20 else row[1],
                    row[2][:15] + '...' if len(row[2]) > 15 else row[2],
                    self._format_currency(row[3]),
                    row[4]
                ])
            
            income_table = Table(income_data, colWidths=[page_width*0.15, page_width*0.25, page_width*0.25, page_width*0.20, page_width*0.15])
            income_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_SMALL),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(income_table)
            story.append(Spacer(1, 4*mm))
        
        # ==================== DETAILED EXPENSES ====================
        if analytics['expense_details']:
            story.append(Paragraph("10. DETAILED EXPENSE BREAKDOWN", section_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=self.COLOR_PURPLE, spaceAfter=3*mm))
            
            expense_data = [['Date', 'Category', 'Description', 'Amount', 'Added By']]
            for row in analytics['expense_details']:
                expense_data.append([
                    row[0],
                    row[1][:15] + '...' if len(row[1]) > 15 else row[1],
                    self._clean_html(row[2][:25] + '...' if len(row[2]) > 25 else row[2]),
                    self._format_currency(row[3]),
                    row[4][:15] + '...' if row[4] and len(row[4]) > 15 else (row[4] or 'N/A')
                ])
            
            expense_table = Table(expense_data, colWidths=[page_width*0.12, page_width*0.18, page_width*0.35, page_width*0.20, page_width*0.15])
            expense_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), self.FONT_SMALL),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.COLOR_BLACK),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_DARKGRAY),
                ('ALIGN', (3, 0), (4, -1), 'RIGHT'),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LINEBELOW', (0, 0), (-1, 0), 1, self.COLOR_BLACK),
                ('GRID', (0, 1), (-1, -1), 0.5, self.COLOR_VERYLIGHTGRAY),
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_ULTRALIGHTGRAY),
            ]))
            story.append(expense_table)
        
        # Build PDF with custom canvas for footers
        doc.build(story, onFirstPage=lambda c, d: None, 
                 onLaterPages=lambda c, d: None, canvasmaker=NumberedCanvas)
        
        return {
            'success': True,
            'filepath': filepath,
            'filename': filename,
            'summary': summary,
            'analytics': analytics
        }


# Convenience functions
def generate_daily_report(db_path='pos_database.db', target_date=None):
    if target_date is None:
        target_date = datetime.now().strftime('%Y-%m-%d')
    generator = ExecutiveReportGenerator(db_path)
    return generator.generate_report(target_date, target_date, 'Daily')


def generate_weekly_report(db_path='pos_database.db', end_date=None):
    if end_date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    start_date = end_date - timedelta(days=6)
    generator = ExecutiveReportGenerator(db_path)
    return generator.generate_report(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 'Weekly')


def generate_monthly_report(db_path='pos_database.db', year=None, month=None):
    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    generator = ExecutiveReportGenerator(db_path)
    return generator.generate_report(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), 'Monthly')
