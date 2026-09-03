from flask import Flask, render_template, request, redirect , url_for, session 
#render_template is used to render the HTML templates, request is used to handle incoming requests, redirect is used to redirect the user to a different route, url_for is used to generate URLs for routes, and session is used to store user session data
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date
import pandas as pd

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

app=Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-change-this")

@app.context_processor
def inject_user_email():
    return dict(session_email=session.get('email'))

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST']) # GET helps to view, POST helps to send data to the server
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session['user_id'] = response.user.id
        session['email'] = email
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        supabase.auth.sign_up({"email": email, "password": password})
        return "Account created! Check your email and click the confirmation link to verify your account."
    return render_template('signup.html')
    \

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    exp_response = supabase.table('expenses').select('*').eq('user_id',user_id).execute()
    df=pd.DataFrame(exp_response.data)

    summary={}
    if not df.empty:
        summary = df.groupby('category')['amount'].sum().sort_values(ascending=False).to_dict()

    budget_response = supabase.table('budgets').select('*').eq('user_id', user_id).execute()
    budgets = {b['category']: b['budget'] for b in budget_response.data}

    return render_template('dashboard.html',
                            expenses=exp_response.data,
                            summary=summary,
                            budgets=budgets,
                            email=session.get('email'))


@app.route('/add_expense', methods=['GET','POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        today = date.today()

        supabase.table('expenses').insert({
            "user_id": user_id,
            "date": today.isoformat(),
            "amount": amount,
            "category": category,
            "description": description
        }).execute()

        return redirect(url_for('dashboard'))
    return render_template('add_expense.html')

@app.route('/set-budget', methods=['GET', 'POST'])
def set_budget():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        category = request.form['category']
        budget = float(request.form['budget'])
        

        supabase.table('budgets').upsert({
            "user_id": user_id,
            "category": category,
            "budget": budget
        },on_conflict="user_id, category").execute()

        return redirect(url_for('dashboard'))
    return render_template('set_budget.html')

if __name__ == '__main__':
    app.run(debug=True)

