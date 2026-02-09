from flask import Flask, request, redirect, url_for, session, render_template_string
import os, hashlib, sqlite3, smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# ---------------- DATABASE ----------------
DATABASE = "users.db"

def get_db():
    return sqlite3.connect(DATABASE)

def migrate_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        email TEXT UNIQUE,
        password TEXT,
        theme TEXT DEFAULT 'dark',
        avatar TEXT,
        verified INTEGER DEFAULT 0
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS diary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        genre TEXT,
        book_title TEXT,
        cover_url TEXT,
        rating INTEGER
    )
    """)

    conn.commit()
    conn.close()

migrate_db()

# ---------------- EMAIL ----------------
def send_email(to, subject, body):
    msg = EmailMessage()
    msg["From"] = os.environ["EMAIL_ADDRESS"]
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
        smtp.send_message(msg)

# ---------------- HOME / SIGNUP ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    msg = ""

    if request.method == "POST":
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO users (name, age, gender, email, password)
            VALUES (?, ?, ?, ?, ?)
            """, (
                request.form["name"],
                request.form["age"],
                request.form["gender"],
                request.form["email"],
                password
            ))
            conn.commit()

            send_email(
                request.form["email"],
                "Verify your account",
                f"Welcome {request.form['name']}! Your account was created successfully."
            )

            msg = f"Welcome {request.form['name']}! Your account is ready 🎉"

        except:
            msg = "Email already exists."

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>

<style>
:root {
    --bg:#33003D;
    --box:#22002A;
    --text:#FF914D;
    --accent:#ffde59;
}

body {
    background-image:url("/static/Book2.png");
    font-family:cursive;
    text-align:center;
}

.text-box {
    width:900px;
    margin:40px auto;
    padding:40px;
    background:var(--box);
    border-radius:20px;
    border:4px solid transparent;
    animation: glow 6s linear infinite;
    box-shadow:0 0 30px rgba(255,145,77,.6);
}

@keyframes glow {
    0% {border-color:#ffde59;}
    33% {border-color:#ff914d;}
    66% {border-color:#b84dff;}
    100% {border-color:#ffde59;}
}

.field {
    position:relative;
    margin-bottom:25px;
}

.field input {
    width:100%;
    padding:14px;
    border-radius:12px;
    border:2px solid var(--accent);
    background:#4b005a;
    color:var(--accent);
}

.field label {
    position:absolute;
    top:50%;
    left:14px;
    transform:translateY(-50%);
    transition:.3s;
    background:var(--box);
    padding:0 6px;
    color:var(--accent);
}

.field input:focus + label,
.field input:not(:placeholder-shown) + label {
    top:-8px;
    font-size:12px;
}

button {
    background:var(--accent);
    padding:16px 40px;
    border:none;
    border-radius:20px;
    font-size:18px;
    cursor:pointer;
    animation:btnGlow 3s infinite;
    transition:.4s;
}

button:hover { transform:scale(1.1); }

@keyframes btnGlow {
    0% {box-shadow:0 0 10px #ffde59;}
    50% {box-shadow:0 0 30px #ff914d;}
    100% {box-shadow:0 0 10px #ffde59;}
}

.success {
    color:var(--text);
    font-size:26px;
    animation:fade 4s forwards;
}

@keyframes fade {
    0% {opacity:0;}
    20% {opacity:1;}
    80% {opacity:1;}
    100% {opacity:0;}
}
</style>
</head>

<body>
<div class="text-box">
<img src="/static/J.png">

<p style="color:var(--text);font-size:22px;">
Hello everyone and welcome to <b><i>Jiya's Reading Diary</i></b>!
My name is Jiya and I am a passionate reader who loves books and would love to recommend some for you!
</p>

<form method="post">
<div class="field"><input name="name" required placeholder=" "><label>Name</label></div>
<div class="field"><input type="number" name="age" required placeholder=" "><label>Age</label></div>
<div class="field"><input name="gender" required placeholder=" "><label>Gender</label></div>
<div class="field"><input type="email" name="email" required placeholder=" "><label>Email</label></div>
<div class="field"><input type="password" name="password" required placeholder=" "><label>Password</label></div>

<button>Let's Get Started!</button>
</form>

{% if msg %}
<p class="success">{{msg}}</p>
<div>
<button>Fantasy</button>
<button>Romance</button>
<button>Mystery</button>
<button>Sci-Fi</button>
<button>Adventure</button>
</div>
{% endif %}

<p style="color:var(--text);font-size:22px;"><b><i>Happy Reading!</i></b></p>
</div>
</body>
</html>
""", msg=msg)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
