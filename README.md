# 🎯 Digital Facial Recognition Attendance System with 3FA

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Complete Setup Guide](#complete-setup-guide)
5. [Gmail OTP Configuration](#gmail-otp-configuration)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Security](#security)

---

## 🌟 System Overview

This is a **Production-Ready Digital Facial Recognition Attendance System** with **3-Factor Authentication (3FA)**:

1. **Factor 1**: Username & Password
2. **Factor 2**: Email OTP (One-Time Password)
3. **Factor 3**: Facial Recognition (Optional for development)

---

## 🚀 Complete Setup Guide

### Step 1: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

### Step 3: Create Environment File

```bash
# Copy the example environment file
cp .env.example .env
```

### Step 4: Configure Environment Variables

Open `.env` file and add:

```env
# Database Configuration
DATABASE_URL=sqlite:///attendance.db

# Secret Key (generate one using: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-generated-secret-key

# Email Configuration (Gmail)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password

# Application Settings
DEBUG=False
PORT=5000
HOST=0.0.0.0
```

### Step 5: Setup Gmail for OTP

#### 5.1: Enable 2-Step Verification

1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the setup process

#### 5.2: Generate App-Specific Password

1. After 2FA is enabled, go to https://myaccount.google.com/apppasswords
2. Select: App = Mail, Device = Windows Computer
3. Click "Generate"
4. Copy the 16-character password

#### 5.3: Add to .env

```env
SMTP_USERNAME=your-gmail@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

### Step 6: Initialize Database

```bash
# Initialize the database
python -c "from database import db; db.init_db(); print('Database initialized!')"
```

---

## 🏃 Running the Application

### Development Server

```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Run the application
python app_auth.py
```

### Production Server

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_auth:app
```

### Access Application

Open browser and go to: `http://localhost:5000`

---

## 🔗 API Endpoints

### Authentication Endpoints

```
GET    /register                      - Registration page
POST   /api/auth/register             - Create user account
GET    /login                         - Login page
POST   /api/auth/step1                - Verify username & password
POST   /api/auth/step2                - Verify OTP code
POST   /api/auth/step3                - Verify facial recognition
POST   /logout                        - End session
```

### Protected Routes

```
GET    /dashboard                     - Main dashboard (requires auth)
GET    /api/user/profile              - User profile (requires auth)
GET    /mark_attendance               - Mark attendance page
POST   /recognize_face                - Facial recognition
GET    /attendance_record             - View records
GET    /download_csv                  - Download CSV
```

---

## ✨ Features

✅ 3-Factor Authentication (Password → OTP → Facial)  
✅ User registration and management  
✅ Facial recognition with MediaPipe + OpenCV  
✅ Email OTP delivery via Gmail  
✅ JWT session tokens (24-hour expiration)  
✅ Attendance tracking and reporting  
✅ Modern, responsive UI design  
✅ Bcrypt password hashing  
✅ Complete error handling  
✅ Activity logging

---

## 🧪 Testing

### Test Registration

```bash
python test_register.py
```

### Manual Testing

1. Register at: http://localhost:5000/register
2. Login at: http://localhost:5000/login
3. Complete 3FA steps (password → OTP → facial)
4. Access dashboard

---

## 🐛 Troubleshooting

| Problem                  | Solution                                                                   |
| ------------------------ | -------------------------------------------------------------------------- |
| Module not found         | Activate venv and run: `pip install -r requirements.txt --force-reinstall` |
| Database error           | Run: `python -c "from database import db; db.init_db()"`                   |
| SMTP failed              | Verify 2FA enabled, app-specific password correct, firewall not blocking   |
| Port in use              | Run: `lsof -i :5000` then `kill -9 <PID>` or use different port            |
| Camera not working       | Allow browser permissions, try different browser                           |
| Facial recognition fails | Ensure good lighting, face clearly visible, centered in frame              |

---

## 🔐 Security Features

- ✅ Bcrypt password hashing (10 rounds)
- ✅ JWT tokens with expiration
- ✅ OTP with 10-minute expiration
- ✅ Secure session management
- ✅ Input validation (frontend & backend)
- ✅ SQL injection prevention
- ✅ XSS prevention

---

## 📊 File Structure

```
├── app_auth.py                    # Main Flask application
├── auth.py                        # Authentication utilities
├── database.py                    # Database operations
├── model.py                       # Facial recognition
├── requirements.txt               # Dependencies
├── .env                          # Configuration (create from .env.example)
│
├── templates/
│   ├── login.html                # 3FA login page
│   ├── register.html             # Registration page
│   ├── dashboard.html            # Main dashboard
│   └── ...
│
└── static/
    ├── css/
    ├── js/
    └── images/
```

---

## ✅ Production Checklist

- [ ] Set DEBUG=False in .env
- [ ] Generate strong SECRET_KEY
- [ ] Setup PostgreSQL for production
- [ ] Configure production email provider
- [ ] Setup HTTPS/SSL certificate
- [ ] Enable rate limiting
- [ ] Setup monitoring and logging
- [ ] Test all features thoroughly

---

## 📞 Support

For help:

1. Check documentation files in repository
2. Review browser console for JavaScript errors
3. Check server logs for backend errors
4. Verify .env configuration is correct
5. Test API endpoints individually

---

**Your system is ready when:**
✅ Virtual environment activated  
✅ Dependencies installed  
✅ .env configured with Gmail credentials  
✅ Database initialized  
✅ Application running at http://localhost:5000

---

**Happy coding! 🚀**

Last Updated: April 6, 2026 | Status: Production Ready ✅
