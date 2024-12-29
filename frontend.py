import tkinter as tk
from tkinter import PhotoImage, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime 
import csv
import openai

# Set up OpenAI API (or any other AI service you choose)
openai.api_key = 'your-openai-api-key-here'  # Replace with your OpenAI API key

# Predefined user goals and expense categories
user_goals = [{"goal": "Buy a house", "amount": 500000, "due_date": "2030-12-31"}]

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budget (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_income REAL NOT NULL,
            expenses REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Save data to database
def save_budget_data(total_income, expenses):
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO budget (total_income, expenses) VALUES (?, ?)", (total_income, expenses))
    conn.commit()
    conn.close()

# Retrieve the latest budget data
def get_latest_budget_data():
    conn = sqlite3.connect("budget_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT total_income, expenses FROM budget ORDER BY timestamp DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0)

# Function to calculate savings
def calculate_savings():
    try:
        total_income = float(total_income_entry.get())
        monthly_expense = sum(expense_categories.values())

        # Save to database
        save_budget_data(total_income, monthly_expense)

        savings = total_income - monthly_expense
        result_label.config(text=f"Savings: ₹{savings:.2f}", fg="green")
    except ValueError:
        result_label.config(text="Please enter valid numbers!", fg="red")

def open_charts():
    charts_window = tk.Toplevel(root)
    charts_window.title("Income vs Expenses Chart")
    charts_window.geometry("600x500")
    charts_window.attributes('-alpha', 0)  # Set initial transparency to 0 (fully transparent)

    # Set light pink background color
    charts_window.configure(bg="#f8c8d6")

    # Animation: Fade-in effect
    def fade_in(window, current_alpha=0):
        if current_alpha < 1:
            current_alpha += 0.05
            window.attributes('-alpha', current_alpha)
            charts_window.after(50, lambda: fade_in(window, current_alpha))

    fade_in(charts_window)

    total_income, expenses = get_latest_budget_data()

    if total_income == 0 and expenses == 0:
        messagebox.showwarning("No Data", "No data available. Please add income and expenses first!")
        return

    savings = total_income - expenses

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Expenses", "Savings"], [expenses, savings], color=["red", "green"])
    ax.set_title("Monthly Income Breakdown")
    ax.set_ylabel("Amount (₹)")
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=charts_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

    def show_pie_chart():
        pie_fig, pie_ax = plt.subplots(figsize=(6, 4))
        labels = ['Expenses', 'Savings']
        sizes = [expenses, savings]
        colors = ['red', 'green']
        
        # Create a 3D-like pie chart using shadow effect
        pie_ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, shadow=True, explode=(0.1, 0))
        pie_ax.set_title("Monthly Income Breakdown")
        pie_ax.axis('equal')

        pie_canvas = FigureCanvasTkAgg(pie_fig, master=charts_window)
        pie_canvas.draw()
        pie_canvas.get_tk_widget().pack(pady=20)

    pie_chart_button = tk.Button(charts_window, text="Show Pie Chart", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=show_pie_chart)
    pie_chart_button.pack(pady=10)


# Function to add expense categories
def add_expense_category():
    category_name = category_entry.get()
    try:
        category_amount = float(category_amount_entry.get())
        expense_categories[category_name] = category_amount
        category_entry.delete(0, tk.END)
        category_amount_entry.delete(0, tk.END)
        update_expenses_display()
        messagebox.showinfo("Success", f"Expense category '{category_name}' added.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount.")

def update_expenses_display():
    expenses_text = "\n".join([f"{cat}: ₹{amt}" for cat, amt in expense_categories.items()])
    expense_display_label.config(text=expenses_text)

# Function to export data to CSV
def export_data():
    try:
        total_income = total_income_entry.get()
        if not total_income:
            messagebox.showerror("Error", "Please enter your total income.")
            return

        data = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Total Income": total_income,
            "Expenses": expense_categories,
        }

        with open('budget_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([data["Date"], data["Total Income"], data["Expenses"]])

        messagebox.showinfo("Success", "Data exported successfully to 'budget_data.csv'.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while exporting data: {e}")

# Predefined expense categories
expense_categories = {"Groceries": 0, "Rent": 0, "Utilities": 0, "Transportation": 0, "Others": 0}
def open_goals():
    goals_window = tk.Toplevel(root)
    goals_window.title("Your Goals")
    goals_window.geometry("400x500")

    goals_label = tk.Label(goals_window, text="Your Goals:", font=("Times New Roman", 14, "bold"), anchor="w")
    goals_label.pack(pady=10, anchor="w")

    goals_listbox = tk.Listbox(goals_window, font=("Times New Roman", 12), height=10, width=40, selectmode=tk.SINGLE)
    goals_listbox.pack(pady=10)

    for goal in user_goals:
        goals_listbox.insert(tk.END, f"{goal['goal']} - ₹{goal['amount']} by {goal['due_date']}")

    new_goal_name_entry = tk.Entry(goals_window, font=("Times New Roman", 12), width=40)
    new_goal_name_entry.pack(pady=10)
    new_goal_amount_entry = tk.Entry(goals_window, font=("Times New Roman", 12), width=40)
    new_goal_amount_entry.pack(pady=10)
    new_goal_due_date_entry = tk.Entry(goals_window, font=("Times New Roman", 12), width=40)
    new_goal_due_date_entry.pack(pady=10)

    def add_goal():
        goal_name = new_goal_name_entry.get()
        goal_amount = new_goal_amount_entry.get()
        goal_due_date = new_goal_due_date_entry.get()

        if goal_name and goal_amount and goal_due_date:
            try:
                goal_amount = float(goal_amount)
                user_goals.append({"goal": goal_name, "amount": goal_amount, "due_date": goal_due_date})
                goals_listbox.insert(tk.END, f"{goal_name} - ₹{goal_amount} by {goal_due_date}")
                messagebox.showinfo("Success", "Goal added successfully!")
                new_goal_name_entry.delete(0, tk.END)
                new_goal_amount_entry.delete(0, tk.END)
                new_goal_due_date_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid goal amount.")
        else:
            messagebox.showwarning("Warning", "Please fill in all goal details.")

    add_button = tk.Button(goals_window, text="Add Goal", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=add_goal)
    add_button.pack(pady=5)
    def update_goal():
        try:
            selected_goal_index = goals_listbox.curselection()[0]
            updated_goal_name = new_goal_name_entry.get()
            updated_goal_amount = float(new_goal_amount_entry.get())
            updated_goal_due_date = new_goal_due_date_entry.get()

            if updated_goal_name and updated_goal_due_date:
                user_goals[selected_goal_index] = {
                    "goal": updated_goal_name,
                    "amount": updated_goal_amount,
                    "due_date": updated_goal_due_date
                }
                goals_listbox.delete(selected_goal_index)
                goals_listbox.insert(selected_goal_index, f"{updated_goal_name} - ₹{updated_goal_amount} by {updated_goal_due_date}")
                messagebox.showinfo("Success", "Goal updated successfully!")
                new_goal_name_entry.delete(0, tk.END)
                new_goal_amount_entry.delete(0, tk.END)
                new_goal_due_date_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Warning", "Please fill in all goal details to update.")
        except (ValueError, IndexError):
            messagebox.showerror("Error", "Please select a valid goal to update.")

    def delete_goal():
        try:
            selected_goal_index = goals_listbox.curselection()[0]
            del user_goals[selected_goal_index]
            goals_listbox.delete(selected_goal_index)
            messagebox.showinfo("Success", "Goal deleted successfully!")
        except IndexError:
            messagebox.showerror("Error", "Please select a valid goal to delete.")

    add_button = tk.Button(goals_window, text="Add Goal", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=add_goal)
    add_button.pack(pady=5)

    update_button = tk.Button(goals_window, text="Update Goal", font=("Times New Roman", 12, "bold"), bg="#ffa500", fg="white", command=update_goal)
    update_button.pack(pady=5)

    delete_button = tk.Button(goals_window, text="Delete Goal", font=("Times New Roman", 12, "bold"), bg="#ff0000", fg="white", command=delete_goal)
    delete_button.pack(pady=5)


def analyze_and_suggest():
    total_income, expenses = get_latest_budget_data()

    if total_income == 0:
        suggestion_label.config(text="Please enter your income and add expenses.")
        return

    savings = total_income - expenses
    expense_percentage = (expenses / total_income) * 100 if total_income > 0 else 0
    if expense_percentage > 70:
        message = f"Your expenses are {expense_percentage:.2f}% of your income. Consider reducing unnecessary costs."
    elif 50 <= expense_percentage <= 70:
        message = f"You're spending a moderate amount ({expense_percentage:.2f}%) of your income. Keep an eye on your savings!"
    else:
        message = f"Great! Your expenses are only {expense_percentage:.2f}% of your income. Focus on building savings or investing."

    # Update UI (without AI suggestion)
    suggestion_label.config(text=message)



expense_categories = {"Groceries": 0, "Rent": 0, "Utilities": 0, "Transportation": 0, "Others": 0}

# Function to open the chatbot
predefined_questions = { "what is a budget?": "A budget is a financial plan that outlines your income and expenses for a specific period.",
    "why should i create a budget?": "Creating a budget helps you control your spending, save money, and achieve financial goals.",
    "what is the 50/30/20 rule?": "The 50/30/20 rule is a budgeting method that allocates 50% of income to needs, 30% to wants, and 20% to savings or debt repayment.",
    "how do i track my expenses?": "You can track expenses using apps, spreadsheets, or by writing them down manually.",
    "what are fixed expenses?": "Fixed expenses are regular costs like rent, utilities, and loan payments that don't change each month.",
    "what are variable expenses?": "Variable expenses are costs that fluctuate, such as groceries, entertainment, or dining out.",
    "how much should i save each month?": "A common recommendation is to save at least 20% of your income, but this depends on your financial goals.",
    "what is an emergency fund?": "An emergency fund is savings set aside for unexpected expenses, such as medical bills or car repairs.",
    "how much should i have in my emergency fund?": "A good goal is to save 3-6 months’ worth of living expenses.",
    "what is a financial goal?": "A financial goal is a target you set for managing your money, such as saving for a house or paying off debt.",
    "what is net worth?": "Net worth is the difference between your total assets and liabilities.",
    "how do i calculate my net worth?": "Add up your assets, subtract your liabilities, and the result is your net worth.",
    "what is a good credit score?": "A credit score above 700 is generally considered good.",
    "how can i improve my credit score?": "Pay bills on time, reduce credit card balances, and avoid opening unnecessary new credit accounts.",
    "what is compound interest?": "Compound interest is the interest on both the initial principal and the accumulated interest from previous periods.",
    "how does inflation affect my savings?": "Inflation decreases the purchasing power of your money over time.",
    "what is a retirement plan?": "A retirement plan is a financial strategy to save and invest money for your retirement years.",
    "what is a mutual fund?": "A mutual fund is an investment vehicle that pools money from multiple investors to invest in stocks, bonds, or other assets.",
    "what is a stock?": "A stock represents ownership in a company and a claim on part of its profits.",
    "what is a bond?": "A bond is a fixed-income investment where you lend money to an entity (like a government or corporation) in exchange for periodic interest payments.",
    "what is the difference between saving and investing?": "Saving is setting aside money for future use with low risk, while investing involves higher risk for potentially greater returns.",
    "what is a loan?": "A loan is borrowed money that you must repay with interest over time.",
    "what is a mortgage?": "A mortgage is a loan specifically for buying real estate, with the property serving as collateral.",
    "what is debt?": "Debt is money owed to another person or institution.",
    "how can i pay off debt faster?": "Use strategies like the snowball or avalanche methods to focus payments on specific debts.",
    "what is a good debt-to-income ratio?": "A ratio below 36% is considered good by most lenders.",
    "what are financial assets?": "Financial assets include cash, stocks, bonds, and other investments.",
}

def open_chatbot():
    chatbot_window = tk.Toplevel(root)
    chatbot_window.title("Chatbot")
    chatbot_window.geometry("400x500")

    chat_box = tk.Text(chatbot_window, font=("Times New Roman", 12), width=50, height=20, state=tk.DISABLED, wrap=tk.WORD)
    chat_box.pack(pady=10)

    user_input_entry = tk.Entry(chatbot_window, font=("Times New Roman", 12), width=40)
    user_input_entry.pack(pady=10)

    def get_chatbot_response():
        user_message = user_input_entry.get().lower()
        
        # Check if the user message is in predefined questions
        if user_message in predefined_questions:
            bot_message = predefined_questions[user_message]
        else:
            # Query OpenAI if the question is not predefined
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=150,
                )
                bot_message = response['choices'][0]['message']['content'].strip()

            except openai.error.OpenAIError as e:
                bot_message = f"Error: {str(e)}"

        chat_box.config(state=tk.NORMAL)
        chat_box.insert(tk.END, f"You: {user_message}\n")
        chat_box.insert(tk.END, f"Bot: {bot_message}\n")
        chat_box.config(state=tk.DISABLED)
        chat_box.yview(tk.END)

        user_input_entry.delete(0, tk.END)

    send_button = tk.Button(chatbot_window, text="Send", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=get_chatbot_response)
    send_button.pack(pady=10)

    def show_predefined_questions():
        questions_window = tk.Toplevel(chatbot_window)
        questions_window.title("Predefined Questions")
        questions_window.geometry("400x300")

        questions_listbox = tk.Listbox(questions_window, font=("Times New Roman", 12), width=50, height=20)
        questions_listbox.pack(pady=10)

        for question in predefined_questions.keys():
            questions_listbox.insert(tk.END, question)

    predefined_button = tk.Button(chatbot_window, text="Show Predefined Questions", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=show_predefined_questions)
    predefined_button.pack(pady=10)
