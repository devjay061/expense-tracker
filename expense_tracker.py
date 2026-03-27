import csv
from datetime import date 
import os
import pandas as pd


def add_expense():
    amt= float(input("Enter the amount of the expense: "))
    category = input("Enter the category of the expense: ")
    description = input("Enter a description for the expense: ")
    today=date.today()

    with open(fname, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([today, amt, category, description])
    print("Expense added successfully!")

    check_budget() # Check budget after adding an expense

def get_monthly_summary(month):#function to make my calculations easier and avoiding reading the exepense file multiple times
    df = pd.read_csv(fname)
    df["Date"] = pd.to_datetime(df["Date"])
    filtered = df[df["Date"].dt.month == month]
    return filtered.groupby("Category")["Amount"].sum()

def show_summary():
    df= pd.read_csv(fname) #reads the entire csv file 
    summary= df.groupby('Category')['Amount'].sum().sort_values(ascending=False) # groups the data by category, sums the amounts for each category, and sorts them in descending order  
    print("\nExpense Summary by Category:")
    print("-----------------------------")
    for category, total in summary.items():
        print(f"{category:<15} ₹{total:.2f}") #formatting, .2f referes to 2 decimal places, <15 means left align with a width of 15 characters
    print("-----------------------------")
    print(f"{'Total':<15} ₹{summary.sum():.2f}") #summary.sum() calculates the total expenses across all categories and formats it similarly to the individual category totals.

def monthly_report():
    df= pd.read_csv(fname)
    df['Date'] = pd.to_datetime(df['Date']) #converts the 'Date' column to datetime format, allowing for easier manipulation and filtering based on date components like month and year.
    month=int(input("Enter the month number (1-12) for the report: ")) 
    filtered= df[df['Date'].dt.month == month] #filters the DataFrame to include only rows where the month component of the 'Date' column matches the user input, effectively isolating expenses for the specified month.
    monthly_summary=filtered.groupby('Category')['Amount'].sum().sort_values(ascending=False) 
    print("\nMonthly Expense Report:")
    print("-----------------------------")
    for category, total in monthly_summary.items():
        print(f"{category:<15} ₹{total:.2f}") #formatting works like tabular format in python 
    print("-----------------------------")
    print(f"{'Total':<15} ₹{monthly_summary.sum():.2f}") 
    
    
def set_budget():
    category = input("Enter the category for which you want to set a budget: ")
    budget = float(input("Enter your monthly budget: "))
    budgets=[]
    found=False
    if os.path.isfile(fname2):  # only read if file exists
        with open(fname2, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # skip header
            for row in reader:
                if row[0] == category:
                    row[1] = str(budget)
                    found = True
                budgets.append(row)
        
    if not found:
        budgets.append([category, budget])

    with open(fname2, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Budget'])  # Write the header
        writer.writerows(budgets)

    print(f"Budget for {category} set to ₹{budget:.2f} successfully!")
    
def check_budget():
    df_budgets = pd.read_csv(fname2)

    summary= get_monthly_summary(date.today().month) # Get the summary of expenses by category
    for category, amount in summary.items():
        budget_row = df_budgets[df_budgets['Category'] == category]
        if not budget_row.empty:
            budget = budget_row.iloc[0]['Budget'] # iloc[0] is used to access the first row of the filtered DataFrame, budget_row is a DataFrame that contains the row(s) where the 'Category' matches the current category from the summary. Since we expect only one budget per category, we take the first row (iloc[0]) and access the 'Budget' column to get the budget value for that category.
            over_budget = amount > budget
            status = "Over Budget" if over_budget else "Within Budget"
            print(f"{category:<15} ₹{amount:.2f} / ₹{budget:.2f} - {status}")
        else:
            print(f"{category:<15} ₹{amount:.2f} - No budget set")



def main():

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
            add_expense()
        elif choice == '2':
            show_summary()
        elif choice == '3':
            monthly_report()
        elif choice == '4':
            set_budget()
        elif choice == '5':
            check_budget()
        elif choice == '6':
            set_budget()
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

main()
