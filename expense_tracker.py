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
    


def main():

    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add Expense")
        print("2. Show Summary")
        print("3. Monthly Report")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            add_expense()
        elif choice == '2':
            show_summary()
        elif choice == '3':
            monthly_report()
        elif choice == '4':
            print("Exiting the Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

#main
fname = 'expenses.csv'
# Create the CSV file with headers if it doesn't exist
file_exists = os.path.isfile(fname)
if not file_exists:
    with open(fname, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Amount', 'Category', 'Description'])

main()