import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for

from database.db import (
    create_user,
    get_db,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
    verify_user,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            return render_template(
                "register.html", error="All fields are required.", name=name, email=email
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="Password must be at least 8 characters.",
                name=name,
                email=email,
            )

        if get_user_by_email(email):
            return render_template(
                "register.html",
                error="An account with that email already exists.",
                name=name,
                email=email,
            )

        user_id = create_user(name, email, password)
        session["user_id"] = user_id
        session["user_name"] = name
        return redirect(url_for("profile"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            return render_template("login.html", error="Invalid email or password.", email=email)

        user = verify_user(email, password)
        if user is None:
            return render_template("login.html", error="Invalid email or password.", email=email)

        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db_user = get_user_by_id(session["user_id"])
    name = db_user["name"]
    initials = "".join(part[0].upper() for part in name.split()[:2]) or "?"
    member_since = datetime.strptime(db_user["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %Y")

    user = {
        "name": name,
        "email": db_user["email"],
        "member_since": member_since,
        "initials": initials,
    }
    stats = {
        "total_spent": "₹18,240",
        "transaction_count": 24,
        "top_category": "Food",
    }
    transactions = [
        {"date": "Jul 10, 2026", "description": "Grocery shopping", "category": "Food", "amount": "₹1,450.00"},
        {"date": "Jul 8, 2026", "description": "Uber rides", "category": "Transport", "amount": "₹620.00"},
        {"date": "Jul 5, 2026", "description": "Electricity bill", "category": "Bills", "amount": "₹2,340.00"},
        {"date": "Jul 3, 2026", "description": "Pharmacy", "category": "Health", "amount": "₹580.00"},
        {"date": "Jun 29, 2026", "description": "Movie night", "category": "Entertainment", "amount": "₹740.00"},
        {"date": "Jun 25, 2026", "description": "New shoes", "category": "Shopping", "amount": "₹3,200.00"},
    ]
    categories = [
        {"name": "Food", "amount": "₹6,760", "percent": 28},
        {"name": "Transport", "amount": "₹2,430", "percent": 13},
        {"name": "Bills", "amount": "₹4,120", "percent": 17},
        {"name": "Health", "amount": "₹1,890", "percent": 8},
        {"name": "Entertainment", "amount": "₹2,260", "percent": 9},
        {"name": "Shopping", "amount": "₹3,780", "percent": 16},
        {"name": "Other", "amount": "₹1,000", "percent": 9},
    ]

    return render_template(
        "profile.html",
        user=user,
        stats=stats,
        transactions=transactions,
        categories=categories,
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
