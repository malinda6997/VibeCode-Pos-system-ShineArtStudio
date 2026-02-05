# Admin Dashboard - Quick Reference Guide

## 🚀 Quick Start (Admin Users)

### Daily Opening Routine
1. ✅ Open application (balance auto-refreshes)
2. ✅ Check Opening Balance card
3. ✅ Review yesterday's performance

### Adding an Expense
```
Step 1: Locate "💸 Manual Expense Entry" section
Step 2: Enter description (e.g., "Office Supplies")
Step 3: Enter amount in LKR (e.g., 5000.00)
Step 4: Click "➕ Add Expense"
Step 5: Verify success message
```

### Switching Filter Views
- Click **📅 Daily** - See today's data
- Click **📆 Weekly** - See last 7 days
- Click **📊 Monthly** - See current month

### Generating Reports
```
Daily Report:   Click "📅 Generate Daily Report"
Weekly Report:  Click "📆 Generate Weekly Report"
Monthly Report: Click "📊 Generate Monthly Report"

→ Review summary popup
→ Click "Yes" to open PDF
→ Reports saved in /reports/ folder
```

---

## 📊 Dashboard Layout (Top to Bottom)

### 1. Header Bar
- Title: "Financial Dashboard"
- Current date
- 🔄 Refresh button

### 2. Filtering Header (Purple section)
- Three filter buttons
- Current period label

### 3. Manual Expense Entry (Red section - Admin Only)
- Description input field
- Amount input field
- Add Expense button

### 4. Daily Balance Summary (Green border - Admin Only)
- Opening Balance
- Total Income
- Total Expenses
- Net Profit/Loss

### 5. PDF Report Generation (Admin Only)
- Three report buttons

### 6. Financial Overview Cards (Admin Only)
- Today's Sales
- Pending Balances
- Weekly Sales
- Monthly Sales

### 7. General Statistics Cards
- Today's Invoices
- Total Invoices
- Total Customers
- Pending Bookings

---

## 💡 Key Formulas

```
Opening Balance (Today) = Closing Balance (Yesterday)

Total Income = Sum of all invoices for period

Total Expenses = Sum of all manual expenses for period

Net Profit/Loss = Total Income - Total Expenses

Closing Balance = Opening Balance + Net Profit/Loss
```

---

## 🎨 Color Guide

| Color | Meaning | Used For |
|-------|---------|----------|
| 🟣 Purple (#8C00FF) | Primary/Active | Buttons, headings, important values |
| 🟢 Green (#00ff88) | Positive/Income | Profit, income amounts |
| 🔴 Red (#ff6b6b) | Negative/Expenses | Losses, expense amounts |
| ⚫ Gray (#444444) | Inactive/Borders | Section borders, inactive buttons |
| ⚪ White (#ffffff) | Primary Text | All main text |

---

## 📝 Report Contents Checklist

Every PDF report includes:
- ✅ Studio logo
- ✅ Studio name
- ✅ Report type and period
- ✅ Generation date/time
- ✅ Opening balance
- ✅ Income breakdown table
- ✅ Bookings table
- ✅ Manual expenses table
- ✅ Financial summary
- ✅ Closing balance

---

## ⚡ Shortcuts & Tips

### Best Practices:
1. Add expenses **immediately** when they occur
2. Generate reports at **end of each week**
3. Review **Net Profit/Loss** daily
4. Keep expense descriptions **clear and specific**
5. Use filters to **analyze trends**

### Common Expense Descriptions:
- "Electricity Bill - [Month]"
- "Office Supplies - [Item]"
- "Equipment Maintenance - [Date]"
- "Staff Refreshments - [Date]"
- "Transportation - [Purpose]"

### Filter Use Cases:
- **Daily**: End-of-day review
- **Weekly**: Weekly team meetings
- **Monthly**: Month-end reporting

---

## 🔧 Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Opening balance is 0 | Normal for first day - builds up from today |
| Can't add expense | Check both fields are filled, amount is valid number |
| Report won't generate | Ensure /reports/ folder exists |
| Numbers look wrong | Click 🔄 Refresh button |
| PDF won't open | Install a PDF reader (Adobe, Chrome, etc.) |

---

## 📞 Need Help?

1. **Check documentation**: Read `DASHBOARD_REVAMP_DOCUMENTATION.md`
2. **Run test**: Execute `test_dashboard_revamp.py`
3. **Check console**: Look for error messages in terminal
4. **Verify database**: Ensure schema is updated

---

## 🎯 Daily Checklist for Admins

Morning:
- [ ] Open application
- [ ] Check opening balance
- [ ] Review previous day's closing

Throughout Day:
- [ ] Add expenses as they occur
- [ ] Monitor income in real-time
- [ ] Check pending balances

End of Day:
- [ ] Add any remaining expenses
- [ ] Generate daily report
- [ ] Review net profit/loss
- [ ] Verify closing balance

End of Week:
- [ ] Generate weekly report
- [ ] Analyze weekly trends
- [ ] Compare to previous weeks

End of Month:
- [ ] Generate monthly report
- [ ] Review monthly performance
- [ ] Archive reports for records

---

**Remember:** Consistent data entry = Accurate financial insights! 💪
