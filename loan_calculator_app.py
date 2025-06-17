import math
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- Calculation functions ---

def calc_flat_payment(principal, annual_rate, months):
    r = annual_rate / 100
    t = months / 12
    total_interest = principal * r * t
    total_amount = principal + total_interest
    return math.ceil(total_amount / months)

def calc_flat_principal(monthly_payment, annual_rate, months):
    r = annual_rate / 100
    t = months / 12
    return math.floor(monthly_payment * months / (1 + r * t))

def calc_reducing_payment(principal, annual_rate, months):
    r = (annual_rate / 100) / 12
    if r == 0:
        return principal / months
    payment = principal * r * ((1 + r) ** months) / (((1 + r) ** months) - 1)
    return math.ceil(payment)

def calc_reducing_principal(monthly_payment, annual_rate, months):
    r = (annual_rate / 100) / 12
    if r == 0:
        return monthly_payment * months
    principal = monthly_payment * (((1 + r) ** months - 1) / (r * (1 + r) ** months))
    return math.floor(principal)

def calc_total_interest(principal, annual_rate, months, method):
    r = annual_rate / 100
    t = months / 12
    if method == "flat":
        return math.ceil(principal * r * t)
    elif method == "reducing":
        monthly_r = r / 12
        monthly_interest = lambda bal: bal * monthly_r
        balance = principal
        total_interest = 0
        monthly_principal = principal / months
        for _ in range(months):
            total_interest += math.ceil(monthly_interest(balance))
            balance -= monthly_principal
        return math.ceil(total_interest)
    return 0

def calc_insurance(principal, months, insurance_rate):
    return math.ceil(principal * (insurance_rate / 100) * (months / 12))

def calc_processing(principal, processing_rate, processing_min):
    return math.ceil(max(principal * (processing_rate / 100), processing_min))

# --- Loan Products ---
loan_products = {
    "1": {"name": "Fanaka Loan", "interest_rate": 24, "type": "flat", "insurance_rate": 3, "processing_rate": 19, "processing_min": 600, "amount_range": (100000, 5000000), "month_range": (1,144)},
    "2": {"name": "Payslip Loan", "interest_rate": 120, "type": "reducing", "insurance_rate": 3, "processing_rate": 3, "processing_min": 600, "amount_range": (500, 500000), "month_range": (1, 144)},
    "3": {"name": "Msingi Loan 1", "interest_rate": 36, "type": "flat", "insurance_rate": 3, "processing_rate": 3, "processing_min": 600, "amount_range": (500, 300000), "month_range": (1, 6)},
    "4": {"name": "Msingi Loan 2", "interest_rate": 42, "type": "flat", "insurance_rate": 3, "processing_rate": 3, "processing_min": 600, "amount_range": (500, 300000), "month_range": (6, 12)},
    "5": {"name": "Bosika Mini", "interest_rate": 48, "type": "flat", "insurance_rate": 3, "processing_rate": 3, "processing_min": 600, "amount_range": (50000, 99999), "month_range": (1, 6)}
}

# --- GUI ---
root = tk.Tk()
root.title("Loan Calculator")

frame = ttk.Frame(root)
frame.pack(fill="both", expand=True)

main_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL)
main_pane.pack(fill=tk.BOTH, expand=True)
main_pane.add(frame)

chart_frame = ttk.Frame(root)
main_pane.add(chart_frame)

frame.grid_columnconfigure(0, weight=1)
frame.grid_columnconfigure(1, weight=1)

chart_canvas = None

# Input fields
mode_var = tk.StringVar(value="monthly")
tk.Label(frame, text="Mode:").grid(row=0, column=0, sticky="e")
tk.OptionMenu(frame, mode_var, "monthly", "amount").grid(row=0, column=1, sticky="w")

repayment_label = tk.Label(frame, text="Target monthly repayment (KES):")
repayment_label.grid(row=1, column=0, sticky="e")
repayment_entry = tk.Entry(frame)
repayment_entry.grid(row=1, column=1)

amount_label = tk.Label(frame, text="Desired loan amount (KES):")
amount_label.grid(row=2, column=0, sticky="e")
amount_entry = tk.Entry(frame)
amount_entry.grid(row=2, column=1)

