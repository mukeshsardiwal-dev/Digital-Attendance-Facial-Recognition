# 📖 Complete Implementation Guide - 3FA Authentication System

## 🎯 System Overview

This document provides a complete overview of the **Three-Factor Authentication (3FA)** system integrated with your Digital Facial Recognition Attendance System.

**Key Technology Stack:**

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Authentication**: JWT + Bcrypt + OTP + Facial Recognition
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **Security**: HTTPS-ready, CORS support, rate limiting ready

---

## 📊 System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         User Interface                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Register → Login (3FA) → Dashboard → Logout               │  │
│  │  HTML5 Forms | Bootstrap UI | Real-time Validation        │  │
│  └──────────────────────────────────────────────────────────────┘  │
└──────────┬────────────────────────────────────────┬─────────────────┘
           │ HTTPS/REST API                         │
           ↓                                        ↓
┌──────────────────────────────────────┐  ┌────────────────────┐
│      Flask Application               │  │  Static Assets     │
│  ┌────────────────────────────────┐  │  │  CSS/JS/Images     │
│  │  Authentication Endpoints:     │  │  └────────────────────┘
│  │  - /register                   │  │
│  │  - /login                      │  │
│  │  - /api/auth/step1-3           │  │
│  │  - /logout                     │  │
│  │  - /dashboard                  │  │
│  │  - /api/user/profile           │  │
│  └────────────────────────────────┘  │
│  ┌────────────────────────────────┐  │
│  │  Middleware/Decorators:        │  │
│  │  - @login_required             │  │
│  │  - JWT Token Verification      │  │
│  │  - CORS Headers                │  │
│  └────────────────────────────────┘  │
└────────┬──────────┬──────────┬────────┘
         │          │          │
         ↓          ↓          ↓
    ┌────────┐ ┌────────┐ ┌──────────────┐
    │Database│ │ Email  │ │ Face Model   │
    │PostgreSQL SMTP   │ OpenCV Embedding
    │        │ │Gmail   │ │ Comparison   │
    └────────┘ └────────┘ └──────────────┘
```

---

## 🔐 Authentication Flow Diagram

### Registration Flow

```
┌─────────────────┐
│  Visit /register│
└────────┬────────┘
         ↓
┌─────────────────────────────────────┐
│  User enters:                       │
│  - Full Name                        │
│  - Username                         │
│  - Email                            │
│  - Password (strength validation)   │
│  - Phone (optional)                 │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Facial Registration:               │
│  - Capture photo from webcam        │
│  - Extract facial embedding         │
│  - Store for verification           │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  POST /api/auth/register            │
│  Send: All user data + facial image │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Server Processing:                 │
│  1. Validate inputs                 │
│  2. Hash password (bcrypt)          │
│  3. Extract facial embedding        │
│  4. Store in PostgreSQL             │
│  5. Generate confirmation email     │
└────────┬────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Account Created Successfully!      │
│  Redirect to Login                  │
└─────────────────────────────────────┘
```

### 3FA Login Flow

```
┌──────────────────┐
│  Visit /login    │
└────────┬─────────┘
         ↓
    ╔═════════════════════════════════════════════╗
    ║            STEP 1: Credentials             ║
    ╚════════════════╤════════════════════════════╝
         ↓
┌──────────────────────────────┐
│ User enters:                 │
│ - Username                   │
│ - Password                   │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ Server:                      │
│ 1. Query user from DB        │
│ 2. Verify password (bcrypt)  │
│ 3. Check account is active   │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ ✅ Step 1 Passed             │
│ ✉️ Generate OTP              │
│ 📧 Send via email            │
└────────┬─────────────────────┘
         ↓
    ╔═════════════════════════════════════════════╗
    ║           STEP 2: Email OTP                ║
    ╚════════════════╤════════════════════════════╝
         ↓