# Tkinter App Initialization
root = tk.Tk()
root.title("Budget Padmanabans")
root.geometry("800x600+100+100")

try:
    background_image = PhotoImage(file="image.png")
    background_label = tk.Label(root, image=background_image)
    background_label.image = background_image
    background_label.place(relwidth=1, relheight=1)
except Exception as e:
    print(f"Error loading image: {e}. Using default background color.")
    root.configure(bg="#f0f0f0")

# Title Label
title_label = tk.Label(root, text="Budget Padmanabans", font=("Times New Roman", 24, "bold"), bg="#1e3a5f", fg="#fff", anchor="w")
title_label.pack(fill="x", padx=10, pady=20)

# Input fields for income and expenses
total_income_label = tk.Label(root, text="Total Income:", font=("Times New Roman", 12))
total_income_label.pack(pady=5)
total_income_entry = tk.Entry(root, font=("Times New Roman", 12))
total_income_entry.pack(pady=5)

# Expense Categories
category_label = tk.Label(root, text="Add Expense Category:", font=("Times New Roman", 12))
category_label.pack(pady=5)
category_entry = tk.Entry(root, font=("Times New Roman", 12))
category_entry.pack(pady=5)

category_amount_label = tk.Label(root, text="Amount:", font=("Times New Roman", 12))
category_amount_label.pack(pady=5)
category_amount_entry = tk.Entry(root, font=("Times New Roman", 12))
category_amount_entry.pack(pady=5)

