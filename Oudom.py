import csv
import hashlib
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import simpledialog

USER_FILE = "users.csv"
TRANS = "transaction.csv"


class User:
    def __init__(self, username, user_id, password, balance):
        self.username = username
        self.user_id = user_id
        self.password = password
        self.__balance = float(balance)

    @property
    def get_balance(self):
        return self.__balance

    def show_deposit(self, root):
        clear_window(root)

        tk.Label(root, text="Enter Deposit Amount:").pack(pady=5)
        entry_amount = tk.Entry(root)
        entry_amount.pack(pady=5)

        def process_deposit():
            try:
                amount = float(entry_amount.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Enter a valid amount!")
                    return

                result = self.deposit(amount, root)

                if result == "Insufficient funds":
                    messagebox.showerror("Error", "Insufficient funds!")
                else:
                    messagebox.showinfo("Success", f"Deposit successful! New balance: ${result}")
                    entry_amount.delete(0, tk.END)
                    back_to_login_success(root, self.username, self.user_id)

            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

        withdraw_button = tk.Button(root, text="Deposit", command=process_deposit)
        withdraw_button.pack(pady=10)

        back_button = tk.Button(root, text="Back", command=lambda: back_to_login_success(root, self))
        back_button.pack(pady=5)

    def deposit(self, amount, root):
        self.__balance += amount
        with open(USER_FILE, "r") as f:
            user = list(csv.reader(f))
        for row in user:
            if row and row[1] == self.user_id:
                row[7] = float(self.__balance)
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(user)
        with open(TRANS, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(     [
                    self.username,
                    self.user_id,
                    None,
                    None,
                    "Deposit",
                    amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ]
            )
        return self.__balance
    
    def withdraw(self, amount, root):
        self.__balance = float(self.__balance)
        if amount > self.__balance:
            return "Insufficient funds"
        self.__balance -= amount
        with open(USER_FILE, "r") as f:
            user = list(csv.reader(f))
        for row in user:
            if row and row[1] == self.user_id:
                row[7] = float(self.__balance)
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(user)
        with open(TRANS, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    self.username,
                    self.user_id,
                    None,
                    None,
                    "Withdraw",
                    amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                ]
            )
        return self.__balance

    def show_withdraw(self, root):
        clear_window(root)

        tk.Label(root, text="Enter Withdrawal Amount:").pack(pady=5)
        entry_amount = tk.Entry(root)
        entry_amount.pack(pady=5)

        def process_withdrawal():
            try:
                amount = float(entry_amount.get())
                if amount <= 0:
                    messagebox.showerror("Error", "Enter a valid amount!")
                    return

                result = self.withdraw(amount, root)

                if result == "Insufficient funds":
                    messagebox.showerror("Error", "Insufficient funds!")
                else:
                    messagebox.showinfo("Success", f"Withdrawal successful! New balance: ${result}")
                    entry_amount.delete(0, tk.END)
                    back_to_login_success(root, self.username, self.user_id)

            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

        withdraw_button = tk.Button(root, text="Withdraw", command=process_withdrawal)
        withdraw_button.pack(pady=10)

        back_button = tk.Button(root, text="Back", command=lambda: back_to_login_success(root, self))
        back_button.pack(pady=5)
    
    def check_balance(self, root):
        clear_window(root)
        tk.Label(root, text=f"Your balance is: ${self.__balance:.2f}", font=("Arial", 14)).pack(pady=10)

        back_button = tk.Button(root, text="Back", command=lambda: back_to_login_success(root, self))
        back_button.pack(pady=10)
    
    def transfer(self, sender_id, sender_password, receiver_id, amount, root):
        users = []
        sender_found = False
        receiver_found = False
        with open(USER_FILE, "r") as f:
            reader = csv.reader(f)

            for row in reader:
                if row and row[1] == sender_id:
                    if not verify(sender_id, sender_password):
                        sender_found = True
                        sender_name = row[0]
                        sender_balance = float(row[7])
                        if sender_balance < amount:
                            return "❌ Insufficient funds."
                        sender_new_balance = sender_balance - amount
                        row[7] = float(sender_new_balance)
                    else:
                        return "❌ Incorrect password."

                if row and row[1] == receiver_id:
                    receiver_found = True
                    receiver_name = row[0]
                    row[7] = str(float(row[7]) + amount)
                users.append(row)
        if not sender_found:
            return "❌ Sender account not found."
        if not receiver_found:
            return "❌ Receiver account not found."
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(users)
        with open(TRANS, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow([sender_name, sender_id, receiver_name, receiver_id, "Transfer", amount, datetime.now().strftime("%Y-%m-%d %H:%M")])
        return "✅ Transfer successful."

    def show_transfer(self, root):
        clear_window(root)

        tk.Label(root, text="Enter Receiver's User ID:").pack(pady=5)
        entry_receiver_id = tk.Entry(root)
        entry_receiver_id.pack(pady=5)

        tk.Label(root, text="Enter Transfer Amount:").pack(pady=5)
        entry_amount = tk.Entry(root)
        entry_amount.pack(pady=5)

        def process_transfer():
            try:
                receiver_id = entry_receiver_id.get()
                amount = float(entry_amount.get())

                if amount <= 0:
                    messagebox.showerror("Error", "Enter a valid amount!")
                    return

                result = self.transfer(self.user_id, self.password, receiver_id, amount, root)

                if "❌" in result:
                    messagebox.showerror("Error", result)
                else:
                    messagebox.showinfo("Success", result)
                    entry_receiver_id.delete(0, tk.END)
                    entry_amount.delete(0, tk.END)

            except ValueError:
                messagebox.showerror("Error", "Invalid amount!")

        transfer_button = tk.Button(root, text="Transfer", command=process_transfer)
        transfer_button.pack(pady=10)
        back_button = tk.Button(root, text="Back", command=lambda: back_to_login_success(root, self))
        back_button.pack(pady=5)

def generate_user_id():
    return os.urandom(4).hex()

def verify(user_id, password):
    with open(USER_FILE, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[1] == user_id:
                return hashlib.sha256((password + row[3]).encode()).hexdigest() == row[2]
    return False


def file_exists():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Username", "User_id", "Password", "Salt", "Sex", "DOB", "Current_Status", "Balance"])
    if not os.path.exists(TRANS):
        with open(TRANS, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Sender_name", "Sender_id", "Receiver_name", "Receiver_id", "Transaction_type", "Amount($)", "Date"])


def hash_password(password, salt):
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed

def show_register(root):
    def register_user():
        username = entry_username.get()
        password = entry_password.get()
        sex = entry_sex.get()
        dob = entry_dob.get()
        current_status = entry_current_status.get()
        balance = entry_balance.get()

        if not username or not password or not sex or not dob or not current_status or not balance:
            messagebox.showerror("Error", "Please fill in all fields!")
            return

        file_exists()
        with open(USER_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0] == username:
                    messagebox.showerror("Error", "Username already exists! Choose another.")
                    return

            user_id = generate_user_id()
            salt = os.urandom(16).hex()
            hashed_password = hash_password(password, salt)
        with open(USER_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([username, user_id, hashed_password, salt, sex, dob, current_status, balance])

        messagebox.showinfo("Registration", f"User registered successfully! Your User ID: {user_id} 🫰 🫰")
        back_to_show_menu(root)

    clear_window(root)
    tk.Label(root, text="Username:").pack(pady=5)
    entry_username = tk.Entry(root)
    entry_username.pack()
    tk.Label(root, text="Password (4-digit):").pack(pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()
    entry_sex = tk.StringVar()
    entry_sex.set("M")
    sex_frame = tk.Frame(root)
    male_radio = tk.Radiobutton(sex_frame, text="Male", variable=entry_sex, value="M")
    male_radio.pack(side=tk.LEFT, padx=10)
    female_radio = tk.Radiobutton(sex_frame, text="Female", variable=entry_sex, value="F")
    female_radio.pack(side=tk.LEFT, padx=10)
    sex_frame.pack()
    tk.Label(root, text="Date of Birth:").pack(pady=5)
    entry_dob = DateEntry(root, width=20, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    entry_dob.pack()
    tk.Label(root, text="Current Status").pack(pady=5)
    status_options = ["Student", "Employee", "Merchant", "Others"]
    entry_current_status = ttk.Combobox(root, values=status_options)
    entry_current_status.set(status_options[0])
    entry_current_status.pack(pady=5)
    tk.Label(root, text="Initial Deposit:").pack(pady=5)
    entry_balance = tk.Entry(root)
    entry_balance.pack()
    register = tk.Button(root, text="Register", command=register_user, width=8)
    register.pack(pady=10)
    exit_button = tk.Button(root, text="Back", command=lambda: back_to_show_menu(root), width=8)
    exit_button.pack(pady=10)

def show_login_user(root):
    attempts = 0 

    def login_user():
        nonlocal attempts  

        username = entry_username.get()
        user_id = entry_user_id.get()
        password = entry_password.get()

        if not username or not user_id or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        file_exists()
        with open(USER_FILE, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == username and row[1] == user_id:
                    stored_hash = row[2]
                    salt = row[3]
                    while attempts < 3:
                        if hash_password(password, salt) == stored_hash:
                            # Create a User object here with appropriate attributes
                            user = User(row[0], row[1], row[2], row[7])  # Assuming row[7] is balance
                            login_success(root, user)  # Pass the User object to login_success
                            return
                        else:
                            attempts += 1
                            if attempts < 3:
                                messagebox.showerror("Error", f"Incorrect password! Attempt {attempts}/3")
                                entry_password.delete(0, tk.END)  # Clear the password entry for retry
                                return  # Exit the function, so the user can input again
                            else:
                                messagebox.showerror("Error", "Too many failed attempts. Please try again later.")
                                back_to_show_menu(root)
                                return
                    return
            messagebox.showerror("Error", "Invalid username or user_id")

    clear_window(root)

    tk.Label(root, text="Username:").pack(pady=5)
    entry_username = tk.Entry(root)
    entry_username.pack()

    tk.Label(root, text="User ID:").pack(pady=5)
    entry_user_id = tk.Entry(root)
    entry_user_id.pack()

    tk.Label(root, text="Password:").pack(pady=5)
    entry_password = tk.Entry(root, show="*")
    entry_password.pack()

    login_button = tk.Button(root, text="Login", command=login_user)
    login_button.pack(pady=10)

    exit_button = tk.Button(root, text="Back", command=lambda: back_to_show_menu(root))
    exit_button.pack(pady=5)

def login_success(root, user):
    clear_window(root)

    tk.Label(root, text=f"Welcome, {user.username}!", font=("Arial", 14)).pack(pady=10)

    check_balance_button = tk.Button(root, text="Check Balance", command=lambda: user.check_balance(root))
    check_balance_button.pack(pady=5)
    
    deposit_button = tk.Button(root, text="Deposit", command=lambda: user.show_deposit(root))
    deposit_button.pack(pady=5)

    withdraw_button = tk.Button(root, text="Withdraw", command=lambda: user.show_withdraw(root))
    withdraw_button.pack(pady=5)

    transfer_button = tk.Button(root, text="Transfer", command=lambda: user.show_transfer(root))
    transfer_button.pack(pady=5)

    view_transaction_button = tk.Button(root, text="View Transaction", command=lambda: show_view_trans_history(root, user.username))
    view_transaction_button.pack(pady=5)

    exit_button = tk.Button(root, text="Logout", command=lambda: back_to_show_menu(root), width=8)
    exit_button.pack(pady=10)

def view_trans_history(user_id):
    with open(TRANS, "r") as f:
        reader = csv.reader(f)
        transactions = [
            row for row in reader if row and (row[1] == user_id or row[2] == user_id)
        ]
    return transactions

def show_view_trans_history(root, user_id):
    
    root = tk.Tk()
    root.geometry("800x500")
    transactions = view_trans_history(user_id)

    tree = ttk.Treeview(root, columns=('Sender', 'Sender ID', 'Receiver', 'Receiver ID', 'Transaction Type', 'Amount', 'Date'), show="headings")

    tree.heading('Sender', text='Sender')
    tree.heading('Sender ID', text='Sender ID')
    tree.heading('Receiver', text='Receiver')
    tree.heading('Receiver ID', text='Receiver ID')
    tree.heading('Transaction Type', text='Transaction Type')
    tree.heading('Amount', text='Amount')
    tree.heading('Date', text='Date')

    tree.column('Sender', )
    tree.column('Sender ID', )
    tree.column('Receiver', )
    tree.column('Receiver ID', )
    tree.column('Transaction Type', )
    tree.column('Amount', )
    tree.column('Date', )

    transactions = view_trans_history(user_id)
    if transactions:
        for transaction in transactions:
            tree.insert("", "end", values=transaction)
    else:
        tree.insert("", "end", values=("No transactions found.",) * 7)

    vertical_scrollbar = tk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.config(yscrollcommand=vertical_scrollbar.set)
    vertical_scrollbar.pack(side="right", fill="y")

    horizontal_scrollbar = tk.Scrollbar(root, orient="horizontal", command=tree.xview)
    tree.config(xscrollcommand=horizontal_scrollbar.set)
    horizontal_scrollbar.pack(side="bottom", fill="x")

    tree.pack(fill="both", expand=True)

    exit_button = tk.Button(root, text="Back", command= lambda: root.destroy(), width=8)
    exit_button.pack(pady=10)

def show_data_transaction(user_id, period_choice, root):
    df = pd.read_csv(TRANS)
    df["Date"] = pd.to_datetime(df["Date"]) 
    today = pd.to_datetime("today")

    if period_choice == "1":
        start_date = today - timedelta(weeks=1)
        period_name = "Last 1 week"
    elif period_choice == "2":
        start_date = today - timedelta(days=30)
        period_name = "Last 1 month"
    elif period_choice == "3":
        start_date = today - timedelta(days=90)
        period_name = "Last 3 months"
    elif period_choice == "4":
        start_date = today - timedelta(days=180)
        period_name = "Last 6 months"

    filtered_df = df[(df["Date"] >= start_date) & ((df["Sender_id"].astype(str) == user_id) | (df["Receiver_id"].astype(str) == user_id))]
    filtered_df["Transaction_Category"] = filtered_df["Transaction_type"]
    filtered_df.loc[filtered_df["Sender_id"].astype(str) == user_id, "Transaction_Category"] = "Transfer Out"  
    filtered_df.loc[filtered_df["Receiver_id"].astype(str) == user_id, "Transaction_Category"] = "Transfer In"
    filtered_df.loc[filtered_df["Transaction_type"] == "Withdraw", "Transaction_Category"] = "Withdraw"
    filtered_df.loc[filtered_df["Transaction_type"] == "Deposit", "Transaction_Category"] = "Deposit"
    
    groupby_df = filtered_df.groupby("Transaction_Category")["Amount($)"].sum()

    result_text = f"\nTotal amounts for {period_name}:\n"
    for category, amount in groupby_df.items():
        result_text += f"{category}: ${amount}\n"
    result_label.config(text=result_text)

    plt.figure(figsize=(7, 7))
    plt.pie(groupby_df, labels=groupby_df.index, autopct="%1.1f%%", startangle=140, textprops=dict(color="black"))
    plt.title(f"Transaction Breakdown for {period_name}")
    plt.show()

def show_data_transaction(user_id, period_choice, root, result_label):
    df = pd.read_csv(TRANS)
    df["Date"] = pd.to_datetime(df["Date"]) 
    today = pd.to_datetime("today")

    # while True:
    #     print("Choose time range to display transactions:")
    #     print("1. Last 1 week")
    #     print("2. Last 1 month")
    #     print("3. Last 3 months")
    #     print("4. Last 6 months")
    #     choice = input("Enter choice (1-4): ")

    if period_choice == "1":
        start_date = today - timedelta(weeks=1)
        period_name = "Last 1 week"
    elif period_choice == "2":
        start_date = today - timedelta(days=30)
        period_name = "Last 1 month"
    elif period_choice == "3":
        start_date = today - timedelta(days=90)
        period_name = "Last 3 months"
    elif period_choice == "4":
        start_date = today - timedelta(days=180)
        period_name = "Last 6 months"

    filtered_df = df[(df["Date"] >= start_date) & ((df["Sender_id"].astype(str) == user_id) | (df["Receiver_id"].astype(str) == user_id))]
    filtered_df["Transaction_Category"] = filtered_df["Transaction_type"]
    filtered_df.loc[filtered_df["Sender_id"].astype(str) == user_id, "Transaction_Category"] = "Transfer Out"  
    filtered_df.loc[filtered_df["Receiver_id"].astype(str) == user_id, "Transaction_Category"] = "Transfer In"
    filtered_df.loc[filtered_df["Transaction_type"] == "Withdraw", "Transaction_Category"] = "Withdraw"
    filtered_df.loc[filtered_df["Transaction_type"] == "Deposit", "Transaction_Category"] = "Deposit"
    
    groupby_df = filtered_df.groupby("Transaction_Category")["Amount($)"].sum()

    result_text = f"\nTotal amounts for {period_name}:\n"
    for category, amount in groupby_df.items():
        result_text += f"{category}: ${amount}\n"
    result_label.config(text=result_text)

    plt.figure(figsize=(7, 7))
    plt.pie(groupby_df, labels=groupby_df.index, autopct="%1.1f%%", startangle=140, textprops=dict(color="black"))
    plt.title(f"Transaction Breakdown for {period_name}")
    plt.show()

def show_data_transaction_gui(user_id, period_choice, root, result_label):
    clear_window(root) 
    root.title("Transaction Breakdown")

    period_label = tk.Label(root, text="Select Period:")
    period_label.pack(pady=10)
    period_choice_combobox = ttk.Combobox(root, values=["1 - Last 1 week", "2 - Last 1 month", "3 - Last 3 months", "4 - Last 6 months"])
    period_choice_combobox.pack(pady=5)
    def submit():
        period = period_choice_combobox.get().split()[0]  
        if period:
            show_data_transaction(user_id, period, root, result_label)

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=20)
    exit_button = tk.Button(root, text="Back", command=lambda: back_to_show_transactions_gui(root))
    exit_button.pack(pady=20)
    result_label = tk.Label(root, text="", justify="left", anchor="w")
    result_label.pack(pady=10)
    root.mainloop()

def trans_in_data(user_id, trans_opt, root, result_label):
    df = pd.read_csv(TRANS)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    today = pd.to_datetime("today").date()
    start_date = today - timedelta(days=7)

   
    if user_id not in df["Receiver_id"].astype(str).values and user_id not in df["Sender_id"].astype(str).values:
        print("User ID not in transaction history or Invalid")
        messagebox.showwarning("Invalid User ID", "User ID not in transaction history or invalid.")
        return

    print("Choose option to display your data in last 1 week:")
    print("1. Deposit")
    print("2. Withdraw")
    print("3. Transfer in")
    print("4. Transfer out")
    print("5. All transactions as pie chart")

    if trans_opt == "1":
        filtered_df = df[(df["Date"] >= start_date) & (df["Transaction_type"] == "Deposit") & (df["Sender_id"].astype(str) == user_id)]
        Trans_category = "Deposit"
    elif trans_opt == "2":
        filtered_df = df[(df["Date"] >= start_date) & (df["Transaction_type"] == "Withdraw") & (df["Sender_id"].astype(str) == user_id)]
        Trans_category = "Withdraw"
    elif trans_opt == "3":
        filtered_df = df[(df["Date"] >= start_date) & (df["Receiver_id"].astype(str) == user_id)]
        Trans_category = "Transfer In"
    elif trans_opt == "4":
        filtered_df = df[(df["Date"] >= start_date) & (df["Sender_id"].astype(str) == user_id)]
        Trans_category = "Transfer Out"
    elif trans_opt == "5":
        show_all_transaction(user_id)
        return
    else:
        print("Invalid option. Please enter a number in range (1-4).")
        messagebox.showwarning("Invalid Input", "Please select a valid transaction type.")
        return

    if filtered_df.empty:
        print("No transactions found in the last 7 days.")
        messagebox.showinfo("No Transactions", "No transactions found in the last 7 days.")
        return
    
    daily_totals = filtered_df.groupby(["Date"])["Amount($)"].sum()
    result_text = f"Transaction History for User ID {user_id}:\n"
    for date, amount in daily_totals.items():
        result_text += f"{date}: ${amount}\n"
    result_label.config(text=result_text)

    daily_totals = filtered_df.groupby(["Date"])["Amount($)"].sum()
    date_range = pd.date_range(start=start_date, end=today).date
    daily_totals = daily_totals.reindex(date_range, fill_value=0)

    plt.figure(figsize=(10, 5))
    bars = daily_totals.plot(kind="bar", color="skyblue", edgecolor="black")
    plt.xlabel("Date")
    plt.ylabel("Total Amount ($)")
    plt.title(f"{Trans_category} Transactions (Last 7 Days) for User ID {user_id}")
    plt.xticks(rotation=0)
    for bar in bars.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, 
                 bar.get_height() + 5,  
                 f"${bar.get_height():.2f}", 
                 ha="center", va="bottom", fontsize=10)
    
    plt.show()

def show_transactions_gui(root):
    global result_label
    root.title("Transaction History")
    def on_search_button_click():
        user_id = user_id_entry.get()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return
        trans_opt = trans_var.get()
        if trans_opt == "5":
            show_data_transaction_gui(user_id, trans_opt, root, result_label)
        else:
            trans_in_data(user_id, trans_opt, root, result_label)
    tk.Label(root, text="Enter User ID:").pack(pady=5)
    user_id_entry = tk.Entry(root)
    user_id_entry.pack(pady=5)
    tk.Label(root, text="Choose Transaction Type:").pack(pady=5)
    trans_var = tk.StringVar(value="0")
    options = [
        ("Deposit", "1"),
        ("Withdraw", "2"),
        ("Transfer In", "3"),
        ("Transfer Out", "4"),
        ("All transactions (Pie Chart)", "5"),
    ]
    for text, value in options:
        tk.Radiobutton(root, text=text, variable=trans_var, value=value).pack(anchor="w")
    search_button = tk.Button(root, text="Show Transactions", command=on_search_button_click)
    search_button.pack(pady=10)
    exit_button = tk.Button(root, text="Back", command=lambda: back_to_show_menu(root))
    exit_button.pack(pady=10)
    result_label = tk.Label(root, text="", justify="left", font=("Arial", 10), width=40, height=5)
    result_label.pack(pady=5)

def show_data_user(root):
    
    df = pd.read_csv(USER_FILE)
    counter = df["Current_Status"].value_counts()
    print(counter)

    # to count
    plt.figure(figsize=(6, 6))  # Set figure size (width=6, height=6 inches)
    plt.pie(counter, labels=counter.index, autopct="%1.1f%%", startangle=90)
    plt.title("User Status Distribution")  # Set title
    plt.show()

def show_data_user_gui(root):

    label_count = tk.Label(root, text="Current Status Counts:", font=("Arial", 14))
    label_count.pack(pady=10)

    df = pd.read_csv(USER_FILE)
    counter = df["Current_Status"].value_counts()  

    for status, count in counter.items():
        status_label = tk.Label(root, text=f"{status}: {count}", font=("Arial", 12))
        status_label.pack(pady=5)
    
    plt.figure(figsize=(6, 6)) 
    plt.pie(counter, labels=counter.index, autopct="%1.1f%%", startangle=90)
    plt.title("User Status Distribution")  
    plt.show()

    back_button = tk.Button(root, text="Back", command=lambda: back_to_show_menu(root), width=20)
    back_button.pack(pady=10)

def view_inc_exsp(user_id):

    df = pd.read_csv(TRANS)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    today = datetime.today().date()
    start_date = today - timedelta(days=6)  # Last 7 days including today

    while True:
        user_id = input("Enter user ID to view transaction history: ")
        if user_id not in df["Sender_id"].astype(str).values and user_id not in df["Receiver_id"].astype(str).values:
            print("User ID not found in transaction history. Try again.")
        else:
            break

    filtered_df = df[(df["Date"] >= start_date) & 
                     ((df["Sender_id"].astype(str) == user_id) | (df["Receiver_id"].astype(str) == user_id))]

    filtered_df["Transaction_Category"] = "Spent"  # Default to Spent
    filtered_df.loc[filtered_df["Receiver_id"].astype(str) == user_id, "Transaction_Category"] = "Income"
    filtered_df.loc[(filtered_df["Transaction_type"] == "Withdraw") & 
                    (filtered_df["Sender_id"].astype(str) == user_id), "Transaction_Category"] = "Spent"
    filtered_df.loc[(filtered_df["Transaction_type"] == "Deposit") & 
                    (filtered_df["Receiver_id"].astype(str) == user_id), "Transaction_Category"] = "Income"

    grouped_df = filtered_df.groupby(["Date", "Transaction_Category"])["Amount($)"].sum().unstack(fill_value=0)
    print(grouped_df)

    date_range = [start_date + timedelta(days=i) for i in range(7)]
    grouped_df = grouped_df.reindex(date_range, fill_value=0)

    grouped_df.plot(kind='bar', color=['green', 'red'])
    plt.title(f"Income vs Expense for User {user_id} (Last 7 Days)")
    plt.xlabel("Date")
    plt.ylabel("Amount ($)")
    plt.xticks(rotation=45)
    plt.legend(["Income", "Expense"])
    plt.show()

def view_inc_exsp_gui(root):
    def on_search_button_click():
        user_id = user_id_entry.get()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return
        
        if not os.path.exists(TRANS):
            messagebox.showerror("File Error", f"Transaction file not found: {TRANS}")
            return

        try:
            df = pd.read_csv(TRANS)
        except Exception as e:
            messagebox.showerror("File Read Error", f"An error occurred while reading the CSV file: {e}")
            return

        if user_id not in df["Sender_id"].astype(str).values and user_id not in df["Receiver_id"].astype(str).values:
            messagebox.showwarning("User Not Found", "User ID not found in transaction history.")
            return
        
        df["Date"] = pd.to_datetime(df["Date"]).dt.date  
        today = datetime.today().date()
        start_date = today - timedelta(days=6) 

        filtered_df = df[(df["Date"] >= start_date) & 
                         ((df["Sender_id"].astype(str) == user_id) | (df["Receiver_id"].astype(str) == user_id))]

        filtered_df["Transaction_Category"] = "Spent" 
        filtered_df.loc[filtered_df["Receiver_id"].astype(str) == user_id, "Transaction_Category"] = "Income"
        filtered_df.loc[(filtered_df["Transaction_type"] == "Withdraw") & 
                        (filtered_df["Sender_id"].astype(str) == user_id), "Transaction_Category"] = "Spent"
        filtered_df.loc[(filtered_df["Transaction_type"] == "Deposit") & 
                        (filtered_df["Receiver_id"].astype(str) == user_id), "Transaction_Category"] = "Income"

        # Create the grouped DataFrame for plotting and treeview
        grouped_df = filtered_df.groupby(["Date", "Transaction_Category"])["Amount($)"].sum().unstack(fill_value=0)
        date_range = [start_date + timedelta(days=i) for i in range(7)]
        grouped_df = grouped_df.reindex(date_range, fill_value=0)

        # Plotting
        grouped_df.plot(kind='bar', color=['green', 'red'])
        plt.title(f"Income vs Expense for User {user_id} (Last 7 Days)")
        plt.xlabel("Date")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)
        plt.show()


        root = tk.Tk()
        root.geometry("800x500")

        tree = ttk.Treeview(root, columns=("Date", "Transaction_Category", "Income", "Spent"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Transaction_Category", text="Transaction Category")
        tree.heading("Income", text="Income ($)")
        tree.heading("Spent", text="Spent ($)")

        for index, row in grouped_df.iterrows():
            transaction_category = "Income" if row["Income"] > 0 else "Spent"
            tree.insert("", "end", values=(index, transaction_category, row["Income"], row["Spent"]))

        tree.pack(pady=20)

        back_button = tk.Button(root, text="Back", command=lambda: root.destroy(), width=20)
        back_button.pack(pady=10)

    user_id_label = tk.Label(root, text="Enter User ID:")
    user_id_label.pack(pady=5)

    user_id_entry = tk.Entry(root)
    user_id_entry.pack(pady=5)

    search_button = tk.Button(root, text="Search", command=on_search_button_click)
    search_button.pack(pady=5)
    
    back_button = tk.Button(root, text="Back", command=lambda: back_to_show_menu(root), width=20)
    back_button.pack(pady=10)


def clear_window(root):
    for widget in root.winfo_children():
        widget.destroy()

def back_to_show_menu(root):
    clear_window(root)
    show_menu(root) 

def back_to_login_success(root, user):
    clear_window(root)
    login_success(root, user) 
def back_to_show_transactions_gui(root):
    clear_window(root)
    show_transactions_gui(root)
def exit_():
    result = messagebox.askyesno('Exit Confirmation', 'Are you sure you want to leave?')
    if result:
        root.destroy()

def show_menu(root):
    def open_register():
        clear_window(root)
        show_register(root)
    def open_login():
        clear_window(root)
        show_login_user(root)
    def open_transaction():
        clear_window(root)
        show_transactions_gui(root)
    def open_user_data():
        clear_window(root)
        show_data_user_gui(root)
    def view_total():
        clear_window(root)
        view_inc_exsp_gui(root)

    tk.Label(root, text="Welcome to the ATM System!", font=("Arial", 16)).pack(pady=20)
    
    register_button = tk.Button(root, text="Register", command=open_register, width=20)
    register_button.pack(pady=10)
    
    login_button = tk.Button(root, text="Login", command=open_login, width=20)
    login_button.pack(pady=10)
    
    transaction_button = tk.Button(root, text="Analyze Transaction", command=open_transaction, width=20)
    transaction_button.pack(pady=10)

    user_data_button = tk.Button(root, text="User Data", command=open_user_data, width=20)
    user_data_button.pack(pady=10)

    view_total_button = tk.Button(root, text="View Total", command=view_total, width=20)
    view_total_button.pack(pady=10)
    
    exit_button = tk.Button(root, text="Exit", command=exit_, width=20) 
    exit_button.pack(pady=10)
    root.mainloop()

root = tk.Tk()
root.title("ATM System")
root.geometry("400x500")

show_menu(root)  
root.mainloop()

