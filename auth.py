import jwt
import uuid
import secrets
import pyotp
import qrcode
from io import BytesIO
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from config import (
    SECRET_KEY,
    JWT_EXPIRATION_HOURS,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
)
from database import db


class AuthenticationManager:

    @staticmethod
    def generate_session_token():
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_jwt_token(user_id, username):
        """Create JWT token"""
        payload = {
            "user_id": user_id,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_jwt_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def setup_2fa(user_id):
        """Setup 2FA for user (TOTP)"""
        secret = pyotp.random_base32()
        db.update_otp_secret(user_id, secret)

        # Generate QR code
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(
            name="facial_attendance", issuer_name="Digital Attendance System"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to bytes
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format="PNG")
        img_byte_arr.seek(0)

        return secret, img_byte_arr

    @staticmethod
    def verify_2fa_totp(user_id, code):
        """Verify TOTP code"""
        user = db.get_user_by_username(None)
        if not user or not user.get("otp_secret"):
            return False

        totp = pyotp.TOTP(user["otp_secret"])
        return totp.verify(code, valid_window=1)

    @staticmethod
    def send_otp_email(email, otp_code):
        """Send OTP via email"""
        try:
            # Strip whitespace from credentials
            smtp_user = SMTP_USERNAME.strip() if SMTP_USERNAME else ""
            smtp_pass = SMTP_PASSWORD.strip() if SMTP_PASSWORD else ""

            # Debug: Print configuration
            print(f"\n{'='*60}")
            print(f"DEBUG: Sending OTP to {email}")
            print(f"DEBUG: SMTP_SERVER={SMTP_SERVER}, SMTP_PORT={SMTP_PORT}")
            print(f"DEBUG: SMTP_USERNAME={smtp_user[:20]}..." if smtp_user else "None")
            print(f"DEBUG: OTP Code: {otp_code}")
            print(f"{'='*60}\n")

            # Check if SMTP credentials are configured (skip if dev mode)
            if (
                smtp_user == "your-email@gmail.com"
                or smtp_pass == "your-app-password"
                or not smtp_user
                or not smtp_pass
            ):
                # Development mode: log OTP to console only
                print(f"INFO: Running in development mode (SMTP not fully configured)")
                print(f"✓ OTP Code for {email}: {otp_code}")
                return True

            subject = "Your OTP Code - Digital Attendance System"
            body = f"""Your One-Time Password (OTP) is: {otp_code}

This code will expire in 10 minutes.
Do not share this code with anyone.

If you didn't request this code, please ignore this email."""

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = email

            print(f"DEBUG: Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
                print(f"DEBUG: Starting TLS...")
                server.starttls()
                print(f"DEBUG: Logging in with user: {smtp_user}...")
                server.login(smtp_user, smtp_pass)
                print(f"DEBUG: Sending message...")
                server.send_message(msg)
                print(f"✓ Message sent successfully to {email}!")

            return True
        except smtplib.SMTPAuthenticationError as e:
            print(f"\n⚠ WARNING: Gmail authentication failed!")
            print(f"Error: {e}")
            print(f"\nPossible solutions:")
            print(
                f"1. Verify your app password is correct (no spaces in the actual password)"
            )
            print(
                f"2. If using Gmail, enable 'Less secure app access' or use an App Password"
            )
            print(f"3. For testing, you can see the OTP code above in console output")
            print(f"   OTP for {email}: {otp_code}\n")
            # Return True to allow testing with console OTP
            return True
        except Exception as e:
            print(f"ERROR: Failed to send OTP email: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()
            # Return True to allow testing with console OTP
            return True

    @staticmethod
    def generate_otp():
        """Generate a random 6-digit OTP"""
        import random

        return str(random.randint(100000, 999999))


auth_manager = AuthenticationManager()