┌──────────────────────────────┐
│ User receives email with:    │
│ 6-digit OTP code             │
│ 10-minute expiration         │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ User enters OTP code         │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ Server:                      │
│ 1. Query OTP from DB         │
│ 2. Check not expired         │
│ 3. Check not already used    │
│ 4. Verify code matches       │
│ 5. Mark OTP as used          │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ ✅ Step 2 Passed             │
│ 📷 Ready for facial recog.   │
└────────┬─────────────────────┘
         ↓
    ╔═════════════════════════════════════════════╗
    ║     STEP 3: Facial Recognition            ║
    ╚════════════════╤════════════════════════════╝
         ↓
┌──────────────────────────────┐
│ Browser:                     │
│ 1. Request camera access     │
│ 2. Display video stream      │
│ 3. User positions face       │
│ 4. Capture image             │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ Server:                      │
│ 1. Extract embedding         │
│ 2. Load stored embedding     │
│ 3. Calculate similarity      │
│ 4. Compare with threshold    │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ ✅ All 3 Factors Verified!   │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ Generate:                    │
│ - JWT Token (24h exp)        │
│ - Session in DB              │
│ - Record login attempt       │
└────────┬─────────────────────┘
         ↓
┌──────────────────────────────┐
│ Return JWT to client         │
│ Redirect to /dashboard       │
└──────────────────────────────┘
```

---

## 🗂️ File Descriptions

### Backend Files

#### `app_auth.py`

**Main Flask application with authentication**

Key Features:

- 3FA authentication endpoints
- Login/logout functionality
- Dashboard route with JWT protection
- Attendance endpoints
- Model training endpoints
- Debug endpoints

Key Routes:

```python
@app.route('/login', methods=['GET'])                    # Login page
@app.route('/api/auth/step1', methods=['POST'])         # Password verify
@app.route('/api/auth/step2', methods=['POST'])         # OTP verify
@app.route('/api/auth/step3', methods=['POST'])         # Facial verify
@app.route('/logout', methods=['POST'])                 # Logout
@app.route('/dashboard')                                # Protected dashboard
@app.route('/api/user/profile')                         # User profile
```

#### `database.py`

**PostgreSQL database management layer**

Classes:

- `DatabaseManager`: Main database interface

Key Methods:

```python
init_db()                          # Create all tables
create_user()                      # Register new user
get_user_by_username()            # Query user
verify_password()                 # Check password
create_session()                  # Create session
verify_otp()                      # Validate OTP
record_login_attempt()            # Log login
```

#### `auth.py`

**Authentication utilities and helpers**

Classes:

- `AuthenticationManager`: Authentication logic

Key Methods:

```python
generate_session_token()          # Secure token generation
create_jwt_token()                # Create JWT
verify_jwt_token()                # Verify JWT
setup_2fa()                       # Setup TOTP (future)
verify_2fa_totp()                 # Verify TOTP
send_otp_email()                  # Send OTP via SMTP
generate_otp()                    # Generate 6-digit code
```

#### `config.py`

**Configuration management**

Configuration Variables:

```python
DATABASE_URL              # PostgreSQL connection string
SECRET_KEY               # Flask secret key
DEBUG                    # Debug mode
SMTP_SERVER             # Email server
SMTP_PORT               # Email port
SMTP_USERNAME           # Email username
SMTP_PASSWORD           # Email password
JWT_EXPIRATION_HOURS    # Token expiration
SESSION_TIMEOUT_MINUTES # Session timeout
```

#### `model.py`

**Facial recognition model (existing)**

Functions:

- `crop_face_and_embed()`: Extract facial embedding
- `extract_embedding_for_image()`: Get embedding from image
- `load_model_if_exists()`: Load trained model
- `predict_with_model()`: Recognize face
- `train_model_background()`: Train recognition model

### Frontend Files

#### `templates/login.html`

**3FA login interface**

Features:

- Multi-step form with progress indicators
- Step 1: Username & Password
- Step 2: OTP input (6 fields with auto-focus)
- Step 3: Facial recognition with video
- Responsive design
- Real-time validation

#### `templates/register.html`

**User registration page**

Features:

- Form validation
- Real-time password strength checking
- Requirements indicator
- Facial capture with preview
- Success/error messages

#### `templates/dashboard.html`

**Main authenticated dashboard**

Features:

- User profile display
- Statistics cards (attendance, students, etc.)
- Attendance chart (Chart.js)
- Quick action buttons
- Navigation sidebar
- Profile dropdown menu
- Logout functionality

#### `static/js/login.js`

**Login flow JavaScript**

Key Functions:

```javascript
handleStep1(); // Process credentials
handleStep2(); // Process OTP
handleStep3(); // Process facial recognition
captureFacialImage(); // Capture from camera
goToStep(); // Navigate steps
showAlert(); // Display messages
setupFacialCamera(); // Initialize camera
```

---

## 💾 Database Schema

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
);
```