add_category_button = tk.Button(root, text="Add Expense Category", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=add_expense_category)
add_category_button.pack(pady=5)

expense_display_label = tk.Label(root, text="", font=("Times New Roman", 12), fg="blue")
expense_display_label.pack(pady=5)

# Calculate Button
calculate_button = tk.Button(root, text="Calculate Savings", font=("Times New Roman", 12, "bold"), bg="#4caf50", fg="white", command=calculate_savings)
calculate_button.pack(pady=5)

# Result Label
result_label = tk.Label(root, text="Savings: ₹", font=("Times New Roman", 14, "bold"))
result_label.pack(pady=5)
# Suggestions label
suggestion_label = tk.Label(root, text="", font=("Times New Roman", 14, "italic"), fg="blue")
suggestion_label.pack(pady=10)

# Export Data Button
export_button = tk.Button(root, text="Export Data", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=export_data)
export_button.pack(pady=10)

# Charts Button

# Top-right aligned Buttons
top_right_frame = tk.Frame(root, bg="#1e3a5f")
top_right_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=20)

charts_button = tk.Button(top_right_frame, text="Charts", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=open_charts)
charts_button.pack(side="left", padx=5)

goals_button = tk.Button(top_right_frame, text="Goals", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=open_goals)
goals_button.pack(side="left", padx=5)

