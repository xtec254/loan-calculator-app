import math
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def estimate_principal_from_repayment_flat(repayment, annual_rate, months, insurance_rate, processing_rate):
    low = 100
    high = 1_000_000
    for _ in range(100):
        mid = (low + high) / 2
        interest_total = mid * (annual_rate / 100)
        insurance_total = mid * (insurance_rate / 100) * (months / 12)
        processing_total = mid * (processing_rate / 100)
        monthly_total = (mid + interest_total + insurance_total + processing_total) / months
        if monthly_total > repayment:
            high = mid
        else:
            low = mid
    return round((low + high) / 2)


def estimate_principal_from_repayment_reducing(repayment, annual_rate, months, insurance_rate, processing_rate):
    low = 100
    high = 1_000_000
    for _ in range(100):
        mid = (low + high) / 2
        principal_payment = mid / months
        monthly_processing = (mid * (processing_rate / 100)) / months
        annual_insurance = mid * (insurance_rate / 100)
        monthly_insurance = (annual_insurance * (months / 12)) / months
        balance = mid
        total = 0
        for _ in range(months):
            interest = (balance * (annual_rate / 100)) / 12
            total_monthly = principal_payment + interest + monthly_processing + monthly_insurance
            total += total_monthly
            balance -= principal_payment
        avg_monthly = total / months
        if avg_monthly > repayment:
            high = mid
        else:
            low = mid
    return round((low + high) / 2)


def generate_amortization_table(principal, annual_rate, months, insurance_rate, processing_rate, loan_type):
    table = []
    if loan_type == "flat":
        interest_total = principal * (annual_rate / 100)
        insurance_total = principal * (insurance_rate / 100) * (months / 12)
        processing_fee_total = principal * (processing_rate / 100)
        total_repayment = principal + interest_total + insurance_total + processing_fee_total
        monthly_payment = round(total_repayment / months)
        monthly_insurance = math.ceil(insurance_total / months)
        monthly_processing = math.ceil(processing_fee_total / months)
        principal_payment = round(principal / months)
        balance = principal
        for i in range(1, months + 1):
            interest = round(interest_total / months)
            row = {
                "Month": i,
                "Interest": interest,
                "Principal": principal_payment,
                "Processing": monthly_processing,
                "Insurance": monthly_insurance,
                "Payment": monthly_payment,
                "Balance": max(0, round(balance - principal_payment))
            }
            table.append(row)
            balance -= principal_payment
    else:
        principal_payment = round(principal / months)
        processing_fee_total = principal * (processing_rate / 100)
        monthly_processing = math.ceil(processing_fee_total / months)
        insurance_total = principal * (insurance_rate / 100) * (months / 12)
        monthly_insurance = math.ceil(insurance_total / months)
        rounded_proc_total = monthly_processing * months
        rounded_ins_total = monthly_insurance * months
        padding = (rounded_proc_total + rounded_ins_total) - (processing_fee_total + insurance_total)
        adjusted_principal = principal - padding
        balance = adjusted_principal
        for i in range(1, months + 1):
            interest = round(balance * (annual_rate / 100 / 12))
            row = {
                "Month": i,
                "Interest": interest,
                "Principal": principal_payment,
                "Processing": monthly_processing,
                "Insurance": monthly_insurance,
                "Payment": principal_payment + interest + monthly_processing + monthly_insurance,
                "Balance": max(0, round(balance - principal_payment))
            }
            table.append(row)
            balance -= principal_payment
    return table


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


root = tk.Tk()
root.title("Loan Calculator")

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

repayment_label = ttk.Label(frame, text="Target monthly repayment (KES):")
repayment_label.grid(row=0, column=0, sticky="w")
repayment_entry = ttk.Entry(frame)
repayment_entry.grid(row=0, column=1, sticky="ew")

months_label = ttk.Label(frame, text="Loan period (months):")
months_label.grid(row=1, column=0, sticky="w")
months_entry = ttk.Entry(frame)
months_entry.grid(row=1, column=1, sticky="ew")

output_label = ttk.Label(frame, text="Available Loan Products:")
output_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10,0))

output = tk.Text(frame, height=30, width=100)
output.grid(row=3, column=0, columnspan=2, pady=5)

frame.columnconfigure(1, weight=1)

chart_frame = ttk.Frame(root)
chart_frame.pack(fill="both", expand=True)

chart_canvas = None


def calculate():
    global chart_canvas
    output.delete(1.0, tk.END)
    for widget in chart_frame.winfo_children():
        widget.destroy()

    try:
        repayment = float(repayment_entry.get())
        months = int(months_entry.get())
    except ValueError:
        output.insert(tk.END, "⚠️ Enter valid numbers.\n")
        return

    results = []
    for product in loan_products.values():
        if not (product["month_range"][0] <= months <= product["month_range"][1]):
            continue

        if product["type"] == "reducing":
            principal = estimate_principal_from_repayment_reducing(
                repayment, product["interest_rate"], months,
                product["insurance_rate"], product["processing_rate"]
            )
        else:
            principal = estimate_principal_from_repayment_flat(
                repayment, product["interest_rate"], months,
                product["insurance_rate"], product["processing_rate"]
            )

        if not (product["amount_range"][0] <= principal <= product["amount_range"][1]):
            continue

        table = generate_amortization_table(
            principal, product["interest_rate"], months,
            product["insurance_rate"], product["processing_rate"], product["type"]
        )

        total_cost = sum(row["Payment"] for row in table)
        results.append({
            "name": product["name"],
            "principal": principal,
            "total": total_cost,
            "table": table,
            "rate": product["interest_rate"]
        })

    if results:
        for idx, res in enumerate(results, start=1):
            output.insert(tk.END, f"\n💡 Option {idx}: {res['name']}\n")
            output.insert(tk.END, f"Principal: KES {res['principal']}, Total Repayment: KES {res['total']}, Rate: {res['rate']}%\n")
            output.insert(tk.END, f"{'Month':<6} {'Interest':<10} {'Principal':<10} {'Processing':<10} {'Insurance':<10} {'Payment':<10} {'Balance':<10}\n")
            for row in res["table"]:
                output.insert(tk.END, f"{row['Month']:<6} {row['Interest']:<10} {row['Principal']:<10} {row['Processing']:<10} {row['Insurance']:<10} {row['Payment']:<10} {row['Balance']:<10}\n")

            months_list = [row["Month"] for row in res["table"]]
            payments = [row["Payment"] for row in res["table"]]
            fig, ax = plt.subplots(figsize=(6, 3))
            ax.plot(months_list, payments, marker='o')
            ax.set_title(f"{res['name']} - Monthly Repayments")
            ax.set_xlabel("Month")
            ax.set_ylabel("KES")
            ax.grid(True)
            chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            chart_canvas.draw()
            chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    else:
        output.insert(tk.END, "⚠️ No matching product found.\n")


ttk.Button(frame, text="Calculate", command=calculate).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()