months_label = tk.Label(frame, text="Loan period (months):")
months_label.grid(row=3, column=0, sticky="e")
months_entry = tk.Entry(frame)
months_entry.grid(row=3, column=1)

# Output area
output = ScrolledText(frame, height=30, width=100, wrap=tk.WORD)
output.grid(row=5, column=0, columnspan=2, pady=5, sticky="nsew")

def update_input_mode(*args):
    if mode_var.get() == "monthly":
        repayment_entry.config(state="normal")
        amount_entry.config(state="disabled")
    else:
        repayment_entry.config(state="disabled")
        amount_entry.config(state="normal")

mode_var.trace_add("write", update_input_mode)
update_input_mode()

def calculate():
    global chart_canvas
    output.delete(1.0, tk.END)
    for widget in chart_frame.winfo_children():
        widget.destroy()

    try:
        months = int(months_entry.get())
        if mode_var.get() == "monthly":
            repayment = float(repayment_entry.get())
        else:
            desired_amount = float(amount_entry.get())
    except ValueError:
        output.insert(tk.END, "Please enter valid numbers.\n")
        return

    results = []
    for product in loan_products.values():
        if months < product["month_range"][0] or months > product["month_range"][1]:
            continue

        if mode_var.get() == "monthly":
            if product["type"] == "reducing":
                principal = calc_reducing_principal(repayment, product["interest_rate"], months)
            else:
                principal = calc_flat_principal(repayment, product["interest_rate"], months)
        else:
            principal = desired_amount
            if principal < product["amount_range"][0] or principal > product["amount_range"][1]:
                continue
            if product["type"] == "reducing":
                repayment = calc_reducing_payment(principal, product["interest_rate"], months)
            else:
                repayment = calc_flat_payment(principal, product["interest_rate"], months)

        if principal < product["amount_range"][0] or principal > product["amount_range"][1]:
            continue

        processing = calc_processing(principal, product["processing_rate"], product["processing_min"])
        insurance = calc_insurance(principal, months, product["insurance_rate"])
        monthly_proc = math.ceil(processing / months)
        monthly_ins = math.ceil(insurance / months)
        rounded_proc = monthly_proc * months
        rounded_ins = monthly_ins * months
        charge_padding = (rounded_proc + rounded_ins) - (processing + insurance)
        adjusted_principal = principal - charge_padding
        interest = calc_total_interest(adjusted_principal, product["interest_rate"], months, product["type"])
        total = adjusted_principal + rounded_proc + rounded_ins + interest

        results.append({
            "name": product["name"],
            "type": product["type"],
            "rate": product["interest_rate"],
            "principal": principal,
            "interest": interest,
            "insurance": insurance,
            "processing": processing,
            "repayment": repayment,
            "total": total
        })

    if results:
        results.sort(key=lambda x: x['total'])
        names = []
        totals = []
        for r in results:
            output.insert(tk.END, f"\n[{r['name']}] ({r['type'].capitalize()} Rate)\n")
            output.insert(tk.END, f"Interest Rate       : {r['rate']}%\n")
            output.insert(tk.END, f"Estimated Principal : KES {r['principal']}\n")
            output.insert(tk.END, f"Interest            : KES {r['interest']}\n")
            output.insert(tk.END, f"Insurance           : KES {r['insurance']}\n")
            output.insert(tk.END, f"Processing Fee      : KES {r['processing']}\n")
            output.insert(tk.END, f"Monthly Repayment   : KES {r['repayment']}\n")
            output.insert(tk.END, f"Total Loan Cost     : KES {r['total']}\n")
            names.append(r['name'])
            totals.append(r['total'])

        best = results[0]
        output.insert(tk.END, f"\n✅ Recommended Product:\n> {best['name']} ({best['type'].capitalize()} Rate) with total cost of KES {best['total']}\n")

        fig, ax = plt.subplots(figsize=(5,4))
        ax.bar(names, totals, color='skyblue')
        ax.set_title('Total Cost by Loan Product')
        ax.set_ylabel('Total Cost (KES)')
        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right')
        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    else:
        output.insert(tk.END, "\n⚠️ No products matched your loan period or inputs. Try adjusting values.\n")

btn = tk.Button(frame, text="Calculate", command=calculate)
btn.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