chatbot_button = tk.Button(top_right_frame, text="Chatbot", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=open_chatbot)
chatbot_button.pack(side="left", padx=5)

# Notifications Button - Top-left
top_left_frame = tk.Frame(root, bg="#1e3a5f")
top_left_frame.place(relx=0.0, rely=0.0, anchor="nw", x=10, y=80)

notifications_button = tk.Button(top_left_frame, text="Notifications", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=lambda: messagebox.showinfo("Notifications", "No new notifications"))
notifications_button.pack(side="left", padx=5)

# Calculator Functionality
def open_calculator():
    calculator_window = tk.Toplevel(root)
    calculator_window.title("Calculator")
    calculator_window.geometry("300x400")

    # Calculator input display
    calc_display = tk.Entry(calculator_window, font=("Times New Roman", 18), bd=10, justify="right")
    calc_display.grid(row=0, column=0, columnspan=4)

    # Add button functionality
    def append_to_expression(char):
        calc_display.insert(tk.END, char)

    def calculate_result():
        try:
            expression = calc_display.get()
            result = eval(expression)
            calc_display.delete(0, tk.END)
            calc_display.insert(tk.END, str(result))
        except Exception:
            calc_display.delete(0, tk.END)
            calc_display.insert(tk.END, "Error")

    def clear_display():
        calc_display.delete(0, tk.END)

    # Calculator buttons
    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        'C', '0', '=', '+'
    ]

    row = 1
    col = 0
    for button in buttons:
        if button == "=":
            tk.Button(calculator_window, text=button, font=("Times New Roman", 18, "bold"), bg="#4caf50", fg="white",
                      command=calculate_result).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        elif button == "C":
            tk.Button(calculator_window, text=button, font=("Times New Roman", 18, "bold"), bg="red", fg="white",
                      command=clear_display).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        else:
            tk.Button(calculator_window, text=button, font=("Times New Roman", 18), command=lambda char=button: append_to_expression(char)).grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        col += 1
        if col > 3:
            col = 0
            row += 1

# Calculator Button - Bottom-left
bottom_left_frame = tk.Frame(root, bg="#1e3a5f")
bottom_left_frame.place(relx=0.0, rely=1.0, anchor="sw", x=10, y=-20)

calculator_button = tk.Button(bottom_left_frame, text="Calculator", font=("Times New Roman", 12, "bold"), fg="white", bg="#4caf50", command=open_calculator)
calculator_button.pack(side="left", padx=5)


# Run the Tkinter app
init_db()
root.mainloop()