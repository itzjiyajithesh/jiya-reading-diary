from flask import Flask, request, render_template_string
import os
import hashlib
import sqlite3

# Try PostgreSQL only if available
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "change_this_later"

# ---------------- DATABASE ----------------
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    if DATABASE_URL and POSTGRES_AVAILABLE:
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect("users.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    if DATABASE_URL and POSTGRES_AVAILABLE:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                age INTEGER,
                gender TEXT,
                email TEXT UNIQUE,
                password TEXT
            )
        """)
    else:
        cur.execute("""
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

# ---------------- HOME / SIGNUP ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""

    if request.method == "POST":
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        try:
            conn = get_db()
            cur = conn.cursor()

            if DATABASE_URL and POSTGRES_AVAILABLE:
                cur.execute(
                    "INSERT INTO users (name, age, gender, email, password) VALUES (%s,%s,%s,%s,%s)",
                    (request.form["name"], request.form["age"], request.form["gender"],
                     request.form["email"], password)
                )
            else:
                cur.execute(
                    "INSERT INTO users (name, age, gender, email, password) VALUES (?,?,?,?,?)",
                    (request.form["name"], request.form["age"], request.form["gender"],
                     request.form["email"], password)
                )

            conn.commit()
            conn.close()
            msg = "Account created successfully!"

        except Exception:
            msg = "Email already exists."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>

<style>
:root {
    --bg: #33003D;
    --box: #22002A;
    --text: #FF914D;
    --accent: #ffde59;
}

body {
    background-image: url("/static/Book2.png);
    font-family: cursive;
    text-align: center;
}

.text-box {
    width: 900px;
    margin: 40px auto;
    padding: 40px;
    background: var(--box);
    border-radius: 20px;
    border: 4px solid #ffde59;
    animation: borderGlow 6s infinite linear;
}

@keyframes borderGlow {
    0% {
        border-color: #ffde59;
        box-shadow: 0 0 15px #ffde59, 0 0 30px rgba(255,222,89,0.6);
    }
    33% {
        border-color: #ff914d;
        box-shadow: 0 0 18px #ff914d, 0 0 36px rgba(255,145,77,0.6);
    }
    66% {
        border-color: #b84dff;
        box-shadow: 0 0 18px #b84dff, 0 0 36px rgba(184,77,255,0.6);
    }
    100% {
        border-color: #ffde59;
        box-shadow: 0 0 15px #ffde59, 0 0 30px rgba(255,222,89,0.6);
    }
}

form {
    text-align: left;
}

.field {
    position: relative;
    margin-bottom: 25px;
}

.field input, .field select {
    width: 100%;
    padding: 14px;
    background: #4b005a;
    border: 2px solid var(--accent);
    border-radius: 12px;
    color: var(--accent);
    font-size: 16px;
}

.field label {
    position: absolute;
    top: 50%;
    left: 14px;
    color: var(--accent);
    font-size: 14px;
    pointer-events: none;
    transform: translateY(-50%);
    transition: 0.3s;
    background: var(--box);
    padding: 0 6px;
}

.field input:focus + label,
.field input:not(:placeholder-shown) + label,
.field select:focus + label {
    top: -8px;
    font-size: 12px;
}

.field input:focus {
    box-shadow: 0 0 15px var(--accent);
}

button {
    background: var(--accent);
    border: none;
    padding: 16px 40px;
    border-radius: 20px;
    font-size: 18px;
    cursor: pointer;
    animation: buttonGlow 3s infinite;
    transition: transform 0.3s;
}

button:hover {
    transform: scale(1.1);
}

@keyframes buttonGlow {
    0% { box-shadow: 0 0 10px #ffde59; }
    50% { box-shadow: 0 0 25px #ff914d; }
    100% { box-shadow: 0 0 10px #ffde59; }
}

.main-text {
    color: var(--text);
    font-size: 22px;
}

.happy {
    color: var(--text);
    font-size: 26px;
    margin-top: 30px;
    text-shadow: 0 0 10px rgba(255,145,77,0.6);
}
</style>
</head>

<body>

<div class="text-box">
<img src="/static/J.png">

<p class="main-text">
Hello everyone and welcome to <b><i>Jiya's Reading Diary</i></b>!
My name is Jiya and I am a passionate reader who loves books and would love to recommend some for you!
</p>

<form method="post">
<div class="field">
<input name="name" required placeholder=" ">
<label>Name</label>
</div>

<div class="field">
<input type="number" name="age" required placeholder=" ">
<label>Age</label>
</div>

<div class="field">
<select name="gender" required>
<option></option>
<option>Female</option>
<option>Male</option>
<option>Other</option>
</select>
<label>Gender</label>
</div>

<div class="field">
<input type="email" name="email" required placeholder=" ">
<label>Email</label>
</div>

<div class="field">
<input type="password" name="password" required placeholder=" ">
<label>Password</label>
</div>

<button type="submit">Let's Get Started!</button>
</form>

<p class="main-text">{{msg}}</p>

<p class="main-text"><i><b>Happy Reading!</b></i></p>
</div>

</body>
</html>
""", msg=msg)

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
