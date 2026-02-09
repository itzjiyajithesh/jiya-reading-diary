from flask import Flask, request, redirect, url_for, session, render_template_string
import os, sqlite3, hashlib, smtplib, uuid
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# ---------------- DATABASE ----------------
DB = "users.db"

def db():
    return sqlite3.connect(DB)

def migrate():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        avatar TEXT,
        theme TEXT DEFAULT 'dark'
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        genre TEXT,
        entry TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS reset_tokens (
        email TEXT,
        token TEXT
    )
    """)

    con.commit()
    con.close()

migrate()

# ---------------- EMAIL (UPDATED FOR OUTLOOK SMTP) ----------------
def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = os.environ["EMAIL_ADDRESS"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("smtp.office365.com", 587) as smtp:
        smtp.starttls()
        smtp.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
        smtp.send_message(msg)

# ---------------- SIGNUP ----------------
@app.route("/", methods=["GET", "POST"])
def signup():
    msg = ""
    if request.method == "POST":
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()
        try:
            con = db()
            con.execute(
                "INSERT INTO users (name,email,password) VALUES (?,?,?)",
                (request.form["name"], request.form["email"], pw)
            )
            con.commit()
            con.close()
            msg = request.form["name"]
        except:
            msg = "exists"

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
body { background:url('/static/Book2.png'); font-family:cursive; text-align:center; }
.box {
    width:900px; margin:40px auto; padding:40px;
    background:#22002A; border-radius:20px;
    border:4px solid transparent;
    animation:glow 6s infinite;
}
@keyframes glow {
    0%{border-color:#ffde59;}
    50%{border-color:#ff914d;}
    100%{border-color:#b84dff;}
}
form.fade { animation:out 1s forwards; }
@keyframes out { to{opacity:0;height:0;overflow:hidden;} }
input,button {
    width:100%; padding:15px; margin:10px;
    border-radius:12px; border:none;
}
button {
    background:#ffde59; font-size:18px; cursor:pointer;
}
a { color:#FF914D; }
.success {
    font-size:28px; color:#FF914D; animation:fade 2s;
}
@keyframes fade { from{opacity:0;} to{opacity:1;} }
</style>
</head>
<body>

<div class="box">
<h2 style="color:#FF914D">Jiya's Reading Diary</h2>

{% if not msg %}
<form method="post" id="form">
<input name="name" placeholder="Name" required>
<input name="email" type="email" placeholder="Email" required>
<input name="password" type="password" placeholder="Password" required>
<button>Let's Get Started!</button>
</form>
<a href="/login">Already have an account? Sign in</a>

{% elif msg == "exists" %}
<p class="success">Email already exists</p>

{% else %}
<p class="success">Welcome {{msg}}!</p>
<div>
<button onclick="location.href='/login'">Fantasy</button>
<button onclick="location.href='/login'">Romance</button>
<button onclick="location.href='/login'">Mystery</button>
<button onclick="location.href='/login'">Sci-Fi</button>
</div>
<script>
document.getElementById("form")?.classList.add("fade");
</script>
{% endif %}

<p style="color:#FF914D; font-size:22px;"><b><i>Happy Reading!</i></b></p>
</div>

</body>
</html>
""", msg=msg)

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()
        con = db()
        cur = con.cursor()
        cur.execute(
            "SELECT id FROM users WHERE email=? AND password=?",
            (request.form["email"], pw)
        )
        user = cur.fetchone()
        con.close()

        if user:
            session["user"] = user[0]
            return redirect("/dashboard")
        msg = "Invalid login"

    return render_template_string("""
<body style="background:#22002A;color:#FF914D;text-align:center;font-family:cursive;">
<h2>Login</h2>
<form method="post">
<input name="email" placeholder="Email"><br>
<input name="password" type="password" placeholder="Password"><br>
<button>Login</button>
</form>
<a href="/reset">Forgot password?</a>
<p>{{msg}}</p>
</body>
""", msg=msg)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template_string("""
<body style="display:flex;font-family:cursive;">
<div style="width:200px;background:#33003D;color:#FF914D;padding:20px;">
<a href="/profile">Profile</a><br><br>
<a href="/diary">Write Diary</a><br><br>
<a href="/logout">Logout</a>
</div>
<div style="flex:1;padding:40px;">
<h2>Welcome to your Reading Diary</h2>
</div>
</body>
""")

# ---------------- DIARY ----------------
@app.route("/diary", methods=["GET", "POST"])
def diary():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        con = db()
        con.execute(
            "INSERT INTO diary (user_id, genre, entry) VALUES (?, ?, ?)",
            (session["user"], request.form["genre"], request.form["entry"])
        )
        con.commit()
        con.close()

    return render_template_string("""
<body style="background:#22002A;color:#FF914D;font-family:cursive;text-align:center;">
<h2>Write Diary Entry</h2>
<form method="post">
<select name="genre">
<option>Fantasy</option>
<option>Romance</option>
<option>Mystery</option>
<option>Sci-Fi</option>
</select><br><br>
<textarea name="entry" rows="6" cols="50"></textarea><br><br>
<button>Save</button>
</form>
</body>
""")

# ---------------- PASSWORD RESET ----------------
@app.route("/reset", methods=["GET", "POST"])
def reset():
    if request.method == "POST":
        token = str(uuid.uuid4())
        con = db()
        con.execute(
            "INSERT INTO reset_tokens (email, token) VALUES (?, ?)",
            (request.form["email"], token)
        )
        con.commit()
        con.close()

        send_email(
            request.form["email"],
            "Password Reset",
            f"Use this token to reset your password:\n\n{token}"
        )

        return "<p style='color:#FF914D'>Password reset email sent.</p>"

    return """
<body style="background:#22002A;color:#FF914D;text-align:center;font-family:cursive;">
<h2>Password Reset</h2>
<form method="post">
<input name="email" placeholder="Your email">
<button>Send reset email</button>
</form>
</body>
"""

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
