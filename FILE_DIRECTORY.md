# 📚 File Directory & Documentation

## Project Files Overview

### 🎯 Main Application Files

| File          | Type   | Purpose                     | Status     |
| ------------- | ------ | --------------------------- | ---------- |
| `app_auth.py` | Python | Enhanced Flask app with 3FA | ✨ NEW     |
| `app.py`      | Python | Original Flask app          | ✓ Existing |
| `model.py`    | Python | Facial recognition model    | ✓ Existing |
| `database.py` | Python | PostgreSQL manager          | ✨ NEW     |
| `auth.py`     | Python | Authentication utilities    | ✨ NEW     |
| `config.py`   | Python | Configuration settings      | ✨ NEW     |

---

## 🎨 Frontend Files

### Templates (HTML)

| File                               | Purpose                       | Status     |
| ---------------------------------- | ----------------------------- | ---------- |
| `templates/login.html`             | 3FA login interface           | ✨ NEW     |
| `templates/register.html`          | User registration page        | ✨ NEW     |
| `templates/dashboard.html`         | Main authenticated dashboard  | ✨ NEW     |
| `templates/add_student.html`       | Add student for attendance    | ✓ Existing |
| `templates/mark_attendance.html`   | Facial recognition attendance | ✓ Existing |
| `templates/attendance_record.html` | Attendance records view       | ✓ Existing |
| `templates/index.html`             | Original dashboard            | ✓ Existing |

### JavaScript Files

| File                              | Purpose                 | Status     |
| --------------------------------- | ----------------------- | ---------- |
| `static/js/login.js`              | 3FA login flow logic    | ✨ NEW     |
| `static/js/dashboard.js`          | Dashboard functionality | ✓ Existing |
| `static/js/camera_add_student.js` | Student camera capture  | ✓ Existing |
| `static/js/camera_mark.js`        | Attendance camera       | ✓ Existing |

### CSS & Static Files

| File                   | Purpose          | Status     |
| ---------------------- | ---------------- | ---------- |
| `static/css/style.css` | Styling          | ✓ Existing |
| `static/images/bg.png` | Background image | ✓ Existing |

---

## 📋 Configuration Files

| File               | Purpose                             | Status     |
| ------------------ | ----------------------------------- | ---------- |
| `requirements.txt` | Python dependencies                 | ✏️ UPDATED |
| `.env.example`     | Environment template                | ✨ NEW     |
| `.env`             | Environment variables (create this) | ⚠️ CREATE  |
| `.gitignore`       | Git ignore rules                    | ✓ Existing |
| `README.md`        | Original project README             | ✓ Existing |

---

## 📖 Documentation Files

### Quick Reference

| File                         | Description            | Read Time |
| ---------------------------- | ---------------------- | --------- |
| `QUICKSTART.md`              | 5-minute setup guide   | 5 min     |
| `IMPLEMENTATION_COMPLETE.md` | Summary of all changes | 10 min    |

### Detailed Guides

| File                               | Description                      | Read Time |
| ---------------------------------- | -------------------------------- | --------- |
| `3FA_SETUP_GUIDE.md`               | Comprehensive setup instructions | 20 min    |
| `3FA_IMPLEMENTATION_SUMMARY.md`    | Feature overview & architecture  | 15 min    |
| `COMPLETE_IMPLEMENTATION_GUIDE.md` | Full technical documentation     | 30 min    |
| `FILE_DIRECTORY.md`                | This file                        | 5 min     |

---

## 📁 Directory Structure

