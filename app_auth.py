import os
import io
import base64
import threading
import sqlite3
import datetime
import json
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    send_file,
    abort,
    session,
    redirect,
    url_for,
)
from functools import wraps
from model import train_model_background, extract_embedding_for_image, MODEL_PATH
from database import db
from auth import auth_manager

# Initialize database on first run
db.init_db()

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "attendance.db")
DATASET_DIR = os.path.join(APP_DIR, "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)

TRAIN_STATUS_FILE = os.path.join(APP_DIR, "train_status.json")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")


# ---------- Authentication Decorator ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try to get token from multiple sources
        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            token = request.args.get("token")  # From URL parameter

        if not token:
            token = session.get("token")  # From Flask session

        if not token:
            print(f"[AUTH] No token found in headers, URL, or session")
            return redirect(url_for("login_page"))

        print(f"[AUTH] Verifying token...")
        payload = auth_manager.verify_jwt_token(token)
        if not payload:
            print(f"[AUTH] Token verification failed")
            return redirect(url_for("login_page"))

        # Store user info in request context
        request.user_id = payload.get("user_id")
        request.username = payload.get("username")
        print(f"[AUTH] Token verified for user: {request.username}")
        return f(*args, **kwargs)

    return decorated_function


# ---------- Auth Routes ----------


@app.route("/login", methods=["GET"])
def login_page():
    """Render login page"""
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_page():
    """Render registration page"""
    return render_template("register.html")


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    """Register a new user"""
    try:
        # Handle both JSON and FormData
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        email = data.get("email", "").strip()
        full_name = data.get("full_name", "").strip()

        if not username or not password or not email or not full_name:
            return jsonify({"message": "All fields are required"}), 400

        if len(password) < 8:
            return jsonify({"message": "Password must be at least 8 characters"}), 400

        # Check if user already exists
        if db.get_user_by_username(username):
            return jsonify({"message": "Username already exists"}), 409

        # Register new user
        result = db.register_user(username, email, password, full_name)

        if result.get("success"):
            user_id = result.get("user_id")

            # Handle facial image if provided
            facial_image_data = data.get("facial_image", "")

            # Check for base64 data URL format (from canvas.toDataURL)
            if (
                facial_image_data
                and isinstance(facial_image_data, str)
                and facial_image_data.startswith("data:")
            ):
                try:
                    # Extract base64 data from data URL
                    # Format: "data:image/jpeg;base64,<base64data>"
                    base64_str = facial_image_data.split(",")[1]
                    facial_binary = base64.b64decode(base64_str)

                    # Use BytesIO to simulate file object for extract_embedding_for_image
                    facial_stream = io.BytesIO(facial_binary)
                    facial_embedding = extract_embedding_for_image(facial_stream)

                    # Store facial data
                    if facial_embedding is not None:
                        facial_json = json.dumps(
                            {"size": len(facial_binary), "captured": True}
                        )
                        db.update_facial_data(user_id, facial_embedding, facial_json)
                        app.logger.info(f"Facial data stored for user {user_id}")
                    else:
                        app.logger.warning(
                            f"Could not extract embedding for user {user_id}"
                        )

                except Exception as e:
                    app.logger.warning(f"Could not process facial image: {str(e)}")

            # Check for file upload format (multipart/form-data)
            elif "facial_image" in request.files:
                facial_file = request.files["facial_image"]
                if facial_file and facial_file.filename != "":
                    try:
                        facial_embedding = extract_embedding_for_image(
                            facial_file.stream
                        )
                        if facial_embedding is not None:
                            facial_json = json.dumps(
                                {"filename": facial_file.filename, "captured": True}
                            )
                            db.update_facial_data(
                                user_id, facial_embedding, facial_json
                            )
                            app.logger.info(f"Facial data stored for user {user_id}")
                        else:
                            app.logger.warning(
                                f"Could not extract embedding from file for user {user_id}"
                            )
                    except Exception as e:
                        app.logger.warning(f"Could not store facial image: {str(e)}")

            return (
                jsonify(
                    {
                        "message": "User registered successfully",
                        "user_id": user_id,
                        "next": "/login",
                    }
                ),
                201,
            )
        else:
            return jsonify({"message": result.get("error", "Registration failed")}), 400

    except Exception as e:
        app.logger.error(f"Registration error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/api/auth/step1", methods=["POST"])
def auth_step1():
    """Step 1: Verify username and password"""
    try:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        user = db.get_user_by_username(username)
        if not user:
            return jsonify({"message": "Invalid username or password"}), 401

        if not db.verify_password(user["password_hash"], password):
            db.log_login_attempt(
                user["id"],
                username,
                "password",
                request.remote_addr,
                False,
                "Invalid password",
            )
            return jsonify({"message": "Invalid username or password"}), 401

        if not user["is_active"]:
            return jsonify({"message": "Account is disabled"}), 403

        # Generate OTP and send email
        otp_code = auth_manager.generate_otp()
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        db.create_otp(user["id"], otp_code, expires_at)

        # Send OTP email
        if not auth_manager.send_otp_email(user["email"], otp_code):
            return jsonify({"message": "Failed to send OTP email"}), 500

        return (
            jsonify({"user_id": user["id"], "message": "OTP sent to your email"}),
            200,
        )

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/api/auth/step2", methods=["POST"])
def auth_step2():
    """Step 2: Verify OTP"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        otp_code = data.get("otp_code")

        if not db.verify_otp(user_id, otp_code):
            return jsonify({"message": "Invalid or expired OTP"}), 401

        db.log_login_attempt(
            user_id, None, "otp", request.remote_addr, True, "OTP verified"
        )
        return jsonify({"message": "OTP verified", "user_id": user_id}), 200

    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/api/auth/step3", methods=["POST"])
def auth_step3():
    """Step 3: Facial recognition verification"""
    try:
        user_id = request.form.get("user_id")
        print(f"\n[STEP3] Starting facial recognition for user_id: {user_id}")

        if not user_id:
            print(f"[STEP3] ERROR: User ID is missing")
            return jsonify({"message": "User ID is required"}), 400

        if "image" not in request.files:
            print(f"[STEP3] ERROR: No image provided")
            return jsonify({"message": "No image provided"}), 400

        img_file = request.files["image"]
        print(f"[STEP3] Image received: {img_file.filename}")

        user = db.get_user_by_id(user_id)  # Get user by ID
        print(f"[STEP3] User lookup result: {'Found' if user else 'Not found'}")

        if not user:
            print(f"[STEP3] ERROR: User {user_id} not found")
            return jsonify({"message": "User not found"}), 400

        # Extract facial embedding from login image
        print(f"[STEP3] Extracting facial embedding from image...")
        login_embedding = extract_embedding_for_image(img_file.stream)
        print(
            f"[STEP3] Facial embedding result: {'Success' if login_embedding is not None else 'Failed - No face detected'}"
        )

        if login_embedding is None:
            print(f"[STEP3] ERROR: No face detected in image")
            return jsonify({"message": "No face detected in image"}), 400

        # If no facial data is registered, allow login for development/testing
        if not user.get("facial_embedding"):
            print(
                f"[STEP3] INFO: No facial data registered for user {user_id}. Allowing login for testing."
            )
            # For development: allow login even without facial data
            pass
        else:
            # Get user's stored facial embedding and compare
            import numpy as np

            stored_embedding = np.frombuffer(user["facial_embedding"], dtype=np.float32)
            similarity = np.dot(login_embedding, stored_embedding) / (
                np.linalg.norm(login_embedding) * np.linalg.norm(stored_embedding)
            )

            if similarity < 0.6:  # Adjust threshold as needed
                print(f"[STEP3] ERROR: Facial similarity too low: {similarity:.3f}")
                return (
                    jsonify(
                        {"message": "Facial recognition failed - face does not match"}
                    ),
                    401,
                )

            print(
                f"[STEP3] SUCCESS: Facial recognition verified. Similarity: {similarity:.3f}"
            )

        # Generate session token and JWT
        print(f"[STEP3] Generating JWT token...")
        session_token = auth_manager.generate_session_token()
        token = auth_manager.create_jwt_token(user_id, user["username"])
        print(f"[STEP3] Token generated successfully")

        # Create session in database
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        db.create_session(
            user_id,
            session_token,
            expires_at,
            request.remote_addr,
            request.headers.get("User-Agent"),
        )

        # Record successful login
        db.log_login_attempt(
            user_id,
            user["username"],
            "facial_recognition",
            request.remote_addr,
            True,
            "Facial recognition verified",
        )

        print(
            f"[STEP3] SUCCESS: User {user_id} ({user['username']}) logged in successfully"
        )

        return (
            jsonify(
                {
                    "message": "Authentication successful",
                    "token": token,
                    "user_id": user_id,
                    "user": {"id": user_id, "username": user["username"]},
                }
            ),
            200,
        )

    except Exception as e:
        print(f"[STEP3] EXCEPTION: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return jsonify({"message": f"Error: {str(e)}"}), 500


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """Logout user"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if token:
            auth_manager.invalidate_session(token)

        session.clear()
        return redirect(url_for("login_page"))
    except Exception as e:
        return jsonify({"message": f"Logout error: {str(e)}"}), 500


# ---------- Dashboard Routes ----------


@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard"""
    return render_template("dashboard.html")


@app.route("/api/user/profile")
@login_required
def get_user_profile():
    """Get logged-in user profile"""
    try:
        user = db.get_user_by_username(request.username)
        return (
            jsonify(
                {
                    "id": user["id"],
                    "username": user["username"],
                    "full_name": user["full_name"],
                    "email": user["email"],
                    "role": user["role"],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500


# ---------- Existing Attendance Routes (Keep from original app.py) ----------


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attendance_stats")
def attendance_stats():
    import pandas as pd

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT timestamp FROM attendance", conn)
    conn.close()
    if df.empty:
        from datetime import date, timedelta

        days = [
            (date.today() - datetime.timedelta(days=i)).strftime("%d-%b")
            for i in range(29, -1, -1)
        ]
        return jsonify({"dates": days, "counts": [0] * 30})
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date
    last_30 = [
        (datetime.date.today() - datetime.timedelta(days=i)) for i in range(29, -1, -1)
    ]
    counts = [int(df[df["date"] == d].shape[0]) for d in last_30]
    dates = [d.strftime("%d-%b") for d in last_30]
    return jsonify({"dates": dates, "counts": counts})


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method == "GET":
        return render_template("add_student.html")
    data = request.form
    name = data.get("name", "").strip()
    roll = data.get("roll", "").strip()
    cls = data.get("class", "").strip()
    sec = data.get("sec", "").strip()
    reg_no = data.get("reg_no", "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO students (name, roll, class, section, reg_no, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, roll, cls, sec, reg_no, now),
    )
    sid = c.lastrowid
    conn.commit()
    conn.close()
    os.makedirs(os.path.join(DATASET_DIR, str(sid)), exist_ok=True)
    return jsonify({"student_id": sid})


@app.route("/upload_face", methods=["POST"])
def upload_face():
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"error": "student_id required"}), 400
    files = request.files.getlist("images[]")
    saved = 0
    folder = os.path.join(DATASET_DIR, student_id)
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
    for f in files:
        try:
            fname = f"{datetime.datetime.utcnow().timestamp():.6f}_{saved}.jpg"
            path = os.path.join(folder, fname)
            f.save(path)
            saved += 1
        except Exception as e:
            app.logger.error("save error: %s", e)
    return jsonify({"saved": saved})


@app.route("/train_model", methods=["GET"])
def train_model_route():
    status = (
        auth_manager.read_train_status()
        if hasattr(auth_manager, "read_train_status")
        else {"running": False}
    )
    if status.get("running"):
        return jsonify({"status": "already_running"}), 202

    student_dirs = [
        d
        for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    ]
    students_with_images = 0
    for sid in student_dirs:
        folder = os.path.join(DATASET_DIR, sid)
        files = [
            f
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if len(files) > 0:
            students_with_images += 1

    if students_with_images == 0:
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "No student images found. Please add students and capture their photos first.",
                }
            ),
            400,
        )

    def progress_callback(p, m):
        write_train_status({"running": True, "progress": p, "message": m})

    write_train_status({"running": True, "progress": 0, "message": "Starting training"})
    t = threading.Thread(
        target=train_model_background, args=(DATASET_DIR, progress_callback)
    )
    t.daemon = True
    t.start()
    return (
        jsonify(
            {
                "status": "started",
                "message": f"Training started with {students_with_images} students",
            }
        ),
        202,
    )


@app.route("/train_status", methods=["GET"])
def train_status():
    return jsonify(read_train_status())


@app.route("/mark_attendance", methods=["GET"])
def mark_attendance_page():
    return render_template("mark_attendance.html")


@app.route("/recognize_face", methods=["POST"])
def recognize_face():
    if "image" not in request.files:
        return jsonify({"recognized": False, "error": "no image"}), 400
    img_file = request.files["image"]
    try:
        emb = extract_embedding_for_image(img_file.stream)
        if emb is None:
            return jsonify({"recognized": False, "error": "no face detected"}), 200
        from model import load_model_if_exists, predict_with_model

        clf = load_model_if_exists()
        if clf is None:
            return jsonify({"recognized": False, "error": "model not trained"}), 200
        pred_label, conf = predict_with_model(clf, emb)
        if conf < 0.5:
            return jsonify({"recognized": False, "confidence": float(conf)}), 200
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM students WHERE id=?", (int(pred_label),))
        row = c.fetchone()
        name = row[0] if row else "Unknown"
        ts = datetime.datetime.utcnow().isoformat()
        c.execute(
            "INSERT INTO attendance (student_id, name, timestamp) VALUES (?, ?, ?)",
            (int(pred_label), name, ts),
        )
        conn.commit()
        conn.close()
        return (
            jsonify(
                {
                    "recognized": True,
                    "student_id": int(pred_label),
                    "name": name,
                    "confidence": float(conf),
                }
            ),
            200,
        )
    except Exception as e:
        app.logger.exception("recognize error")
        return jsonify({"recognized": False, "error": str(e)}), 500


@app.route("/attendance_record", methods=["GET"])
def attendance_record():
    period = request.args.get("period", "all")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    q = "SELECT id, student_id, name, timestamp FROM attendance"
    params = ()
    if period == "daily":
        today = datetime.date.today().isoformat()
        q += " WHERE date(timestamp) = ?"
        params = (today,)
    elif period == "weekly":
        start = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
        q += " WHERE date(timestamp) >= ?"
        params = (start,)
    elif period == "monthly":
        start = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
        q += " WHERE date(timestamp) >= ?"
        params = (start,)
    q += " ORDER BY timestamp DESC LIMIT 5000"
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    return render_template("attendance_record.html", records=rows, period=period)


@app.route("/download_csv", methods=["GET"])
def download_csv():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, student_id, name, timestamp FROM attendance ORDER BY timestamp DESC"
    )
    rows = c.fetchall()
    conn.close()
    output = io.StringIO()
    output.write("id,student_id,name,timestamp\n")
    for r in rows:
        output.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(
        mem, as_attachment=True, download_name="attendance.csv", mimetype="text/csv"
    )


@app.route("/students", methods=["GET"])
def students_list():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, name, roll, class, section, reg_no, created_at FROM students ORDER BY id DESC"
    )
    rows = c.fetchall()
    conn.close()
    data = [
        {
            "id": r[0],
            "name": r[1],
            "roll": r[2],
            "class": r[3],
            "section": r[4],
            "reg_no": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]
    return jsonify({"students": data})


@app.route("/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (sid,))
    c.execute("DELETE FROM attendance WHERE student_id=?", (sid,))
    conn.commit()
    conn.close()
    folder = os.path.join(DATASET_DIR, str(sid))
    if os.path.isdir(folder):
        import shutil

        shutil.rmtree(folder, ignore_errors=True)
    return jsonify({"deleted": True})


@app.route("/debug/check_dataset", methods=["GET"])
def check_dataset():
    result = {"students_in_db": [], "dataset_folders": [], "ready_to_train": False}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name FROM students ORDER BY id")
    result["students_in_db"] = [{"id": r[0], "name": r[1]} for r in c.fetchall()]
    conn.close()
    if os.path.exists(DATASET_DIR):
        for item in os.listdir(DATASET_DIR):
            folder_path = os.path.join(DATASET_DIR, item)
            if os.path.isdir(folder_path):
                images = [
                    f
                    for f in os.listdir(folder_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ]
                result["dataset_folders"].append(
                    {"folder": item, "image_count": len(images), "images": images[:5]}
                )
    result["ready_to_train"] = any(
        f["image_count"] > 0 for f in result["dataset_folders"]
    )
    return jsonify(result)


@app.route("/cleanup_empty_students", methods=["POST"])
def cleanup_empty_students():
    student_dirs = [
        d
        for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    ]
    removed_count = 0
    for sid in student_dirs:
        folder = os.path.join(DATASET_DIR, sid)
        files = [
            f
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if len(files) == 0:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE id=?", (int(sid),))
            conn.commit()
            conn.close()
            import shutil

            shutil.rmtree(folder, ignore_errors=True)
            removed_count += 1
    return jsonify(
        {
            "cleaned_up": removed_count,
            "message": f"Removed {removed_count} empty student records",
        }
    )


# Helper functions for training status
def write_train_status(status_dict):
    with open(TRAIN_STATUS_FILE, "w") as f:
        json.dump(status_dict, f)


def read_train_status():
    if not os.path.exists(TRAIN_STATUS_FILE):
        return {"running": False, "progress": 0, "message": "Not trained"}
    with open(TRAIN_STATUS_FILE, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
