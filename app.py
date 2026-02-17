import json
import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

def get_personalized_banner(email: str, first_name: str) -> dict:
    """
    Industry-style banner payload your UI can render.
    Swap this logic later to call AJO/Decisioning and map the response into this format.
    """
    # Simple segments (example logic)
    if email.endswith("@demo.com") and email.startswith("admin"):
        return {
            "eyebrow": "ADMIN ACCESS",
            "title": f"Welcome back, {first_name}!",
            "subtitle": "Review system activity, manage users, and monitor site health.",
            "cta_label": "Go to Admin Dashboard",
            "cta_url": "#",
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=1200&q=60",
        }

    return {
        "eyebrow": "JUST FOR YOU",
        "title": f"Welcome back, {first_name}!",
        "subtitle": "Your personalized deals and recommendations are ready.",
        "cta_label": "Shop Recommended",
        "cta_url": "#",
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=60",
    }
def load_users() -> dict:
    """Load users from users.json. Returns dict keyed by email."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, dict) else {}


def save_users(users: dict) -> None:
    """Persist users to users.json."""
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


# Load on startup
users = load_users()

# Home Page
@app.route("/")
def index():
    return render_template("index.html")

# Login Page (renders the industry-standard login.html you shared)
@app.route("/templates/login")
def login_page():
    # If already logged in, go straight to success page
    if "user" in session:
        return redirect(url_for("success"))
    return render_template("login.html")

# Handle Login Form Submission
@app.route("/authenticate", methods=["POST"])
def authenticate():
    username = request.form.get("username", "").strip().lower()  # email input
    password = request.form.get("password", "")
    if username in users and users[username].get("password")== password:
        session["user"] = username
        remember = request.form.get("remember")
        if remember:
            session.permanent = True
            app.permanent_session_lifetime = 60 * 60 * 24 * 30  # 30 days in seconds
        return redirect(url_for("success"))
    else:
        return "Invalid credentials. Go back and try again."

# Success Page
@app.route("/success")
def success():
    if "user" in session:
        email = session["user"]
        user = users.get(email, {})
        first_name = user.get("first_name", "") or "Customer"

        banner = get_personalized_banner(email=email, first_name=first_name)

        return render_template(
            "successfullogin.html",
            username=email,
            first_name=first_name,
            banner=banner
        )
        return render_template("successfullogin.html", username=session["user"])

    return redirect(url_for("index"))

# Logout
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

# ---- Create Account routes ----
@app.route("/create-account")
def create_account_page():
    return render_template("create_account.html")


@app.route("/register", methods=["POST"])
def register():
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if not first_name or not last_name or not email:
        return render_template("create_account.html", error="Please fill in all required fields.")

    if password != confirm_password:
        return render_template("create_account.html", error="Passwords do not match.")

    global users
    users = load_users()

    if email in users:
        return render_template("create_account.html", error="An account with this email already exists.")

    # Save new user to file-backed object
    users[email] = {
        "password": password,
        "first_name": first_name,
        "last_name": last_name
    }
    save_users(users)

    # Optional: auto-login after signup
    session["user"] = email
    return redirect(url_for("success"))

if __name__ == "__main__":
    app.run(debug=True)
