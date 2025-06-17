import math
import tkinter as tk

root = tk.Tk()
root.title("Loan Calculator")
tk.Label(root, text="Welcome to the calculator ").pack()
root.mainloop()

# --- Loan Calculator App ---           


# --- Calculation functions ---

def calc_reducing_principal(monthly_payment, annual_rate, months):
    r = (annual_rate / 100) / 12
    if r == 0:
        principal = monthly_payment * months
    else:
        principal = monthly_payment * (1 - (1 + r) ** -months) / r
    return math.ceil(principal)

def calc_flat_principal(monthly_payment, annual_rate, months):
    t = months / 12
    r = annual_rate / 100
    principal = (monthly_payment * months) / (1 + r * t)
    return math.ceil(principal)

def calc_total_interest(principal, annual_rate, months, method):
    r = annual_rate / 100
    t = months / 12

    if method == "flat":
        return math.ceil(principal * r * t)
    elif method == "reducing":
        monthly_r = r / 12
        total_payment = principal * monthly_r * (1 + (1 + monthly_r) ** months) / ((1 + monthly_r) ** months - 1) * months
        return math.ceil(total_payment - principal)
    return 0


def calc_insurance(principal, months, insurance_rate):
    return math.ceil(principal * (insurance_rate / 100) * (months / 12))

def calc_processing(principal, processing_rate, processing_min):
    return math.ceil(max(principal * (processing_rate / 100), processing_min))

def generate_amortization_table(principal, annual_rate, months):
    r = (annual_rate / 100) / 12
    monthly_payment = math.ceil(principal * r * (1 + r) ** months / ((1 + r) ** months - 1))

    balance = principal
    table = []

    for i in range(1, months + 1):
        interest = round(balance * r)
        principal_payment = round(principal / months)
        processing_fee = math.ceil((calc_processing(principal, 3, 600))/months)  # Assuming a fixed processing rate of 3% and min 600
        insurance_fee = round((calc_insurance(principal, months, 3))/months)  # Assuming a fixed insurance rate of 3%
        monthly_payment = repayment 
        balance = max(0, round(balance - principal_payment))

        table.append({
            "Month": i,
            "Interest": interest,
            "Principal": principal_payment,
            "Processing": processing_fee,
            "Insurance": insurance_fee,
            "Payment": monthly_payment,
            "Balance": balance
        })

    return table


# --- Loan Products (fully configured per product) ---

loan_products = {
    "1": {
        "name": "Fanaka Loan", "interest_rate": 24, "type": "flat",
        "insurance_rate": 3, "processing_rate": 19, "processing_min": 600,
        "amount_range": (100000, 5000000), "month_range": (1,144)
    },
    "2": {
        "name": "Payslip Loan", "interest_rate": 120, "type": "reducing",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (500, 500000), "month_range": (1, 144)
    },
    "3": {
        "name": "Msingi Loan 1", "interest_rate": 36, "type": "flat",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (500, 300000), "month_range": (1, 6)
    },
    "4": {
        "name": "Msingi Loan 2", "interest_rate": 42, "type": "flat",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (500, 300000), "month_range": (6, 12)
    },
    "5": {
        "name": "Bosika Mini", "interest_rate": 48, "type": "flat",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (50000, 99999), "month_range": (1, 6)
    }
}

# --- Input ---

print("\n💰 Loan Product Estimator")
repayment = float(input("Enter your target monthly repayment (KES): "))
months = int(input("Enter desired loan period in months: "))

# --- Calculation & Filtering ---

results = []

for product in loan_products.values():
    if months < product["month_range"][0] or months > product["month_range"][1]:
        continue  # Skip if loan period is outside allowed range

    # Calculate principal
    if product["type"] == "reducing":
        principal = calc_reducing_principal(repayment, product["interest_rate"], months)
    else:
        principal = calc_flat_principal(repayment, product["interest_rate"], months)

    # Skip if principal is outside allowed amount range
    if principal < product["amount_range"][0] or principal > product["amount_range"][1]:
        continue

    insurance = calc_insurance(principal, months, product["insurance_rate"])
    processing  = calc_processing(principal, product["processing_rate"], product["processing_min"])
    interest = calc_total_interest(principal, product["interest_rate"], months, product["type"])
    total = principal + insurance + processing + interest

    results.append({
        "name": product["name"],
        "type": product["type"],
        "rate": product["interest_rate"],
        "principal": principal,
        "interest": interest,
        "insurance": insurance,
        "processing": processing,
        "total": total
    })

# --- Output ---
if results:
    for r in results:
        print(f"\n[{r['name']}] ({r['type'].capitalize()} Rate)")
        print(f"Interest Rate       : {r['rate']}%")
        print(f"Estimated Principal : KES {r['principal']}")
        print(f"Interest            : KES {r['interest']}")
        print(f"Insurance ({loan_products['1']['insurance_rate']}%) : KES {r['insurance']}")
        print(f"Processing Fee      : KES {r['processing']}")
        print(f"Total Loan Cost     : KES {r['total']}")

    best = min(results, key=lambda x: x['total'])
    print("\n✅ Recommended Product:")
    print(f"> {best['name']} ({best['type'].capitalize()} Rate) with total cost of KES {best['total']}")
else:
    print("\n⚠️ No products matched your loan period or repayment capacity. Try adjusting inputs.")

if best['type'] == "reducing":
    print("\n📊 Amortization Schedule:")
    amort_table = generate_amortization_table(best['principal'], best['rate'], months)
    print(f"{'Month':<6} {'Interest':<10} {'Principal':<10} {'Processing':<10} {'Insurance':<10} {'Payment':<10} {'Balance':<10}")
    for row in amort_table:
        print(f"{row['Month']:<6} {row['Interest']:<10} {row['Principal']:<10} {row['Processing']:<10} {row['Insurance']:<10} {row['Payment']:<10} {row['Balance']:<10}")

