# Advance Payment Bill - Quick Start Guide

## 🚀 Quick Steps

### 1️⃣ Select Advance Payment
In the billing screen, you'll see:
- ⚪ Full Payment
- 🔵 **Advance Payment** ← Click this!

### 2️⃣ Enter Advance Amount
- The "Advance Amount" field becomes active
- Type the partial payment amount (e.g., 5000)
- Balance updates automatically (shown in red)

### 3️⃣ Generate Bill
- Click "Generate Bill" button
- Bill PDF opens showing:
  - **Advance Paid: Rs. 5,000.00**
  - **BALANCE DUE: Rs. 7,500.00**

---

## ✅ What Changed?

### Before Update:
```
❌ Error Message:
"Bills do not support advance payment. 
Use full payment or create a booking 
for advance payments."
```

### After Update:
```
✅ Bill Generated Successfully!

Bill shows:
TOTAL:           Rs.12,500.00

Advance Paid:    Rs.5,000.00
BALANCE DUE:     Rs.7,500.00
```

---

## 🔍 Example Scenarios

### Scenario A: Wedding Package Advance
```
Cart:
- Wedding Photography: Rs. 25,000
- Photo Frames: Rs. 5,000
- Service Charge: Rs. 3,000
─────────────────────────────────
TOTAL: Rs. 33,000

Payment Type: Advance Payment
Advance Amount: Rs. 10,000
─────────────────────────────────
✅ BALANCE DUE: Rs. 23,000
```

### Scenario B: Children Session Partial
```
Cart:
- Children Photography: Rs. 8,000
- Service Charge: Rs. 1,000
─────────────────────────────────
TOTAL: Rs. 9,000

Payment Type: Advance Payment
Advance Amount: Rs. 3,000
─────────────────────────────────
✅ BALANCE DUE: Rs. 6,000
```

---

## ⚠️ Important Rules

1. **Advance must be greater than 0**
2. **Advance cannot exceed total amount**
3. **Customer must be selected** (or guest name entered)
4. **Cart must have items**

---

## 💡 Tips

- **Guest Customers**: Enable "Guest Customer (Walk-in)" toggle for walk-ins
- **Balance Tracking**: Balance shown in red color on screen
- **Bill Format**: Thermal receipt format (80mm width)
- **Storage**: Bills saved to `bills/` folder automatically

---

## 🎯 Success!

Your advance payment bill feature is now working! Generate bills with confidence for both **full** and **advance** payments. 🎉