```
Digital-Facial-Recognisation-Attendance-System/
│
├── 📄 Python Backend Files
│   ├── app_auth.py              ✨ NEW - Enhanced Flask with 3FA
│   ├── app.py                   ✓ Original Flask app
│   ├── model.py                 ✓ Facial recognition
│   ├── database.py              ✨ NEW - PostgreSQL manager
│   ├── auth.py                  ✨ NEW - Authentication
│   └── config.py                ✨ NEW - Configuration
│
├── 📁 templates/
│   ├── login.html               ✨ NEW - 3FA login
│   ├── register.html            ✨ NEW - Registration
│   ├── dashboard.html           ✨ NEW - Auth dashboard
│   ├── add_student.html         ✓ Add student
│   ├── mark_attendance.html     ✓ Mark attendance
│   ├── attendance_record.html   ✓ Records
│   └── index.html               ✓ Original dashboard
│
├── 📁 static/
│   ├── js/
│   │   ├── login.js             ✨ NEW - Login logic
│   │   ├── dashboard.js         ✓ Dashboard
│   │   ├── camera_add_student.js ✓ Student camera
│   │   └── camera_mark.js       ✓ Attendance camera
│   ├── css/
│   │   └── style.css            ✓ Styling
│   └── images/
│       └── bg.png               ✓ Background
│
├── 📁 dataset/                  ✓ Student facial images
│   └── [student_id]/
│       └── [face_images].jpg
│
├── 🔧 Configuration & Dependencies
│   ├── requirements.txt         ✏️ UPDATED - All packages
│   ├── .env.example            ✨ NEW - Env template
│   ├── .env                    ⚠️ CREATE - Your config
│   └── .gitignore             ✓ Git ignore
│
├── 📚 Documentation
│   ├── QUICKSTART.md           ✨ NEW - 5-min setup
│   ├── IMPLEMENTATION_COMPLETE.md ✨ NEW - Summary
│   ├── 3FA_SETUP_GUIDE.md     ✨ NEW - Detailed guide
│   ├── 3FA_IMPLEMENTATION_SUMMARY.md ✨ NEW - Features
│   ├── COMPLETE_IMPLEMENTATION_GUIDE.md ✨ NEW - Full guide
│   ├── FILE_DIRECTORY.md       ✨ NEW - This file
│   └── README.md              ✓ Original README
│
├── 📊 Database Files
│   ├── attendance.db           ✓ SQLite (original)
│   ├── train_status.json       ✓ Training status
│   └── model.pkl              ✓ Trained model
│
├── 🔍 Version Control
│   └── .git/                   ✓ Git repository
│
└── 🐍 Virtual Environment
    └── venv/                   ✓ Python venv
```

---

## 🚀 Getting Started - Which File to Read First?

### 👤 I'm New to This Project

**Start Here:** `QUICKSTART.md` (5 minutes)

- 5-minute setup guide
- Installation steps
- Access URLs
- Troubleshooting

### 👨‍💻 I'm a Developer

**Read:** `COMPLETE_IMPLEMENTATION_GUIDE.md` (30 minutes)

- Complete technical details
- API documentation
- Database schema
- Code examples

### 🔧 I'm Setting Up for Production

**Read:** `3FA_SETUP_GUIDE.md` (20 minutes)

- Production setup
- Email configuration
- Security checklist
- Deployment tips

### 📊 I Want to Understand the Features

**Read:** `3FA_IMPLEMENTATION_SUMMARY.md` (15 minutes)

- Feature overview
- Architecture diagrams
- Security features
- Next steps

### 🎯 I Want a Quick Summary

**Read:** `IMPLEMENTATION_COMPLETE.md` (10 minutes)

- Summary of changes
- New features
- Quick start
- Technology stack

---

## 📋 What Each File Does

### Backend Python Files

#### `app_auth.py` (NEW)

**What it does:**

- Main Flask application with 3FA authentication
- Handles user registration, login, and dashboard
- Manages JWT tokens and sessions
- Integrates facial recognition

**Key functions:**

```python
auth_step1()      # Username & password verification
auth_step2()      # OTP verification
auth_step3()      # Facial recognition
logout()          # Session termination
dashboard()       # Protected route
```

**When to use:**

- Production deployment
- 3FA authentication needed
- JWT token security required

#### `database.py` (NEW)

**What it does:**

- PostgreSQL connection and management
- User CRUD operations
- Session tracking
- OTP handling
- Login history recording

**Key classes:**

```python
DatabaseManager   # Main database interface
```

**Key methods:**

