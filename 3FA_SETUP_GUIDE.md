# Digital Facial Recognition Attendance System - 3FA Authentication Setup

## Overview

This system now includes a **Three-Factor Authentication (3FA)** system with:

1. **Username & Password** verification
2. **Email OTP** (One-Time Password)
3. **Facial Recognition** verification

All user data is securely stored in **PostgreSQL** with encrypted passwords and session management.

---

## Prerequisites

- Python 3.8+
- PostgreSQL 12+ installed and running
- All packages in `requirements.txt`

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure PostgreSQL

Create a database for the system:

```bash
createdb facial_attendance_db
```

Or using psql:

```sql
CREATE DATABASE facial_attendance_db;
```

### Step 3: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/facial_attendance_db

# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True

# Email Configuration (for OTP delivery)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# JWT Configuration
JWT_EXPIRATION_HOURS=24
SESSION_TIMEOUT_MINUTES=30
```

#### Generating App Password (Gmail):

1. Enable 2FA on your Gmail account
2. Go to myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password and paste it in `SMTP_PASSWORD`

### Step 4: Initialize Database

```bash
python -c "from database import db; db.init_db(); print('Database initialized!')"
```

### Step 5: Run the Application

Choose which version to run:

**With Authentication (3FA):**

```bash
python app_auth.py
```

**Original Version (without auth):**

```bash
python app.py
```

---

## API Endpoints

### Authentication Endpoints

#### 1. Register New User

**POST** `/api/auth/register`

Request:

```json
{
  "full_name": "John Doe",
  "username": "johndoe",
  "email": "john@example.com",
  "phone_number": "+1234567890",
  "password": "SecurePass123!",
  "facial_image": "base64_encoded_image_data"
}
```

Response:

```json
{
  "user_id": 1,
  "message": "User created successfully"
}
```

#### 2. Step 1 - Username & Password

**POST** `/api/auth/step1`

Request:

```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

Response:

```json
{
  "user_id": 1,
  "message": "OTP sent to your email"
}
```

#### 3. Step 2 - Email OTP

**POST** `/api/auth/step2`

Request:

```json
{
  "user_id": 1,
  "otp_code": "123456"
}
```

Response:

```json
{
  "message": "OTP verified",
  "user_id": 1
}
```

#### 4. Step 3 - Facial Recognition

**POST** `/api/auth/step3`

Request: (Form-data with image file)

- `user_id`: 1
- `image`: [image file]

Response:

```json
{
  "message": "Authentication successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": 1,
  "user": { "id": 1 }
}
```

#### 5. Logout

**POST** `/api/auth/logout`

Headers:

```
Authorization: Bearer <jwt_token>
```

Response:

```json
{
  "message": "Logged out successfully"
}
```

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  full_name VARCHAR(200) NOT NULL,
  role VARCHAR(50) DEFAULT 'admin',
  is_2fa_enabled BOOLEAN DEFAULT FALSE,
  otp_secret VARCHAR(255),
  facial_embedding BYTEA,
  facial_data_json JSON,
  phone_number VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
)
```

### Sessions Table

```sql
CREATE TABLE sessions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  session_token VARCHAR(500) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  ip_address VARCHAR(45),
  user_agent TEXT
)
```

### Login History Table

```sql
CREATE TABLE login_history (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  username VARCHAR(100),
  login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  authentication_method VARCHAR(50),
  ip_address VARCHAR(45),
  success BOOLEAN DEFAULT TRUE,
  notes TEXT
)
```

---

## Usage

### User Registration Flow

1. Navigate to `http://localhost:5000/register`
2. Fill in your information:
   - Full Name
   - Username
   - Email
   - Phone Number (optional)
   - Password (must contain uppercase, lowercase, number, special character)
3. Capture your facial image using the camera
4. Click "Create Account"
5. You'll be redirected to login page

### 3FA Login Flow

1. Navigate to `http://localhost:5000/login`
2. **Step 1**: Enter username and password
3. **Step 2**: Check email and enter the 6-digit OTP
4. **Step 3**: Position your face in the camera and capture it
5. Upon successful authentication, you'll be redirected to dashboard

---

## Security Features

### Password Security

- Passwords are hashed using bcrypt
- Salt is automatically generated and included

### Session Management

- JWT tokens with expiration
- Session tracking in database
- IP address and User-Agent logging
- Automatic session invalidation on logout

### OTP Security

- 6-digit random codes
- 10-minute expiration
- Single use (marked as used after verification)
- Email delivery with SMTP

### Facial Recognition

- Embedding-based comparison
- Configurable similarity threshold (0.6 default)
- Support for different lighting conditions

### Login History

- All login attempts are logged
- Success/failure tracking
- Authentication method recorded
- IP address tracking for security audit

---

## File Structure

```
├── app_auth.py              # Main Flask app with 3FA
├── database.py              # PostgreSQL database manager
├── auth.py                  # Authentication logic
├── config.py                # Configuration settings
├── model.py                 # Facial recognition model
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── templates/
│   ├── login.html          # 3FA login interface
│   ├── register.html       # User registration
│   ├── dashboard.html      # Main dashboard
│   └── ...
└── static/
    ├── js/
    │   ├── login.js        # Login flow JS
    │   └── ...
    └── css/
        └── style.css
```

---

## Configuration Tips

### Email Configuration

For different email providers:

**Gmail:**

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=app-specific-password
```

**Outlook:**

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

**Custom Server:**

```env
SMTP_SERVER=smtp.your-domain.com
SMTP_PORT=587
SMTP_USERNAME=your-email@your-domain.com
SMTP_PASSWORD=your-password
```

---

## Troubleshooting

### "No connection to database"

- Ensure PostgreSQL is running: `sudo systemctl start postgresql`
- Check DATABASE_URL in .env
- Verify credentials

### "OTP email not received"

- Check SMTP configuration
- Verify email provider settings
- Check spam folder
- Increase SMTP_PORT to 465 for SSL

### "Facial recognition failed"

- Ensure good lighting
- Camera positioned correctly
- Adjust similarity threshold in `auth.py` (line ~140)

### "Port 5000 already in use"

```bash
python app_auth.py --port 5001
```

---

## Next Steps

1. **Create admin account** after initial setup
2. **Configure email provider** for OTP delivery
3. **Test 3FA flow** with different scenarios
4. **Review login history** for security audits
5. **Set up automated backups** for PostgreSQL
6. **Deploy to production** with HTTPS

---

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Use strong database password
- [ ] Enable PostgreSQL password authentication
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS/SSL certificates
- [ ] Enable firewall rules
- [ ] Regular security audits
- [ ] Implement rate limiting on auth endpoints
- [ ] Monitor login_history table
- [ ] Regular backups

---

## Support & Documentation

For more information:

- OpenCV Face Recognition: https://docs.opencv.org/
- Flask Documentation: https://flask.palletsprojects.com/
- PostgreSQL: https://www.postgresql.org/docs/
- PyOTP Documentation: https://pyauth.github.io/pyotp/
