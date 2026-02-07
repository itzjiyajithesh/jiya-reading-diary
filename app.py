from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = "super_secret_key_change_later"

# ---------- DATABASE SETUP ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- HOME / SIGN UP ----------
@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        try:
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name, age, gender, email, password) VALUES (?, ?, ?, ?, ?)",
                (name, age, gender, email, password)
            )
            conn.commit()
            conn.close()
            message = "Account created successfully! You can now log in."
        except sqlite3.IntegrityError:
            message = "An account with this email already exists."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>
<style>
body {
    background-image: url("/static/Book1.jpg");
    text-align: center;
    font-family: cursive;
}
.text-box {
    border: 3px solid #ffde59;
    padding: 40px;
    margin: 40px auto;
    background-color: #33003D;
    width: 900px;
    border-radius: 15px;
    box-shadow: 0 0 20px #ffde59;
}
input, select {
    padding: 10px;
    margin: 8px;
    width: 60%;
}
button {
    background-color: #ffde59;
    border: none;
    padding: 15px 30px;
    font-size: 16px;
    border-radius: 15px;
    cursor: pointer;
}
p { color: #FF914D; font-size: 20px; }
a { color: #ffde59; }
</style>
</head>

<body>
<div class="text-box">
<img src="/static/J.png" alt="Logo">

<p>
Hello everyone and welcome to <b><i>Jiya's Reading Diary</i></b>!
My name is Jiya and I am a passionate reader who loves books and would love to recommend some for you!
</p>

<h2 style="color:#ffde59;">Create an Account</h2>

<form method="post">
<input name="name" placeholder="Name" required><br>
<input name="age" type="number" placeholder="Age" required><br>
<select name="gender" required>
<option value="">Select Gender</option>
<option>Female</option>
<option>Male</option>
<option>Other</option>
</select><br>
<input name="email" type="email" placeholder="Email" required><br>
<input name="password" type="password" placeholder="Password" required><br>
<button type="submit">Let's Get Started!</button>
</form>

<p>{{message}}</p>

<p><a href="/login">Already have an account? Log in</a></p>

<br><br>
<p><i><b>Happy Reading!</b></i></p>
</div>
</body>
</html>
""", message=message)

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            error = "Invalid email or password."

    return render_template_string("""
<html>
<head>
<title>Login</title>
<style>
body { background-color:#33003D; text-align:center; font-family:cursive; }
.text-box { margin:100px auto; padding:40px; width:500px; background:#22002A; border-radius:15px; box-shadow:0 0 20px #ffde59; }
input { padding:10px; margin:10px; width:80%; }
button { padding:12px 25px; background:#ffde59; border:none; border-radius:15px; }
p { color:#FF914D; }
</style>
</head>
<body>
<div class="text-box">
<h2 style="color:#ffde59;">Login</h2>
<form method="post">
<input name="email" type="email" placeholder="Email" required><br>
<input name="password" type="password" placeholder="Password" required><br>
<button type="submit">Login</button>
</form>
<p>{{error}}</p>
</div>
</body>
</html>
""", error=error)

# ---------- PROFILE ----------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()
    conn.close()

    return render_template_string("""
<html>
<head>
<title>Your Profile</title>
<style>
body { background-color:#33003D; text-align:center; font-family:cursive; }
.text-box { margin:100px auto; padding:40px; width:600px; background:#22002A; border-radius:15px; box-shadow:0 0 25px #ffde59; }
p { color:#FF914D; font-size:20px; }
a { color:#ffde59; }
</style>
</head>
<body>
<div class="text-box">
<h2 style="color:#ffde59;">Welcome, {{user["name"]}}!</h2>
<p>Age: {{user["age"]}}</p>
<p>Gender: {{user["gender"]}}</p>
<p>Email: {{user["email"]}}</p>

<p><a href="/logout">Logout</a></p>
</div>
</body>
</html>
""", user=user)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------- RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)