```python
init_db()                    # Create tables
create_user()                # New user
get_user_by_username()       # Query user
verify_otp()                 # Check OTP
record_login_attempt()       # Audit trail
```

#### `auth.py` (NEW)

**What it does:**

- Authentication utilities
- JWT token creation/verification
- OTP generation/sending
- Session token generation

**Key class:**

```python
AuthenticationManager        # Auth utilities
```

**Key methods:**

```python
create_jwt_token()           # Generate JWT
verify_jwt_token()           # Check JWT
generate_otp()               # Create OTP
send_otp_email()            # Send email
setup_2fa()                 # Setup TOTP
```

#### `config.py` (NEW)

**What it does:**

- Centralized configuration
- Environment variable loading
- Secret management
- Default settings

**Configuration options:**

```python
DATABASE_URL                # PostgreSQL connection
SECRET_KEY                  # Flask secret
DEBUG                       # Debug mode
SMTP_SERVER                 # Email server
SMTP_USERNAME               # Email user
SMTP_PASSWORD               # Email pass
```

#### `model.py` (EXISTING)

**What it does:**

- Facial recognition model training
- Face embedding extraction
- Face comparison and recognition

**Key functions:**

```python
crop_face_and_embed()        # Extract embedding
extract_embedding_for_image() # Get face embedding
train_model_background()      # Train model
load_model_if_exists()       # Load trained model
predict_with_model()         # Recognize face
```

#### `app.py` (EXISTING)

**What it does:**

- Original Flask application
- Student management
- Attendance marking
- Model training
- Record management

**Can still be used:**

- For original features
- Without authentication
- For attendance tracking only

---

### Frontend Template Files

#### `templates/login.html` (NEW)

**What it displays:**

- Step-by-step 3FA login interface
- Username & password input
- OTP code entry (6 fields)
- Facial recognition camera
- Progress indicators
- Real-time validation

#### `templates/register.html` (NEW)

**What it displays:**

- User registration form
- Password strength validator
- Facial image capture
- Form validation messages
- Account creation confirmation

#### `templates/dashboard.html` (NEW)

**What it displays:**

- Main user dashboard
- Attendance statistics
- 30-day chart
- Quick action buttons
- User profile menu
- Logout option

#### `templates/add_student.html` (EXISTING)

**What it displays:**

- Student information form
- Camera capture interface
- Photo progress bar
- Student record completion

#### `templates/mark_attendance.html` (EXISTING)

**What it displays:**

- Facial recognition camera
- Live face detection
- Attendance confirmation
- Student identification

---

### Frontend JavaScript Files

#### `static/js/login.js` (NEW)

**What it does:**

- Handle 3FA login flow
- Validate inputs
- Manage multi-step form
- Camera operations
- API communication

**Key functions:**

```javascript
handleStep1(); // Credentials
handleStep2(); // OTP
handleStep3(); // Facial
captureFacialImage(); // Camera
goToStep(); // Navigation
```

#### `static/js/dashboard.js` (EXISTING)

**What it does:**

- Dashboard functionality
- Chart rendering
- Statistics updates
- Training progress

#### `static/js/camera_add_student.js` (EXISTING)

**What it does:**

- Capture student photos
- Upload images
- Progress tracking

---

### Configuration Files

#### `requirements.txt` (UPDATED)

**Contains:**

- All Python dependencies
- Version specifications
- Grouped by category

**Key packages added:**

- psycopg2-binary (PostgreSQL)
- pyjwt (JWT tokens)
- bcrypt (Password hashing)
- pyotp (OTP generation)
- qrcode (QR codes)

#### `.env.example` (NEW)

**Shows:**

- All configurable options
- Example values
- Comments for guidance
- Alternative settings

**Create `.env` from this:**

```bash
cp .env.example .env
# Edit .env with your values
```

---

### Documentation Files

#### `QUICKSTART.md` (NEW)

**Purpose:** Get started in 5 minutes
**Contains:**

- Installation steps
- PostgreSQL setup
- Configuration
- Access URLs

