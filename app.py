from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# -----------------------------
# Create Database
# -----------------------------
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# -----------------------------
# Home Page (Register)
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# Register User
# -----------------------------
@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        (name,email,password)
    )

    conn.commit()
    conn.close()

    return redirect("/login")


# -----------------------------
# Login Page
# -----------------------------
@app.route("/login")
def login_page():
    return render_template("login.html")


# -----------------------------
# Login Logic
# -----------------------------
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[3], password):
        session["user"] = user[1]
        return redirect("/dashboard")
    else:
        return "Invalid Email or Password"


# -----------------------------
# Dashboard
# -----------------------------
@app.route("/dashboard")
def dashboard():

    if "user" in session:
        return render_template("dashboard.html", user=session["user"])
    else:
        return redirect("/login")


# -----------------------------
# View Users
# -----------------------------
@app.route("/users")
def users():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()

    conn.close()

    return render_template("users.html", users=data)


# -----------------------------
# Logout
# -----------------------------
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

@app.route("/edit-profile")
def edit_profile():

    if "user" in session:

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE name=?",
            (session["user"],)
        )

        user = cursor.fetchone()

        conn.close()

        return render_template("edit_profile.html", user=user)

    else:
        return redirect("/login")
    

@app.route("/update-profile", methods=["POST"])
def update_profile():

    name = request.form["name"]
    email = request.form["email"]

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET name=?, email=? WHERE name=?",
        (name, email, session["user"])
    )

    conn.commit()
    conn.close()

    session["user"] = name

    return redirect("/dashboard")
@app.route("/delete/<int:id>")
def delete_user(id):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/users")
@app.route("/api/users")
def api_users():

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id,name,email FROM users")

    users = cursor.fetchall()

    conn.close()

    user_list = []

    for u in users:

        user_list.append({
            "id": u[0],
            "name": u[1],
            "email": u[2]
        })

    return jsonify(user_list)

@app.route("/api/register", methods=["POST"])
def api_register():

    name = request.json["name"]
    email = request.json["email"]
    password = generate_password_hash(request.json["password"])

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users(name,email,password) VALUES(?,?,?)",
        (name,email,password)
    )

    conn.commit()
    conn.close()

    return jsonify({"message":"User registered"})
app.run(debug=True)