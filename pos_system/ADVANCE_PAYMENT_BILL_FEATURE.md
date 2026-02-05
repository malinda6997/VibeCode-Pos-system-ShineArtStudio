# 💰 Advance Payment Bill Generation Feature

## ✅ Feature Implemented Successfully

The billing system now supports **advance payment bills** with proper tracking of advance amounts and balance due.

---

## 🎯 What's New?

### Before:
❌ System showed error: "Bills do not support advance payment"  
❌ Users had to select "Full Payment" only  
❌ No way to track partial payments

### After:
✅ **Advance Payment** option now generates bills  
✅ Bills show **Advance Paid** and **Balance Due**  
✅ Full payment tracking in database  
✅ Professional bill format with payment breakdown

---

## 📋 How to Use

### Step 1: Select Advance Payment Option
1. Open **Billing & Invoice** section
2. Select customer or enter guest customer
3. Add items to cart
4. In the **Payment Type** section, select **"Advance Payment"** radio button

### Step 2: Enter Advance Amount
1. The **Advance Amount** field becomes active
2. Enter the advance payment amount (must be greater than 0)
3. System automatically calculates **Balance Due** (shown in red)

### Step 3: Generate Bill
1. Click **"Generate Bill"** button
2. System validates:
   - Advance amount > 0
   - Advance amount ≤ Total amount
   - All required fields filled
3. Bill is generated and saved to `bills/` folder
4. PDF opens automatically

---

## 🧾 Bill Format

### Full Payment Bill:
```
================================
        STUDIO SHINE ART
    No:52/1/1, Maravila Road
           Nattandiya
      Reg No: 26/3610
  Tel: 0767898604 / 0322051680
================================
Bill No: BILL-0001
Date: 2026-02-03 10:30:45
Cashier: Admin User

Customer: John Doe
Mobile: 0771234567

Item                     Amt
Wedding Photography
  1 x Rs.15000.00  Rs.15000.00
Photo Frame Gold
  2 x Rs.500.00    Rs.1000.00

Subtotal:        Rs.16000.00
Service Charge:  Rs.2000.00
--------------------------------
TOTAL:           Rs.18000.00
Paid:            Rs.18000.00
Change:          Rs.0.00
================================
    Thank you! Come again.
```

### Advance Payment Bill:
```
================================
        STUDIO SHINE ART
    No:52/1/1, Maravila Road
           Nattandiya
      Reg No: 26/3610
  Tel: 0767898604 / 0322051680
================================
Bill No: BILL-0002
Date: 2026-02-03 11:15:30
Cashier: Admin User

Customer: Jane Smith
Mobile: 0779876543

Item                     Amt
Children Photography
  1 x Rs.8000.00   Rs.8000.00
Photo Album Premium
  1 x Rs.3000.00   Rs.3000.00

Subtotal:        Rs.11000.00
Service Charge:  Rs.1500.00
--------------------------------
TOTAL:           Rs.12500.00

Advance Paid:    Rs.5000.00
BALANCE DUE:     Rs.7500.00
================================
    Thank you! Come again.
```

---

## 🔧 Technical Implementation

### Database Changes:

#### New Columns Added to `bills` Table:
```sql
ALTER TABLE bills ADD COLUMN advance_amount REAL DEFAULT 0;
ALTER TABLE bills ADD COLUMN balance_due REAL DEFAULT 0;
```

#### Updated `create_bill()` Method:
```python
def create_bill(
    bill_number, customer_id, subtotal, discount, 
    total_amount, created_by, service_charge=0, 
    cash_given=0, guest_name=None, 
    advance_amount=0,  # NEW
    balance_due=0      # NEW
)
```

### Files Modified:

1. **database/schema.py**
   - Added `advance_amount` column to bills table
   - Added `balance_due` column to bills table
   - Included migration logic for existing databases

2. **database/db_manager.py**
   - Updated `create_bill()` method signature
   - Added `advance_amount` and `balance_due` parameters
   - Updated INSERT query to include new fields

3. **ui/billing_frame.py**
   - **Removed restriction** that blocked advance payment bills
   - Added advance payment validation:
     - Must be > 0
     - Cannot exceed total amount
   - Calculate `balance_due = total - advance_amount`
   - Pass advance and balance to `create_bill()`

4. **services/bill_generator.py**
   - Enhanced bill layout to show advance payment info
   - Display "Advance Paid: Rs. X.XX"
   - Display "BALANCE DUE: Rs. X.XX" in bold
   - Conditional rendering (full payment vs advance payment)

---

## ✅ Validation Rules

### Advance Payment Validation:
1. **Advance amount must be greater than 0**
   - Error: "Advance payment must be greater than 0"

2. **Advance cannot exceed total**
   - Error: "Advance payment cannot exceed total amount"

3. **Advance entry must be valid number**
   - Error: "Please enter valid advance payment amount"

4. **Customer must be selected**
   - Error: "Please select a customer" or "Please enter guest customer name"

5. **Cart must have items**
   - Error: "Please add items to cart"

---

## 💾 Database Storage

### Bill Record Example (Advance Payment):
```python
{
    'id': 2,
    'bill_number': 'BILL-0002',
    'customer_id': 5,
    'guest_name': None,
    'subtotal': 11000.00,
    'discount': 0.00,
    'service_charge': 1500.00,
    'total_amount': 12500.00,
    'cash_given': 0.00,
    'advance_amount': 5000.00,    # NEW
    'balance_due': 7500.00,       # NEW
    'created_by': 1,
    'created_at': '2026-02-03 11:15:30'
}
```

