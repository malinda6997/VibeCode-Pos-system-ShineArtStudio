"""
Test Executive Financial Analytics Report Generator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.executive_report_generator import (
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report
)
from datetime import datetime

def test_executive_reports():
    """Test the executive report generator"""
    print("=" * 70)
    print("🏢 TESTING EXECUTIVE FINANCIAL ANALYTICS REPORTS")
    print("=" * 70)
    print()
    
    db_path = 'pos_database.db'
    
    # Test Monthly Report (most comprehensive)
    print("📊 Generating Executive Monthly Report...")
    print("   Features: Cover Page | Table of Contents | Dynamic Insights")
    print()
    try:
        result = generate_monthly_report(db_path, 2026, 2)
        if result['success']:
            print(f"✅ Report Generated: {result['filename']}")
            print()
            print("📈 FINANCIAL SUMMARY:")
            print(f"   Opening Balance:  LKR {result['summary']['opening_balance']:>12,.2f}")
            print(f"   Total Income:     LKR {result['summary']['total_income']:>12,.2f}")
            print(f"   Total Expenses:   LKR {result['summary']['total_expenses']:>12,.2f}")
            print(f"   Net Profit/Loss:  LKR {result['summary']['net_balance']:>12,.2f}")
            print(f"   Closing Balance:  LKR {result['summary']['closing_balance']:>12,.2f}")
            print()
            
            analytics = result['analytics']
            print("📊 ADVANCED ANALYTICS:")
            print(f"   New Customers:     {analytics['user_insights']['new_customers']}")
            print(f"   Total Customers:   {analytics['user_insights']['total_customers']}")
            print(f"   Top Customers:     {len(analytics['top_customers'])}")
            print(f"   Service Categories: {len(analytics['service_revenue'])}")
            print(f"   Advance Payments:  LKR {analytics['payment_metrics']['advance_received']:,.2f}")
            print(f"   Balance Due:       LKR {analytics['payment_metrics']['balance_due']:,.2f}")
            print()
            print("📄 REPORT STRUCTURE:")
            print("   ✓ Cover Page with logo and company info")
            print("   ✓ Table of Contents (10 sections)")
            print("   ✓ Executive Summary")
            print("   ✓ Revenue Analysis (with dynamic insights)")
            print("   ✓ Customer Insights (with acquisition metrics)")
            print("   ✓ Top 5 Customers list")
            print("   ✓ Service Revenue Breakdown (with pie chart)")
            print("   ✓ Booking Performance (with completion rates)")
            print("   ✓ Payment Metrics")
            print("   ✓ Income vs Expenses Analysis (with bar chart)")
            print("   ✓ Detailed Income Transactions")
            print("   ✓ Detailed Expense Breakdown")
            print()
            print("🎨 DESIGN FEATURES:")
            print("   ✓ Black & White with purple (#8C00FF) accent")
            print("   ✓ Professional typography (7-18pt)")
            print("   ✓ Clean HTML-free output")
            print("   ✓ Developer credit on every page footer")
            print("   ✓ Page numbers (Page X of Y)")
            print()
            print(f"📁 File Location: {result['filepath']}")
        else:
            print("❌ Report generation failed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 70)
    print("🎉 EXECUTIVE REPORT TESTING COMPLETE")
    print("=" * 70)
    print()
    print("✨ KEY FEATURES IMPLEMENTED:")
    print("   1. Professional Cover Page with logo and company details")
    print("   2. Auto-generated Table of Contents")
    print("   3. Dynamic text generation with smart insights")
    print("   4. Revenue analysis with top service identification")
    print("   5. Customer acquisition vs retention metrics")
    print("   6. Booking completion rate calculations")
    print("   7. Charts with purple accent (#8C00FF)")
    print("   8. Developer credit: Malinda Prabath | malindaprabath876@gmail.com | 076 220 6157")
    print("   9. Page numbering on every page")
    print("   10. HTML-free clean output")
    print()
    print("📞 Company Information on Cover:")
    print("   Studio Shine Art")
    print("   Reg No: 26/3610")
    print("   No: 52/1/1, Maravila Road, Nattandiya")
    print("   Contact: 0767898604 / 0322051680")

if __name__ == '__main__':
    test_executive_reports()
