# 📋 Bill History - Guest Customer Support & Filter Feature

## ✅ Implementation Complete

Successfully implemented **guest customer bills** in bill history with **filter toggle** for registered vs guest customers.

---

## 🎯 What's New?

### Before:
❌ Guest customer bills not showing in bill history  
❌ Only registered customer bills visible  
❌ No way to filter between customer types  
❌ Using wrong database table (invoices instead of bills)

### After:
✅ **All bills show in history** (guest + registered)  
✅ **Filter toggle buttons** (All / Registered / Guest)  
✅ **Correct database table** (bills table)  
✅ **Guest customer indicator** ("Guest Customer" in mobile column)  
✅ **Advance/Balance columns** (instead of Paid/Balance)  
✅ **Search works for all bills**  
✅ **Reprint works for both types**  
✅ **View details shows customer type**

---

## 🔧 Filter Toggle Buttons

### Filter Options:
```
┌─────────────────────────────────────────┐
│ Filter:  ⚪ All  ⚪ Registered  ⚪ Guest │
└─────────────────────────────────────────┘
```

### Filter Behavior:
- **All** (default): Shows all bills (guest + registered)
- **Registered**: Shows only bills with registered customers
- **Guest**: Shows only bills with guest customers (walk-ins)

---

## 📊 Bill History Display

### Table Columns:
| Bill # | Date | Customer | Mobile | Items | Total | Paid | Balance |
|--------|------|----------|--------|-------|-------|------|---------|
| BILL-0001 | 2026-02-03 | John Doe | 0771234567 | 3 | 18000.00 | 18000.00 | 0.00 |
| BILL-0002 | 2026-02-03 | Sarah | Guest Customer | 2 | 12500.00 | 5000.00 | 7500.00 |

### Visual Indicators:
- **Green text**: Registered customer with mobile number
- **"Guest Customer"**: Guest/walk-in customer (no mobile)
- **Yellow highlight**: Bills with balance due > 0
- **Alternating rows**: Black/dark gray for easy reading

---

## 🔍 How Filters Work

### Example 1: View All Bills
```
Filter: ⚪ All  ○ Registered  ○ Guest

Result: Shows 5 bills
- 3 registered customer bills
- 2 guest customer bills
```

### Example 2: View Only Registered Customers
```
Filter: ○ All  ⚪ Registered  ○ Guest

Result: Shows 3 bills
- Only bills with registered customers
- Guest bills hidden
```

### Example 3: View Only Guest Customers
```
Filter: ○ All  ○ Registered  ⚪ Guest

Result: Shows 2 bills
- Only bills with guest/walk-in customers
- Registered customer bills hidden
```

---

## 🔎 Search Functionality

### Search Works Across All Fields:
1. **Bill Number**: Search "BILL-0001"
2. **Customer Name**: Search "Sarah" or "John"
3. **Mobile Number**: Search "0771234567"

### Search + Filter Combined:
```
Search: "Sarah"
Filter: Guest
Result: Only guest customer bills matching "Sarah"
```

---

## 📄 View Details Dialog

### Guest Customer Bill:
```
📄 Bill Number: BILL-0002
📅 Date: 2026-02-03 10:30:45
👤 Guest Customer
👤 Customer: Sarah Johnson
📱 Mobile: Guest Customer

Items:
- Children Photography     1 x 8000.00 = 8000.00
- Photo Album Premium      1 x 3000.00 = 3000.00

-----------------------------------
Subtotal:        LKR 11,000.00
Discount:        LKR 0.00
Service Charge:  LKR 1,500.00
Total Amount:    LKR 12,500.00
Advance Paid:    LKR 5,000.00
Balance Due:     LKR 7,500.00
```

### Registered Customer Bill:
```
📄 Bill Number: BILL-0001
📅 Date: 2026-02-03 09:15:20
👤 Registered Customer
👤 Customer: John Doe
📱 Mobile: 0771234567

Items:
- Wedding Photography      1 x 15000.00 = 15000.00
- Photo Frame Gold         2 x 500.00 = 1000.00

-----------------------------------
Subtotal:        LKR 16,000.00
Discount:        LKR 0.00
Service Charge:  LKR 2,000.00
Total Amount:    LKR 18,000.00
Advance Paid:    LKR 18,000.00
Balance Due:     LKR 0.00
```

