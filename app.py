from flask import Flask, render_template_string, request, redirect, session, url_for
import sqlite3, hashlib, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

# ---------------- DATABASE ----------------
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

# ---------------- STYLES (SHARED) ----------------
BASE_STYLE = """
<style>
body{
    background:url('/static/Book2.png');
    background-size:cover;
    font-family:cursive;
    color:#FF914D;
    margin:0;
}
.glow-box{
    background:rgba(30,0,40,0.9);
    border-radius:25px;
    padding:40px;
    animation:glowBorder 6s infinite;
}
@keyframes glowBorder{
    0%{box-shadow:0 0 15px #ffde59;}
    50%{box-shadow:0 0 35px #ff914d;}
    100%{box-shadow:0 0 15px #b84dff;}
}
.glow-btn{
    padding:18px 45px;
    font-size:24px;
    border:none;
    border-radius:30px;
    cursor:pointer;
    background:#ffde59;
    transition:transform 0.3s, box-shadow 0.3s;
}
.glow-btn:hover{
    transform:scale(1.1);
    box-shadow:0 0 30px #ff914d;
}
input, textarea{
    width:100%;
    padding:15px;
    margin:12px 0;
    border-radius:14px;
    border:2px solid transparent;
    background:#3a004d;
    color:#ffde59;
}
input:focus, textarea:focus{
    outline:none;
    border-color:#ffde59;
    box-shadow:0 0 15px #ffde59;
}
.sidebar{
    width:240px;
    background:#22002A;
    padding:25px;
    height:100vh;
}
.sidebar a{
    display:block;
    color:#FF914D;
    text-decoration:none;
    margin:15px 0;
    font-size:18px;
}
.center{
    padding:60px;
    flex:1;
}
.genre-btn{
    margin:12px;
    padding:16px 32px;
    border-radius:22px;
    border:none;
    background:#ffde59;
    font-size:18px;
    cursor:pointer;
    transition:transform 0.3s, box-shadow 0.3s;
}
.genre-btn:hover{
    transform:scale(1.1);
    box-shadow:0 0 25px #ff914d;
}
</style>
"""

# ---------------- MAIN PAGE ----------------
@app.route("/")
def home():
    user = session.get("user")
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>{{style}}</head>
<body>
{% if not user %}
<div style="max-width:900px;margin:80px auto;text-align:center;" class="glow-box">
    <img src="/static/J.png" width="260"><br><br>
    <h2>Welcome to Jiya’s Reading Diary</h2>
    <p>
        This is a personal reading space where stories live, genres unfold,
        and readers discover worlds through books.<br><br>
        Founded by Jiya, this app is built for thoughtful readers who love
        reflection, imagination, and storytelling.
    </p><br>
    <button class="glow-btn" onclick="location.href='/signup'">
        Let’s Get Started!
    </button>
</div>
{% else %}
<div style="display:flex;">
    <div class="sidebar">
        <a href="/profile">👤 Profile</a>
        <a href="/genres">📚 Genres</a>
        <a href="/story">✍ Make Your Own Story</a>
        <a href="/settings">⚙ Settings</a>
        <a href="/logout">🚪 Logout</a>
    </div>
    <div class="center">
        <div class="glow-box" style="max-width:800px;margin:auto;text-align:center;">
            <img src="/static/J.png" width="260"><br><br>
            <h2>Account successfully created!</h2>
            <h3>Welcome {{user}}!</h3><br>
            <button class="genre-btn" onclick="location.href='/genre/Fantasy'">Fantasy</button>
            <button class="genre-btn" onclick="location.href='/genre/Romance'">Romance</button>
            <button class="genre-btn" onclick="location.href='/genre/Mystery'">Mystery</button>
            <button class="genre-btn" onclick="location.href='/genre/Sci-Fi'">Sci-Fi</button>
        </div>
    </div>
</div>
{% endif %}
</body>
</html>
""", user=user, style=BASE_STYLE)

# ---------------- SIGNUP ----------------
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
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>{{style}}</head>
<body>
<div style="max-width:500px;margin:80px auto;" class="glow-box">
    <h2>Create an Account</h2>
    <form method="post">
        <input name="name" placeholder="Name" required>
        <input name="email" type="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <button class="glow-btn">Submit</button>
    </form>
    <p style="margin-top:15px;">
        If you already have an account,
        <a href="/">Sign In</a>
    </p>
</div>
</body>
</html>
""", style=BASE_STYLE)

# ---------------- GENRE PAGE ----------------
@app.route("/genre/<genre>")
def genre(genre):
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>{{style}}</head>
<body>
<div style="max-width:900px;margin:80px auto;" class="glow-box">
    <h1>{{genre}}</h1>
    <p>Curated book reviews will appear here for readers to explore.</p>
</div>
</body>
</html>
""", genre=genre, style=BASE_STYLE)

# ---------------- STORY PAGE ----------------
@app.route("/story")
def story():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>{{style}}</head>
<body>
<div style="max-width:900px;margin:80px auto;" class="glow-box">
    <h1>Make Your Own Story</h1>
    <textarea placeholder="Begin your story here..."></textarea>
</div>
</body>
</html>
""", style=BASE_STYLE)

# ---------------- PLACEHOLDERS ----------------
@app.route("/profile")
def profile(): return "<h2>Profile page coming soon</h2>"

@app.route("/settings")
def settings(): return "<h2>Settings page coming soon</h2>"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
