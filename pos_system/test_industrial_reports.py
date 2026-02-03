"""
Test the Industrial Financial Analytics Report Generator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.industrial_report_generator import (
    IndustrialReportGenerator,
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report
)
from datetime import datetime

def test_industrial_reports():
    """Test the new industrial report generator"""
    print("=" * 60)
    print("🏭 TESTING INDUSTRIAL FINANCIAL ANALYTICS REPORTS")
    print("=" * 60)
    print()
    
    db_path = 'pos_database.db'
    
    # Test 1: Daily Report
    print("📊 TEST 1: Generating Daily Industrial Report...")
    try:
        result = generate_daily_report(db_path)
        if result['success']:
            print(f"✅ Daily Report Generated: {result['filename']}")
            print(f"   Opening Balance: {result['summary']['opening_balance']:,.2f}")
            print(f"   Total Income: {result['summary']['total_income']:,.2f}")
            print(f"   Total Expenses: {result['summary']['total_expenses']:,.2f}")
            print(f"   Net P/L: {result['summary']['net_balance']:,.2f}")
            print(f"   Closing Balance: {result['summary']['closing_balance']:,.2f}")
            print(f"   📁 File: {result['filepath']}")
        else:
            print("❌ Daily report generation failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Weekly Report
    print("📊 TEST 2: Generating Weekly Industrial Report...")
    try:
        result = generate_weekly_report(db_path)
        if result['success']:
            print(f"✅ Weekly Report Generated: {result['filename']}")
            print(f"   Opening Balance: {result['summary']['opening_balance']:,.2f}")
            print(f"   Total Income: {result['summary']['total_income']:,.2f}")
            print(f"   Total Expenses: {result['summary']['total_expenses']:,.2f}")
            print(f"   Net P/L: {result['summary']['net_balance']:,.2f}")
            print(f"   Closing Balance: {result['summary']['closing_balance']:,.2f}")
        else:
            print("❌ Weekly report generation failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Monthly Report
    print("📊 TEST 3: Generating Monthly Industrial Report...")
    try:
        result = generate_monthly_report(db_path, 2026, 2)
        if result['success']:
            print(f"✅ Monthly Report Generated: {result['filename']}")
            print(f"   Opening Balance: {result['summary']['opening_balance']:,.2f}")
            print(f"   Total Income: {result['summary']['total_income']:,.2f}")
            print(f"   Total Expenses: {result['summary']['total_expenses']:,.2f}")
            print(f"   Net P/L: {result['summary']['net_balance']:,.2f}")
            print(f"   Closing Balance: {result['summary']['closing_balance']:,.2f}")
            
            # Show analytics data
            analytics = result['analytics']
            print()
            print("   📈 ADVANCED ANALYTICS:")
            print(f"      New Customers: {analytics['user_insights']['new_customers']}")
            print(f"      Total Customers: {analytics['user_insights']['total_customers']}")
            print(f"      Top Customers: {len(analytics['top_customers'])}")
            print(f"      Service Categories: {len(analytics['service_revenue'])}")
            print(f"      Advance Payments: LKR {analytics['payment_metrics']['advance_received']:,.2f}")
            print(f"      Balance Due: LKR {analytics['payment_metrics']['balance_due']:,.2f}")
        else:
            print("❌ Monthly report generation failed")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)
    print("🎉 INDUSTRIAL REPORT TESTING COMPLETE")
    print("=" * 60)
    print()
    print("📁 All reports saved in 'reports/' directory")
    print("✨ Features included:")
    print("   - Black & White minimalist design")
    print("   - Advanced analytics (User Insights, Top Customers)")
    print("   - Service Revenue Breakdown with charts")
    print("   - Booking Status Summary")
    print("   - Payment Metrics (Advance vs Balance)")
    print("   - Income vs Expense visualization")
    print("   - Professional typography (11pt/9pt fonts)")
    print("   - Elegant thin lines (0.5pt separators)")
    print("   - Clean tables without HTML tags")
    print("   - Currency formatting (LKR with decimals)")

if __name__ == '__main__':
    test_industrial_reports()
