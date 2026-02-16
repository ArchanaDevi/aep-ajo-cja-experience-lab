from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Demo users
users = {
    "admin": "1234",
    "jwala": "abcd"
}

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Login Page
@app.route("/login")
def login_page():
    return render_template("login.html")

# Handle Login Form Submission
@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form["username"]
    password = request.form["password"]

    if username in users and users[username] == password:
        session["user"] = username
        return redirect(url_for("success"))
    else:
        return "Invalid credentials. Go back and try again."

# Success Page
@app.route("/success")
def success():
    if "user" in session:
        return render_template("successfullogin.html", username=session["user"])
    return redirect(url_for("index"))

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