**Indexes:**

```sql
CREATE INDEX idx_users_username ON users(username);
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
);
```

### OTP Attempts Table

```sql
CREATE TABLE otp_attempts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    otp_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    used BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0
);
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
);
```

**Indexes:**

```sql
CREATE INDEX idx_login_history_user ON login_history(user_id);
```

---

## 🔌 API Documentation

### Authentication Endpoints

#### 1. User Registration

```
POST /api/auth/register
Content-Type: multipart/form-data

Parameters:
- full_name: string (required)
- username: string (required, unique)
- email: string (required, unique)
- phone_number: string (optional)
- password: string (required)
- facial_image: file (required)

Response (Success):
{
    "user_id": 1,
    "message": "User created successfully",
    "email": "user@example.com"
}

Response (Error):
{
    "message": "Username already exists"
}
```

#### 2. Step 1 - Credentials

```
POST /api/auth/step1
Content-Type: application/json

Body:
{
    "username": "johndoe",
    "password": "SecurePass123!"
}

Response (Success):
{
    "user_id": 1,
    "message": "OTP sent to your email"
}

Response (Error):
{
    "message": "Invalid username or password"
}
```

#### 3. Step 2 - OTP Verification

```
POST /api/auth/step2
Content-Type: application/json

Body:
{
    "user_id": 1,
    "otp_code": "123456"
}

Response (Success):
{
    "message": "OTP verified",
    "user_id": 1
}

Response (Error):
{
    "message": "Invalid or expired OTP"
}
```

#### 4. Step 3 - Facial Recognition

```
POST /api/auth/step3
Content-Type: multipart/form-data

Parameters:
- user_id: integer (required)
- image: file (required, JPEG)

Response (Success):
{
    "message": "Authentication successful",
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user_id": 1,
    "user": { "id": 1 }
}

Response (Error):
{
    "message": "Facial recognition failed"
}
```

#### 5. Get User Profile

```
GET /api/user/profile
Authorization: Bearer <jwt_token>

Response:
{
    "id": 1,
    "username": "johndoe",
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "admin"
}
```

#### 6. Logout

```
POST /logout
Authorization: Bearer <jwt_token>

Response:
{
    "message": "Logged out successfully"
}
```

---

## 🔒 Security Implementation

### Password Security

**Hashing Algorithm: Bcrypt**

```python
import bcrypt

# Generate hash
password = "UserPassword123!"
salt = bcrypt.gensalt(rounds=10)
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

# Verify password
is_valid = bcrypt.checkpw(password.encode('utf-8'), password_hash)
```

**Benefits:**

- Salts automatically included
- Cost factor of 10 makes brute-force difficult
- Password never stored in plaintext

### Session Management

**JWT Token Structure:**

```
Header:
{
    "typ": "JWT",
    "alg": "HS256"
}

Payload:
{
    "user_id": 1,
    "username": "johndoe",
    "exp": 1712345600,
    "iat": 1712259200
}

Signature:
HMACSHA256(
    base64UrlEncode(header) + "." +
    base64UrlEncode(payload),
    secret
)
```

**Validation:**

