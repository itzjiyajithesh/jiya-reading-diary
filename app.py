from flask import Flask, render_template_string, request, redirect, session
import sqlite3, hashlib, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------- DATABASE ----------
def db():
    return sqlite3.connect("users.db")

def init_db():
    con = db()
    con.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    con.commit()
    con.close()

init_db()

# ---------- BASE HTML ----------
BASE_HTML_START = """
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>
<style>
body{
    background:url('/static/Book2.png');
    background-size:cover;
    margin:0;
    font-family:cursive;
    color:#FF914D;
}

.glow-box{
    background:rgba(35,0,45,0.92);
    padding:45px;
    border-radius:30px;
    animation:glow 6s infinite;
}

@keyframes glow{
    0%{box-shadow:0 0 15px #ffde59;}
    50%{box-shadow:0 0 40px #ff914d;}
    100%{box-shadow:0 0 15px #b84dff;}
}

.glow-btn{
    padding:20px 55px;
    font-size:26px;
    border:none;
    border-radius:35px;
    background:#ffde59;
    cursor:pointer;
    transition:transform 0.3s, box-shadow 0.3s;
}

.glow-btn:hover{
    transform:scale(1.15);
    box-shadow:0 0 35px #ff914d;
}

input, textarea{
    width:100%;
    padding:16px;
    margin:14px 0;
    border-radius:16px;
    border:2px solid transparent;
    background:#3a004d;
    color:#ffde59;
    font-size:16px;
}

input:focus, textarea:focus{
    outline:none;
    border-color:#ffde59;
    box-shadow:0 0 18px #ffde59;
}

.layout{
    display:flex;
    min-height:100vh;
}

.sidebar{
    width:250px;
    background:#22002A;
    padding:30px;
}

.sidebar a{
    display:block;
    color:#FF914D;
    text-decoration:none;
    font-size:18px;
    margin:18px 0;
}

.content{
    flex:1;
    display:flex;
    justify-content:center;
    align-items:center;
}

.genre-btn{
    margin:12px;
    padding:18px 34px;
    border:none;
    border-radius:25px;
    background:#ffde59;
    font-size:18px;
    cursor:pointer;
    transition:transform 0.3s, box-shadow 0.3s;
}

.genre-btn:hover{
    transform:scale(1.12);
    box-shadow:0 0 30px #ff914d;
}
</style>
</head>
<body>
"""

BASE_HTML_END = """
</body>
</html>
"""

# ---------- MAIN PAGE ----------
@app.route("/")
def home():
    user = session.get("user")

    if not user:
        return render_template_string(BASE_HTML_START + """
<div style="max-width:900px;margin:90px auto;text-align:center;" class="glow-box">
    <img src="/static/J.png" width="300"><br><br>
    <h2>Welcome to Jiya’s Reading Diary</h2>
    <p>
        A curated reading space designed for thoughtful readers.<br><br>
        Discover genres, explore reviews, and immerse yourself in stories.<br><br>
        Founded by Jiya, for readers who love imagination and reflection.
    </p><br><br>
    <button class="glow-btn" onclick="location.href='/signup'">
        Let’s Get Started!
    </button>
</div>
""" + BASE_HTML_END)

    return render_template_string(BASE_HTML_START + """
<div class="layout">
    <div class="sidebar">
        <a href="/profile">👤 Profile</a>
        <a href="/genres">📚 Genres</a>
        <a href="/story">✍ Make Your Own Story</a>
        <a href="/settings">⚙ Settings</a>
        <a href="/logout">🚪 Logout</a>
    </div>

    <div class="content">
        <div class="glow-box" style="max-width:850px;text-align:center;">
            <img src="/static/J.png" width="300"><br><br>
            <h2>Account successfully created!</h2>
            <h3>Welcome {{user}}!</h3><br><br>

            <button class="genre-btn" onclick="location.href='/genre/Fantasy'">Fantasy</button>
            <button class="genre-btn" onclick="location.href='/genre/Romance'">Romance</button>
            <button class="genre-btn" onclick="location.href='/genre/Mystery'">Mystery</button>
            <button class="genre-btn" onclick="location.href='/genre/Sci-Fi'">Sci-Fi</button>
        </div>
    </div>
</div>
""" + BASE_HTML_END, user=user)

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        pw = hashlib.sha256(request.form["password"].encode()).hexdigest()
        con = db()
        con.execute(
            "INSERT INTO users (name,email,password) VALUES (?,?,?)",
            (request.form["name"], request.form["email"], pw)
        )
        con.commit()
        con.close()
        session["user"] = request.form["name"]
        return redirect("/")

    return render_template_string(BASE_HTML_START + """
<div style="max-width:520px;margin:90px auto;" class="glow-box">
    <h2>Create an Account</h2>
    <form method="post">
        <input name="name" placeholder="Name" required>
        <input name="email" type="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <br>
        <button class="glow-btn">Submit</button>
    </form>
    <p style="margin-top:18px;">
        If you already have an account, <a href="/">Sign In</a>
    </p>
</div>
""" + BASE_HTML_END)

# ---------- GENRE PAGE ----------
@app.route("/genre/<genre>")
def genre(genre):
    return render_template_string(BASE_HTML_START + f"""
<div style="max-width:900px;margin:90px auto;" class="glow-box">
    <h1>{genre}</h1>
    <p>Curated book reviews will appear here.</p>
</div>
""" + BASE_HTML_END)

# ---------- STORY PAGE ----------
@app.route("/story")
def story():
    return render_template_string(BASE_HTML_START + """
<div style="max-width:900px;margin:90px auto;" class="glow-box">
    <h1>Make Your Own Story</h1>
    <textarea placeholder="Begin your story here..."></textarea>
</div>
""" + BASE_HTML_END)

@app.route("/profile")
def profile():
    return "Profile page coming soon"

@app.route("/settings")
def settings():
    return "Settings page coming soon"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
