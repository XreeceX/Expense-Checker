from flask import Flask, render_template, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
import csv
from io import StringIO
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=db.func.current_timestamp())

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class DeletedExpense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_deleted = db.Column(db.DateTime, default=datetime.now)

with app.app_context():
    db.create_all()

@app.route('/', methods=["GET", "POST"])
def index():
    budget_entry = Budget.query.first()
    budget = budget_entry.value if budget_entry else 0

    if request.method == "POST":
        description = request.form['description']
        amount = float(request.form['amount'])
        new_expense = Expense(description=description, amount=amount)
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for('index'))
    expenses = Expense.query.order_by(Expense.date_added.desc()).all()
    total = sum(expense.amount for expense in expenses)
    alert = None
    if total > budget:
        alert = "You've exceeded the budget!"
    
    deleted_expenses = DeletedExpense.query.all()

    return render_template("index.html", expenses=expenses, total=total, budget=budget, alert=alert, deleted_expenses=deleted_expenses)

@app.route("/chart")
def chart():
    expenses = Expense.query.all()
    monthly_expenses = sum(expense.amount for expense in expenses)
    budget_entry = Budget.query.first()
    monthly_budget = budget_entry.value if budget_entry else 0

    return render_template("chart.html", total=monthly_expenses, budget=monthly_budget)

@app.route("/remove_expense", methods=["POST"])
def remove_expense():
    expense_id = int(request.form['expense_id'])
    expense_to_delete = Expense.query.get(expense_id)

    if expense_to_delete:
        deleted_expense = DeletedExpense(
            description=expense_to_delete.description,
            amount=expense_to_delete.amount
        )
        db.session.add(deleted_expense)
        db.session.delete(expense_to_delete)
        db.session.commit()

    return redirect(url_for("index"))

@app.route("/set_budget", methods=["GET", "POST"])
def set_budget():
    if request.method == "POST":
        budget_value = float(request.form['budget'])
        existing_budget = Budget.query.first()
        
        if existing_budget:
            existing_budget.value = budget_value
        else:
            new_budget = Budget(value=budget_value)
            db.session.add(new_budget)
        
        db.session.commit()
        return redirect(url_for("index"))

    return render_template("set_budget.html")

@app.route("/export", methods=["GET"])
def export_expenses():
    expenses = Expense.query.all()
    budget_entry = Budget.query.first()
    budget = budget_entry.value if budget_entry else 0

    if not expenses:
        return "No expenses found", 404  

    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["Date", "Item", "Amount", "Total", "Remaining"])
    
    total = 0
    for expense in expenses:
        total += expense.amount
        writer.writerow([
            expense.date_added.strftime("%Y-%m-%d"),
            expense.description,
            expense.amount,
            total,
            budget - total
        ])
    
    output.seek(0)
    return Response(output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=expenses.csv"})

@app.route('/update_expense', methods=['POST'])
def update_expense():
    expense_id = request.form['expense_id']
    description = request.form['description']
    amount = request.form['amount']

    expense = Expense.query.get(expense_id)
    if expense:
        expense.description = description
        expense.amount = amount
        db.session.commit()

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