```python
import jwt
from config import SECRET_KEY

# Create token
payload = {
    'user_id': user_id,
    'username': username,
    'exp': datetime.utcnow() + timedelta(hours=24),
    'iat': datetime.utcnow()
}
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

# Verify token
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
except jwt.ExpiredSignatureError:
    # Token expired
except jwt.InvalidTokenError:
    # Token invalid
```

### OTP Security

**OTP Generation & Verification:**

```python
import random
import secrets
from datetime import datetime, timedelta

# Generate OTP
otp_code = str(random.randint(100000, 999999))  # 6 digits

# Set expiration
expires_at = datetime.utcnow() + timedelta(minutes=10)

# Verify OTP
def verify_otp(stored_code, submitted_code, expires_at):
    if datetime.utcnow() > expires_at:
        return False  # Expired
    if stored_code != submitted_code:
        return False  # Mismatch
    return True
```

**Features:**

- Random 6-digit generation
- 10-minute expiration
- Single-use validation
- Database tracking

### Facial Recognition Security

**Embedding Comparison:**

```python
import numpy as np

# Calculate cosine similarity
def calculate_similarity(embedding1, embedding2):
    return np.dot(embedding1, embedding2) / (
        np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )

# Threshold-based verification
threshold = 0.6
similarity = calculate_similarity(login_embedding, stored_embedding)
is_verified = similarity >= threshold
```

---

## 📋 Setup Instructions

### Step 1: PostgreSQL Installation

**macOS:**

```bash
brew install postgresql
brew services start postgresql
createdb facial_attendance_db
```

**Linux:**

```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb facial_attendance_db
```

**Windows:**

- Download from postgresql.org
- Run installer
- Remember the password
- Use pgAdmin to create `facial_attendance_db`

### Step 2: Dependencies Installation

```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/facial_attendance_db
SECRET_KEY=<generate-with-python-secrets>
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=<app-specific-password>
```

### Step 4: Database Initialization

```python
from database import db

# Initialize all tables
db.init_db()
print("Database initialized!")
```

### Step 5: Run Application

```bash
python app_auth.py
```

Application running on: `http://localhost:5000`

---

## 🧪 Testing Scenarios

### Test 1: User Registration

1. Navigate to /register
2. Fill all fields
3. Capture facial image
4. Submit
5. Verify user created in database

### Test 2: 3FA Login

1. Navigate to /login
2. Enter credentials
3. Check email for OTP
4. Enter OTP
5. Capture facial recognition
6. Verify JWT token received

### Test 3: Session Management

1. Login successfully
2. Check localStorage for token
3. Open Developer Tools → Network
4. Verify Authorization header in requests
5. Logout
6. Verify token removed

### Test 4: Security

1. Try invalid password
2. Verify login attempt logged
3. Try expired OTP
4. Try invalid facial match
5. Check login_history table

---

## 🚀 Deployment Checklist

- [ ] Change SECRET_KEY to random value
- [ ] Set DEBUG=False in production
- [ ] Configure strong database password
- [ ] Setup HTTPS/SSL certificates
- [ ] Configure email provider credentials
- [ ] Setup regular database backups
- [ ] Enable firewall rules
- [ ] Configure CORS origins
- [ ] Setup monitoring & logging
- [ ] Test complete flow
- [ ] Document API endpoints
- [ ] Create admin accounts
- [ ] Setup rate limiting

---

## 📞 Troubleshooting

### Issue: "psycopg2 module not found"

```bash
pip install psycopg2-binary
```

### Issue: "Database connection refused"

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Or macOS
brew services list | grep postgresql
```

### Issue: "OTP email not received"

1. Verify SMTP credentials in .env
2. Check Gmail app password (not regular password)
3. Check spam folder
4. Review server logs

### Issue: "Facial recognition fails"

- Ensure good lighting
- Position face clearly
- Adjust threshold in auth.py (line ~140)
- Verify camera permissions

---

**Congratulations! Your 3FA authentication system is fully implemented and ready to use!** 🎉
