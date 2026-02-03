"""
Test script for the revamped Admin Dashboard features
Tests: Expense tracking, Balance management, PDF report generation
"""

from services.dashboard_service import DashboardService
from services.financial_report_generator import FinancialReportGenerator
from datetime import datetime, timedelta

def test_expense_management():
    """Test expense management functionality"""
    print("\n" + "="*60)
    print("TEST 1: Expense Management")
    print("="*60)
    
    service = DashboardService()
    
    # Test adding expense
    today = datetime.now().strftime('%Y-%m-%d')
    success = service.add_manual_expense(
        description="Test Expense - Office Supplies",
        amount=5000.00,
        created_by=1,  # Admin user
        expense_date=today
    )
    
    if success:
        print("✅ Expense added successfully")
    else:
        print("❌ Failed to add expense")
    
    # Test getting expenses by date
    expenses = service.get_expenses_by_date(today)
    print(f"📊 Total expenses for today: LKR {expenses:,.2f}")
    
    # Test getting expense details
    details = service.get_expense_details_by_range(today, today)
    print(f"📋 Number of expense records: {len(details)}")
    
    return success

def test_balance_management():
    """Test balance tracking functionality"""
    print("\n" + "="*60)
    print("TEST 2: Balance Management")
    print("="*60)
    
    service = DashboardService()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Update daily balance
    success = service.update_daily_balance(today)
    
    if success:
        print("✅ Daily balance updated successfully")
    else:
        print("❌ Failed to update daily balance")
    
    # Get opening balance
    opening = service.get_opening_balance(today)
    print(f"💰 Opening balance: LKR {opening:,.2f}")
    
    # Get income
    income = service.get_today_sales()
    print(f"📈 Today's income: LKR {income:,.2f}")
    
    # Get expenses
    expenses = service.get_expenses_by_date(today)
    print(f"📉 Today's expenses: LKR {expenses:,.2f}")
    
    # Calculate net
    net = income - expenses
    print(f"💵 Net profit/loss: LKR {net:,.2f}")
    
    return success

def test_report_generation():
    """Test PDF report generation"""
    print("\n" + "="*60)
    print("TEST 3: PDF Report Generation")
    print("="*60)
    
    generator = FinancialReportGenerator()
    
    # Test daily report
    print("\n📄 Generating Daily Report...")
    try:
        result = generator.generate_daily_report()
        if result['success']:
            print(f"✅ Daily report generated: {result['filename']}")
            summary = result['summary']
            print(f"   Opening: LKR {summary['opening_balance']:,.2f}")
            print(f"   Income: LKR {summary['total_income']:,.2f}")
            print(f"   Expenses: LKR {summary['total_expenses']:,.2f}")
            print(f"   Net: LKR {summary['net_balance']:,.2f}")
            print(f"   Closing: LKR {summary['closing_balance']:,.2f}")
        else:
            print("❌ Failed to generate daily report")
            return False
    except Exception as e:
        print(f"❌ Error generating daily report: {e}")
        return False
    
    # Test weekly report
    print("\n📆 Generating Weekly Report...")
    try:
        result = generator.generate_weekly_report()
        if result['success']:
            print(f"✅ Weekly report generated: {result['filename']}")
        else:
            print("❌ Failed to generate weekly report")
            return False
    except Exception as e:
        print(f"❌ Error generating weekly report: {e}")
        return False
    
    # Test monthly report
    print("\n📊 Generating Monthly Report...")
    try:
        today = datetime.now()
        result = generator.generate_monthly_report(today.year, today.month)
        if result['success']:
            print(f"✅ Monthly report generated: {result['filename']}")
        else:
            print("❌ Failed to generate monthly report")
            return False
    except Exception as e:
        print(f"❌ Error generating monthly report: {e}")
        return False
    
    return True

def test_filter_modes():
    """Test filter modes functionality"""
    print("\n" + "="*60)
    print("TEST 4: Filter Modes")
    print("="*60)
    
    service = DashboardService()
    
    # Test daily filter
    print("\n📅 Daily Filter:")
    today = datetime.now().strftime('%Y-%m-%d')
    expenses = service.get_expenses_by_date(today)
    print(f"   Today's expenses: LKR {expenses:,.2f}")
    
    # Test weekly filter
    print("\n📆 Weekly Filter:")
    weekly_expenses = service.get_weekly_expenses()
    print(f"   This week's expenses: LKR {weekly_expenses:,.2f}")
    
    # Test monthly filter
    print("\n📊 Monthly Filter:")
    monthly_expenses = service.get_monthly_expenses()
    print(f"   This month's expenses: LKR {monthly_expenses:,.2f}")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING REVAMPED ADMIN DASHBOARD")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Expense Management", test_expense_management()))
    results.append(("Balance Management", test_balance_management()))
    results.append(("PDF Report Generation", test_report_generation()))
    results.append(("Filter Modes", test_filter_modes()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️ Some tests failed. Please review the errors above.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