---

## 🖨️ Reprint Functionality

### Works for Both Types:
1. Select bill from list
2. Click **"Reprint Bill"** button
3. System generates PDF with correct customer info:
   - Guest bills: "Guest Customer" in mobile field
   - Registered bills: Actual mobile number

### Reprint Output:
```
Guest Bill:
Customer: Sarah Johnson
Mobile: Guest Customer

Registered Bill:
Customer: John Doe
Mobile: 0771234567
```

---

## 🔧 Technical Implementation

### Files Modified:

#### 1. `database/db_manager.py`
**New Methods Added:**
```python
def search_bills(search_term: str)
    # Search bills by bill number, customer name, or mobile
    # Supports both guest and registered customers

def get_bill_by_number(bill_number: str)
    # Get specific bill with full details
    # Includes customer info for both types
```

**Updated Method:**
```python
def get_all_bills(limit: int)
    # Now includes created_by_name
    # Better query for guest vs registered
```

#### 2. `ui/bill_history_frame.py`
**Major Changes:**
- Changed from `invoices` table to `bills` table
- Added `filter_type` state variable
- Added filter toggle radio buttons (All/Registered/Guest)
- Updated all methods to use correct database methods
- Changed column headers from "Paid/Balance" to "Paid/Balance Due"
- Added guest customer detection and display

**Updated Methods:**
- `load_bills()`: Filter support + bills table
- `search_bills()`: Filter support + bills table
- `view_bill_details()`: Guest customer indicator
- `reprint_bill()`: Handle both customer types
- `delete_selected_bill()`: Delete from bills table

**New Method:**
- `apply_filter()`: Apply selected filter and reload

---

## 💾 Database Query Changes

### Before (Wrong):
```sql
-- Was querying invoices table (booking invoices)
SELECT * FROM invoices 
WHERE invoice_number NOT LIKE 'BK-%'
```

### After (Correct):
```sql
-- Now querying bills table (thermal receipts)
SELECT b.*, 
       COALESCE(c.full_name, b.guest_name) as full_name,
       c.mobile_number,
       u.full_name as created_by_name
FROM bills b
LEFT JOIN customers c ON b.customer_id = c.id
LEFT JOIN users u ON b.created_by = u.id
ORDER BY b.created_at DESC
```

### Filter Logic:
```python
# All bills
bills = all_bills

# Registered only
bills = [b for b in all_bills if b['customer_id'] is not None]

# Guest only
bills = [b for b in all_bills if b['customer_id'] is None and b['guest_name']]
```

---

## ✅ Features Checklist

- [x] Guest customer bills appear in bill history
- [x] Registered customer bills still working
- [x] Filter toggle: All / Registered / Guest
- [x] "Guest Customer" shown in mobile column
- [x] Search works for both customer types
- [x] View details shows customer type indicator
- [x] Reprint works for both types
- [x] Delete works for both types (Admin only)
- [x] Advance/Balance columns display correctly
- [x] Balance due highlighted in yellow
- [x] Mobile number or "Guest Customer" displayed
- [x] Record count updates with filter
- [x] Double-click to view details works
- [x] No errors when loading bills

---

## 🎯 Use Cases

### Use Case 1: View All Bills
**Action**: Open Bill History page  
**Default Filter**: All  
**Result**: All bills displayed (guest + registered)

### Use Case 2: Find Guest Customer Bills
**Action**: Click "Guest" filter button  
**Result**: Only guest/walk-in customer bills shown  
**Mobile Column**: Shows "Guest Customer"

### Use Case 3: View Registered Customers Only
**Action**: Click "Registered" filter button  
**Result**: Only registered customer bills shown  
**Mobile Column**: Shows actual mobile numbers

### Use Case 4: Search Guest Customer by Name
**Action**: 
1. Type "Sarah" in search box
2. Click "Guest" filter
**Result**: Only guest customer bills matching "Sarah"

### Use Case 5: Reprint Guest Customer Bill
**Action**:
1. Select guest customer bill
2. Click "Reprint Bill"
**Result**: PDF generated with "Guest Customer" mobile

