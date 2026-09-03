import csv
from datetime import date 
import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def login_or_signup():
    print('''1. Login
    2. Sign Up''')
    choice = int(input("Enter your choice: "))

    email = input("Enter your email: ")
    password = input("Enter your password: ")

    if choice == 1:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_id = response.user.id
        print(f"Logged in successfully! Logged in as {email}")
        return user_id
    
    else:
        supabase.auth.sign_up({"email": email, "password": password})
        print("Account created! Check your email and click the confirmation link to verify your account.:")
        input("Once you've verified your account, press Enter to continue...")
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user_id = response.user.id
        print(f"Logged in successfully! Logged in as {email}")
        return user_id


def add_expense(current_user_id):
    amt= float(input("Enter the amount of the expense: "))
    category = input("Enter the category of the expense: ")
    description = input("Enter a description for the expense: ")
    today=date.today()

    supabase.table('expenses').insert({
        "user_id": current_user_id,
        "date": today.isoformat(),
        "amount": amt,
        "category": category,
        "description": description
    }).execute()
    check_budget(current_user_id) # Check budget after adding an expense

def get_monthly_summary(current_user_id, month):#function to make my calculations easier and avoiding reading the exepense file multiple times
    response = supabase.table('expenses').select('*').eq('user_id', current_user_id).execute()
    df = pd.DataFrame(response.data)

    if df.empty : 
        return pd.Series(dtype=float)
    df["date"] = pd.to_datetime(df["date"])
    filtered = df[df["date"].dt.month == month]
    return filtered.groupby("category")["amount"].sum()

def show_summary(current_user_id):
    response= supabase.table('expenses').select('*').eq('user_id', current_user_id).execute()
    df = pd.DataFrame(response.data)

    if df.empty:
        print("No expenses recorded yet.")
        return
    
    summary= df.groupby('category')['amount'].sum().sort_values(ascending=False) # groups the data by category, sums the amounts for each category, and sorts them in descending order  
    print("\nExpense Summary by Category:")
    print("-----------------------------")
    for category, total in summary.items():
        print(f"{category:<15} ₹{total:.2f}") #formatting, .2f referes to 2 decimal places, <15 means left align with a width of 15 characters
    print("-----------------------------")
    print(f"{'Total':<15} ₹{summary.sum():.2f}") #summary.sum() calculates the total expenses across all categories and formats it similarly to the individual category totals.

def monthly_report(current_user_id):
    month = int(input("Enter the month (1-12) for which you want the report: "))
    monthly_summary = get_monthly_summary(current_user_id, month)

    if monthly_summary.empty:
        print("No expenses recorded for this month.")
        return

    print("\nMonthly Expense Report:")
    print("-----------------------------")
    for category, total in monthly_summary.items():
        print(f"{category:<15} ₹{total:.2f}") #formatting works like tabular format in python 
    print("-----------------------------")
    print(f"{'Total':<15} ₹{monthly_summary.sum():.2f}") 
    
    
def set_budget(current_user_id):
    category = input("Enter the category for which you want to set a budget: ")
    budget = float(input("Enter your monthly budget: "))

    supabase.table('budgets').upsert({
        "user_id": current_user_id,
        "category": category,
        "budget": budget
    }, on_conflict="user_id,category").execute() #upsert is used to insert a new row or update an existing row if it already exists. The on_conflict parameter specifies the columns that should be used to determine if a row already exists (in this case, user_id and category). If a row with the same user_id and category already exists, it will be updated with the new budget value; otherwise, a new row will be inserted.

    print(f"Budget for {category} set to ₹{budget:.2f} successfully!")
    
def check_budget(current_user_id):
    response = supabase.table('budgets').select('*').eq('user_id', current_user_id).execute()
    df_budgets = pd.DataFrame(response.data)

    summary = get_monthly_summary(current_user_id, date.today().month) # Get the summary of expenses by category for the current month

    if summary.empty :
        print("No expenses recorded yet for this month.")
        return


    for category, amount in summary.items():
        budget_row = df_budgets[df_budgets['category'] == category]
        if not budget_row.empty:
            budget = budget_row.iloc[0]['budget'] # iloc[0] is used to access the first row of the filtered DataFrame, budget_row is a DataFrame that contains the row(s) where the 'Category' matches the current category from the summary. Since we expect only one budget per category, we take the first row (iloc[0]) and access the 'Budget' column to get the budget value for that category.
            over_budget = amount > budget
            status = "Over Budget" if over_budget else "Within Budget"
            print(f"{category:<15} ₹{amount:.2f} / ₹{budget:.2f} - {status}")
        else:
            print(f"{category:<15} ₹{amount:.2f} - No budget set")



def main(current_user_id):

    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add Expense")
        print("2. Show Summary")
        print("3. Monthly Report")
        print("4. Set Budget")
        print("5. Check Budget")
        print("6. Set Budget")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            add_expense(current_user_id)
        elif choice == '2':
            show_summary(current_user_id)
        elif choice == '3':
            monthly_report( current_user_id)
        elif choice == '4':
            set_budget(current_user_id)
        elif choice == '5':
            check_budget(current_user_id)
        elif choice == '6':
            set_budget(current_user_id)
        elif choice == '7':
            print("Exiting the Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

#main
fname = 'expenses.csv'
# Create the CSV file with headers if it doesn't exist
file_exists = os.path.isfile(fname)
if not file_exists:
    with open(fname, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Amount', 'Category', 'Description'])

# Create the budgets CSV file with headers if it doesn't exist
fname2 = 'budgets.csv'
budgets_file_exists = os.path.isfile(fname2)
if not budgets_file_exists:
    with open(fname2, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Budget'])

if __name__ == "__main__":
    current_user_id = login_or_signup()
    main(current_user_id)
