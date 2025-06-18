import math
import tkinter as tk

# --- Constants ---
INSURANCE_RATE = 3  # Annual
PROCESSING_RATE = 3  # One-time
PROCESSING_MIN = 600
TOLERANCE = 1  # Acceptable error in KES for reverse calculation

# --- Loan Products ---
loan_products = {
    "1": {
        "name": "Reducing Balance Loan",
        "interest_rate": 120,
        "type": "reducing",
        "amount_range": (500, 5000000),
        "month_range": (1, 144)
    },
}

# --- Calculation Functions ---

def generate_amortization(principal, annual_rate, months):
    r = (annual_rate / 100) / 12
    monthly_principal = principal / months
    balance = principal

    # Insurance: 3% annually, recurring for each year in the loan term
    years = math.ceil(months / 12)
    total_insurance = math.ceil(principal * (INSURANCE_RATE / 100) * years)
    monthly_insurance = math.ceil(total_insurance / months)

    total_processing = max(principal * (PROCESSING_RATE / 100), PROCESSING_MIN)
    monthly_processing = math.ceil(total_processing / months)

    amortization = []
    total_payment = 0

    for month in range(1, months + 1):
        interest = round(balance * r)
        payment = math.ceil(monthly_principal + interest + monthly_insurance + monthly_processing)
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

    return amortization, total_payment


def reverse_amortize(target_repayment, annual_rate, months):
    low = 100  # Start from a low guess
    high = 10000000  # Upper guess

    while low <= high:
        mid = (low + high) // 2
        amort, _ = generate_amortization(mid, annual_rate, months)
        avg_monthly = sum([x['Payment'] for x in amort]) / months

        if abs(avg_monthly - target_repayment) <= TOLERANCE:
            return mid, amort
        elif avg_monthly > target_repayment:
            high = mid - 1
        else:
            low = mid + 1

    return None, None

# --- GUI ---
root = tk.Tk()
root.title("Custom Reducing Loan Calculator")

tk.Label(root, text="Monthly Repayment (KES):").grid(row=0, column=0)
repayment_entry = tk.Entry(root)
repayment_entry.grid(row=0, column=1)

tk.Label(root, text="Loan Period (months):").grid(row=1, column=0)
months_entry = tk.Entry(root)
months_entry.grid(row=1, column=1)

output = tk.Text(root, width=100, height=25)
output.grid(row=3, column=0, columnspan=2)

def calculate():
    output.delete("1.0", tk.END)
    try:
        repayment = float(repayment_entry.get())
        months = int(months_entry.get())
    except ValueError:
        output.insert(tk.END, "Please enter valid numbers.\n")
        return

    product = loan_products["1"]
    if not (product["month_range"][0] <= months <= product["month_range"][1]):
        output.insert(tk.END, f"Loan period must be between {product['month_range'][0]} and {product['month_range'][1]} months.\n")
        return

    principal, amort_table = reverse_amortize(repayment, product["interest_rate"], months)
    if principal is None:
        output.insert(tk.END, "Could not find a matching principal. Try adjusting repayment or duration.\n")
        return

    output.insert(tk.END, f"\n[Product: {product['name']}]\n")
    output.insert(tk.END, f"Estimated Principal: KES {principal}\n")
    output.insert(tk.END, f"Interest Rate: {product['interest_rate']}% annual (reducing)\n")
    output.insert(tk.END, f"Loan Duration: {months} months\n")
    output.insert(tk.END, f"Monthly Repayment: KES {repayment} (approx)\n")

    output.insert(tk.END, "\nAmortization Table:\n")
    output.insert(tk.END, f"{'Month':<6}{'Interest':<10}{'Principal':<10}{'Processing':<12}{'Insurance':<10}{'Payment':<10}{'Balance':<10}\n")
    for row in amort_table:
        output.insert(tk.END, f"{row['Month']:<6}{row['Interest']:<10}{row['Principal']:<10}{row['Processing']:<12}{row['Insurance']:<10}{row['Payment']:<10}{row['Balance']:<10}\n")


btn = tk.Button(root, text="Calculate", command=calculate)
btn.grid(row=2, columnspan=2, pady=10)

root.mainloop()
