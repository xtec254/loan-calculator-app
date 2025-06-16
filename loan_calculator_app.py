import math

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

def calc_insurance(principal, months, insurance_rate):
    return math.ceil(principal * (insurance_rate / 100) * (months / 12))

def calc_processing(principal, processing_rate, processing_min):
    return math.ceil(max(principal * (processing_rate / 100), processing_min))

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
    processing = calc_processing(principal, product["processing_rate"], product["processing_min"])
    total = principal + insurance + processing

    results.append({
        "name": product["name"],
        "type": product["type"],
        "rate": product["interest_rate"],
        "principal": principal,
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
        print(f"Insurance ({loan_products['1']['insurance_rate']}%) : KES {r['insurance']}")
        print(f"Processing Fee      : KES {r['processing']}")
        print(f"Total Loan Cost     : KES {r['total']}")

    best = min(results, key=lambda x: x['total'])
    print("\n✅ Recommended Product:")
    print(f"> {best['name']} ({best['type'].capitalize()} Rate) with total cost of KES {best['total']}")
else:
    print("\n⚠️ No products matched your loan period or repayment capacity. Try adjusting inputs.")
