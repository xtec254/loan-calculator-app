import math
import tkinter as tk

# --- Constants ---
TOLERANCE = 1  # Acceptable error in KES for reverse calculation

# --- Loan Products ---
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
        "amount_range": (10000, 300000), "month_range": (1, 6)
    },
    "4": {
        "name": "Msingi Loan 2", "interest_rate": 42, "type": "flat",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (10000, 300000), "month_range": (6, 12)
    },
    "5": {
        "name": "Bosika Mini", "interest_rate": 48, "type": "flat",
        "insurance_rate": 3, "processing_rate": 3, "processing_min": 600,
        "amount_range": (50000, 99999), "month_range": (1, 36)
    }
}

# --- Calculation Functions ---
def calculate_insurance(principal, months, rate):
    years = math.ceil(months / 12)
    return math.ceil(principal * (rate / 100) * years)

def generate_amortization(principal, annual_rate, months, product):
    r = (annual_rate / 100) / 12
    total_insurance = calculate_insurance(principal, months, product["insurance_rate"])
    monthly_insurance = math.ceil(total_insurance / months)
    total_processing = max(principal * (product["processing_rate"] / 100), product["processing_min"])
    monthly_processing = math.ceil(total_processing / months)

    amortization = []
    total_payment = 0

    if product["type"] == "reducing":
        monthly_principal = principal / months
        balance = principal
        for month in range(1, months + 1):
            interest = round(balance * r)
            payment = round(monthly_principal + interest + monthly_insurance + monthly_processing)
            total_payment += payment

            amortization.append({
                "Month": month,
                "Interest": interest,
                "Principal": round(monthly_principal),
                "Processing": monthly_processing,
                "Insurance": monthly_insurance,
                "Payment": payment,
                "Balance": max(0, round(balance - monthly_principal))
            })

            balance -= monthly_principal
    elif product["type"] == "flat":
        interest = round((principal * (annual_rate / 100)) * (months / 12))
        monthly_interest = round(interest / months)
        monthly_principal = principal / months
        for month in range(1, months + 1):
            payment = round(monthly_principal + monthly_interest + monthly_insurance + monthly_processing)
            total_payment += payment

            amortization.append({
                "Month": month,
                "Interest": monthly_interest,
                "Principal": round(monthly_principal),
                "Processing": monthly_processing,
                "Insurance": monthly_insurance,
                "Payment": payment,
                "Balance": max(0, round(principal - monthly_principal * month))
            })

    return amortization, total_payment

def reverse_amortize(target_repayment, annual_rate, months, product):
    low = 100
    high = 10000000
    best_mid = None
    best_diff = float('inf')
    best_amort = None

    while low <= high:
        mid = (low + high) // 2
        amort, _ = generate_amortization(mid, annual_rate, months, product)
        avg_monthly = sum([x['Payment'] for x in amort]) / months
        diff = abs(avg_monthly - target_repayment)

        if diff < best_diff:
            best_diff = diff
            best_mid = mid
            best_amort = amort

        if avg_monthly > target_repayment:
            high = mid - 1
        else:
            low = mid + 1

    if best_diff <= TOLERANCE:
        return best_mid, best_amort
    return None, None

# --- GUI ---
root = tk.Tk()
root.title("Custom Loan Calculator")

# Input fields
tk.Label(root, text="Monthly Repayment (KES):").grid(row=0, column=0)
repayment_entry = tk.Entry(root)
repayment_entry.grid(row=0, column=1)

tk.Label(root, text="Loan Period (months):").grid(row=1, column=0)
months_entry = tk.Entry(root)
months_entry.grid(row=1, column=1)

output = tk.Text(root, width=100, height=30)
output.grid(row=3, column=0, columnspan=2)

def calculate():
    output.delete("1.0", tk.END)
    try:
        repayment = float(repayment_entry.get())
        months = int(months_entry.get())
    except ValueError:
        output.insert(tk.END, "Please enter valid numbers.\n")
        return

    found = False
    for key, product in loan_products.items():
        if not (product["month_range"][0] <= months <= product["month_range"][1]):
            continue

        principal, amort_table = reverse_amortize(repayment, product["interest_rate"], months, product)
        if principal is None or not (product["amount_range"][0] <= principal <= product["amount_range"][1]):
            continue

        found = True
        output.insert(tk.END, f"\n[Product: {product['name']}]\n")
        output.insert(tk.END, f"Estimated Principal: KES {principal}\n")
        output.insert(tk.END, f"Interest Rate: {product['interest_rate']}% annual ({product['type']})\n")
        output.insert(tk.END, f"Loan Duration: {months} months\n")
        output.insert(tk.END, f"Monthly Repayment: KES {repayment} (approx)\n")

        output.insert(tk.END, "\nAmortization Table:\n")
        output.insert(tk.END, f"{'Month':<6}{'Interest':<10}{'Principal':<10}{'Processing':<12}{'Insurance':<10}{'Payment':<10}{'Balance':<10}\n")
        for row in amort_table:
            output.insert(tk.END, f"{row['Month']:<6}{row['Interest']:<10}{row['Principal']:<10}{row['Processing']:<12}{row['Insurance']:<10}{row['Payment']:<10}{row['Balance']:<10}\n")

    if not found:
        output.insert(tk.END, "\nCould not find a matching principal. Try adjusting repayment or duration.\n")

btn = tk.Button(root, text="Calculate", command=calculate)
btn.grid(row=2, columnspan=2, pady=10)

root.mainloop()
