import sqlite3
import os
from datetime import datetime
import bcrypt
import json

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "facial_attendance.db")


class DatabaseManager:
    def __init__(self):
        self.db_path = DB_PATH

    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                is_2fa_enabled BOOLEAN DEFAULT FALSE,
                otp_secret TEXT,
                facial_embedding BLOB,
                facial_data_json TEXT,
                phone_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """
        )

        # Login history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                authentication_method TEXT,
                ip_address TEXT,
                success BOOLEAN DEFAULT TRUE,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # OTP attempts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS otp_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                otp_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                used BOOLEAN DEFAULT FALSE,
                attempts INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # Sessions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        # Students table (for attendance)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll TEXT,
                class TEXT,
                section TEXT,
                reg_no TEXT UNIQUE,
                facial_embedding BLOB,
                facial_data_json TEXT,
                phone_number TEXT,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """
        )

        # Attendance records table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                attendance_date DATE NOT NULL,
                attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'present',
                confidence FLOAT,
                marked_by INTEGER,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (marked_by) REFERENCES users(id)
            )
        """
        )

        # Audit logs table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def register_user(self, username, email, password, full_name):
        """Register a new user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        try:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, full_name, is_active)
                VALUES (?, ?, ?, ?, TRUE)
                """,
                (username, email, password_hash, full_name),
            )
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {"success": True, "user_id": user_id}
        except sqlite3.IntegrityError as e:
            conn.close()
            return {"success": False, "error": str(e)}

    def get_user_by_username(self, username):
        """Get user by username"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def verify_password(self, stored_hash, password):
        """Verify password against hash"""
        try:
            # stored_hash should be bytes or utf-8 string
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode("utf-8")
            return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
        except Exception as e:
            print(f"Password verification error: {str(e)}")
            return False

    def update_facial_data(self, user_id, facial_embedding, facial_data_json):
        """Update user's facial data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users 
            SET facial_embedding = ?, facial_data_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (facial_embedding, facial_data_json, user_id),
        )
        conn.commit()
        conn.close()

    def create_session(
        self, user_id, session_token, expires_at, ip_address, user_agent
    ):
        """Create a new session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO sessions (user_id, session_token, expires_at, is_active, ip_address, user_agent)
            VALUES (?, ?, ?, TRUE, ?, ?)
            """,
            (user_id, session_token, expires_at, ip_address, user_agent),
        )
        conn.commit()
        conn.close()

    def get_session(self, session_token):
        """Get session by token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM sessions 
            WHERE session_token = ? AND is_active = TRUE AND expires_at > datetime('now')
            """,
            (session_token,),
        )
        session = cursor.fetchone()
        conn.close()
        return dict(session) if session else None

    def invalidate_session(self, session_token):
        """Invalidate a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE sessions SET is_active = FALSE WHERE session_token = ?",
            (session_token,),
        )
        conn.commit()
        conn.close()

    def log_login_attempt(
        self, user_id, username, authentication_method, ip_address, success, notes=""
    ):
        """Log a login attempt"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO login_history (user_id, username, authentication_method, ip_address, success, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, username, authentication_method, ip_address, success, notes),
        )
        conn.commit()
        conn.close()

    def create_otp(self, user_id, otp_code, expires_at):
        """Create an OTP record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO otp_attempts (user_id, otp_code, expires_at, used, attempts)
            VALUES (?, ?, ?, FALSE, 0)
            """,
            (user_id, otp_code, expires_at),
        )
        conn.commit()
        conn.close()

    def verify_otp(self, user_id, otp_code):
        """Verify OTP code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM otp_attempts 
            WHERE user_id = ? AND otp_code = ? AND used = FALSE 
            AND expires_at > datetime('now')
            ORDER BY created_at DESC LIMIT 1
            """,
            (user_id, otp_code),
        )
        otp = cursor.fetchone()

        if otp:
            # Mark as used
            cursor.execute(
                "UPDATE otp_attempts SET used = TRUE WHERE id = ?", (otp["id"],)
            )
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def add_audit_log(self, user_id, action, resource_type, resource_id, details=""):
        """Add an audit log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, action, resource_type, resource_id, details),
        )
        conn.commit()
        conn.close()

    def get_all_students(self):
        """Get all active students"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE is_active = TRUE ORDER BY name")
        students = cursor.fetchall()
        conn.close()
        return [dict(s) for s in students]

    def get_student_by_id(self, student_id):
        """Get student by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        conn.close()
        return dict(student) if student else None

    def add_attendance_record(
        self, student_id, status, confidence, marked_by, notes=""
    ):
        """Add attendance record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO attendance (student_id, attendance_date, status, confidence, marked_by, notes)
            VALUES (?, date('now'), ?, ?, ?, ?)
            """,
            (student_id, status, confidence, marked_by, notes),
        )
        conn.commit()
        conn.close()

    def close(self):
        """Close database connection"""
        pass


# Global database manager instance
db = DatabaseManager()