#### `3FA_SETUP_GUIDE.md` (NEW)

**Purpose:** Complete setup documentation
**Contains:**

- Detailed installation
- API documentation
- Database schema
- Troubleshooting

#### `3FA_IMPLEMENTATION_SUMMARY.md` (NEW)

**Purpose:** Feature overview
**Contains:**

- Feature list
- Architecture diagrams
- Security details
- Next steps

#### `COMPLETE_IMPLEMENTATION_GUIDE.md` (NEW)

**Purpose:** Full technical documentation
**Contains:**

- Architecture details
- Authentication flows
- File descriptions
- Code examples
- Testing scenarios

#### `IMPLEMENTATION_COMPLETE.md` (NEW)

**Purpose:** Summary of changes
**Contains:**

- What's new
- File listings
- Quick start
- Next steps

#### `FILE_DIRECTORY.md` (NEW - This File)

**Purpose:** File reference guide
**Contains:**

- All files and purposes
- Directory structure
- Getting started guide
- File descriptions

---

## 🎯 Common Tasks - Which File to Edit?

### I want to change the password hashing algorithm

**Edit:** `database.py` → `verify_password()` method

### I want to change OTP expiration time

**Edit:** `database.py` → `create_otp()` method

### I want to change JWT token expiration

**Edit:** `config.py` → `JWT_EXPIRATION_HOURS`

### I want to customize the login UI

**Edit:** `templates/login.html` and `static/js/login.js`

### I want to add more database fields

**Edit:** `database.py` → `init_db()` method

### I want to configure email provider

**Edit:** `.env` file → SMTP settings

### I want to change facial recognition threshold

**Edit:** `app_auth.py` → `/api/auth/step3` route

### I want to add a new authentication method

**Edit:** `auth.py` → Add new method to `AuthenticationManager`

### I want to customize the dashboard

**Edit:** `templates/dashboard.html` and `static/js/dashboard.js`

---

## 🔒 Security-Related Files

| File          | Security Feature                  |
| ------------- | --------------------------------- |
| `database.py` | Password hashing, session storage |
| `auth.py`     | JWT generation, OTP handling      |
| `config.py`   | Secret key management             |
| `.env`        | Credential storage (local only)   |
| `app_auth.py` | @login_required decorator         |

---

## 📊 Database-Related Files

| File          | Database Purpose             |
| ------------- | ---------------------------- |
| `database.py` | All database operations      |
| `config.py`   | Connection string            |
| `.env`        | Database credentials         |
| `app_auth.py` | Database initialization call |

---

## 🚀 Deployment Files

| File                 | For Production        |
| -------------------- | --------------------- |
| `requirements.txt`   | Install all packages  |
| `.env`               | Set production values |
| `app_auth.py`        | Use instead of app.py |
| `3FA_SETUP_GUIDE.md` | Production setup      |

---

## ✅ Checklist for First-Time Users

- [ ] Read `QUICKSTART.md`
- [ ] Install `requirements.txt`
- [ ] Create `.env` from `.env.example`
- [ ] Setup PostgreSQL database
- [ ] Run `python -c "from database import db; db.init_db()"`
- [ ] Start application with `python app_auth.py`
- [ ] Visit `http://localhost:5000/register`
- [ ] Create a test account
- [ ] Test 3FA login flow
- [ ] Access dashboard
- [ ] Read detailed guide if needed

---

## 📞 Getting Help

### If you don't understand something:

1. **Check documentation** - Look in relevant `.md` file
2. **Search for function** - Check which file contains it
3. **Read comments** - Code has inline explanations
4. **Check examples** - Look for usage examples

### If something doesn't work:

1. **Check troubleshooting** - In `3FA_SETUP_GUIDE.md`
2. **Check requirements** - In `requirements.txt`
3. **Check configuration** - In `.env` file
4. **Check database** - In `database.py` initialization

---

**Happy coding! 🎉**

For more information, start with `QUICKSTART.md` or `COMPLETE_IMPLEMENTATION_GUIDE.md`
