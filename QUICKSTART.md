# 🚀 Quick Start Guide - 3FA Authentication System

## 5-Minute Setup

### 1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 2. **Setup PostgreSQL**

**macOS:**

```bash
brew install postgresql
brew services start postgresql
createdb facial_attendance_db
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb facial_attendance_db
```

**Windows:**

- Download from https://www.postgresql.org/download/windows/
- During installation, remember the password you set
- Open pgAdmin and create database `facial_attendance_db`

### 3. **Configure Environment**

Copy the example file and edit:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/facial_attendance_db
SECRET_KEY=your-generated-secret-key
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. **Initialize Database**

```bash
python -c "from database import db; db.init_db(); print('✅ Database initialized!')"
```

### 5. **Run the Application**

```bash
python app_auth.py
```

**Output should show:**

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 6. **Access the Application**

Open in browser:

- **Register**: http://localhost:5000/register
- **Login**: http://localhost:5000/login
- **Dashboard**: http://localhost:5000/dashboard (after login)

---

## 📝 Test Account (Optional - After DB Setup)

Create a test user manually:

```python
from database import db

# Initialize database
db.init_db()

# Create test user
user_id = db.create_user(
    username='testuser',
    email='test@example.com',
    password='TestPass123!',
    full_name='Test User',
    phone_number='+1234567890'
)

print(f"✅ Test user created with ID: {user_id}")
```

---

## 🔐 Gmail Setup for OTP (Recommended)

1. Go to **myaccount.google.com**
2. Select **Security** from left menu
3. Enable **2-Step Verification**
4. Go to **App passwords** (search for it)
5. Select "Mail" and "Windows Computer"
6. Copy the **16-character password**
7. Paste in `.env` as `SMTP_PASSWORD`

---

## 📊 3FA Login Flow Explained

```
┌─────────────────────┐
│  User Registration  │
│  (Email + Face)     │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Login Page        │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│  STEP 1: Credentials│
│  Username + Password│
└──────────┬──────────┘
           ↓
    OTP sent to email
           ↓
┌─────────────────────┐
│  STEP 2: Email OTP  │
│  Enter 6-digit code │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ STEP 3: Facial Rec. │
│  Verify with camera │
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   JWT Token Issued  │
│   Redirect to Dashboard
└─────────────────────┘
```

---

## 🛠️ Troubleshooting

### Database Connection Error

```
Error: FATAL:  role "postgres" does not exist
```

**Solution:**

```bash
sudo -u postgres psql
CREATE USER postgres SUPERUSER;
```

### "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### "OTP not received"

1. Check `.env` SMTP settings
2. Verify email password is app-specific password (not Gmail password)
3. Check spam folder
4. Try Gmail settings with `SMTP_PORT=465` instead of 587

### Camera not working

- Grant browser camera permissions
- Check if another app is using camera
- Try different browser (Chrome/Firefox)

### Port 5000 already in use

```bash
python app_auth.py --port 5001
```

---

## 📁 Project Structure

```
.
├── app_auth.py                 # Main Flask app (3FA enabled)
├── database.py                 # PostgreSQL database layer
├── auth.py                     # Authentication logic
├── config.py                   # Configuration settings
├── model.py                    # Facial recognition model
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── 3FA_SETUP_GUIDE.md         # Detailed setup documentation
├── QUICKSTART.md              # This file
│
├── templates/
│   ├── login.html             # 3FA Login interface
│   ├── register.html          # User registration
│   ├── dashboard.html         # Main dashboard
│   ├── add_student.html       # Add student for attendance
│   ├── mark_attendance.html   # Facial recognition attendance
│   └── ...
│
├── static/
│   ├── js/
│   │   ├── login.js          # Login flow logic
│   │   ├── dashboard.js      # Dashboard functionality
│   │   └── ...
│   ├── css/
│   │   └── style.css
│   └── images/
│
└── dataset/                    # Student facial images
    └── [student_id]/
        └── [face_images].jpg
```

---

## 🔒 Security Best Practices

| Task                              | Status  |
| --------------------------------- | ------- |
| Change `SECRET_KEY` in production | ⚠️ TODO |
| Use strong database password      | ⚠️ TODO |
| Enable HTTPS/SSL                  | ⚠️ TODO |
| Set `DEBUG=False` in production   | ⚠️ TODO |
| Configure firewall rules          | ⚠️ TODO |
| Enable PostgreSQL authentication  | ⚠️ TODO |
| Setup automated backups           | ⚠️ TODO |

---

## 📞 Support

### Common Issues & Solutions

**Q: How do I reset a user password?**
A: Run in Python shell:

```python
from database import db
import bcrypt

password_hash = bcrypt.hashpw(b'NewPassword123!', bcrypt.gensalt()).decode()
# Then update in database
```

**Q: How do I view login history?**
A: Query the database:

```python
conn = db.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM login_history ORDER BY login_time DESC LIMIT 10")
for row in cursor.fetchall():
    print(row)
```

**Q: Can I use MySQL instead of PostgreSQL?**
A: Yes, but requires code changes. PostgreSQL is recommended.

---

## 🎯 Next Steps

1. ✅ Complete 5-minute setup
2. 📧 Configure email provider
3. 🧪 Create test accounts
4. 🎓 Add students and train model
5. 🔍 Test complete 3FA flow
6. 📊 Review dashboard
7. 🚀 Deploy to production

---

## 🎓 Learning Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **PostgreSQL Tutorial**: https://www.postgresql.org/docs/
- **Face Recognition**: https://github.com/ageitgey/face_recognition
- **JWT**: https://jwt.io/introduction
- **PyOTP**: https://pyauth.github.io/pyotp/

---

**Created: 2026**  
**Last Updated: 2026-04-05**  
**Version: 1.0.0**
