from flask import Flask, request, render_template_string, redirect, url_for, session
import os
import hashlib
import sqlite3

# Optional PostgreSQL
try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "change_this_later"

DATABASE_URL = os.environ.get("DATABASE_URL")

# ---------------- DATABASE ----------------
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
                password TEXT,
                theme TEXT DEFAULT 'dark'
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
                password TEXT,
                theme TEXT DEFAULT 'dark'
            )
        """)

    conn.commit()
    conn.close()

init_db()

# ---------------- SIGNUP ----------------
@app.route("/", methods=["GET", "POST"])
def signup():
    msg = ""

    if request.method == "POST":
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        try:
            conn = get_db()
            cur = conn.cursor()

            query = "INSERT INTO users (name, age, gender, email, password) VALUES (?,?,?,?,?)"
            values = (
                request.form["name"],
                request.form["age"],
                request.form["gender"],
                request.form["email"],
                password
            )

            if DATABASE_URL and POSTGRES_AVAILABLE:
                query = query.replace("?", "%s")

            cur.execute(query, values)
            conn.commit()
            conn.close()

            session["success"] = True
            return redirect(url_for("login"))

        except Exception:
            msg = "Email already exists."

    # Example image and text before and after form
    pre_content = '<img src="/static/Book2.png" alt="Book" style="width:200px;"><p>Fill in your details to create an account:</p>'
    post_content = '<p>Already a member? Use the login link below.</p>'

    full_content = f"{pre_content}<div id='form-wrapper'>{signup_form()}</div>{post_content}"

    return render_page("Create Account", full_content, msg)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""

    if request.method == "POST":
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        conn = get_db()
        cur = conn.cursor()

        query = "SELECT id, theme FROM users WHERE email=? AND password=?"
        if DATABASE_URL and POSTGRES_AVAILABLE:
            query = query.replace("?", "%s")

        cur.execute(query, (request.form["email"], password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["theme"] = user[1]
            return redirect(url_for("profile"))
        else:
            msg = "Invalid login details."

    pre_content = '<p>Login with your email and password:</p>'
    full_content = f"<div id='form-wrapper'>{login_form()}</div>"
    return render_page("Login", pre_content + full_content, msg)

# ---------------- PROFILE ----------------
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cur = conn.cursor()

    query = "SELECT name, age, gender, email FROM users WHERE id=?"
    if DATABASE_URL and POSTGRES_AVAILABLE:
        query = query.replace("?", "%s")

    cur.execute(query, (session["user_id"],))
    user = cur.fetchone()
    conn.close()

    return render_page(
        "Profile",
        f"""
        <h2>Welcome, {user[0]}!</h2>
        <p>Age: {user[1]}</p>
        <p>Gender: {user[2]}</p>
        <p>Email: {user[3]}</p>
        <a href="/toggle-theme">Toggle Theme</a><br><br>
        <a href="/logout">Logout</a>
        """,
        ""
    )

# ---------------- THEME TOGGLE ----------------
@app.route("/toggle-theme")
def toggle_theme():
    if "user_id" not in session:
        return redirect(url_for("login"))

    new_theme = "light" if session.get("theme") == "dark" else "dark"
    session["theme"] = new_theme

    conn = get_db()
    cur = conn.cursor()

    query = "UPDATE users SET theme=? WHERE id=?"
    if DATABASE_URL and POSTGRES_AVAILABLE:
        query = query.replace("?", "%s")

    cur.execute(query, (new_theme, session["user_id"]))
    conn.commit()
    conn.close()

    return redirect(url_for("profile"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- UI TEMPLATES ----------------
def render_page(title, content, msg):
    theme = session.get("theme", "dark")
    success = session.pop("success", False)

    return render_template_string(f"""
<!DOCTYPE html>
<html>
<head>
<title>{title}</title>
<style>
:root {{
    --bg: #33003D;
    --box: #22002A;
    --text: #FF914D;
    --accent: #ffde59;
}}
.light {{
    --bg: #f5f5f5;
    --box: #ffffff;
    --text: #333;
    --accent: #ff914d;
}}

body {{
    background-image: url("/static/Book2.png"); 
    font-family: cursive;
    text-align: center;
}}

.text-box {{
    width: 600px;
    margin: 50px auto;
    padding: 40px;
    background: var(--box);
    border-radius: 20px;
    border: 4px solid var(--accent);
    animation: glow 6s infinite;
}}

@keyframes glow {{
    0% {{ box-shadow: 0 0 15px var(--accent); }}
    50% {{ box-shadow: 0 0 35px var(--text); }}
    100% {{ box-shadow: 0 0 15px var(--accent); }}
}}

input {{
    width: 100%;
    padding: 12px;
    margin: 10px 0;
    border-radius: 10px;
    border: none;
}}

button {{
    padding: 14px 30px;
    border-radius: 20px;
    background: var(--accent);
    border: none;
    cursor: pointer;
    transition: transform 0.3s;
}}

button:hover {{
    transform: scale(1.1);
}}

.success {{
    color: var(--accent);
    font-size: 22px;
    opacity: 1;
    animation: flicker 1.5s infinite, fadeOut 3s ease-in 0.5s forwards;
}}

@keyframes flicker {{
    0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {{ opacity: 1; }}
    20%, 22%, 24%, 55% {{ opacity: 0.4; }}
}}

@keyframes fadeOut {{
    0% {{ opacity: 1; }}
    100% {{ opacity: 0; }}
}}

#form-wrapper.fade-out {{
    opacity: 0;
    transition: opacity 2s ease-in-out;
}}
</style>
</head>

<body class="{theme}">
<div class="text-box">
<h1>{title}</h1>

{"<p id='success-msg' class='success'>Account created successfully!</p>" if success else ""}

{content}

<p style="color:var(--text);">{msg}</p>
</div>

<script>
// Smoothly hide form if success, then remove from DOM
const successMsg = document.getElementById("success-msg");
if(successMsg){{
    const formWrapper = document.getElementById("form-wrapper");
    if(formWrapper){{
        setTimeout(() => {{
            formWrapper.classList.add("fade-out");

            // Remove from DOM after fade completes
            setTimeout(() => {{
                formWrapper.remove();
            }}, 2000); // matches CSS transition duration
        }}, 500); // start fading after 0.5s
    }}

    // Remove success message from DOM after fade
    successMsg.addEventListener('animationend', () => {{
        successMsg.remove();
    }});
}}
</script>
</body>
</html>
""")

def signup_form():
    return """
<form method="post">
<input name="name" placeholder="Name" required>
<input name="age" type="number" placeholder="Age" required>
<input name="gender" placeholder="Gender" required>
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button>Create Account</button>
</form>
<a href="/login">Already have an account? Login</a>
"""

def login_form():
    return """
<form method="post">
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button>Login</button>
</form>
"""

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
