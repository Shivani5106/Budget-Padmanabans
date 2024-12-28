import tkinter as tk
import requests

def calculate_savings():
    try:
        # Get user inputs
        income = float(income_entry.get())
        expense = float(expense_entry.get())

        # Send data to backend
        response = requests.post('http://127.0.0.1:5000/calculate', json={
            'income': income,
            'expense': expense
        })

        # Handle response
        if response.status_code == 200:
            result = response.json()
            result_label.config(text=f"Savings: ${result['savings']:.2f}")
        else:
            result_label.config(text="Error in calculation!")
    except ValueError:
        result_label.config(text="Please enter valid numbers!")

# Set up GUI
root = tk.Tk()
root.title("Budget Padmanabans")

tk.Label(root, text="Monthly Income:").pack(pady=5)
income_entry = tk.Entry(root)
income_entry.pack(pady=5)

tk.Label(root, text="Total Expenses:").pack(pady=5)
expense_entry = tk.Entry(root)
expense_entry.pack(pady=5)

calculate_button = tk.Button(root, text="Calculate Savings", command=calculate_savings)
calculate_button.pack(pady=10)

result_label = tk.Label(root, text="Savings: ")
result_label.pack(pady=5)

root.mainloop()
