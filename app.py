from flask import Flask, render_template_string, request
import sqlite3
import os

app = Flask(__name__)
DATABASE = "users.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():
    user_created = False
    user_name = ""

    if request.method == "POST":
        name = request.form.get("name")
        age = request.form.get("age")
        gender = request.form.get("gender")
        email = request.form.get("email")

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, age, gender, email) VALUES (?, ?, ?, ?)",
                (name, age, gender, email)
            )
            conn.commit()
            user_created = True
            user_name = name
        except sqlite3.IntegrityError:
            user_created = False
        finally:
            conn.close()

    html_code = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Jiya's Reading Diary</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <style>
          body {
            background-image: url("/static/Book2.png");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            text-align: center;
          }

          @keyframes glowBorder {
            0% { border-color: #ffde59; box-shadow: 0 0 12px #ffde59; }
            33% { border-color: #ff914d; box-shadow: 0 0 20px 4px #ff914d; }
            66% { border-color: #a200ff; box-shadow: 0 0 20px 4px #a200ff; }
            100% { border-color: #ffde59; box-shadow: 0 0 12px #ffde59; }
          }

          .text-box {
            border: 3px solid #ffde59;
            padding: 45px;
            margin: 60px auto;
            background-color: #33003D;
            width: 900px;
            font-family: cursive;
            border-radius: 10px;
            animation: glowBorder 4.5s infinite ease-in-out;
          }

          .logo {
            margin-bottom: 20px;
            max-width: 100%;
            height: auto;
          }

          p {
            color: #FF914D;
            font-size: 22px;
            text-align: left;
          }

          .form-group {
            margin: 15px 0;
            text-align: left;
          }

          label {
            color: #ffde59;
            font-size: 18px;
          }

          input, select {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            border-radius: 8px;
            border: none;
            font-size: 16px;
          }

          .glow-button {
            margin-top: 25px;
            padding: 15px 30px;
            font-size: 20px;
            font-family: cursive;
            color: #33003D;
            background-color: #ffde59;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            box-shadow: 0 0 10px #ffde59;
          }

          .success {
            margin-top: 25px;
            color: #ffde59;
            font-size: 22px;
          }
        </style>
      </head>

      <body>
        <div class="text-box">
          <img src="{{ url_for('static', filename='J.png') }}" class="logo">

          <p>
            Hello everyone and welcome to <b><i>Jiya's Reading Diary</i></b>!
            My name is Jiya and I am a passionate reader who loves books and would love to recommend some for you!
          </p>

          <br><br>

          <form method="POST">
            <div class="form-group">
              <label>Name</label>
              <input type="text" name="name" required>
            </div>

            <div class="form-group">
              <label>Age</label>
              <input type="number" name="age" required>
            </div>

            <div class="form-group">
              <label>Gender</label>
              <select name="gender" required>
                <option value="">Select</option>
                <option>Female</option>
                <option>Male</option>
                <option>Other</option>
                <option>Prefer not to say</option>
              </select>
            </div>

            <div class="form-group">
              <label>Email</label>
              <input type="email" name="email" required>
            </div>

            <button type="submit" class="glow-button">
              Let's Get Started!
            </button>
          </form>

          {% if user_created %}
            <div class="success">
              Account created successfully for {{ user_name }}!
            </div>
          {% endif %}

          <p><i><b>Happy Reading!</b></i></p>
        </div>
      </body>
    </html>
    """

    return render_template_string(
        html_code,
        user_created=user_created,
        user_name=user_name
    )


if __name__ == "__main__":
    init_db()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
