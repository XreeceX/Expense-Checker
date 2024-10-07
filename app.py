from flask import Flask, render_template, request, redirect, url_for,Response
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database model for expenses
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

# Database model for budget
class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

# Create the database
with app.app_context():
    db.create_all()

@app.route('/', methods=["GET", "POST"])
def index():
    # Load budget from the database, if it exists
    budget_entry = Budget.query.first()
    budget = budget_entry.value if budget_entry else 0

    if request.method == "POST":
        # Adding a new expense
        description = request.form['description']
        amount = float(request.form['amount'])
        new_expense = Expense(description=description, amount=amount)
        db.session.add(new_expense)
        db.session.commit()

        # Redirect to avoid duplicate entries on page reload
        return redirect(url_for('index'))

    # Retrieve all expenses from the database
    expenses = Expense.query.all()

    # Calculate the total expenses
    total = sum(expense.amount for expense in expenses)

    # Budget alert
    alert = None
    if total > budget:
        alert = "You've exceeded the budget!"

    return render_template("index.html", expenses=expenses, total=total, budget=budget, alert=alert)

@app.route("/chart")
def chart():
    # Get total expenses for the chart
    expenses = Expense.query.all()
    monthly_expenses = sum(expense.amount for expense in expenses)

    # Load budget for the chart
    budget_entry = Budget.query.first()
    monthly_budget = budget_entry.value if budget_entry else 0

    return render_template("chart.html", total=monthly_expenses, budget=monthly_budget)


@app.route("/remove_expense", methods=["POST"])
def remove_expense():
    expense_id = int(request.form['expense_id'])
    
    # Debugging output to check what's happening
    print(f"Attempting to remove expense with ID: {expense_id}")
    
    # Find the expense to delete
    expense_to_delete = Expense.query.get(expense_id)
    
    if expense_to_delete:
        db.session.delete(expense_to_delete)
        db.session.commit()
        print(f"Removed expense: {expense_to_delete.description}")
    else:
        print(f"No expense found with ID: {expense_id}")
    
    return redirect(url_for("index"))


@app.route("/set_budget", methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        # Set new budget
        budget_value = float(request.form['budget'])

        # Check if there's already a budget set
        existing_budget = Budget.query.first()
        
        if existing_budget:
            # Update the existing budget
            existing_budget.value = budget_value
        else:
            # Create a new budget entry
            new_budget = Budget(value=budget_value)
            db.session.add(new_budget)
        
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("set_budget.html")



if __name__ == "__main__":
    app.run(debug=True)
