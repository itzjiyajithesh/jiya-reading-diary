from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = "super_secret_key_change_later"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            email TEXT UNIQUE,
            password TEXT
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
        try:
            password_hash = hashlib.sha256(request.form["password"].encode()).hexdigest()
            conn = get_db()
            conn.execute(
                "INSERT INTO users (name, age, gender, email, password) VALUES (?, ?, ?, ?, ?)",
                (
                    request.form["name"],
                    request.form["age"],
                    request.form["gender"],
                    request.form["email"],
                    password_hash
                )
            )
            conn.commit()
            conn.close()
            message = "Account created successfully! You can now log in."
        except sqlite3.IntegrityError:
            message = "This email already has an account."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>
<style>
body {
    background-image: url("/static/Book2.png");
    font-family: cursive;
    text-align: center;
}

.text-box {
    width: 900px;
    margin: 40px auto;
    padding: 40px;
    background-color: #33003D;
    border-radius: 18px;
    border: 3px solid #ffde59;
    box-shadow: 0 0 25px rgba(255, 222, 89, 0.7);
}

form {
    text-align: left;
    margin-top: 30px;
}

label {
    color: #ffde59;
    font-size: 18px;
}

input, select {
    width: 100%;
    padding: 12px;
    margin-top: 6px;
    margin-bottom: 16px;
    background-color: #4b005a;
    border: 2px solid #ffde59;
    color: #ffde59;
    border-radius: 12px;
    font-size: 16px;
}

input::placeholder {
    color: #ffde59aa;
}

button {
    display: block;
    margin: 30px auto;
    background-color: #ffde59;
    color: #33003D;
    border: none;
    padding: 15px 35px;
    font-size: 18px;
    border-radius: 18px;
    cursor: pointer;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    box-shadow: 0 0 12px rgba(255, 222, 89, 0.8);
}

button:hover {
    transform: scale(1.08);
    box-shadow: 0 0 25px rgba(255, 222, 89, 1);
}

@keyframes glowShift {
    0% { box-shadow: 0 0 12px #ffde59; }
    50% { box-shadow: 0 0 22px #ff914d; }
    100% { box-shadow: 0 0 12px #ffde59; }
}

button {
    animation: glowShift 3s infinite;
}

p {
    color: #FF914D;
    font-size: 20px;
}

a {
    color: #ffde59;
}
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
<label>Name</label>
<input name="name" placeholder="Your name" required>

<label>Age</label>
<input type="number" name="age" placeholder="Your age" required>

<label>Gender</label>
<select name="gender" required>
<option value="">Select</option>
<option>Female</option>
<option>Male</option>
<option>Other</option>
</select>

<label>Email</label>
<input type="email" name="email" placeholder="Your email" required>

<label>Password</label>
<input type="password" name="password" placeholder="Create a password" required>

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
        password_hash = hashlib.sha256(request.form["password"].encode()).hexdigest()
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (request.form["email"], password_hash)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("profile"))
        else:
            error = "Invalid email or password."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Login</title>
<style>
body { background:#33003D; font-family:cursive; text-align:center; }
.box {
    width: 450px;
    margin: 120px auto;
    padding: 40px;
    background:#22002A;
    border-radius: 18px;
    box-shadow: 0 0 25px #ffde59;
}
input {
    width:100%;
    padding:12px;
    margin:12px 0;
    background:#4b005a;
    border:2px solid #ffde59;
    color:#ffde59;
    border-radius:12px;
}
button {
    background:#ffde59;
    border:none;
    padding:14px 30px;
    border-radius:16px;
    font-size:16px;
    cursor:pointer;
}
p { color:#FF914D; }
</style>
</head>
<body>
<div class="box">
<h2 style="color:#ffde59;">Login</h2>
<form method="post">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
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
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Profile</title>
<style>
body { background:#33003D; font-family:cursive; text-align:center; }
.box {
    width:500px;
    margin:120px auto;
    padding:40px;
    background:#22002A;
    border-radius:18px;
    box-shadow:0 0 25px #ffde59;
}
p { color:#FF914D; font-size:20px; }
a { color:#ffde59; }
</style>
</head>
<body>
<div class="box">
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
