from flask import Flask, request, jsonify, render_template_string, redirect
import os
import json
from datetime import datetime

app = Flask(__name__)

DATA_FILE = "data.json"
UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# -------------------------
# DATA
# -------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "audios": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    return render_template_string("""
    <h1>MENOTEK</h1>
    <p>Alzheimer Care System</p>
    <a href="/register">Register</a> |
    <a href="/login">Login</a>
    """)

# -------------------------
# REGISTER
# -------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = load_data()

        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        data["users"].append({
            "id": len(data["users"]) + 1,
            "email": email,
            "password": password,
            "role": role
        })

        save_data(data)
        return redirect("/login")

    return render_template_string("""
    <h2>Register</h2>
    <form method="POST">
        Email:<br><input name="email"><br><br>
        Password:<br><input name="password" type="password"><br><br>

        Role:<br>
        <select name="role">
            <option value="patient">Patient</option>
            <option value="relative">Relative</option>
        </select><br><br>

        <button type="submit">Register</button>
    </form>
    """)

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = load_data()

        email = request.form["email"]
        password = request.form["password"]

        user = next((u for u in data["users"]
                     if u["email"] == email and u["password"] == password), None)

        if not user:
            return "Invalid login"

        if user["role"] == "patient":
            return redirect(f"/patient/{user['id']}")
        else:
            return redirect(f"/relative/{user['id']}")

    return render_template_string("""
    <h2>Login</h2>
    <form method="POST">
        Email:<br><input name="email"><br><br>
        Password:<br><input name="password" type="password"><br><br>
        <button type="submit">Login</button>
    </form>
    """)

# -------------------------
# PATIENT PANEL
# -------------------------
@app.route("/patient/<int:user_id>")
def patient(user_id):
    data = load_data()

    user = next(u for u in data["users"] if u["id"] == user_id)
    audios = [a for a in data["audios"] if a["user_id"] == user_id]

    audio_html = ""
    for a in audios:
        audio_html += f"<p>🎧 {a['file']}</p>"

    return f"""
    <h1>Patient Panel</h1>
    <p>Welcome {user['email']}</p>

    <h3>Device Status</h3>
    <p>Serial: MENOTEK-DEVICE-001</p>

    <h3>Audio Records</h3>
    {audio_html if audio_html else "No recordings yet"}
    """

# -------------------------
# RELATIVE PANEL
# -------------------------
@app.route("/relative/<int:user_id>")
def relative(user_id):
    data = load_data()

    audios = data["audios"][-5:]

    audio_html = ""
    for a in audios:
        audio_html += f"<p>🎧 {a['file']}</p>"

    return f"""
    <h1>Relative Panel</h1>
    <p>User ID: {user_id}</p>

    <h3>Latest Patient Audio</h3>
    {audio_html if audio_html else "No audio yet"}
    """

# -------------------------
# AUDIO UPLOAD API
# -------------------------
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    data = load_data()

    file = request.files["file"]
    user_id = int(request.form["user_id"])

    filename = f"{datetime.now().timestamp()}_{file.filename}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    data["audios"].append({
        "user_id": user_id,
        "file": filename
    })

    # keep last 5 only
    data["audios"] = data["audios"][-5:]

    save_data(data)

    return jsonify({
        "status": "ok",
        "file": filename
    })

# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
