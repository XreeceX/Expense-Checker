from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Store expenses and removed expenses
expenses = []
removed_expenses = []

# Default budget
budget = 0

@app.route("/", methods=["GET", "POST"])
def index():
    global expenses
    global budget
    
    if request.method == "POST":
        # Adding a new expense
        description = request.form['description']
        amount = float(request.form['amount'])
        expenses.append({"description": description, "amount": amount})

    # Calculate the total every time the page is loaded
    total = sum(expense['amount'] for expense in expenses)

    # Budget alert
    alert = None
    if total > budget:
        alert = "You've exceeded the budget!"

    return render_template("index.html", expenses=expenses, total=total, budget=budget, alert=alert, removed_expenses=removed_expenses)

@app.route("/remove_expense", methods=["POST"])
def remove_expense():
    global expenses, removed_expenses
    # Find the expense by its index and remove it
    expense_id = int(request.form['expense_id'])
    removed_expense = expenses.pop(expense_id)
    
    # Add the removed expense to the history
    removed_expenses.append(removed_expense)
    
    return redirect(url_for("index"))

@app.route("/set_budget", methods=["GET", "POST"])
def set_budget():
    global budget
    if request.method == "POST":
        # Set new budget
        budget = float(request.form['budget'])
        return redirect(url_for("index"))

    return render_template("set_budget.html")

if __name__ == "__main__":
    app.run(debug=True)