---

## 🔐 Permission Control

### Admin Only:
- **Delete Selected** button (visible only to Admin)
- Can delete both guest and registered customer bills

### All Users:
- View bill history
- Search bills
- Filter bills
- View details
- Reprint bills

---

## 🎨 UI Layout

```
┌────────────────────────────────────────────────────────────┐
│                    Bills History                           │
├────────────────────────────────────────────────────────────┤
│ Search: [______________] [Refresh]                         │
│ Filter: ⚪ All ⚪ Registered ⚪ Guest                        │
│ [View Details] [Reprint Bill] [Delete Selected]            │
├────────────────────────────────────────────────────────────┤
│ 🧾 Bill Records                            5 records       │
├────────────────────────────────────────────────────────────┤
│ Bill #    │ Date       │ Customer │ Mobile        │ ...    │
├───────────┼────────────┼──────────┼───────────────┼────────┤
│ BILL-0001 │ 2026-02-03 │ John Doe │ 0771234567    │ ...    │
│ BILL-0002 │ 2026-02-03 │ Sarah    │ Guest Customer│ ...    │
│ BILL-0003 │ 2026-02-03 │ Jane S.  │ 0779876543    │ ...    │
└────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Scenarios

### Test 1: Guest Bill Appears ✅
1. Create bill with guest customer
2. Open Bill History
3. **Expected**: Guest bill appears with "Guest Customer" in mobile

### Test 2: Filter to Guest Only ✅
1. Click "Guest" filter
2. **Expected**: Only guest bills shown

### Test 3: Filter to Registered Only ✅
1. Click "Registered" filter
2. **Expected**: Only registered customer bills shown

### Test 4: Search Guest Customer ✅
1. Type guest name in search
2. **Expected**: Guest bills matching search appear

### Test 5: View Guest Bill Details ✅
1. Select guest bill
2. Click "View Details"
3. **Expected**: Dialog shows "👤 Guest Customer" indicator

### Test 6: Reprint Guest Bill ✅
1. Select guest bill
2. Click "Reprint Bill"
3. **Expected**: PDF opens with "Guest Customer" mobile

### Test 7: Advance Payment Display ✅
1. Create bill with advance payment
2. View in history
3. **Expected**: Advance and balance columns show correct amounts

### Test 8: Balance Highlighting ✅
1. Create bill with balance due > 0
2. View in history
3. **Expected**: Row highlighted in yellow

---

## 📊 Data Integrity

### Guest Customer Bill:
```python
{
    'id': 2,
    'bill_number': 'BILL-0002',
    'customer_id': None,          # No customer ID
    'guest_name': 'Sarah Johnson', # Guest name stored
    'mobile_number': None,         # No mobile in query result
    'full_name': 'Sarah Johnson',  # From COALESCE
    'total_amount': 12500.00,
    'advance_amount': 5000.00,
    'balance_due': 7500.00
}
```

### Registered Customer Bill:
```python
{
    'id': 1,
    'bill_number': 'BILL-0001',
    'customer_id': 5,              # Customer ID present
    'guest_name': None,            # No guest name
    'mobile_number': '0771234567', # Mobile from customer
    'full_name': 'John Doe',       # From customer record
    'total_amount': 18000.00,
    'advance_amount': 18000.00,
    'balance_due': 0.00
}
```

---

## 🎉 Success Summary

✅ **Guest customer bills now visible in bill history**  
✅ **Filter toggle implemented (All/Registered/Guest)**  
✅ **Search works for all bill types**  
✅ **View details shows customer type**  
✅ **Reprint works for both types**  
✅ **Delete works for both types**  
✅ **Mobile column shows "Guest Customer" for walk-ins**  
✅ **Advance/Balance columns accurate**  
✅ **No database errors**  
✅ **Clean UI with filter controls**  
✅ **Record count updates with filters**

---

**Status**: ✅ Production Ready  
**Version**: 1.2 (Bill History Enhancement)  
**Date**: February 3, 2026  
**Files Modified**: 2  
**New Methods**: 2  
**Testing**: ✅ All Passed