### Bill Record Example (Full Payment):
```python
{
    'id': 1,
    'bill_number': 'BILL-0001',
    'customer_id': 3,
    'guest_name': None,
    'subtotal': 16000.00,
    'discount': 0.00,
    'service_charge': 2000.00,
    'total_amount': 18000.00,
    'cash_given': 20000.00,
    'advance_amount': 18000.00,   # Full payment = total
    'balance_due': 0.00,          # No balance
    'created_by': 1,
    'created_at': '2026-02-03 10:30:45'
}
```

---

## 🎨 UI Changes

### Payment Type Section:
```
┌─────────────────────────────────────┐
│        Payment Type                  │
├─────────────────────────────────────┤
│  ⚪ Full Payment                     │
│  🔵 Advance Payment                 │
│                                      │
│  Advance Amount: [___________]      │
│                                      │
└─────────────────────────────────────┘
```

### Balance Display (Red if balance > 0):
```
┌─────────────────────────────────────┐
│  Subtotal:      LKR 11,000.00       │
│  Service:       LKR  1,500.00       │
│  ─────────────────────────────      │
│  TOTAL:         LKR 12,500.00       │
│  Balance:       LKR  7,500.00 🔴    │
└─────────────────────────────────────┘
```

---

## 📊 Use Cases

### Use Case 1: Wedding Photography Advance
**Scenario**: Customer books wedding photography package

1. Add "Wedding Photography" service (Rs. 25,000)
2. Add photo frames (Rs. 5,000)
3. **Total**: Rs. 30,000 + Rs. 3,000 service = **Rs. 33,000**
4. Select **"Advance Payment"**
5. Enter **Rs. 10,000** as advance
6. **Balance Due**: Rs. 23,000
7. Generate Bill → Customer receives bill showing advance and balance

### Use Case 2: Children Photo Session Partial Payment
**Scenario**: Parent pays partial amount today

1. Add "Children Photography" service (Rs. 8,000)
2. **Total**: Rs. 8,000 + Rs. 1,000 service = **Rs. 9,000**
3. Select **"Advance Payment"**
4. Enter **Rs. 3,000** as advance
5. **Balance Due**: Rs. 6,000
6. Generate Bill → Parent has proof of payment with remaining balance

### Use Case 3: Guest Customer Advance
**Scenario**: Walk-in customer (no registration)

1. Enable **"Guest Customer (Walk-in)"** toggle
2. Enter guest name: "Sarah Johnson"
3. Add items to cart
4. Select **"Advance Payment"**
5. Enter advance amount
6. Generate Bill → Bill shows guest name with advance/balance info

---

## 🔐 Backward Compatibility

✅ **Existing bills remain unchanged**  
✅ **Database migration runs automatically**  
✅ **Old bills show 0 for advance_amount and balance_due**  
✅ **Full payment bills still work as before**  
✅ **No data loss during upgrade**

---

## 🧪 Testing Checklist

- [x] Full payment generates correct bill
- [x] Advance payment generates bill with advance/balance
- [x] Advance = 0 shows validation error
- [x] Advance > total shows validation error
- [x] Invalid advance amount shows validation error
- [x] Database fields created successfully
- [x] Migration runs on existing databases
- [x] Bill PDF displays advance information correctly
- [x] Balance Due appears in bold
- [x] Guest customer advance payment works
- [x] Registered customer advance payment works
- [x] Cart validation still works
- [x] Customer validation still works

---

## 📁 Generated Files

### Bill Naming Convention:
- **Full Payment**: `BILL-0001.pdf`, `BILL-0002.pdf`, etc.
- **Advance Payment**: Same format (no difference in filename)

### Storage Location:
```
pos_system/
  bills/
    BILL-0001.pdf  (Full Payment)
    BILL-0002.pdf  (Advance Payment)
    BILL-0003.pdf
    ...
```

---

## 🎯 Key Benefits

1. **Flexible Payment Options**
   - Customers can pay partial amounts
   - Business can track advance payments
   - Reduces payment collection issues

2. **Professional Documentation**
   - Clear breakdown of advance vs balance
   - Professional thermal receipt format
   - Customer proof of payment

3. **Accurate Tracking**
   - Database stores complete payment information
   - Easy to query advance vs full payment bills
   - Financial reporting includes payment status

4. **No Workflow Disruption**
   - Same billing interface
   - No additional steps required
   - Seamless integration with existing system

---

## 📞 Support Information

**System Developed By**: Malinda Prabath  
**Email**: malindaprabath876@gmail.com  
**Phone**: 076 220 6157

---

## 🎉 Success Summary

✅ **Advance payment bills now fully functional**  
✅ **Database upgraded with new fields**  
✅ **Bill format enhanced with payment breakdown**  
✅ **All validations in place**  
✅ **Backward compatible with existing data**  
✅ **Professional thermal receipt layout**  
✅ **Ready for production use**

---

**Status**: ✅ Production Ready  
**Version**: 1.1 (Advance Payment Support)  
**Date**: February 3, 2026  
**Files Modified**: 4  
**Database Changes**: 2 new columns  
**Testing**: ✅ Passed
