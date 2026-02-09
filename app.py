from flask import Flask, render_template_string, request, redirect, url_for, session
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

# ---------- MAIN PAGE ----------
@app.route("/")
def home():
    logged_in = "user" in session
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>Jiya's Reading Diary</title>
<style>
body{
    background:url('/static/Book2.png');
    background-size:cover;
    font-family:cursive;
    text-align:center;
    color:#FF914D;
}
.container{
    margin-top:80px;
}
.glow-btn{
    padding:20px 50px;
    font-size:26px;
    border:none;
    border-radius:25px;
    cursor:pointer;
    background:#ffde59;
    animation:glow 2.5s infinite;
}
@keyframes glow{
    0%{box-shadow:0 0 10px #ffde59;}
    50%{box-shadow:0 0 30px #ff914d;}
    100%{box-shadow:0 0 10px #ffde59;}
}
.genre-btn{
    margin:10px;
    padding:15px 30px;
    border-radius:20px;
    border:none;
    background:#ffde59;
    font-size:18px;
    cursor:pointer;
}
</style>
</head>

<body>
<div class="container">
    <img src="/static/J.png" width="180"><br><br>

    {% if not logged_in %}
        <button class="glow-btn" onclick="location.href='/signup'">
            Let’s Get Started!
        </button>
    {% else %}
        <h2>Select a Genre</h2>
        <button class="genre-btn" onclick="location.href='/genre/Fantasy'">Fantasy</button>
        <button class="genre-btn" onclick="location.href='/genre/Romance'">Romance</button>
        <button class="genre-btn" onclick="location.href='/genre/Mystery'">Mystery</button>
        <button class="genre-btn" onclick="location.href='/genre/Sci-Fi'">Sci-Fi</button>
        <button class="genre-btn" onclick="location.href='/genre/Adventure'">Adventure</button>
    {% endif %}
</div>
</body>
</html>
""", logged_in=logged_in)

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
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
            session["user"] = request.form["email"]
            return redirect("/")
        except:
            pass

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
body{
    background:#22002A;
    font-family:cursive;
    text-align:center;
    color:#FF914D;
}
.box{
    width:500px;
    margin:80px auto;
    padding:40px;
    border-radius:20px;
    background:#33003D;
    animation:borderGlow 6s infinite;
}
@keyframes borderGlow{
    0%{box-shadow:0 0 15px #ffde59;}
    50%{box-shadow:0 0 30px #ff914d;}
    100%{box-shadow:0 0 15px #ffde59;}
}
input,button{
    width:100%;
    padding:14px;
    margin:10px 0;
    border-radius:12px;
    border:none;
}
button{
    background:#ffde59;
    font-size:18px;
    cursor:pointer;
}
</style>
</head>
<body>
<div class="box">
    <img src="/static/J.png" width="120"><br><br>
    <h2>Create an Account</h2>
    <form method="post">
        <input name="name" placeholder="Name" required>
        <input name="email" type="email" placeholder="Email" required>
        <input name="password" type="password" placeholder="Password" required>
        <button>Create Account</button>
    </form>
</div>
</body>
</html>
""")

# ---------- GENRE PAGE ----------
@app.route("/genre/<genre>")
def genre_page(genre):
    if "user" not in session:
        return redirect("/")
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<style>
body{
    background:#22002A;
    color:#FF914D;
    font-family:cursive;
    text-align:center;
}
.box{
    width:800px;
    margin:60px auto;
    padding:40px;
    background:#33003D;
    border-radius:20px;
}
textarea{
    width:100%;
    height:200px;
    border-radius:12px;
    padding:15px;
}
</style>
</head>
<body>
<div class="box">
    <h1>{{genre}}</h1>
    <p>Write your book review here:</p>
    <textarea placeholder="Your review..."></textarea>
</div>
</body>
</html>
""", genre=genre)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
